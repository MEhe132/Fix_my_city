"""
Fix My City - Views & API Controllers
Provides citizen reporting, AI image verification pipeline, 1-click social campaigns,
formal PDF petitions, municipal authority dashboard, and public ward accountability board.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Count, Avg, F
from django.contrib import messages
from django.contrib.auth import login, logout
from django.utils import timezone
from .models import Issue, Ward, Department, Upvote, StatusHistory, CustomUser
from .forms import IssueForm, MunicipalTriageForm
from .image_verifier import verify_civic_image
from .campaign_utils import generate_social_campaign_data
from .pdf_generator import generate_petition_pdf
from .notifications import send_council_threshold_email


def index_view(request):
    """
    Main Civic Infrastructure Dashboard (Map + Feed + Filters + Modal)
    """
    ward_filter = request.GET.get('ward', 'all')
    category_filter = request.GET.get('category', 'all')
    status_filter = request.GET.get('status', 'all')
    search_query = request.GET.get('search', '').strip()
    sort_by = request.GET.get('sort', 'upvotes')

    issues = Issue.objects.select_related('ward', 'department').all()

    if ward_filter and ward_filter != 'all':
        issues = issues.filter(ward__id=ward_filter)

    if category_filter and category_filter != 'all':
        issues = issues.filter(category=category_filter)

    if status_filter and status_filter != 'all':
        issues = issues.filter(status=status_filter)

    if search_query:
        issues = issues.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(address__icontains=search_query) |
            Q(ward__name__icontains=search_query) |
            Q(ward__ward_number__icontains=search_query)
        )

    if sort_by == 'upvotes':
        issues = issues.order_by('-upvotes_count', '-created_at')
    elif sort_by == 'newest':
        issues = issues.order_by('-created_at')
    elif sort_by == 'oldest':
        issues = issues.order_by('created_at')

    # Aggregated civic statistics
    total_count = Issue.objects.count()
    in_progress_count = Issue.objects.filter(status='In Progress').count()
    resolved_count = Issue.objects.filter(status='Resolved').count()
    resolution_rate = round((resolved_count / total_count * 100), 1) if total_count > 0 else 0.0

    stats = {
        'total': total_count,
        'in_progress': in_progress_count,
        'resolved': resolved_count,
        'rate': resolution_rate
    }

    wards = Ward.objects.all().order_by('ward_number')
    form = IssueForm()

    context = {
        'issues': issues,
        'stats': stats,
        'wards': wards,
        'selected_ward': ward_filter,
        'selected_category': category_filter,
        'selected_status': status_filter,
        'search_query': search_query,
        'sort_by': sort_by,
        'form': form,
    }
    return render(request, 'issues/index.html', context)


def issue_detail_view(request, issue_id):
    """
    Dedicated SEO-Indexable public page for an individual civic issue.
    Shows timeline, evidence photo, verification badge, and citizen action buttons.
    """
    issue = get_object_or_404(Issue.objects.select_related('ward', 'department', 'reporter'), id=issue_id)
    history = issue.status_logs.select_related('changed_by').all().order_by('timestamp')
    campaign = generate_social_campaign_data(issue, request)
    triage_form = MunicipalTriageForm(initial={
        'status': issue.status,
        'department': issue.department,
        'resolution_notes': issue.resolution_notes
    })

    context = {
        'issue': issue,
        'history': history,
        'campaign': campaign,
        'triage_form': triage_form,
    }
    return render(request, 'issues/issue_detail.html', context)


def create_issue_view(request):
    """
    Processes Photo Upload, AI/EXIF Combine Verification, and Issue Submission.
    """
    if request.method == 'POST':
        form = IssueForm(request.POST, request.FILES)
        photo_file = request.FILES.get('photo')

        if form.is_valid():
            issue = form.save(commit=False)

            # Link logged-in reporter if authenticated
            if request.user.is_authenticated:
                issue.reporter = request.user
                if not issue.reporter_name or issue.reporter_name == 'Anonymous Citizen':
                    issue.reporter_name = request.user.get_full_name() or request.user.username

            # 1. Combine AI Verification & Hardware EXIF Pipeline
            if photo_file:
                verification = verify_civic_image(photo_file)

                # Rejection if flagged as AI or digital art
                if not verification['is_genuine']:
                    error_msg = verification.get(
                        'alert_message',
                        "⚠️ Image detected as AI-generated or digital art. Please upload a genuine on-site photograph."
                    )
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'status': 'error', 'ai_flagged': True, 'message': error_msg}, status=400)
                    messages.error(request, error_msg)
                    return redirect('index')

                # Store verification results
                issue.verification_status = verification['verification_status']
                issue.ai_confidence_score = verification['confidence_score']
                issue.camera_make = verification['camera_make']
                issue.camera_model = verification['camera_model']
                issue.exif_timestamp = verification['exif_timestamp']

                # Automatically adopt EXIF GPS if not manually dragged on map
                if verification['lat'] and verification['lng'] and (not issue.latitude or issue.latitude == 23.8103):
                    issue.latitude = verification['lat']
                    issue.longitude = verification['lng']

            # Dhaka center default fallback
            if not issue.latitude or not issue.longitude:
                issue.latitude = 23.8103
                issue.longitude = 90.4125

            issue.save()

            # Record initial status log
            StatusHistory.objects.create(
                issue=issue,
                changed_by=request.user if request.user.is_authenticated else None,
                old_status='Created',
                new_status=issue.status,
                comment=f"Report logged by {issue.reporter_name}. Verification: {issue.verification_status}."
            )

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success', 'issue_id': issue.id, 'redirect_url': f'/issues/{issue.id}/'})

            messages.success(request, f"Issue #{issue.id} registered successfully with {issue.verification_status}!")
            return redirect('issue_detail', issue_id=issue.id)
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                errors = form.errors.as_json()
                return JsonResponse({'status': 'error', 'errors': errors}, status=400)
            messages.error(request, "Please check the form inputs.")

    return redirect('index')


def verify_image_api(request):
    """
    Live AJAX pre-flight check when citizen selects a photo in the report modal.
    Returns EXIF camera details, GPS coordinates, or AI digital art warning.
    """
    if request.method == 'POST' and request.FILES.get('photo'):
        photo = request.FILES['photo']
        res = verify_civic_image(photo)
        return JsonResponse({
            'success': res['is_genuine'],
            'verification_status': res['verification_status'],
            'confidence_score': res['confidence_score'],
            'camera_make': res['camera_make'],
            'camera_model': res['camera_model'],
            'lat': res['lat'],
            'lng': res['lng'],
            'alert_message': res.get('alert_message')
        })
    return JsonResponse({'success': False, 'message': 'No image received.'}, status=400)


def api_issues_json(request):
    """
    JSON API endpoint for Leaflet.js map markers with ward and category filters.
    """
    ward_id = request.GET.get('ward')
    category = request.GET.get('category')

    qs = Issue.objects.select_related('ward').all()

    if ward_id and ward_id != 'all':
        qs = qs.filter(ward_id=ward_id)
    if category and category != 'all':
        qs = qs.filter(category=category)

    data = []
    for issue in qs:
        data.append({
            'id': issue.id,
            'title': issue.title,
            'description': issue.description[:120],
            'category': issue.category,
            'severity': issue.severity,
            'lat': issue.latitude,
            'lng': issue.longitude,
            'address': issue.address,
            'ward': issue.ward.ward_number if issue.ward else "Ward Unassigned",
            'ward_name': issue.ward.name if issue.ward else "",
            'upvotes': issue.upvotes_count,
            'status': issue.status,
            'verification_status': issue.verification_status,
            'photo_url': issue.photo.url if issue.photo else None,
            'created_at': issue.created_at.strftime('%Y-%m-%d %H:%M')
        })
    return JsonResponse({'issues': data})


def upvote_issue_api(request, issue_id):
    """
    AJAX Upvote endpoint with session de-duplication and Priority Threshold alert.
    """
    if request.method == 'POST':
        issue = get_object_or_404(Issue, id=issue_id)
        
        # Ensure session exists
        if not request.session.session_key:
            request.session.save()
        session_key = request.session.session_key

        user = request.user if request.user.is_authenticated else None

        # Check existing upvote
        already_voted = False
        if user:
            already_voted = Upvote.objects.filter(issue=issue, user=user).exists()
        else:
            already_voted = Upvote.objects.filter(issue=issue, session_key=session_key).exists()

        if already_voted:
            return JsonResponse({
                'status': 'already_voted',
                'message': 'You have already upvoted this civic issue.',
                'upvotes': issue.upvotes_count
            })

        Upvote.objects.create(
            issue=issue,
            user=user,
            session_key=session_key
        )

        issue.upvotes_count = F('upvotes_count') + 1
        issue.save()
        issue.refresh_from_db()

        # Check threshold (10+ upvotes triggers civic escalation)
        notified = False
        if issue.upvotes_count >= 10 and not issue.threshold_notified:
            issue.threshold_notified = True
            if issue.status == 'Pending Verification':
                issue.status = 'Under Review'
            issue.save()
            send_council_threshold_email(issue)
            notified = True

        return JsonResponse({
            'status': 'success',
            'upvotes': issue.upvotes_count,
            'is_escalated': issue.is_escalated,
            'threshold_notified': notified,
            'message': 'Upvote recorded!'
        })

    return JsonResponse({'status': 'error', 'message': 'Invalid HTTP method'}, status=400)


def download_petition_pdf_view(request, issue_id):
    """
    Generates and downloads the formal municipal complaint letter / memorandum in PDF format.
    """
    issue = get_object_or_404(Issue.objects.select_related('ward', 'department'), id=issue_id)
    pdf_content = generate_petition_pdf(issue)
    
    filename = f"FixMyCity_Petition_Ward_{issue.ward.ward_number if issue.ward else 'General'}_Issue_{issue.id}.pdf"
    response = HttpResponse(pdf_content, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


def social_campaign_api(request, issue_id):
    """
    Returns 1-click social campaign text and links for Facebook & WhatsApp sharing.
    """
    issue = get_object_or_404(Issue.objects.select_related('ward'), id=issue_id)
    data = generate_social_campaign_data(issue, request)
    return JsonResponse({'status': 'success', 'campaign': data})


def accountability_board_view(request):
    """
    Public Ward Accountability Board
    Displays resolution rates, average turnaround days, and performance metrics per ward.
    """
    wards = Ward.objects.annotate(
        issues_total=Count('issues'),
        issues_resolved=Count('issues', filter=Q(issues__status='Resolved')),
        issues_in_progress=Count('issues', filter=Q(issues__status='In Progress')),
        issues_pending=Count('issues', filter=Q(issues__status__in=['Pending Verification', 'Under Review']))
    ).all()

    ward_metrics = []
    total_city_issues = 0
    total_city_resolved = 0

    for w in wards:
        total = w.issues_total
        resolved = w.issues_resolved
        total_city_issues += total
        total_city_resolved += resolved

        rate = round((resolved / total * 100), 1) if total > 0 else 0.0
        avg_days = w.avg_resolution_days

        ward_metrics.append({
            'ward': w,
            'total': total,
            'resolved': resolved,
            'in_progress': w.issues_in_progress,
            'pending': w.issues_pending,
            'rate': rate,
            'avg_days': avg_days,
        })

    # Sort by highest resolution rate
    ward_metrics.sort(key=lambda x: x['rate'], reverse=True)

    citywide_rate = round((total_city_resolved / total_city_issues * 100), 1) if total_city_issues > 0 else 0.0

    context = {
        'ward_metrics': ward_metrics,
        'citywide_total': total_city_issues,
        'citywide_resolved': total_city_resolved,
        'citywide_rate': citywide_rate,
    }
    return render(request, 'issues/accountability_board.html', context)


def authority_dashboard_view(request):
    """
    Municipal Authority & Ward Official Dashboard
    Allows officials to triage issues, update lifecycle statuses, and upload resolution proof photos.
    """
    # Demo/Convenience: If user is not logged in as official, allow viewing or provide easy toggle
    selected_ward_id = request.GET.get('ward', 'all')
    status_filter = request.GET.get('status', 'all')

    issues = Issue.objects.select_related('ward', 'department').all()

    if selected_ward_id != 'all':
        issues = issues.filter(ward_id=selected_ward_id)
    elif request.user.is_authenticated and request.user.assigned_ward:
        # Default to official's ward
        issues = issues.filter(ward=request.user.assigned_ward)
        selected_ward_id = str(request.user.assigned_ward.id)

    if status_filter != 'all':
        issues = issues.filter(status=status_filter)

    wards = Ward.objects.all().order_by('ward_number')
    departments = Department.objects.all()

    context = {
        'issues': issues,
        'wards': wards,
        'departments': departments,
        'selected_ward': selected_ward_id,
        'selected_status': status_filter,
    }
    return render(request, 'issues/authority_dashboard.html', context)


def update_issue_status_view(request, issue_id):
    """
    Processes official triage actions: changing status, resolution proof photo, remarks.
    """
    issue = get_object_or_404(Issue, id=issue_id)

    if request.method == 'POST':
        form = MunicipalTriageForm(request.POST, request.FILES)
        if form.is_valid():
            old_status = issue.status
            new_status = form.cleaned_data['status']
            department = form.cleaned_data.get('department')
            notes = form.cleaned_data.get('resolution_notes')
            proof_photo = form.cleaned_data.get('resolution_proof_photo')

            issue.status = new_status
            if department:
                issue.department = department
            if notes:
                issue.resolution_notes = notes
            if proof_photo:
                issue.resolution_proof_photo = proof_photo

            if new_status == 'Resolved' and not issue.resolved_at:
                issue.resolved_at = timezone.now()

            issue.save()

            # Record audit history
            StatusHistory.objects.create(
                issue=issue,
                changed_by=request.user if request.user.is_authenticated else None,
                old_status=old_status,
                new_status=new_status,
                comment=notes or f"Status updated to {new_status} by municipal official.",
                proof_photo=proof_photo
            )

            messages.success(request, f"Issue #{issue.id} updated to '{new_status}' successfully.")
            
            next_url = request.POST.get('next') or request.META.get('HTTP_REFERER')
            if next_url:
                return redirect(next_url)
            return redirect('issue_detail', issue_id=issue.id)

    return redirect('issue_detail', issue_id=issue.id)


def quick_demo_role_switch(request, role):
    """
    Convenience view for academic project demo & grading.
    Allows testing both Citizen and Municipal Official personas instantly.
    """
    if role == 'official':
        official_user = CustomUser.objects.filter(role='OFFICIAL').first()
        if not official_user:
            ward = Ward.objects.first()
            dept = Department.objects.first()
            official_user = CustomUser.objects.create_user(
                username='ward19_official',
                email='official19@dncc.gov.bd',
                password='password123',
                role='OFFICIAL',
                assigned_ward=ward,
                assigned_department=dept,
                designation='Assistant Executive Engineer'
            )
        login(request, official_user)
        messages.info(request, f"Logged in as Municipal Authority: {official_user.username}")
        return redirect('authority_dashboard')
    elif role == 'citizen':
        citizen_user = CustomUser.objects.filter(role='CITIZEN').first()
        if not citizen_user:
            citizen_user = CustomUser.objects.create_user(
                username='citizen_arif',
                email='arif@gmail.com',
                password='password123',
                role='CITIZEN'
            )
        login(request, citizen_user)
        messages.info(request, f"Logged in as Citizen: {citizen_user.username}")
        return redirect('index')
    else:
        logout(request)
        messages.info(request, "Logged out to Anonymous Citizen mode.")
        return redirect('index')


def reverse_geocode_api(request):
    """
    High-Speed Free Reverse Geocoding API (OpenStreetMap Nominatim proxy)
    Resolves decimal latitude and longitude into human-readable Bangladesh street address & ward.
    """
    import requests
    lat = request.GET.get('lat')
    lng = request.GET.get('lng')

    if not lat or not lng:
        return JsonResponse({'status': 'error', 'message': 'Latitude and longitude parameters required'}, status=400)

    try:
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lng}&zoom=18&addressdetails=1"
        headers = {'User-Agent': 'FixMyCity-Bangladesh/1.0 (academic civic tracker)'}
        resp = requests.get(url, headers=headers, timeout=3.5)
        if resp.status_code == 200:
            data = resp.json()
            full_addr = data.get('display_name', '')
            details = data.get('address', {})

            road = details.get('road', '')
            suburb = details.get('suburb', details.get('neighbourhood', details.get('residential', '')))
            city_dist = details.get('city_district', details.get('city', 'Dhaka'))
            
            clean_parts = [p for p in [road, suburb, city_dist] if p]
            clean_addr = ", ".join(clean_parts) if clean_parts else full_addr

            return JsonResponse({
                'status': 'success',
                'clean_address': clean_addr,
                'full_address': full_addr,
                'details': details
            })
    except Exception as e:
        pass

    return JsonResponse({
        'status': 'fallback',
        'clean_address': f"Location Pin ({float(lat):.4f}, {float(lng):.4f})"
    })


def ip_locate_api(request):
    """
    Automatic Network IP Geolocation Fallback
    Provides seamless location estimation when browser GPS permission is denied or device lacks GPS chip.
    """
    import requests

    # 1. Try FreeIPAPI (HTTPS)
    try:
        resp = requests.get('https://freeipapi.com/api/json', headers={'User-Agent': 'FixMyCity-BD/1.0'}, timeout=3)
        if resp.status_code == 200:
            d = resp.json()
            lat = d.get('latitude')
            lng = d.get('longitude')
            city = d.get('cityName', 'Dhaka')
            if lat and lng:
                return JsonResponse({
                    'status': 'success',
                    'method': 'ip_network',
                    'lat': float(lat),
                    'lng': float(lng),
                    'city': city,
                    'message': f'Located approx. via Network IP ({city}, Bangladesh)'
                })
    except Exception:
        pass

    # 2. Try IP-API
    try:
        resp = requests.get('http://ip-api.com/json', timeout=3)
        if resp.status_code == 200:
            d = resp.json()
            if d.get('status') == 'success':
                return JsonResponse({
                    'status': 'success',
                    'method': 'ip_network',
                    'lat': float(d.get('lat')),
                    'lng': float(d.get('lon')),
                    'city': d.get('city', 'Dhaka'),
                    'message': f'Located approx. via Network IP ({d.get("city")}, Bangladesh)'
                })
    except Exception:
        pass

    # 3. Default fallback to Dhaka city center
    return JsonResponse({
        'status': 'success',
        'method': 'default_dhaka',
        'lat': 23.8103,
        'lng': 90.4125,
        'city': 'Dhaka',
        'message': 'Defaulted to Dhaka City Center'
    })



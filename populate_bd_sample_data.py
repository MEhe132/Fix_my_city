"""
Seed script to populate realistic Bangladesh wards, municipal departments,
two-tier accounts, and realistic civic infrastructure issues across Dhaka.
"""

import os
import django
from django.utils import timezone
from datetime import timedelta
from PIL import Image, ImageDraw, ImageFont

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fix_my_city.settings')
django.setup()

from django.conf import settings
from issues.models import CustomUser, Ward, Department, Issue, Upvote, StatusHistory

# Create media dirs
os.makedirs(os.path.join(settings.MEDIA_ROOT, 'issue_photos'), exist_ok=True)
os.makedirs(os.path.join(settings.MEDIA_ROOT, 'resolution_proofs'), exist_ok=True)


def generate_civic_sample_image(filename, title, bg_color, text_color):
    """Creates a realistic placeholder photo with canvas rendering."""
    filepath = os.path.join(settings.MEDIA_ROOT, 'issue_photos', filename)
    img = Image.new('RGB', (640, 420), color=bg_color)
    draw = ImageDraw.Draw(img)

    # Add visual design elements (texture / banner)
    draw.rectangle([(20, 20), (620, 400)], outline=(255, 255, 255), width=2)
    draw.rectangle([(30, 30), (610, 80)], fill=(0, 0, 0, 160))
    draw.text((45, 45), f"FIX MY CITY BD EVIDENCE: {title.upper()}", fill=(255, 255, 255))
    
    # Grid & GPS watermark simulation
    draw.line([(320, 100), (320, 360)], fill=(255, 255, 255, 80), width=1)
    draw.line([(40, 230), (600, 230)], fill=(255, 255, 255, 80), width=1)
    draw.text((45, 360), f"GPS VERIFIED ON-SITE EVIDENCE | {timezone.now().strftime('%Y-%m-%d %H:%M')}", fill=(255, 255, 255))
    
    img.save(filepath, 'JPEG', quality=85)
    return f'issue_photos/{filename}'


def run_seed():
    print("Clearing old seed data...")
    Issue.objects.all().delete()
    Ward.objects.all().delete()
    Department.objects.all().delete()
    CustomUser.objects.all().delete()

    print("Creating municipal departments...")
    dept_roads = Department.objects.create(
        name="Civil Infrastructure & Road Engineering (DNCC/DSCC)",
        code="ENG-ROADS",
        description="Responsible for arterial roads, pothole resurfacing, overpasses, and asphalt repairs.",
        emergency_hotline="333",
        contact_email="roads.engineering@dncc.gov.bd"
    )
    dept_wasa = Department.objects.create(
        name="Dhaka WASA (Water Supply & Sewerage Authority)",
        code="WASA",
        description="Pipeline leaks, deep drainage overflow, drinking water pressure, and sewer blockages.",
        emergency_hotline="16162",
        contact_email="complaints@dwasa.org.bd"
    )
    dept_sanitation = Department.objects.create(
        name="Waste Management & Environmental Sanitation",
        code="WASTE-CLEAN",
        description="Secondary transfer stations (STS), illegal municipal garbage dumps, and street sweeping.",
        emergency_hotline="16123",
        contact_email="clean.city@dncc.gov.bd"
    )
    dept_electrical = Department.objects.create(
        name="Public Electrical & LED Streetlighting",
        code="ELEC-LIGHT",
        description="Street illumination, short circuits, exposed high-voltage cables, and lampposts.",
        emergency_hotline="333",
        contact_email="lighting@dncc.gov.bd"
    )
    dept_drainage = Department.objects.create(
        name="Stormwater Drainage & Flood Control",
        code="DRAINAGE",
        description="Monsoon waterlogging mitigation, canal clearance, and surface culverts.",
        emergency_hotline="333",
        contact_email="drainage@dncc.gov.bd"
    )

    print("Creating Dhaka Municipal Wards...")
    w19 = Ward.objects.create(
        ward_number="Ward 19",
        name="Banani, Gulshan-2 & Baridhara",
        city_corporation="Dhaka North City Corporation (DNCC)",
        councillor_name="Md. Mofizur Rahman",
        contact_email="councillor.ward19@dncc.gov.bd",
        contact_phone="+880 1711-543019",
        office_address="House 42, Road 11, Block E, Banani, Dhaka",
        center_latitude=23.7937,
        center_longitude=90.4066
    )

    w18 = Ward.objects.create(
        ward_number="Ward 18",
        name="Shahjadpur, Kalachandpur & Norda",
        city_corporation="Dhaka North City Corporation (DNCC)",
        councillor_name="Zakir Hossain Babul",
        contact_email="councillor.ward18@dncc.gov.bd",
        contact_phone="+880 1711-543018",
        office_address="Shahjadpur Main Road, Gulshan, Dhaka",
        center_latitude=23.8052,
        center_longitude=90.4224
    )

    w11 = Ward.objects.create(
        ward_number="Ward 11",
        name="Mirpur Section 10 & Kallyanpur",
        city_corporation="Dhaka North City Corporation (DNCC)",
        councillor_name="Dewan Abdul Mannan",
        contact_email="councillor.ward11@dncc.gov.bd",
        contact_phone="+880 1711-543011",
        office_address="Mirpur-10 Community Center, Dhaka",
        center_latitude=23.8071,
        center_longitude=90.3686
    )

    w32 = Ward.objects.create(
        ward_number="Ward 32",
        name="Dhanmondi, Sukrabad & Sobhanbagh",
        city_corporation="Dhaka South City Corporation (DSCC)",
        councillor_name="Md. Emdadul Haque",
        contact_email="councillor.ward32@dscc.gov.bd",
        contact_phone="+880 1711-543032",
        office_address="Road 8/A, Dhanmondi R/A, Dhaka",
        center_latitude=23.7461,
        center_longitude=90.3742
    )

    w7 = Ward.objects.create(
        ward_number="Ward 7",
        name="Lalbagh, Chawkbazar & Old Dhaka",
        city_corporation="Dhaka South City Corporation (DSCC)",
        councillor_name="Md. Shahidul Islam",
        contact_email="councillor.ward7@dscc.gov.bd",
        contact_phone="+880 1711-543007",
        office_address="Lalbagh Road, Chawkbazar, Dhaka",
        center_latitude=23.7196,
        center_longitude=90.3882
    )

    print("Creating Two-Tier User Accounts...")
    admin_user = CustomUser.objects.create_superuser(
        username='admin',
        email='admin@fixmycity.bd',
        password='adminpassword123',
        role='ADMIN',
        designation='System Super Administrator'
    )

    official_w19 = CustomUser.objects.create_user(
        username='ward19_official',
        email='official19@dncc.gov.bd',
        password='password123',
        role='OFFICIAL',
        assigned_ward=w19,
        assigned_department=dept_roads,
        designation='Assistant Executive Engineer, Zone-3'
    )

    citizen_arif = CustomUser.objects.create_user(
        username='arif_ahmed',
        email='arif.ahmed@gmail.com',
        password='password123',
        role='CITIZEN',
        phone_number='+880 1712-987654'
    )

    print("Generating photographic assets & realistic issues...")
    p1 = generate_civic_sample_image('banani_crater.jpg', 'Road 11 Crater', (71, 85, 105), (255, 255, 255))
    p2 = generate_civic_sample_image('gulshan_drain.jpg', 'Gulshan Waterlogging', (30, 58, 138), (255, 255, 255))
    p3 = generate_civic_sample_image('dhanmondi_wasa.jpg', 'WASA Pipe Leak', (15, 118, 110), (255, 255, 255))
    p4 = generate_civic_sample_image('mirpur_manhole.jpg', 'Open Manhole Hazard', (185, 28, 28), (255, 255, 255))
    p5 = generate_civic_sample_image('lalbagh_dump.jpg', 'Sanitation Cleared', (22, 101, 52), (255, 255, 255))
    p6 = generate_civic_sample_image('baridhara_light.jpg', 'Streetlight Replaced', (202, 138, 4), (255, 255, 255))

    # Issue 1: High-priority Banani Pothole (Escalated 46 Upvotes)
    i1 = Issue.objects.create(
        title="Dangerous Deep Crater & Exposed Steel Rebar on Road 11 Banani",
        description="A major 4-foot wide crater has opened up in front of Block D, Road 11. Steel construction rebars are protruding, having caused multiple vehicle punctures and severe pedestrian fall hazards during nighttime.",
        category="Pothole",
        severity="Critical",
        ward=w19,
        department=dept_roads,
        latitude=23.7938,
        longitude=90.4045,
        address="Road 11, Block D, Banani, Dhaka-1213",
        photo=p1,
        verification_status="Auto-Verified (Camera EXIF)",
        ai_confidence_score=0.99,
        camera_make="Samsung",
        camera_model="Galaxy S23 Ultra",
        exif_timestamp="2026-10-18 14:22:10",
        upvotes_count=46,
        status="In Progress",
        threshold_notified=True,
        reporter=citizen_arif,
        reporter_name="Arif Ahmed",
        reporter_phone="+880 1712-987654"
    )
    StatusHistory.objects.create(
        issue=i1,
        changed_by=citizen_arif,
        old_status="Created",
        new_status="Pending Verification",
        comment="Citizen submission with verified Samsung Galaxy S23 Ultra camera metadata."
    )
    StatusHistory.objects.create(
        issue=i1,
        changed_by=official_w19,
        old_status="Pending Verification",
        new_status="In Progress",
        comment="Work order #ENG-2026-402 issued to asphalt repair contractor. Materials dispatched."
    )

    # Issue 2: Gulshan-2 Waterlogging (Escalated 18 Upvotes)
    i2 = Issue.objects.create(
        title="Severe Waterlogging & Choked Storm Drain at Gulshan-2 Circle",
        description="Surface drainage culvert completely choked with plastic waste. 1.5 feet of stagnant rainwater accumulates after every rainfall, paralyzing commuter movement towards North Avenue.",
        category="Waterlogging",
        severity="High",
        ward=w19,
        department=dept_drainage,
        latitude=23.7925,
        longitude=90.4150,
        address="Gulshan-2 Roundabout, North Avenue, Dhaka",
        photo=p2,
        verification_status="Auto-Verified (Camera EXIF)",
        ai_confidence_score=0.98,
        camera_make="Apple",
        camera_model="iPhone 15 Pro",
        exif_timestamp="2026-10-19 09:15:33",
        upvotes_count=18,
        status="Under Review",
        threshold_notified=True,
        reporter_name="Farzana Kabir",
        reporter_phone="+880 1819-456789"
    )
    StatusHistory.objects.create(
        issue=i2,
        changed_by=official_w19,
        old_status="Pending Verification",
        new_status="Under Review",
        comment="Site inspection team scheduled with WASA drainage division."
    )

    # Issue 3: Dhanmondi WASA Pipe Burst (Escalated 24 Upvotes)
    i3 = Issue.objects.create(
        title="Burst WASA Main Pipeline Flooding Footpath on Road 27 Dhanmondi",
        description="High-pressure underground freshwater distribution pipe ruptured, eroding the brick footpath pavement and wasting thousands of gallons of potable drinking water daily.",
        category="Water Leak",
        severity="High",
        ward=w32,
        department=dept_wasa,
        latitude=23.7539,
        longitude=90.3768,
        address="Road 27 (Old), Dhanmondi R/A, Dhaka-1209",
        photo=p3,
        verification_status="Auto-Verified (Camera EXIF)",
        ai_confidence_score=0.99,
        camera_make="Google",
        camera_model="Pixel 8 Pro",
        exif_timestamp="2026-10-17 11:45:00",
        upvotes_count=24,
        status="In Progress",
        threshold_notified=True,
        reporter_name="Tanvir Hassan",
        reporter_phone="+880 1911-332211"
    )

    # Issue 4: Mirpur Open Manhole (Escalated 35 Upvotes)
    i4 = Issue.objects.create(
        title="Collapsed Heavy Concrete Manhole Lid at Mirpur-10 Main Junction",
        description="Disintegrated circular sewer cover left open on a high-speed vehicle lane. Critical danger for night rickshaws, motorbikes, and buses.",
        category="Pothole",
        severity="Critical",
        ward=w11,
        department=dept_roads,
        latitude=23.8069,
        longitude=90.3687,
        address="Mirpur-10 Roundabout, Begum Rokeya Sarani, Dhaka",
        photo=p4,
        verification_status="Auto-Verified (Camera EXIF)",
        ai_confidence_score=0.97,
        camera_make="Xiaomi",
        camera_model="Redmi Note 12",
        exif_timestamp="2026-10-16 16:30:12",
        upvotes_count=35,
        status="In Progress",
        threshold_notified=True,
        reporter_name="Kamrul Islam",
        reporter_phone="+880 1677-889900"
    )

    # Issue 5: Lalbagh Sanitation Cleared (Resolved)
    resolved_time = timezone.now() - timedelta(days=2)
    i5 = Issue.objects.create(
        title="Illegal Secondary Waste Dump Blocking Lalbagh Historical Approach",
        description="Large accumulation of unsorted domestic municipal refuse spilling into the heritage corridor. Severe odor and disease hazard.",
        category="Sanitation",
        severity="Medium",
        ward=w7,
        department=dept_sanitation,
        latitude=23.7198,
        longitude=90.3885,
        address="Lalbagh Fort Road, Old Dhaka",
        photo=p5,
        resolution_proof_photo=p5,
        resolution_notes="DNCC Waste Management dispatched 3 compactor trucks. All refuse cleared, area disinfected with lime and bleaching powder.",
        verification_status="AI-Verified (Genuine Photo)",
        ai_confidence_score=0.92,
        camera_make="Stripped EXIF (Chat)",
        camera_model="Authentic Sensor Noise Profile",
        upvotes_count=14,
        status="Resolved",
        threshold_notified=True,
        resolved_at=resolved_time,
        reporter_name="Sabbir Ahmed"
    )
    StatusHistory.objects.create(
        issue=i5,
        changed_by=official_w19,
        old_status="In Progress",
        new_status="Resolved",
        comment="Cleared by night sanitation squad. Resolution proof photo verified.",
        timestamp=resolved_time
    )

    # Issue 6: Baridhara Streetlights Repaired (Resolved)
    resolved_time_2 = timezone.now() - timedelta(days=1)
    i6 = Issue.objects.create(
        title="Row of 4 High-Efficiency Streetlights Non-Operational on Park Road",
        description="Four sequential lampposts extinguished due to water intrusion into underground junction box, creating unsafe dark stretch.",
        category="Streetlight",
        severity="Medium",
        ward=w18,
        department=dept_electrical,
        latitude=23.8048,
        longitude=90.4215,
        address="Park Road, Baridhara Diplomatic Zone, Dhaka",
        photo=p6,
        resolution_proof_photo=p6,
        resolution_notes="Electrical crew replaced faulty 150W LED driver units and insulated junction box.",
        verification_status="Auto-Verified (Camera EXIF)",
        ai_confidence_score=0.99,
        camera_make="Apple",
        camera_model="iPhone 14",
        exif_timestamp="2026-10-15 20:10:00",
        upvotes_count=9,
        status="Resolved",
        threshold_notified=False,
        resolved_at=resolved_time_2,
        reporter_name="Nadia Chowdhury"
    )
    StatusHistory.objects.create(
        issue=i6,
        changed_by=official_w19,
        old_status="In Progress",
        new_status="Resolved",
        comment="LED drivers replaced by DNCC electrical division.",
        timestamp=resolved_time_2
    )

    print("Seeding completed successfully! 6 Bangladesh issues across 5 Dhaka Wards initialized.")

if __name__ == '__main__':
    run_seed()

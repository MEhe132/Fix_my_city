from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class Ward(models.Model):
    """
    Municipal Ward representation (e.g. Ward 19, DNCC).
    Used for jurisdiction routing, councillor notifications, and accountability metrics.
    """
    ward_number = models.CharField(max_length=50, unique=True, help_text="e.g. Ward 19")
    name = models.CharField(max_length=150, help_text="e.g. Banani, Gulshan-2, Baridhara")
    city_corporation = models.CharField(
        max_length=120,
        default='Dhaka North City Corporation (DNCC)',
        help_text="e.g. Dhaka North City Corporation (DNCC), Dhaka South City Corporation (DSCC)"
    )
    councillor_name = models.CharField(max_length=100)
    contact_email = models.EmailField(blank=True, default='')
    contact_phone = models.CharField(max_length=30, blank=True, default='')
    office_address = models.CharField(max_length=255, blank=True, default='')
    center_latitude = models.FloatField(default=23.7925)
    center_longitude = models.FloatField(default=90.4078)

    class Meta:
        ordering = ['ward_number']

    def __str__(self):
        return f"{self.ward_number} - {self.name} ({self.city_corporation})"

    @property
    def total_issues_count(self):
        return self.issues.count()

    @property
    def resolved_issues_count(self):
        return self.issues.filter(status='Resolved').count()

    @property
    def in_progress_count(self):
        return self.issues.filter(status='In Progress').count()

    @property
    def pending_count(self):
        return self.issues.filter(status__in=['Pending Verification', 'Under Review']).count()

    @property
    def resolution_rate(self):
        total = self.total_issues_count
        if total == 0:
            return 0.0
        return round((self.resolved_issues_count / total) * 100, 1)

    @property
    def avg_resolution_days(self):
        resolved = self.issues.filter(status='Resolved', resolved_at__isnull=False)
        if not resolved.exists():
            return 0.0
        total_days = sum((item.resolved_at - item.created_at).total_seconds() / 86400 for item in resolved)
        return round(total_days / resolved.count(), 1)


class Department(models.Model):
    """
    Municipal operational departments responsible for specific infrastructure domains.
    """
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=30, unique=True, help_text="e.g. WASA, ROADS, SANITATION")
    description = models.TextField(blank=True, default='')
    emergency_hotline = models.CharField(max_length=30, blank=True, default='333')
    contact_email = models.EmailField(blank=True, default='')

    def __str__(self):
        return f"{self.name} ({self.code})"


class CustomUser(AbstractUser):
    """
    Two-Tier User model supporting regular citizens, ward officials, and city administrators.
    """
    ROLE_CHOICES = [
        ('CITIZEN', 'Citizen / Community Reporter'),
        ('OFFICIAL', 'Municipal / Ward Authority'),
        ('ADMIN', 'City Administrator / Super Admin'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='CITIZEN')
    phone_number = models.CharField(max_length=25, blank=True, default='')
    assigned_ward = models.ForeignKey(
        Ward,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='officials'
    )
    assigned_department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='officials'
    )
    designation = models.CharField(max_length=120, blank=True, default='')

    def is_official(self):
        return self.role in ['OFFICIAL', 'ADMIN'] or self.is_staff or self.is_superuser

    def __str__(self):
        if self.role == 'OFFICIAL' and self.assigned_ward:
            return f"{self.username} (Official - {self.assigned_ward.ward_number})"
        return f"{self.username} ({self.get_role_display()})"


class Issue(models.Model):
    CATEGORY_CHOICES = [
        ('Pothole', 'Pothole & Road Damage'),
        ('Streetlight', 'Streetlight & Electrical'),
        ('Water Leak', 'Water Leak & WASA Pipeline'),
        ('Sanitation', 'Waste & Sanitation Dump'),
        ('Waterlogging', 'Drainage & Waterlogging'),
        ('Footpath', 'Footpath Encroachment / Obstruction'),
        ('Other', 'Other Civic Infrastructure'),
    ]

    SEVERITY_CHOICES = [
        ('Low', 'Low Priority'),
        ('Medium', 'Medium Priority'),
        ('High', 'High Priority'),
        ('Critical', 'Critical Emergency'),
    ]

    STATUS_CHOICES = [
        ('Pending Verification', 'Pending Verification'),
        ('Under Review', 'Under Review'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved'),
        ('Rejected', 'Rejected / Invalid'),
    ]

    VERIFICATION_STATUS_CHOICES = [
        ('Auto-Verified (Camera EXIF)', 'Auto-Verified (Camera EXIF)'),
        ('AI-Verified (Genuine Photo)', 'AI-Verified (Genuine Photo)'),
        ('Flagged AI / Digital Art', 'Flagged AI / Digital Art'),
        ('Manual Review Required', 'Manual Review Required'),
    ]

    # Core details
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Pothole')
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='Medium')
    
    # Jurisdiction & Administrative routing
    ward = models.ForeignKey(Ward, on_delete=models.SET_NULL, null=True, blank=True, related_name='issues')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='issues')
    
    # Geographic Location (Dhaka, Bangladesh default)
    latitude = models.FloatField(default=23.8103)
    longitude = models.FloatField(default=90.4125)
    address = models.CharField(max_length=255, blank=True, default='')

    # Visual Evidence & AI Verification
    photo = models.ImageField(upload_to='issue_photos/', blank=True, null=True)
    verification_status = models.CharField(
        max_length=50,
        choices=VERIFICATION_STATUS_CHOICES,
        default='Auto-Verified (Camera EXIF)'
    )
    ai_confidence_score = models.FloatField(default=0.95, help_text="Confidence that photo is authentic")
    camera_make = models.CharField(max_length=100, blank=True, default='')
    camera_model = models.CharField(max_length=100, blank=True, default='')
    exif_timestamp = models.CharField(max_length=100, blank=True, default='')

    # Resolution details by Municipal Authority
    resolution_proof_photo = models.ImageField(upload_to='resolution_proofs/', blank=True, null=True)
    resolution_notes = models.TextField(blank=True, default='')
    resolved_at = models.DateTimeField(null=True, blank=True)

    # Citizen engagement & civic thresholds
    upvotes_count = models.IntegerField(default=1)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending Verification')
    threshold_notified = models.BooleanField(default=False)
    
    # Reporter metadata
    reporter = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='reported_issues')
    reporter_name = models.CharField(max_length=100, default='Anonymous Citizen')
    reporter_phone = models.CharField(max_length=30, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        ward_label = self.ward.ward_number if self.ward else "Unassigned Ward"
        return f"[{ward_label}] {self.title} - {self.status}"

    @property
    def is_escalated(self):
        """Escalated if 10+ upvotes or marked critical"""
        return self.upvotes_count >= 10 or self.severity == 'Critical'

    @property
    def resolution_delay_days(self):
        end_time = self.resolved_at or timezone.now()
        delta = end_time - self.created_at
        return round(delta.total_seconds() / 86400, 1)


class Upvote(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='upvotes')
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='user_upvotes')
    session_key = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('issue', 'session_key')

    def __str__(self):
        return f"Upvote for {self.issue.title}"


class StatusHistory(models.Model):
    """
    Immutable audit trail for issue triage and lifecycle updates by municipal authorities.
    """
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='status_logs')
    changed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    old_status = models.CharField(max_length=50)
    new_status = models.CharField(max_length=50)
    comment = models.TextField(blank=True, default='')
    proof_photo = models.ImageField(upload_to='audit_proofs/', blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"Issue #{self.issue_id}: {self.old_status} -> {self.new_status} at {self.timestamp}"

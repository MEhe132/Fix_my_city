from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def send_council_threshold_email(issue):
    """
    Automated SMTP Email Dispatch Service (SendGrid/SMTP integration spec).
    Sends a formal report email to the municipal authority once an issue reaches 10+ upvotes.
    """
    subject = f"[URGENT MUNICIPAL REPORT] {issue.title} - Priority Upvote Threshold Reached"
    
    message = f"""
    OFFICIAL CIVIC ISSUE DISPATCH REPORT
    ==================================================
    Issue ID       : #{issue.id}
    Title          : {issue.title}
    Category       : {issue.category}
    Severity       : {issue.severity}
    Community Votes: {issue.upvotes_count} Upvotes (Threshold: 10)
    Location Pin   : Lat {issue.latitude}, Lng {issue.longitude}
    Address        : {issue.address}
    Date Reported  : {issue.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}
    ==================================================

    Description:
    {issue.description}

    Status Notice:
    This civic infrastructure issue has been validated and prioritized by the local community.
    It has automatically crossed the upvote threshold and requires formal inspection and repair scheduling.
    """

    recipient_list = [settings.COUNCIL_CONTACT_EMAIL]

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=False
        )
        logger.info(f"Successfully dispatched automated council notification email for Issue #{issue.id}")
        return True
    except Exception as e:
        logger.error(f"Failed to dispatch email notification: {e}")
        return False

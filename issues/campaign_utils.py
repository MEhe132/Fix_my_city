"""
Fix My City - Bangladesh 1-Click Social Campaign Generator
Generates pre-formatted viral civic alert copy and share URLs for Facebook, WhatsApp, and social media.
"""

import urllib.parse
from django.urls import reverse


def generate_social_campaign_data(issue, request=None):
    """
    Produces structured social campaign payload for an issue.
    """
    ward = issue.ward
    ward_num = ward.ward_number if ward else "Ward Unassigned"
    ward_name = ward.name if ward else "Dhaka Municipality"
    city_corp = ward.city_corporation if ward else "City Corporation"
    councillor = ward.councillor_name if ward else "Local Ward Representative"

    if request:
        try:
            issue_url = request.build_absolute_uri(reverse('issue_detail', args=[issue.id]))
        except Exception:
            issue_url = f"https://fixmycity.bd/issues/{issue.id}/"
    else:
        issue_url = f"https://fixmycity.bd/issues/{issue.id}/"

    clean_ward_tag = ward_num.replace(" ", "") if ward else "WardBD"
    city_tag = "DNCC" if "North" in city_corp else "DSCC" if "South" in city_corp else "BDGov"

    campaign_headline = f"🚨 [CIVIC ACTION] {issue.title} ({ward_num}) has {issue.upvotes_count} Citizen Upvotes!"

    campaign_text = (
        f"📢 CIVIC INFRASTRUCTURE ALERT — BANGLADESH\n"
        f"==================================================\n"
        f"🏛️ Jurisdiction: {ward_num} ({ward_name}), {city_corp}\n"
        f"⚠️ Infrastructure Defect: {issue.title}\n"
        f"📋 Category: {issue.category} | Priority: {issue.severity}\n"
        f"📍 Location: {issue.address or 'GPS Verified Coordinates'}\n"
        f"🗳️ Citizen Endorsements: {issue.upvotes_count} Verified Upvotes\n"
        f"👤 Honorable Councillor: {councillor}\n"
        f"==================================================\n"
        f"Citizens demand immediate inspection and repair from the municipal engineering department.\n\n"
        f"👉 Track status & add your upvote:\n{issue_url}\n\n"
        f"#{clean_ward_tag} #{city_tag} #FixMyCityBD #CivicAccountability #SafeRoadsBangladesh #DhakaLive"
    )

    whatsapp_url = f"https://api.whatsapp.com/send?text={urllib.parse.quote(campaign_text)}"
    facebook_url = f"https://www.facebook.com/sharer/sharer.php?u={urllib.parse.quote(issue_url)}&quote={urllib.parse.quote(campaign_headline)}"
    twitter_url = f"https://twitter.com/intent/tweet?text={urllib.parse.quote(campaign_headline)}&url={urllib.parse.quote(issue_url)}&hashtags={clean_ward_tag},FixMyCityBD,{city_tag}"

    return {
        'headline': campaign_headline,
        'full_text': campaign_text,
        'issue_url': issue_url,
        'whatsapp_url': whatsapp_url,
        'facebook_url': facebook_url,
        'twitter_url': twitter_url,
        'ward_num': ward_num,
        'councillor': councillor,
        'upvotes': issue.upvotes_count
    }

from django.urls import path
from . import views

urlpatterns = [
    # Citizen Interface
    path('', views.index_view, name='index'),
    path('create/', views.create_issue_view, name='create_issue'),
    path('issues/<int:issue_id>/', views.issue_detail_view, name='issue_detail'),
    path('issues/<int:issue_id>/petition-pdf/', views.download_petition_pdf_view, name='download_petition_pdf'),
    path('issues/<int:issue_id>/campaign/', views.social_campaign_api, name='social_campaign_api'),
    path('issues/<int:issue_id>/update-status/', views.update_issue_status_view, name='update_issue_status'),

    # Public Ward Accountability Board
    path('accountability/', views.accountability_board_view, name='accountability_board'),

    # Municipal Authority Dashboard
    path('authority/dashboard/', views.authority_dashboard_view, name='authority_dashboard'),

    # Quick Demo Persona Switcher (Citizen vs Municipal Official)
    path('demo-role/<str:role>/', views.quick_demo_role_switch, name='quick_demo_role'),

    # JSON APIs
    path('api/issues/', views.api_issues_json, name='api_issues'),
    path('api/upvote/<int:issue_id>/', views.upvote_issue_api, name='api_upvote'),
    path('api/verify-image/', views.verify_image_api, name='api_verify_image'),
    path('api/reverse-geocode/', views.reverse_geocode_api, name='api_reverse_geocode'),
    path('api/ip-locate/', views.ip_locate_api, name='api_ip_locate'),
]



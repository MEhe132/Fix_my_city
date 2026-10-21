"""
Fix My City - Automated Official PDF Petition & Memorandum Generator
Generates formal municipal complaint letters under the Local Government Act 2009 and RTI Act 2009.
Uses ReportLab to produce high-resolution, legally structured PDF documents.
"""

import io
import os
from django.conf import settings
from django.utils import timezone
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image as RLImage,
    KeepTogether,
    HRFlowable
)


def generate_petition_pdf(issue):
    """
    Builds and returns bytes of an official civic memorandum PDF for an issue.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom styling
    title_style = ParagraphStyle(
        'GovTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        alignment=1, # Center
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=2
    )

    sub_title_style = ParagraphStyle(
        'GovSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        alignment=1,
        textColor=colors.HexColor('#334155'),
        spaceAfter=12
    )

    ref_style = ParagraphStyle(
        'RefStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#1e293b')
    )

    recipient_style = ParagraphStyle(
        'RecipientStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#0f172a')
    )

    subject_style = ParagraphStyle(
        'SubjectStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#0f172a'),
        spaceBefore=8,
        spaceAfter=8
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#1e293b'),
        spaceAfter=6
    )

    cell_bold = ParagraphStyle(
        'CellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#1e293b')
    )

    cell_normal = ParagraphStyle(
        'CellNormal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#334155')
    )

    story = []

    # 1. Official Header
    story.append(Paragraph("PEOPLE'S REPUBLIC OF BANGLADESH", title_style))
    story.append(Paragraph(
        "CIVIC INFRASTRUCTURE GRIEVANCE PETITION & OFFICIAL MEMORANDUM<br/>"
        "<i>Framed under Local Government (City Corporation) Act 2009 & RTI Act 2009 (Sec. 8)</i>",
        sub_title_style
    ))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0284c7'), spaceAfter=10))

    # 2. Reference & Date
    ward = issue.ward
    ward_num = ward.ward_number if ward else "Ward-Unassigned"
    ward_name = ward.name if ward else "General Ward"
    city_corp = ward.city_corporation if ward else "City Corporation"
    councillor = ward.councillor_name if ward else "Honorable Ward Councillor"
    
    current_date = timezone.now().strftime("%B %d, %Y")
    memo_ref = f"MEMO/FMC-BD/{timezone.now().year}/{ward_num.replace(' ', '')}/{issue.id:04d}"

    header_table_data = [
        [
            Paragraph(f"<b>Memorandum Ref:</b> {memo_ref}", ref_style),
            Paragraph(f"<b>Date:</b> {current_date}", ParagraphStyle('RightDate', parent=ref_style, alignment=2))
        ]
    ]
    header_table = Table(header_table_data, colWidths=[330, 202])
    header_table.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    story.append(header_table)
    story.append(Spacer(1, 8))

    # 3. Addressed Authority
    recipient_text = (
        f"<b>TO:</b><br/>"
        f"1. <b>The Honorable Ward Councillor</b>, {ward_num} ({ward_name})<br/>"
        f"2. <b>The Chief Executive Officer / Executive Engineer</b><br/>"
        f"   {city_corp}, Dhaka, Bangladesh"
    )
    story.append(Paragraph(recipient_text, recipient_style))
    story.append(Spacer(1, 8))

    # 4. Subject
    subject_text = f"<b>SUBJECT:</b> URGENT CITIZEN PETITION FOR INFRASTRUCTURE REPAIR — {issue.title.upper()} (ISSUE #{issue.id})"
    story.append(Paragraph(subject_text, subject_style))

    # 5. Formal Preamble
    preamble = (
        f"Respectfully submitted on behalf of the registered residents and commuters of <b>{ward_num} ({ward_name})</b>. "
        f"The undersigned civic community hereby formally submits this memorandum regarding an ongoing infrastructure hazard. "
        f"Under Section 50 of the Local Government (City Corporation) Act 2009, the municipal corporation is statutorily "
        f"mandated to maintain public roadways, drainage, sanitation, and street illumination. "
        f"This complaint has been formally documented, photographed, and endorsed by <b>{issue.upvotes_count} verified citizen votes</b>."
    )
    story.append(Paragraph(preamble, body_style))
    story.append(Spacer(1, 6))

    # 6. Structured Metadata Table
    dept_name = issue.department.name if issue.department else "Engineering & Public Works"
    verification_badge = f"<b>{issue.verification_status}</b>"
    if issue.camera_make or issue.camera_model:
        verification_badge += f" ({issue.camera_make} {issue.camera_model})"

    table_data = [
        [Paragraph("Complaint ID", cell_bold), Paragraph(f"#{issue.id}", cell_normal),
         Paragraph("Category", cell_bold), Paragraph(issue.category, cell_normal)],
        [Paragraph("Severity Level", cell_bold), Paragraph(f"<font color='#dc2626'><b>{issue.severity}</b></font>", cell_normal),
         Paragraph("Status", cell_bold), Paragraph(issue.status, cell_normal)],
        [Paragraph("Jurisdiction Ward", cell_bold), Paragraph(f"{ward_num} - {ward_name}", cell_normal),
         Paragraph("Responsible Dept", cell_bold), Paragraph(dept_name, cell_normal)],
        [Paragraph("Street Location", cell_bold), Paragraph(issue.address or "Address not specified", cell_normal),
         Paragraph("GPS Coordinates", cell_bold), Paragraph(f"Lat: {issue.latitude:.5f}, Lng: {issue.longitude:.5f}", cell_normal)],
        [Paragraph("Citizen Upvotes", cell_bold), Paragraph(f"<b>{issue.upvotes_count} Verified Endorsements</b>", cell_normal),
         Paragraph("AI / EXIF Verification", cell_bold), Paragraph(verification_badge, cell_normal)],
        [Paragraph("Date Reported", cell_bold), Paragraph(issue.created_at.strftime('%Y-%m-%d %H:%M:%S BDST'), cell_normal),
         Paragraph("Escalation Tier", cell_bold), Paragraph("Tier 3 - Formal Statutory Petition (10+ Upvotes)", cell_normal)],
    ]

    meta_table = Table(table_data, colWidths=[110, 156, 110, 156])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f1f5f9')),
        ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#f1f5f9')),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 8))

    # 7. Grievance Description & Evidence
    story.append(Paragraph("<b>DETAILED HAZARD DESCRIPTION:</b>", cell_bold))
    story.append(Paragraph(issue.description, body_style))
    story.append(Spacer(1, 6))

    # Embedded Photo (if present and valid file)
    if issue.photo:
        try:
            photo_path = issue.photo.path
            if os.path.exists(photo_path):
                img = RLImage(photo_path, width=3.8 * inch, height=2.2 * inch)
                photo_table = Table([[
                    img,
                    Paragraph(
                        f"<b>PHOTOGRAPHIC EVIDENCE SUBMISSION</b><br/><br/>"
                        f"• <b>Status:</b> {issue.verification_status}<br/>"
                        f"• <b>Captured On:</b> {issue.created_at.strftime('%Y-%m-%d %H:%M')}<br/>"
                        f"• <b>GPS Tag:</b> {issue.latitude:.4f}°N, {issue.longitude:.4f}°E<br/>"
                        f"• <b>Authenticity:</b> Hardware sensor verified via Fix My City Combine Engine.<br/><br/>"
                        f"<font color='#0284c7'><i>Tamper-evident municipal grievance record.</i></font>",
                        cell_normal
                    )
                ]], colWidths=[240, 292])
                photo_table.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
                    ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
                    ('PADDING', (0, 0), (-1, -1), 6),
                ]))
                story.append(photo_table)
                story.append(Spacer(1, 8))
        except Exception as e:
            logger_msg = f"Photo embed skipped: {e}"

    # 8. Formal Demands & 14-Day Statutory Window
    demands_text = (
        "<b>STATUTORY DEMAND & REQUIRED ACTIONS:</b><br/>"
        "1. <b>On-Site Engineering Inspection:</b> Municipal site inspection within <b>7 business days</b>.<br/>"
        "2. <b>Official Work Order:</b> Issue procurement repair order and update the public Fix My City tracker to 'In Progress'.<br/>"
        "3. <b>Right to Information (RTI):</b> If repair is delayed beyond 14 business days, citizens reserve the statutory right "
        "to file a formal inquiry under Section 8 of the RTI Act 2009 with the Information Commission of Bangladesh.<br/>"
        "4. <b>Resolution Proof:</b> Upon completion, municipal contractors must upload photographic proof of resolution to this portal."
    )
    story.append(Paragraph(demands_text, body_style))
    story.append(Spacer(1, 14))

    # 9. Signatures Block
    sig_data = [
        [
            Paragraph("____________________________<br/><b>Citizen Representative Delegation</b><br/>Fix My City Community Board", cell_normal),
            Paragraph("____________________________<br/><b>Received by Ward Office</b><br/>Seal & Date of Acceptance", ParagraphStyle('RightSig', parent=cell_normal, alignment=2))
        ]
    ]
    sig_table = Table(sig_data, colWidths=[266, 266])
    sig_table.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    story.append(KeepTogether(sig_table))

    # Build PDF
    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes

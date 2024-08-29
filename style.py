from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, TableStyle
from reportlab.lib import colors

def P(txt):
    if txt is None:
        txt = ''
    style = getSampleStyleSheet()['BodyText']
    style.alignment = 0
    return Paragraph(txt, style)

style = TableStyle([
        ('RIGHTPADDING', (0, 0), (1, -1), 0),
        ('LEFTPADDING', (0,0), (1, -1), 0),
        ('LINEBELOW', (0,0), (-1,0), 1, colors.black),
        ('LINEABOVE', (0,2), (-1,-1), 0.25, colors.black),
        ('LINEBELOW', (0,-1), (-1,-1), 0.15, colors.lightsteelblue),
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold')
        ])

title_table_style = TableStyle([
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.lightgrey),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10)
    ])

title_column_style = TableStyle([
        ('VALIGN', (1, 0), (1, 0), 'MIDDLE'),
        ('ALIGN', (1, 0), (1, 0), 'LEFT'),
    ])

title_style = ParagraphStyle(
    'Title',
    parent=getSampleStyleSheet()['Title'],
    fontSize=16,
    fontName='Helvetica-Bold',
    alignment = 0
    )

info_style = ParagraphStyle(
    'Info',
    parent=getSampleStyleSheet()['Title'],
    fontSize=14,
    fontName='Helvetica',
    alignment = 0
    )

image_table_style = TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('VALIGN', (1, 0), (1, 0), 'MIDDLE'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (1, 0), (1, -1), 0),
    ])

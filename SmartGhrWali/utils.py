from reportlab.lib.pagesizes import A4
# from reportlab.pdfgen import canvas
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet

# def generate_pdf(response, title, data):
#     # Set up the PDF canvas
#     # p = canvas.Canvas(response, pagesize=A4)
#     p = SimpleDocTemplate(response, pagesize=A4)
#     width, height = A4
#     y_position = height - 50  # Starting Y position for content

#     # Add title
#     p.setFont("Helvetica-Bold", 18)
#     p.drawString(50, y_position, title)
#     y_position -= 30

#     # Add timestamp
#     p.setFont("Helvetica", 10)
#     p.drawString(50, y_position, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
#     y_position -= 30

#     # Purchase Title
#     p.setFont("Helvetica-Bold", 14)
#     p.drawString(50, y_position, 'Purchases')
#     y_position -= 25

#     # Purchase headers
#     p.setFont("Helvetica-Bold", 12)
#     purchase_head = data['headers'][0]
#     columns_px = [50, 150, 250, 350, 450]

#     for i, header in enumerate(purchase_head):
#         p.drawString(columns_px[i], y_position, header)
#     y_position -= 20
    
#     # Purchase rows
#     purchases = data['rows'][0]
#     p.setFont("Helvetica", 10)
#     for row in purchases:
#         for i, item in enumerate(row):
#             p.drawString(columns_px[i], y_position, str(item))
#         y_position -= 20
#     y_position -= 25

#     # Usage Title
#     p.setFont("Helvetica-Bold", 14)
#     p.drawString(50, y_position, 'Usages')
#     y_position -= 25
    
#     # Usage headers
#     p.setFont("Helvetica-Bold", 14)
#     usage_head = data['headers'][1]
#     columns_ux = [50, 250, 450]

#     for i, header in enumerate(usage_head):
#         p.drawString(columns_ux[i], y_position, header)
#     y_position -= 20
    
#     # Usage rows
#     usages = data['rows'][1]
#     p.setFont("Helvetica", 10)
#     for row in usages:
#         for i, item in enumerate(row):
#             p.drawString(columns_ux[i], y_position, str(item))
#         y_position -= 20  

#     p.showPage()
#     p.save()

def generate_pdf(response, title, data):
    # Create the PDF object
    doc = SimpleDocTemplate(response, pagesize=A4)
    elements = []  # Store elements like table and title
    title = ['Purchases', 'Usages']
    # Title
    for i in range(2):
        styles = getSampleStyleSheet()
        title_style = styles['Title']
        title_style.fontSize = 18
        title_style.leading = 22  # Space between lines
        elements.append(Paragraph(title[i], title_style))
        
        # Table Data (headers + rows)
        table_data = [data['headers'][i]] + data['rows'][i]

        # Create table with data
        table = Table(table_data)
        
        # Style the table
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),      # Header background
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke), # Header text color
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),             # Center align
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),   # Header font
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),            # Padding for header
            ('GRID', (0, 0), (-1, -1), 1, colors.black),       # Grid lines
        ]))

        # Add the table to elements
        elements.append(table)

    # Build the PDF
    doc.build(elements)
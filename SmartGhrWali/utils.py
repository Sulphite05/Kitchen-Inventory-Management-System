# utils.py
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from datetime import datetime

def generate_pdf(response, title, data):
    # Set up the PDF canvas
    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    y_position = height - 50  # Starting Y position for content

    # Add title
    p.setFont("Helvetica-Bold", 18)
    p.drawString(50, y_position, title)
    y_position -= 30

    # Add timestamp
    p.setFont("Helvetica", 10)
    p.drawString(50, y_position, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    y_position -= 20

    # Draw table headers
    p.setFont("Helvetica-Bold", 12)
    headers = data['headers']
    columns_x = [50, 150, 250, 350]  # X positions for columns, adjust as needed
    for i, header in enumerate(headers):
        p.drawString(columns_x[i], y_position, header)
    y_position -= 20

    # Draw table rows
    p.setFont("Helvetica", 10)
    for row in data['rows']:
        for i, item in enumerate(row):
            p.drawString(columns_x[i], y_position, str(item))
        y_position -= 20

    # Finish up
    p.showPage()
    p.save()
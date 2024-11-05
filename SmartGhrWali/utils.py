from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.shapes import Drawing
from datetime import datetime
from reportlab.graphics.charts.legends import Legend

def generate_pdf(response, title, data, summary):
    doc = SimpleDocTemplate(response, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    
    # Title Page
    title_style = ParagraphStyle(name='Title', fontSize=24, alignment=1, spaceAfter=20)
    elements.append(Paragraph("Monthly Inventory Report", title_style))
    
    subtitle_style = ParagraphStyle(name='Subtitle', fontSize=14, alignment=1, spaceAfter=30)
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", subtitle_style))

    # Purchases Table
    elements.append(Paragraph("Purchases", styles['Heading2']))
    purchases_data = [data['headers'][0]] + data['rows'][0]
    purchases_table = Table(purchases_data, colWidths=[80, 120, 80, 80, 100])
    purchases_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(purchases_table)
    elements.append(Spacer(1, 12))

    elements.append(PageBreak())

    # Usages Table
    elements.append(Paragraph("Usages", styles['Heading2']))
    usages_data = [data['headers'][1]] + data['rows'][1]
    usages_table = Table(usages_data, colWidths=[120, 180, 100])
    usages_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(usages_table)
    elements.append(Spacer(1, 20))

    elements.append(PageBreak())

    # Chart Section
    elements.append(Paragraph("Monthly Purchase and Usage Chart", styles['Heading2']))
    drawing = Drawing(400, 200)
    bar_chart = VerticalBarChart()
    bar_chart.width = 350
    bar_chart.height = 150
    bar_chart.data = [[float(summary['total_purchase_cost'])], [float(summary['total_usage_quantity'])]]
    bar_chart.categoryAxis.categoryNames = ['Purchases', 'Usages']
    bar_chart.valueAxis.valueMin = 0
    bar_chart.valueAxis.valueMax = float(max(summary['total_purchase_cost'], summary['total_usage_quantity'])) * 1.2
    num = int(bar_chart.valueAxis.valueMax / 5)
    bar_chart.valueAxis.valueStep = num if num else int(bar_chart.valueAxis.valueMax) # to escape zeroDivisionError
    bar_chart.bars[0].fillColor = colors.blue
    bar_chart.bars[1].fillColor = colors.green

    # Legend
    legend = Legend()
    legend.alignment = 'right'
    legend.x = 340
    legend.y = 150
    legend.fontName = 'Helvetica'
    legend.fontSize = 10
    legend.boxAnchor = 'ne'
    legend.columnMaximum = 3
    legend.colorNamePairs = [(colors.blue, 'Purchases'), (colors.green, 'Usages')]
    drawing.add(bar_chart)
    drawing.add(legend)
    elements.append(drawing)

    # Summary Section
    elements.append(Paragraph("Summary", styles['Heading2']))
    summary_data = [
        ["Total Purchase Cost", f"{summary['total_purchase_cost']}"],
        ["Total Purchase Quantity", f"{summary['total_purchase_quantity']}"],
        ["Total Usage Quantity", f"{summary['total_usage_quantity']}"],
        ["Net Change", f"{summary['net_change']}"]
    ]
    summary_table = Table(summary_data, colWidths=[200, 200])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 12))

    # Build PDF
    doc.build(elements)
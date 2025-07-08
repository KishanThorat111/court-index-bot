# # Generate Index PDF
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import mm
from reportlab.graphics.shapes import Drawing, Line
from reportlab.lib import colors
import os
from textwrap import wrap

OUTPUT_PATH = "data/processed/Index.pdf"

# --- Style Definitions (Refined for precise design matching) ---
styles = getSampleStyleSheet()

# 1. Case No: Top Right, Bold, Size 11
style_meta_right = ParagraphStyle(
    name="MetaRight",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    alignment=2, # RIGHT
    fontSize=11,
    leading=15,
)

# 2. Court Name & BETWEEN: Left, Bold, Size 12
style_bold_left = ParagraphStyle(
    name="BoldLeft",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    alignment=0, # LEFT
    fontSize=12,
    leading=16,
)

# 4 & 6. Party Names (Mr. A (1)): Center, Bold, Size 12
style_bold_center = ParagraphStyle(
    name="BoldCenter",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    alignment=1, # CENTER
    fontSize=12,
    leading=16,
)

# 4 & 6. Role Descriptions (Applicant(s)): Right, Bold, Size 10
style_role_right = ParagraphStyle(
    name="RoleRight",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    alignment=2, # RIGHT
    fontSize=10,
    leading=14,
)

# 7. Main Title: Center, Bold, Size 14
style_title_heading = ParagraphStyle(
    name="TitleHeading",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    alignment=1, # CENTER
    fontSize=14,
    leading=18,
    spaceAfter=4*mm
)

def generate_index_pdf(case_number, court_name, claimants, defendants, index_title, hearing_date):
    """
    Generates the PDF index header with the new, highly specific styling.
    """
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    doc = SimpleDocTemplate(
        OUTPUT_PATH, pagesize=A4,
        rightMargin=20*mm, leftMargin=20*mm,
        topMargin=20*mm, bottomMargin=20*mm
    )
    elements = []

    # 1. Case No.
    elements.append(Paragraph(f"Case No: {case_number}", style_meta_right))
    elements.append(Spacer(1, 6 * mm))

    # 2. Court Name - Respects user's capitalization and wraps if long.
    # We do NOT use .upper() here anymore.
    for line in wrap(court_name, width=55):
        elements.append(Paragraph(line, style_bold_left))
    elements.append(Spacer(1, 6 * mm))

    # 3. BETWEEN:
    elements.append(Paragraph("BETWEEN:", style_bold_left))
    elements.append(Spacer(1, 4 * mm))

    # 4. Claimants/Applicants - with numbering
    for i, claimant in enumerate(claimants, 1):
        elements.append(Paragraph(f"{claimant.strip()} ({i})", style_bold_center))
    elements.append(Paragraph("Applicant(s)", style_role_right))
    elements.append(Spacer(1, 4 * mm))

    # 5. "Vs" instead of "V"
    elements.append(Paragraph("Vs", style_bold_center))
    elements.append(Spacer(1, 4 * mm))

    # 6. Defendants/Respondents - with numbering
    for i, defendant in enumerate(defendants, 1):
        elements.append(Paragraph(f"{defendant.strip()} ({i})", style_bold_center))
    elements.append(Paragraph("Respondent(s)", style_role_right))
    elements.append(Spacer(1, 12 * mm))

    # --- 7. Final Title Block ---
    usable_width = A4[0] - doc.leftMargin - doc.rightMargin
    line_drawing = Drawing(usable_width, 1.5) # Slightly thicker line
    line_drawing.add(Line(0, 0, usable_width, 0, strokeColor=colors.black, strokeWidth=1.2))
    
    elements.append(line_drawing)
    elements.append(Spacer(1, 2 * mm))
    
    # We use .upper() only for the final title line as requested.
    title = f"INDEX FOR {index_title.upper()} ON {hearing_date.upper()}"
    elements.append(Paragraph(title, style_title_heading))
    
    elements.append(line_drawing)

    doc.build(elements)
    print(f"[OK] Generated refined Index.pdf at {OUTPUT_PATH}")
    return OUTPUT_PATH
from io import BytesIO
from datetime import datetime
from collections import Counter
from typing import List
import logging

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Image, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

from image import create_image
from models import Vehicle, MotTest
from plot import create_line_graph

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def create_paragraph_styles(styles) -> dict:
    return {
        "BOLD": ParagraphStyle("BoldStyle", parent=styles["Normal"], fontName="Helvetica-Bold"),
        "RED": ParagraphStyle("RedText", parent=styles["Normal"], textColor=colors.red),
        "AMBER": ParagraphStyle("AmberText", parent=styles["Normal"], textColor=colors.orangered)
    }

def create_image_buffer(registration: str) -> BytesIO:
    """Creates a buffer for our PIL generated image and creates a reportlab Image using it"""
    img_buffer = BytesIO()
    create_image(registration).save(img_buffer, format="PNG")
    img_buffer.seek(0)

    return img_buffer

def calculate_avg_mileage(mot_tests: List[MotTest]) -> float:
    """Calculates the average mileage per year across all of the vehicles MOTs"""
    avg_mileage = int(mot_tests[0].odometerValue) # Default to the first MOT mileage reading
    for i in range(1, len(mot_tests)): # Start at index 1 to skip including the first mot reading twice
        prev = mot_tests[i-1].odometerValue
        curr = mot_tests[i].odometerValue
        avg_mileage += int(prev) - int(curr)

    return avg_mileage / len(mot_tests)

def create_pdf(filename: str, vehicle: Vehicle) -> None:
    """Creates a PDF file displaying information from the provided Vehicle"""
    document = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    custom_styles = create_paragraph_styles(styles)

    bold_style = custom_styles["BOLD"]
    red_text = custom_styles["RED"]
    amber_text = custom_styles["AMBER"]

    reg_img_buffer = create_image_buffer(vehicle.registration)
    reportlab_image = Image(reg_img_buffer, 173.25, 41.75)
    elements.append(reportlab_image)
    elements.append(Spacer(0, 10))

    # VEHICLE INFORMATION SECTION
    vehicle_info = [
        ("Registration", vehicle.registration),
        ("Make & Model", f"{vehicle.make} {vehicle.model}"),
        ("Registered Date", (datetime.strptime(vehicle.registrationDate, "%Y-%m-%d").strftime("%d/%m/%Y"))),
        ("Body Colour", vehicle.primaryColour),
        ("Fuel Type", vehicle.fuelType),
        ("Engine Capacity", vehicle.engineSize),
        ("No. Doors", "N/A"),
        ("No. Seats", "N/A")
    ]

    elements.append(Paragraph("<b>Vehicle Information</b>", styles["Heading2"]))
    for label, value in vehicle_info:
        # Preventing data that is None from showing
        if value != None:
            elements.append(Paragraph(f"{label}: {value}", styles["Normal"]))

    # SAFETY INFORMATION SECTION
    safety_info = [
        ("Outstanding Recall?", vehicle.hasOutstandingRecall)
    ]

    elements.append(Paragraph("<b>Safety Information</b>", styles["Heading2"]))
    for label, value in safety_info:
        elements.append(Paragraph(f"{label}: {value}", styles["Normal"]))

    # Checking that there is MOT data
    if len(vehicle.motTests) != 0:
        # MOT STATUS SECTION
        mot_valid = (vehicle.motTests[0].testResult == "PASSED" and datetime.strptime(vehicle.motTests[0].expiryDate, "%Y-%m-%d") >= datetime.now() if len(vehicle.motTests) > 0 else "None")
        mot_status = [
            ("MOT Valid", "Yes" if mot_valid else "No"),
            ("Recent Test Date", (datetime.strptime(vehicle.motTests[0].completedDate, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%d/%m/%Y %H:%M"))),
            ("Recent Result", vehicle.motTests[0].testResult),
            ("Recent Odometer Reading", f"{int(vehicle.motTests[0].odometerValue):,} {vehicle.motTests[0].odometerUnit}"),
            ("Recent Location", vehicle.motTests[0].location if vehicle.motTests[0].location is not None else "N/A")
        ]

        elements.append(Paragraph("<b>MOT Status</b>", styles["Heading2"]))
        for label, value in mot_status:
            elements.append(Paragraph(f"{label}: {value}", styles["Normal"]))

        # MOT INFORMATION SECTION
        mots = [["Date", "Mileage", "Comments", "Result"]]
        
        # Populate the mots list with lists of mots
        for mot in vehicle.motTests:
            mots.append([
                (datetime.strptime(mot.completedDate, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%d/%m/%Y %H:%M")), 
                f"{int(mot.odometerValue):,}", 
                len(mot.defects), 
                mot.testResult
            ])

        advisories = [] 
        majors = []

        # Populate the advisories and majors lists and add the odometerValue differences to the avg_mileage variable
        for i, mot in enumerate(vehicle.motTests):
            for defect in mot.defects:
                if defect.type == "ADVISORY":
                    advisories.append(defect.text)
                elif defect.type in ["PRM", "MAJOR"]:
                    majors.append(defect.text)
        
        avg_mileage = calculate_avg_mileage(vehicle.motTests)
        total_passes = sum(1 for x in vehicle.motTests if x.testResult == "PASSED")
        total_fails = sum(1 for x in vehicle.motTests if x.testResult == "FAILED")

        mot_info = [
            ("Total No. Passes", total_passes),
            ("Total No. Fails", total_fails),
            ("Pass Rate", f"{round((total_passes / (total_passes + total_fails) * 100))}%"),
            ("Average Annual Mileage", f"{round(avg_mileage):,}")
        ]

        elements.append(Paragraph(f"<b>MOT Information</b>", styles["Heading2"]))
        for key, value in mot_info:
            elements.append(Paragraph(f"{key}: {value}", styles["Normal"]))
            
        elements.append(Spacer(0, 10))

        advisory_counts = Counter(advisories) # Count is more efficient than calling x.count() inside of a loop
        major_counts = Counter(majors)
        advisories_sorted = [item for item, count in advisory_counts.items() if count > 1]
        majors_sorted = [item for item, count in major_counts.items() if count > 1]

        elements.append(Paragraph(f"Recurring faults ({len(advisories_sorted)}):", bold_style))

        if majors_sorted:
            for major in majors_sorted:
                elements.append(Paragraph(f"{major} (x{major_counts[major]})", red_text, bulletText="-"))

        if advisories_sorted:
            for advisory in advisories_sorted:
                elements.append(Paragraph(f"{advisory} (x{advisory_counts[advisory]})", amber_text, bulletText="-"))

        elements.append(PageBreak())

        # MOT HISTORY SECTION
        elements.append(Paragraph(f"<b>MOT History</b>", styles["Heading2"]))

        dates = []
        mileage = []

        # Populate the dates and milage lists
        for mot in vehicle.motTests:
            dates.append(datetime.strptime(mot.completedDate, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%y"))
            mileage.append(mot.odometerValue)

        # Create graph
        graph = create_line_graph(x=dates[::-1], y=mileage[::-1], title="Vehicle Mileage by Year (yy)", x_label="", y_label="", marker="")
        plot_img = Image(graph, width=500, height=300)
        elements.append(plot_img)

        # Create and style the MOT history table
        table = Table(mots, colWidths=[100, 100, 100, 100])
        table.setStyle(TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
            ("GRID", (0, 0), (-1, -1), 1, colors.black)
        ]))

        elements.append(table)
    else:
        if vehicle.motTestDueDate:
            mot_due = datetime.strptime(vehicle.motTestDueDate, "%Y-%m-%d").strftime("%d/%m/%Y")
            elements.append(Paragraph(f"<b>MOT due: {mot_due}</b>", styles["Heading2"]))
            elements.append(Paragraph("MOT data will be available after the vehicle's first MOT test", styles["Normal"]))
        else:
            elements.append(Paragraph(f"<b>No MOT data available</b>", styles["Heading2"]))

    document.build(elements)
    logging.info(f"Generated PDF for {vehicle.registration} to {filename}")

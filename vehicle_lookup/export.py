from io import BytesIO
from datetime import datetime
from collections import Counter
from typing import List
import re

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Image, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

from .image import create_image
from .models import Vehicle, MotTest
from .plot import create_line_graph, create_stacked_bar_graph
from .logging_config import logger

def create_paragraph_styles(styles) -> dict:
    """Returns pre-set Paragraph styling"""
    bold = ParagraphStyle("BoldStyle", parent=styles["Normal"], fontName="Helvetica-Bold")
    return {
        "BOLD": bold,
        "AMBER": ParagraphStyle("AmberText", parent=styles["Normal"], textColor=colors.orangered),
        "MAJOR": ParagraphStyle("RedText", parent=bold, textColor=colors.red),
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
    amber_text = custom_styles["AMBER"]
    major_text = custom_styles["MAJOR"]

    reg_img_buffer = create_image_buffer(vehicle.registration)
    reportlab_image = Image(reg_img_buffer, 173.25, 41.75)
    elements.append(reportlab_image)
    elements.append(Spacer(0, 10))

    # VEHICLE IDENTIFICATION AND REGISTRATION SECTION
    vehicle_info = [
        ("Registration", vehicle.registration),
        ("Make & Model", f"{vehicle.make} {vehicle.model}"),
        ("Colour", vehicle.primaryColour),
        ("Wheel Plan", vehicle.wheelplan),
        ("Registration Date", (datetime.strptime(vehicle.registrationDate, "%Y-%m-%d").strftime("%d/%m/%Y")) if vehicle.registrationDate else "Unavailable"),
        ("First Used Date", (datetime.strptime(vehicle.firstUsedDate, "%Y-%m-%d").strftime("%d/%m/%Y")) if vehicle.firstUsedDate else "Unavailable"),
        ("Last V5C Issued", datetime.strptime(vehicle.dateOfLastV5CIssued, "%Y-%m-%d").strftime("%d/%m/%Y") if vehicle.dateOfLastV5CIssued else "Unavailable"),
        ("Type Approval", vehicle.typeApproval),
        ("Marked for Export", vehicle.markedForExport)
    ]

    elements.append(Paragraph("<b>Vehicle Identification and Registration</b>", styles["Heading2"]))
    for label, value in vehicle_info:
        elements.append(Paragraph(f"{label}: {value}", styles["Normal"]))

    # VEHICLE CONDITION AND INSPECTION SECTION
    condition_info = [
        ("Fuel Type", vehicle.fuelType),
        ("Engine Capacity", vehicle.engineCapacity),
        ("Co2 Emissions", f"{vehicle.co2Emissions} g/km"),
        ("Mot Due", vehicle.motTestDueDate if vehicle.motTestDueDate else "Unavailable"),
        ("Mot Expiry Date", datetime.strptime(vehicle.motExpiryDate, "%Y-%m-%d").strftime("%d/%m/%Y") if vehicle.motExpiryDate else "Unavilable"),
        ("Recalls?", "No" if vehicle.hasOutstandingRecall == "Unknown" else vehicle.hasOutstandingRecall),
        ("Tax Status", vehicle.taxStatus),
        ("Tax Due", datetime.strptime(vehicle.taxDueDate, "%Y-%m-%d").strftime("%d/%m/%Y") if vehicle.taxDueDate else "Unavailable"),
    ]

    elements.append(Paragraph("<b>Vehicle Condition and Inspection</b>", styles["Heading2"]))
    for label, value in condition_info:
        elements.append(Paragraph(f"{label}: {value}", styles["Normal"]))

    # Checking that there is MOT data
    if len(vehicle.motTests) != 0:
        # MOT INFORMATION SECTION
        mots = [["Date", "Mileage", "Comments", "Result"]]
        advisories = [] 
        majors = []
        
        # Populate the mots list with lists of mots
        for mot in vehicle.motTests:
            mots.append([
                (datetime.strptime(mot.completedDate, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%d/%m/%Y %H:%M")), 
                f"{int(mot.odometerValue):,}", 
                len(mot.defects), 
                mot.testResult
            ])

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
            ("MOT Valid", vehicle.motStatus),
            ("Recent Test Date", (datetime.strptime(vehicle.motTests[0].completedDate, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%d/%m/%Y"))),
            ("Recent Result", vehicle.motTests[0].testResult),
            ("Recent Odometer Reading", f"{int(vehicle.motTests[0].odometerValue):,}"),
            ("Odometer Unit", "Miles" if vehicle.motTests[0].odometerUnit == "MI" else "Kilometers"),
            ("Recent Location", vehicle.motTests[0].location),
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

        re_format = "\(.*?\)[()]" # Removes all items inside of () and any hanging parenthesis left over

        if majors_sorted:
            for major in majors_sorted:
                elements.append(Paragraph(f"MAJOR: {re.sub(re_format, "", major)} (x{major_counts[major]})", major_text, bulletText="-"))

        if advisories_sorted:
            for advisory in advisories_sorted:
                elements.append(Paragraph(f"ADVISE: {re.sub(re_format, "", advisory)} (x{advisory_counts[advisory]})", amber_text, bulletText="-"))

        elements.append(PageBreak())

        # VISUAL INSIGHTS SECTION
        elements.append(Paragraph(f"<b>Visual Insights</b>", styles["Heading2"]))

        dates = []
        mileage = []

        # Populate the dates and milage lists
        for mot in vehicle.motTests:
            dates.append(datetime.strptime(mot.completedDate, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%y"))
            mileage.append(mot.odometerValue)

        # GRAPHS
        mileage_by_year_graph = create_line_graph(
            x=dates[::-1], 
            y=mileage[::-1], 
            title="Vehicle Mileage by Year (yy)"
        )
        plot_img = Image(mileage_by_year_graph, width=500, height=300)
        elements.append(plot_img)

        data = {}
        for m in vehicle.motTests:
            if len(m.defects) > 0:
                data[round(int(m.odometerValue), -3)] = {
                    "advisories": len([x for x in m.defects if x.type == "ADVISORY"]),
                    "majors": len([x for x in m.defects if x.type == "MAJOR"])
                }

        data = dict(reversed(list(data.items())))

        comments_by_mileage_graph = create_stacked_bar_graph(
            [str(x) for x in data.keys()], 
            [value["advisories"] for value in data.values()], 
            [value["majors"] for value in data.values()],
            title="Majors & Advisories by Mileage"
        )
        _plot_img = Image(comments_by_mileage_graph, width=500, height=300)
        elements.append(_plot_img)

        elements.append(PageBreak())

        # MOT HISTORY SECTION
        elements.append(Paragraph(f"<b>MOT History</b>", styles["Heading2"]))

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
    logger.info(f"Generated PDF for {vehicle.registration} to {filename}")

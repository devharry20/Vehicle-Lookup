import requests
import os
from dataclasses import fields

from dotenv import load_dotenv

from models import Defect, MotTest, Vehicle
from export import create_pdf

load_dotenv()

MOT_VEHICLE_ENDPOINT = "https://history.mot.api.gov.uk/v1/trade/vehicles/registration/"
VES_API_ENDPOINT = "https://driver-vehicle-licensing.api.gov.uk/vehicle-enquiry/v1/vehicles"
VES_API_KEY = os.getenv("VES_API_KEY")
MOT_AUTHORIZATION_KEY = os.getenv("MOT_AUTHORIZATION_KEY")
MOT_API_KEY = os.getenv("MOT_API_KEY")

def clean_vehicle_data(data: dict) -> dict:
    """Cleans data to remove unwanted fields"""
    expected_keys = {field.name for field in fields(Vehicle)}

    cleaned_data = {key: value for key, value in data.items() if key in expected_keys}

    return cleaned_data

def fetch_ves_data(reg: str) -> dict:
    """Fetch vehicle data from the VES api"""
    headers = {
    "x-api-key": VES_API_KEY,
    "Content-Type": "application/json"
    }

    response = requests.request("POST", VES_API_ENDPOINT, headers=headers, data = "{\n\t\"registrationNumber\": \"" + reg + "\"\n}")
    res_json = response.json()

    return res_json

def fetch_mot_data(reg: str) -> dict:
    """Fetch vehicle data from the MOT data api"""
    url = f"{MOT_VEHICLE_ENDPOINT}{reg}"

    headers = {
        "Authorization": f"Bearer {MOT_AUTHORIZATION_KEY}",
        "X-API-Key": MOT_API_KEY
    }
    response = requests.get(url, headers=headers)

    return response.json()

def merge_data(mot_data, ves_data) -> dict:
    """Merge data from 2 dictionaries into one"""
    merged_data = {
        "registration": mot_data.get("registration", ves_data.get("registrationNumber")),
        "make": mot_data.get("make", ves_data.get("make")),
        "model": mot_data.get("model", ves_data.get("model")),
        "firstUsedDate": mot_data.get("firstUsedDate"),
        "fuelType": mot_data.get("fuelType", ves_data.get("fuelType")),
        "primaryColour": mot_data.get("primaryColour", ves_data.get("colour")),
        "registrationDate": mot_data.get("registrationDate"),
        "manufactureDate": mot_data.get("manufactureDate"),
        "engineSize": mot_data.get("engineSize", ves_data.get("engineCapacity")),
        "motTestDueDate": mot_data.get("motTestDueDate"),
        "hasOutstandingRecall": mot_data.get("hasOutstandingRecall"),
        "motTests": mot_data.get("motTests", []),
        "taxStatus": ves_data.get("taxStatus"),
        "taxDueDate": ves_data.get("taxDueDate"),
        "motStatus": ves_data.get("motStatus"),
        "yearOfManufacture": ves_data.get("yearOfManufacture"),
        "co2Emissions": ves_data.get("co2Emissions"),
        "markedForExport": ves_data.get("markedForExport"),
        "typeApproval": ves_data.get("typeApproval"),
        "dateOfLastV5CIssued": ves_data.get("dateOfLastV5CIssued"),
        "motExpiryDate": ves_data.get("motExpiryDate"),
        "wheelplan": ves_data.get("wheelplan"),
        "monthOfFirstRegistration": ves_data.get("monthOfFirstRegistration"),
        "monthOfFirstDvlaRegistration": ves_data.get("monthOfFirstDvlaRegistration")
    }

    return merged_data

def fetch(reg: str) -> Vehicle:
    """Return a Vehicle object using cleaned, merged data"""
    mot_data = fetch_mot_data(reg)
    ves_data = fetch_ves_data(reg)

    if "errorMessage" in mot_data:
        raise Exception(mot_data["errorMessage"])

    clean_mot_data = clean_vehicle_data(mot_data)
    clean_ves_data = clean_vehicle_data(ves_data)

    clean_mot_data["motTests"] = [
        MotTest(**{k: v for k, v in test.items() if k != 'defects'}, defects=[Defect(**defect) for defect in test['defects']])
        for test in clean_mot_data.get("motTests", [])
    ]

    merged_data = merge_data(clean_mot_data, clean_ves_data)

    return Vehicle(**merged_data)

def main():
    vehicle = fetch("ls51aux")
    create_pdf("output.pdf", vehicle)

if __name__ == "__main__":
    main()

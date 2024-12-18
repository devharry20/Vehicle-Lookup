import requests
import json
import os
import argparse
from dataclasses import fields

from dotenv import load_dotenv

from .models import Defect, MotTest, Vehicle
from .export import create_pdf
from . import MOT_VEHICLE_ENDPOINT, VES_API_ENDPOINT

load_dotenv()

VES_API_KEY = os.getenv("VES_API_KEY")
MOT_AUTHORIZATION_KEY = os.getenv("MOT_AUTHORIZATION_KEY")
MOT_API_KEY = os.getenv("MOT_API_KEY")

def clean_vehicle_data(data: dict) -> dict:
    """Cleans data to remove unwanted fields"""
    vehicle_fields = {field.name for field in fields(Vehicle)}
    cleaned_data = {key: value for key, value in data.items() if key in vehicle_fields}
    
    # Default all field values if they are None
    for key, _ in cleaned_data.items():
        if key == None:
            cleaned_data[key] = "Unavailable"

    return cleaned_data

def fetch_ves_data(reg: str) -> dict:
    """Fetch vehicle data from the VES api"""
    headers = {
        "x-api-key": VES_API_KEY,
        "Content-Type": "application/json"
    }

    rq_data = {
        "registrationNumber": reg 
    }

    response = requests.post(
        VES_API_ENDPOINT,
        data=json.dumps(rq_data), 
        headers=headers
    )
    
    return response.json()

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
    merged_data = {}

    _fields = [x.name for x in fields(Vehicle)]

    for field in _fields:
        merged_data[field] = mot_data.get(field) if field in mot_data else ves_data.get(field)

    merged_data["motTests"] = [
        MotTest(**{k: v for k, v in test.items() if k != 'defects'}, defects=[Defect(**defect) for defect in test['defects']])
        for test in mot_data.get("motTests", [])
    ]

    return merged_data

def fetch(reg: str) -> Vehicle:
    """Return a Vehicle object using cleaned, merged data"""
    mot_data = fetch_mot_data(reg)
    ves_data = fetch_ves_data(reg)

    if "errorMessage" in mot_data:
        raise Exception(mot_data["errorMessage"])
    
    if "message" in ves_data:
        if ves_data["message"] == "Forbidden":
            raise Exception(ves_data["message"])

    clean_mot_data = clean_vehicle_data(mot_data)
    clean_ves_data = clean_vehicle_data(ves_data)
    merged_data = merge_data(clean_mot_data, clean_ves_data)

    return Vehicle(**merged_data)

def main():
    parser = argparse.ArgumentParser(description="Process a vehicle registration.")
    parser.add_argument('-r', '--reg', required=True, help="Vehicle registration number")
    parser.add_argument('-o', '--output', required=True, help="Output file (PDF)")
    
    args = parser.parse_args()

    vehicle = fetch(args.reg.strip())

    if not args.output.endswith(".pdf"):
        args.output = f"{args.output}.pdf"

    create_pdf(args.output, vehicle)

if __name__ == "__main__":
    main()

import requests
import os
from dataclasses import fields

from dotenv import load_dotenv

from models import Defect, Vehicle, MotTest
from export import create_pdf
from logging_config import logger

load_dotenv()

VEHICLE_ENDPOINT = "https://history.mot.api.gov.uk/v1/trade/vehicles/registration/"
AUTHORIZATION_KEY = os.getenv("AUTHORIZATION_KEY")
API_KEY = os.getenv("API_KEY")

def clean_vehicle_data(data: dict) -> dict:
    """Cleans data to remove unwanted fields"""
    expected_keys = {field.name for field in fields(Vehicle)}

    cleaned_data = {key: value for key, value in data.items() if key in expected_keys}

    return cleaned_data

def fetch(reg: str) -> Vehicle:
    """Fetch and return vehicle data from the API"""
    url = f"{VEHICLE_ENDPOINT}{reg}"

    headers = {
        "Authorization": f"Bearer {AUTHORIZATION_KEY}",
        "X-API-Key": API_KEY
    }
    response = requests.get(VEHICLE_ENDPOINT + reg, headers=headers)

    data = response.json()

    if "errorMessage" in data:
        raise Exception(data["errorMessage"])

    clean_data = clean_vehicle_data(data)

    clean_data["motTests"] = [
        MotTest(**{k: v for k, v in test.items() if k != 'defects'}, defects=[Defect(**defect) for defect in test['defects']])
        for test in clean_data.get("motTests", [])
    ]

    return Vehicle(**clean_data)

def main():
    vehicle = fetch("ls51aux")
    create_pdf("output.pdf", vehicle)

if __name__ == "__main__":
    main()
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Defect:
    dangerous: Optional[bool] = None
    text: Optional[str] = "Unavailable"
    type: Optional[str] = "Unavailable"

@dataclass
class MotTest:
    motTestNumber: Optional[str] = "Unavailable"
    completedDate: Optional[str] = None
    expiryDate: Optional[str] = "Unavailable"
    odometerValue: Optional[str] = "Unavailable"
    odometerUnit: Optional[str] = "Unavailable"
    odometerResultType: Optional[str] = "Unavailable"
    testResult: Optional[str] = "Unavailable"
    dataSource: Optional[str] = "Unavailable"
    defects: List[Defect] = field(default_factory=list)
    location: Optional[str] = "Unavailable"

@dataclass
class Vehicle:
    # MOT API data
    registration: Optional[str] = "Unavailable"
    make: Optional[str] = "Unavailable"
    model: Optional[str] = "Unavailable"
    firstUsedDate: Optional[str] = None
    fuelType: Optional[str] = "Unavailable"
    primaryColour: Optional[str] = "Unavailable"
    registrationDate: Optional[str] = None
    manufactureDate: Optional[str] = None
    engineSize: Optional[str] = "Unavailable"
    motTestDueDate: Optional[str] = None
    hasOutstandingRecall: Optional[str] = "Unavailable"
    motTests: List[MotTest] = field(default_factory=list)

    # VES API data
    registrationNumber: Optional[str] = "Unavailable"
    taxStatus: Optional[str] = "Unavailable"
    taxDueDate: Optional[str] = None
    motStatus: Optional[str] = "Unavailable"
    yearOfManufacture: Optional[str] = "Unavailable"
    engineCapacity: Optional[int] = None
    co2Emissions: Optional[int] = "Unavailable"
    markedForExport: Optional[str] = "Unavailable"
    colour: Optional[str] = "Unavailable"
    typeApproval: Optional[str] = "Unavailable"
    dateOfLastV5CIssued: Optional[str] = None
    motExpiryDate: Optional[str] = None
    wheelplan: Optional[str] = "Unavailable"
    monthOfFirstRegistration: Optional[str] = "Unavailable"
    monthOfFirstDvlaRegistration: Optional[str] = "Unavailable"
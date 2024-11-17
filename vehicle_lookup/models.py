from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Defect:
    dangerous: Optional[bool] = None
    text: Optional[str] = None
    type: Optional[str] = None

@dataclass
class MotTest:
    motTestNumber: Optional[str] = None
    completedDate: Optional[str] = None
    expiryDate: Optional[str] = None
    odometerValue: Optional[str] = None
    odometerUnit: Optional[str] = None
    odometerResultType: Optional[str] = None
    testResult: Optional[str] = None
    dataSource: Optional[str] = None
    defects: List[Defect] = field(default_factory=list)
    location: Optional[str] = None

@dataclass
class Vehicle:
    # MOT API data
    registration: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None
    firstUsedDate: Optional[str] = None
    fuelType: Optional[str] = None
    primaryColour: Optional[str] = None
    registrationDate: Optional[str] = None
    manufactureDate: Optional[str] = None
    engineSize: Optional[str] = None
    motTestDueDate: Optional[str] = None
    hasOutstandingRecall: Optional[str] = None
    motTests: List[MotTest] = field(default_factory=list)

    # VES API data
    registrationNumber: Optional[str] = None
    taxStatus: Optional[str] = None
    taxDueDate: Optional[str] = None
    motStatus: Optional[str] = None
    yearOfManufacture: Optional[str] = None
    engineCapacity: Optional[int] = None
    co2Emissions: Optional[int] = None
    markedForExport: Optional[str] = None
    colour: Optional[str] = None
    typeApproval: Optional[str] = None
    dateOfLastV5CIssued: Optional[str] = None
    motExpiryDate: Optional[str] = None
    wheelplan: Optional[str] = None
    monthOfFirstRegistration: Optional[str] = None
    monthOfFirstDvlaRegistration: Optional[str] = None
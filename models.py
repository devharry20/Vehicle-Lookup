from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Defect:
    dangerous: bool
    text: str
    type: str

@dataclass
class MotTest:
    motTestNumber: str
    completedDate: str
    expiryDate: str
    odometerValue: str
    odometerUnit: str
    odometerResultType: str
    testResult: str
    dataSource: str
    defects: List[Defect]
    location: Optional[str] = None

@dataclass
class Vehicle:
    registration: str
    make: str
    model: str
    firstUsedDate: Optional[str] = None
    fuelType: Optional[str] = None
    primaryColour: Optional[str] = None
    registrationDate: Optional[str] = None
    manufactureDate: Optional[str] = None
    engineSize: Optional[str] = None
    motTestDueDate: Optional[str] = None
    hasOutstandingRecall: Optional[str] = None
    motTests: List[MotTest] = field(default_factory=list) 
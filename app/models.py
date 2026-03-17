from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class ClinicalEvidence:
    patient_id: str
    source: str
    date: datetime
    text: str
    lbp_score: float
    improvement_score: float


@dataclass
class PatientResult:
    patient_id: str
    full_name: str
    latest_event_date: datetime
    latest_event_status: str
    lbp_score: float
    improvement_score: float
    evidence_count: int
    evidence_samples: List[str]

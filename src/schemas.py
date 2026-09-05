from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class DisputeReason(str, Enum):
    FRAUDULENT = "fraudulent"
    PRODUCT_NOT_RECEIVED = "product_not_received"
    NOT_AS_DESCRIBED = "not_as_described"
    DUPLICATE_CHARGE = "duplicate_charge"

class DefenseAction(str, Enum):
    CONCEDE = "CONCEDE"                    # Do not contest; saves representment fee penalties
    CONTEST = "CONTEST"                    # Build and submit bank representment dossier
    HUMAN_ESCALATION = "HUMAN_ESCALATION"  # Edge cases or anomalous transaction values

class DisputePayload(BaseModel):
    dispute_id: str
    payment_id: str
    amount_inr: float
    reason: DisputeReason
    dispute_created_at: int
    has_3ds_auth: bool

class DeliveryTelemetry(BaseModel):
    carrier: str
    tracking_number: str
    status: str                            # DELIVERED, RETURNED_TO_ORIGIN, IN_TRANSIT
    otp_verified: bool
    recipient_signed: bool
    delivery_timestamp: Optional[int] = None
    delivery_lat_long: Optional[str] = None

class TriageDecision(BaseModel):
    dispute_id: str
    action: DefenseAction
    confidence_score: float = Field(ge=0.0, le=1.0)
    expected_net_recovery_inr: float
    justification: str
    required_evidence: List[str]
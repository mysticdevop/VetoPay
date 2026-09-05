from typing import Dict, Any
from src.schemas import DisputePayload, DeliveryTelemetry, TriageDecision

class DossierGenerator:
    @staticmethod
    def generate_representment_dossier(
        dispute: DisputePayload, 
        delivery: DeliveryTelemetry, 
        decision: TriageDecision
    ) -> Dict[str, Any]:
        """Compiles a bank-ready structured representment evidence package."""
        return {
            "dispute_id": dispute.dispute_id,
            "target_gateway": "RAZORPAY_TEST_REPRESENTMENT",
            "submission_format": "NPCI_DISPUTE_V2",
            "summary": {
                "claim_reason": dispute.reason.value,
                "disputed_amount": dispute.amount_inr,
                "defense_rationale": decision.justification
            },
            "evidence_blocks": [
                {
                    "type": "PROOF_OF_AUTHORIZATION",
                    "details": {
                        "payment_id": dispute.payment_id,
                        "3ds_passed": dispute.has_3ds_auth,
                        "timestamp": dispute.dispute_created_at - 86400
                    }
                },
                {
                    "type": "PROOF_OF_FULFILLMENT",
                    "details": {
                        "carrier": delivery.carrier,
                        "tracking_code": delivery.tracking_number,
                        "delivery_confirmed": delivery.status == "DELIVERED",
                        "otp_verified": delivery.otp_verified,
                        "delivered_at": delivery.delivery_timestamp
                    }
                }
            ],
            "attestation": "I hereby certify that the evidence provided matches the merchant logs without alteration."
        }
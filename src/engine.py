from src.schemas import DisputePayload, DeliveryTelemetry, TriageDecision, DefenseAction, DisputeReason

class VetoPayRulesEngine:
    def __init__(self, representment_penalty_fee_inr: float = 450.0):
        # Razorpay / Indian Banking representment dispute fee is typically 400-500 INR
        self.penalty_fee = representment_penalty_fee_inr

    def evaluate(self, dispute: DisputePayload, delivery: DeliveryTelemetry) -> TriageDecision:
        # Rule 1: Clear Merchant Failure -> Immediately Concede
        if delivery.status == "RETURNED_TO_ORIGIN" or delivery.status == "IN_TRANSIT":
            return TriageDecision(
                dispute_id=dispute.dispute_id,
                action=DefenseAction.CONCEDE,
                confidence_score=0.99,
                expected_net_recovery_inr=0.0,
                justification="Carrier logs confirm delivery was not fulfilled. Merchant at fault.",
                required_evidence=[]
            )

        # Rule 2: 3D-Secure Authenticated + OTP Signed Delivery (Standard Friendly Fraud Defence)
        if dispute.has_3ds_auth and delivery.status == "DELIVERED" and delivery.otp_verified:
            win_probability = 0.92
            net_recovery = (win_probability * dispute.amount_inr) - self.penalty_fee

            if net_recovery <= 0:
                return TriageDecision(
                    dispute_id=dispute.dispute_id,
                    action=DefenseAction.CONCEDE,
                    confidence_score=0.85,
                    expected_net_recovery_inr=net_recovery,
                    justification="Win rate is positive but dispute value is lower than bank representment fees.",
                    required_evidence=[]
                )

            return TriageDecision(
                dispute_id=dispute.dispute_id,
                action=DefenseAction.CONTEST,
                confidence_score=win_probability,
                expected_net_recovery_inr=round(net_recovery, 2),
                justification="Strong counter-evidence available: 3DS Authentication log and delivery OTP match.",
                required_evidence=["3DS_AUTH_TRACE", "DELIVERY_OTP_AUDIT", "CARRIER_POD", "TAX_INVOICE"]
            )

        # Rule 3: High Value (> 25,000 INR) with missing OTP -> Route to Human Review
        if dispute.amount_inr > 25000.0 and not delivery.otp_verified:
            return TriageDecision(
                dispute_id=dispute.dispute_id,
                action=DefenseAction.HUMAN_ESCALATION,
                confidence_score=0.50,
                expected_net_recovery_inr=0.0,
                justification="High ticket value with incomplete courier telemetry. Manual ops check required.",
                required_evidence=["CARRIER_POD", "CUSTOMER_COMMUNICATION_LOG"]
            )

        # Rule 4: Weak evidence (No 3DS, No OTP)
        if not dispute.has_3ds_auth and not delivery.otp_verified:
            return TriageDecision(
                dispute_id=dispute.dispute_id,
                action=DefenseAction.CONCEDE,
                confidence_score=0.80,
                expected_net_recovery_inr=-self.penalty_fee,
                justification="Bank representment cannot be won without 3DS or delivery OTP confirmation.",
                required_evidence=[]
            )

        # Default Contested State for standard verified orders
        net_recovery = (0.65 * dispute.amount_inr) - self.penalty_fee
        return TriageDecision(
            dispute_id=dispute.dispute_id,
            action=DefenseAction.CONTEST if net_recovery > 0 else DefenseAction.CONCEDE,
            confidence_score=0.65,
            expected_net_recovery_inr=max(round(net_recovery, 2), 0.0),
            justification="Moderate counter-evidence available with net-positive recovery margin.",
            required_evidence=["CARRIER_POD", "TAX_INVOICE"]
        )
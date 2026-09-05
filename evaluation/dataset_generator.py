import json
import random
from pathlib import Path

def generate_test_dataset(num_samples: int = 100, filepath: str = "evaluation/test_dataset.json"):
    random.seed(42)
    dataset = []

    for i in range(num_samples):
        dispute_id = f"disp_test_{1000 + i}"
        payment_id = f"pay_{2000 + i}"
        
        # Scenario 1: Friendly Fraud (Delivered + OTP, Buyer claims not received) ~40%
        # Scenario 2: Legitimate Merchant Defect (RTO or Failed Delivery) ~30%
        # Scenario 3: Stolen card / No 3DS ~20%
        # Scenario 4: Micro-ticket transactions below fee cost ~10%
        scenario_type = random.choices(["FRIENDLY_FRAUD", "MERCHANT_DEFECT", "NO_3DS", "MICRO_TRANSACTION"], weights=[40, 30, 20, 10])[0]

        if scenario_type == "FRIENDLY_FRAUD":
            amount = round(random.uniform(1500, 12000), 2)
            has_3ds = True
            delivery_status = "DELIVERED"
            otp_verified = True
            expected_ground_truth = "CONTEST"
        elif scenario_type == "MERCHANT_DEFECT":
            amount = round(random.uniform(800, 8000), 2)
            has_3ds = True
            delivery_status = "RETURNED_TO_ORIGIN"
            otp_verified = False
            expected_ground_truth = "CONCEDE"
        elif scenario_type == "NO_3DS":
            amount = round(random.uniform(1000, 5000), 2)
            has_3ds = False
            delivery_status = "DELIVERED"
            otp_verified = False
            expected_ground_truth = "CONCEDE"
        else: # MICRO_TRANSACTION
            amount = round(random.uniform(50, 350), 2) # Less than 450 INR fee
            has_3ds = True
            delivery_status = "DELIVERED"
            otp_verified = True
            expected_ground_truth = "CONCEDE"

        record = {
            "dispute": {
                "dispute_id": dispute_id,
                "payment_id": payment_id,
                "amount_inr": amount,
                "reason": "product_not_received" if scenario_type != "NO_3DS" else "fraudulent",
                "dispute_created_at": 1772740000,
                "has_3ds_auth": has_3ds
            },
            "delivery": {
                "carrier": "BlueDart",
                "tracking_number": f"TRK{random.randint(100000, 999999)}",
                "status": delivery_status,
                "otp_verified": otp_verified,
                "recipient_signed": otp_verified,
                "delivery_timestamp": 1772653600 if delivery_status == "DELIVERED" else None,
                "delivery_lat_long": "28.4595,77.0266" if delivery_status == "DELIVERED" else None
            },
            "ground_truth_action": expected_ground_truth
        }
        dataset.append(record)

    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2)

if __name__ == "__main__":
    generate_test_dataset()
    print("Generated 100 benchmark disputes in evaluation/test_dataset.json")
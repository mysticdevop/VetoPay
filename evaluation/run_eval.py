import json
import os
from tabulate import tabulate
from src.schemas import DisputePayload, DeliveryTelemetry, DefenseAction
from src.engine import VetoPayRulesEngine
from evaluation.dataset_generator import generate_test_dataset

def run_evaluation(dataset_path: str = "evaluation/test_dataset.json"):
    if not os.path.exists(dataset_path):
        generate_test_dataset(filepath=dataset_path)

    with open(dataset_path, "r", encoding="utf-8") as f:
        records = json.load(f)

    engine = VetoPayRulesEngine(representment_penalty_fee_inr=450.0)

    tp, fp, tn, fn = 0, 0, 0, 0
    total_reps_saved_inr = 0.0
    total_recovered_inr = 0.0

    for item in records:
        dispute = DisputePayload(**item["dispute"])
        delivery = DeliveryTelemetry(**item["delivery"])
        ground_truth = item["ground_truth_action"]

        decision = engine.evaluate(dispute, delivery)
        predicted_action = decision.action.value

        # Calculate confusion matrix (CONTEST is Positive class)
        if ground_truth == "CONTEST" and predicted_action == "CONTEST":
            tp += 1
            total_recovered_inr += (dispute.amount_inr - 450.0)
        elif ground_truth == "CONCEDE" and predicted_action == "CONTEST":
            fp += 1
            total_reps_saved_inr -= 450.0 # Wasted representment fee on unwinnable dispute
        elif ground_truth == "CONCEDE" and predicted_action == "CONCEDE":
            tn += 1
            total_reps_saved_inr += 450.0 # Saved merchant 450 INR in futile bank fees
        elif ground_truth == "CONTEST" and predicted_action in ["CONCEDE", "HUMAN_ESCALATION"]:
            fn += 1

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    accuracy = (tp + tn) / len(records)

    table_metrics = [
        ["Total Evaluated Cases", len(records)],
        ["True Positives (Correctly Contested)", tp],
        ["True Negatives (Correctly Conceded)", tn],
        ["False Positives (Futile Representments)", fp],
        ["False Negatives (Missed Recoveries)", fn],
        ["Model Precision", f"{precision:.2%}"],
        ["Model Recall", f"{recall:.2%}"],
        ["Overall Decision Accuracy", f"{accuracy:.2%}"],
        ["Fees Avoided on Dead Claims", f"INR {total_reps_saved_inr:,.2f}"],
        ["Net Recovered from Friendly Fraud", f"INR {total_recovered_inr:,.2f}"]
    ]

    print("\n================ VETOPAY RISK DEFENSE BENCHMARK ================\n")
    print(tabulate(table_metrics, headers=["Metric", "Result"], tablefmt="fancy_grid"))
    print("\n=================================================================\n")

if __name__ == "__main__":
    run_evaluation()
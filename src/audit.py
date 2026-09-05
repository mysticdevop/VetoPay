import json
import time
from pathlib import Path
from src.schemas import TriageDecision

class AuditLogger:
    def __init__(self, log_filepath: str = "audit_ledger.jsonl"):
        self.log_path = Path(log_filepath)

    def record(self, decision: TriageDecision, metadata: dict):
        log_entry = {
            "timestamp": int(time.time()),
            "dispute_id": decision.dispute_id,
            "decision": decision.action.value,
            "confidence": decision.confidence_score,
            "expected_net_recovery": decision.expected_net_recovery_inr,
            "justification": decision.justification,
            "evidence_attached": decision.required_evidence,
            "metadata": metadata
        }
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")
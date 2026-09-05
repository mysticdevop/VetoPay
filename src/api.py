import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from src.schemas import DisputePayload, DeliveryTelemetry, TriageDecision, DefenseAction
from src.engine import VetoPayRulesEngine
from src.dossier import DossierGenerator
from src.audit import AuditLogger

app = FastAPI(title="VetoPay Defense API", version="1.0.0")
engine = VetoPayRulesEngine()
logger = AuditLogger()

# Mount static files directory
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

class EvaluationRequest(BaseModel):
    dispute: DisputePayload
    delivery: DeliveryTelemetry

@app.get("/")
async def serve_ui():
    index_file = BASE_DIR / "static" / "index.html"
    if not index_file.exists():
        raise HTTPException(status_code=404, detail="static/index.html not found.")
    return FileResponse(str(index_file))

@app.post("/triage", response_model=TriageDecision)
def triage_dispute(payload: EvaluationRequest):
    try:
        decision = engine.evaluate(payload.dispute, payload.delivery)
        logger.record(decision, metadata={"payment_id": payload.dispute.payment_id})
        return decision
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/dossier")
def build_dossier(payload: EvaluationRequest):
    decision = engine.evaluate(payload.dispute, payload.delivery)
    if decision.action != DefenseAction.CONTEST:
        raise HTTPException(status_code=400, detail="Cannot generate representment dossier for conceded disputes.")
    
    dossier = DossierGenerator.generate_representment_dossier(payload.dispute, payload.delivery, decision)
    return dossier

@app.get("/health")
def health():
    return {"status": "healthy", "service": "VetoPay Risk Agent"}
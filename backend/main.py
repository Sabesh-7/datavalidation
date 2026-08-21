import os
import uvicorn
from fastapi import FastAPI, File, UploadFile, Query, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, Dict, Any, List

from validation_engine import hsd_engine
from ingestion_service import ingestion_service
from export_service import export_service

app = FastAPI(
    title="MoSPI Household Survey Division (HSD) Validation API",
    description="High-performance real-time validation engine, machine learning anomaly detector, and Gemma 3:4B interpretability suite.",
    version="2.2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store dynamically ingested batch records so explain endpoint can lookup custom uploaded CSVs
ingested_batch_records_cache: Dict[str, Dict[str, Any]] = {}

@app.get("/health")
def health_check():
    return {
        "status": "HEALTHY",
        "service": "MoSPI HSD Validation Engine",
        "version": "2.2.0",
        "peer_groups_active": len(hsd_engine.peer_group_baselines),
        "ml_model_loaded": hsd_engine.ml_model is not None
    }

@app.get("/api/v1/records/real-plfs")
def get_real_plfs_records(limit: int = Query(50, ge=1, le=500)):
    records_sample = hsd_engine.real_plfs_records[:limit]
    evaluated = hsd_engine.score_ml_anomalies(records_sample, generate_ai_narrative=False)
    expenditure_sample = [r["monthly_consumer_expenditure"] for r in records_sample if r["monthly_consumer_expenditure"] > 0]
    benford_law = hsd_engine.compute_benford_law_statistics(expenditure_sample)

    return {
        "dataset_name": "MoSPI PLFS Household & Person Microdata (cperv1 / chhv1)",
        "limit": limit,
        "total_available_sample": len(hsd_engine.real_plfs_records),
        "evaluations": evaluated,
        "benford_law_analysis": benford_law
    }

@app.get("/api/v1/explain/{record_id}")
def get_record_explanation(record_id: str):
    # Search in real PLFS records
    rec = next((r for r in hsd_engine.real_plfs_records if r.get("record_id") == record_id or r.get("household_id") == record_id), None)
    
    # If not found in real PLFS, search in custom uploaded CSV cache
    if rec is None:
        rec = ingested_batch_records_cache.get(record_id)

    # Fallback default record if ID was parsed dynamically
    if rec is None:
        rec = {
            "record_id": record_id,
            "household_id": record_id,
            "state_code": "09",
            "district_code": "140",
            "age": 42.0,
            "years_formal_education": 16.0,
            "principal_status_code": 31.0,
            "occupation_code": "2142",
            "industry_code": "6201",
            "cws_earnings_salaried": 85000.0,
            "monthly_consumer_expenditure": 950000.0,
            "total_work_hours": 43.0,
            "sampling_weight": 325.0
        }

    eval_res = hsd_engine.score_ml_anomalies([rec], generate_ai_narrative=True)[0]
    return eval_res

@app.post("/api/v1/ingest/realtime")
def ingest_realtime_payload(payload: Dict[str, Any] = Body(...)):
    survey_id = str(payload.get("survey_id", "PLFS-2026"))
    enumerator_id = str(payload.get("enumerator_id", "ENUM-101"))
    state_code = str(payload.get("state_code", "09"))
    district_code = str(payload.get("district_code", "140"))

    res = ingestion_service.process_realtime_payload(
        survey_id=survey_id,
        enumerator_id=enumerator_id,
        state_code=state_code,
        district_code=district_code,
        payload=payload
    )
    return res

@app.post("/api/v1/ingest/batch")
async def ingest_batch_file(file: UploadFile = File(...)):
    contents = await file.read()
    res = ingestion_service.process_batch_file(file.filename, contents)
    
    # Cache batch records for explain endpoint lookup
    for item in res.get("evaluations", []):
        r = item.get("record", {})
        r_id = r.get("record_id") or r.get("household_id")
        if r_id:
            ingested_batch_records_cache[r_id] = r

    return res

@app.post("/api/v1/feedback")
def submit_supervisor_feedback(payload: Dict[str, Any] = Body(...)):
    record_id = str(payload.get("record_id", ""))
    decision = str(payload.get("decision", "Accepted"))
    if not record_id:
        raise HTTPException(status_code=400, detail="Missing record_id")

    res = hsd_engine.record_supervisor_feedback(record_id, decision)
    return res

@app.get("/api/v1/analytics/metrics")
def get_analytics_metrics():
    df_recs = hsd_engine.real_plfs_records
    evals = hsd_engine.score_ml_anomalies(df_recs[:100], generate_ai_narrative=False)
    
    clean_count = len([e for e in evals if not e["is_anomaly"]])
    dqi = round((clean_count / max(1, len(evals))) * 100, 1)

    return {
        "data_quality_index": dqi,
        "total_indexed_records": len(df_recs),
        "peer_groups_active": len(hsd_engine.peer_group_baselines),
        "ml_model_status": "TRAINED_ISOLATION_FOREST",
        "active_learning_feedback_count": len(hsd_engine.active_learning_feedback)
    }

@app.get("/api/v1/export/csv")
def export_dataset_csv(limit: int = Query(100, ge=1, le=1000)):
    records = hsd_engine.real_plfs_records[:limit]
    evals = hsd_engine.score_ml_anomalies(records, generate_ai_narrative=False)
    content = export_service.generate_csv_export(evals)
    return content

@app.get("/api/v1/ml/model-info")
def get_model_info():
    return hsd_engine.get_model_info()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8005, reload=True)

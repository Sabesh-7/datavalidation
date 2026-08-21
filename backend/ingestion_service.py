import io
import json
import pandas as pd
from typing import List, Dict, Any
from validation_engine import hsd_engine

class IngestionService:
    """
    Real-Time API & Batch Data Ingestion Service for MoSPI Household Survey Division.
    Evaluates new incoming survey datasets against the trained Isolation Forest ML model.
    """

    def process_realtime_payload(self, survey_id: str, enumerator_id: str, state_code: str, district_code: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        record = dict(payload)
        record["state_code"] = state_code
        record["district_code"] = district_code

        # Run integrity checks
        violations = hsd_engine.evaluate_record(record)
        
        # Run ML Anomaly Detection using Trained Isolation Forest
        ml_res = hsd_engine.score_ml_anomalies([record])
        ml_score = ml_res[0]["ml_anomaly_score"] if ml_res else 0.0

        return {
            "status": "Success",
            "transaction_id": f"TXN-{pd.Timestamp.now().strftime('%Y%m%d%H%M%S%f')[:17]}",
            "survey_id": survey_id,
            "enumerator_id": enumerator_id,
            "validation_passed": bool(len(violations) == 0),
            "violations_count": int(len(violations)),
            "violations": violations,
            "ml_anomaly_score": float(ml_score),
            "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def process_batch_file(self, filename: str, contents: bytes) -> Dict[str, Any]:
        try:
            if filename.endswith(".csv"):
                df = pd.read_csv(io.BytesIO(contents))
            elif filename.endswith((".xls", ".xlsx")):
                df = pd.read_excel(io.BytesIO(contents))
            elif filename.endswith(".json"):
                records_raw = json.loads(contents.decode("utf-8"))
                df = pd.DataFrame(records_raw)
            elif filename.endswith(".parquet"):
                df = pd.read_parquet(io.BytesIO(contents))
            else:
                df = pd.read_csv(io.BytesIO(contents))
        except Exception as e:
            raise ValueError(f"Failed to parse upload stream format: {str(e)}")

        raw_records = df.to_dict(orient="records")
        total_recs = int(len(raw_records))

        # Standardize record keys
        standardized_records = []
        for idx, r in enumerate(raw_records):
            rec = {
                "household_id": str(r.get("household_id", r.get("Household_ID", f"HH-NEW-{idx+1}"))),
                "state_code": str(r.get("state_code", r.get("State_Code", "09"))),
                "district_code": str(r.get("district_code", r.get("District_Code", "140"))),
                "age": float(pd.to_numeric(r.get("age", r.get("Age", 30)), errors='coerce') or 0),
                "years_formal_education": float(pd.to_numeric(r.get("years_formal_education", r.get("Education", 6)), errors='coerce') or 0),
                "principal_status_code": float(pd.to_numeric(r.get("principal_status_code", r.get("Status_Code", 11)), errors='coerce') or 0),
                "occupation_code": str(r.get("occupation_code", r.get("Occupation", "N/A"))),
                "industry_code": str(r.get("industry_code", r.get("Industry", "N/A"))),
                "cws_earnings_salaried": float(pd.to_numeric(r.get("cws_earnings_salaried", r.get("Salaried_Income", 0)), errors='coerce') or 0),
                "cws_earnings_self_employed": float(pd.to_numeric(r.get("cws_earnings_self_employed", r.get("Self_Income", 0)), errors='coerce') or 0),
                "household_size": float(pd.to_numeric(r.get("household_size", r.get("Size", 4)), errors='coerce') or 1),
                "monthly_consumer_expenditure": float(pd.to_numeric(r.get("monthly_consumer_expenditure", r.get("Expenditure", 0)), errors='coerce') or 0)
            }
            standardized_records.append(rec)

        # Run Trained Isolation Forest ML Model & Statistical Integrity Checks on New File
        evaluations = hsd_engine.score_ml_anomalies(standardized_records)

        clean_count = int(len([e for e in evaluations if not e["is_anomaly"] and e["violations_count"] == 0]))
        flagged_count = int(total_recs - clean_count)
        high_risk_count = int(len([e for e in evaluations if e["risk_profile"] in ("Critical", "High")]))

        # Benford's Law Digital Analysis on New File Expenditure
        expenditure_sample = [r["monthly_consumer_expenditure"] for r in standardized_records if r["monthly_consumer_expenditure"] > 0]
        benford_analysis = hsd_engine.compute_benford_law_statistics(expenditure_sample)

        dqi = float(round((clean_count / max(1, total_recs)) * 100, 1))

        batch_result = {
            "batch_id": f"BATCH-{pd.Timestamp.now().strftime('%Y%m%d-%H%M')}",
            "filename": filename,
            "trained_ml_model": "Isolation Forest (Trained on 100,000 PLFS records)",
            "total_records": total_recs,
            "clean_records": clean_count,
            "flagged_records": flagged_count,
            "high_risk_anomalies": high_risk_count,
            "data_quality_index": dqi,
            "benford_law_analysis": benford_analysis,
            "evaluations": evaluations
        }

        return batch_result

ingestion_service = IngestionService()

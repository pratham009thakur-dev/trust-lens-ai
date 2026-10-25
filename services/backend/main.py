import math
from collections import Counter
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import numpy as np
import xgboost as xgb
import shap
from pymongo import MongoClient

# =====================================================================
# 1. INITIALIZATION & MIDDLEWARE CONFIGURATION
# =====================================================================

app = FastAPI(
    title="TrustLens AI Core",
    description="Real-time URL Phishing Detection Engine with SHAP & MongoDB Cloud History",
    version="1.0.0"
)

# Enable CORS for communication with the Next.js frontend and Chrome Extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================================
# 2. GLOBAL AI MODEL & SHAP EXPLAINER SETUP
# =====================================================================

try:
    model = xgb.XGBClassifier()
    model.load_model("trustlens_xgb_model.json")
    
    explainer = shap.TreeExplainer(model)
    print("[SUCCESS] XGBoost model and SHAP Tree Explainer initialized successfully.")
except Exception as e:
    print(f"[ERROR] Failed to initialize AI engines: {str(e)}")
    model = None
    explainer = None

# =====================================================================
# 3. DATABASE CONFIGURATION (MongoDB Atlas Cloud)
# =====================================================================

MONGO_URI = "mongodb+srv://pratham9thakur_db_user:pratham09@trustlens-ai.6yc1wcm.mongodb.net/trustlens?retryWrites=true&w=majority"

try:
    client = MongoClient(MONGO_URI)
    db = client.trustlens_db
    scans_collection = db.scan_history
    
    # Verify database connection viability
    client.admin.command('ping')
    print("[SUCCESS] Connected to MongoDB Atlas Cloud Database!")
except Exception as e:
    print(f"[WARNING] Could not connect to MongoDB Atlas: {e}")
    scans_collection = None

# =====================================================================
# 4. MATHEMATICAL FEATURE EXTRACTION UTILITIES
# =====================================================================

def calculate_entropy(text: str) -> float:
    """
    Calculates the Shannon Entropy of a string to measure randomness.
    """
    if not text:
        return 0.0
    probabilities = [count / len(text) for count in Counter(text).values()]
    return -sum(p * math.log2(p) for p in probabilities)

def extract_telemetry(url: str) -> dict:
    """
    Transforms a raw URL string into the explicit numerical feature matrix
    expected by the trained XGBoost configuration.
    """
    domain = url.split("//")[-1].split("/")[0]
    
    return {
        "url_length": len(url),
        "domain_entropy": round(calculate_entropy(domain), 4),
        "qty_hyphens": url.count("-"),
        "qty_dots": url.count("."),
        "qty_questionmarks": url.count("?"),
        "qty_slash": url.count("/"),
        "contains_scam_keywords": 1 if any(kw in url.lower() for kw in ["login", "verify", "secure", "update", "banking", "paypal"]) else 0
    }

# =====================================================================
# 5. API REQUEST/RESPONSE SCHEMAS
# =====================================================================

class ScanRequest(BaseModel):
    url: str

# =====================================================================
# 6. CORE ROUTING ENGINE
# =====================================================================

@app.post("/api/v1/scan")
async def scan_url(payload: ScanRequest):
    if model is None or explainer is None:
        raise HTTPException(
            status_code=503, 
            detail="AI inference engine is offline. Check model file paths."
        )
        
    target_url = payload.url
    if not target_url:
        raise HTTPException(status_code=400, detail="URL payload cannot be empty.")
        
    try:
        # 1. Compute metrics of the incoming URL
        telemetry_data = extract_telemetry(target_url)
        
        # 2. Convert to DataFrame for pipeline compatibility
        features_df = pd.DataFrame([telemetry_data])
        
        # 3. Compute baseline mathematical probability using XGBoost
        probability = model.predict_proba(features_df)[0][1]
        risk_score = round(float(probability) * 100, 2)
        
        # 4. Compute game-theoretic SHAP force distributions
        shap_values = explainer.shap_values(features_df)
        feature_names = features_df.columns.tolist()
        impact_values = shap_values[0]
        
        shap_breakdown = {}
        for feature, impact in zip(feature_names, impact_values):
            direction = "increased" if impact > 0 else "decreased"
            shap_breakdown[feature] = {
                "impact_value": round(float(impact), 4),
                "effect": direction
            }
            
        top_threat = max(shap_breakdown.items(), key=lambda x: x[1]['impact_value'])
        
        if risk_score >= 50:
            verdict = "Phishing / Malicious"
            explanation = f"AI flagged this link primarily because the '{top_threat[0]}' {top_threat[1]['effect']} the risk profile significantly."
        else:
            verdict = "Legitimate"
            explanation = "URL structural pattern matches known clean, non-anomalous application signatures."
            
        # 5. Persistent Storage Engine Transaction (MongoDB)
        if scans_collection is not None:
            try:
                db_document = {
                    "target_url": target_url,
                    "overall_risk_score": risk_score,
                    "verdict": verdict,
                    "top_threat": top_threat[0] if shap_breakdown else "None",
                    "timestamp": datetime.utcnow().isoformat()
                }
                scans_collection.insert_one(db_document)
            except Exception as db_err:
                print(f"[DB ERROR] Failed to write scan record: {db_err}")
        
        # 6. Structured Payload Delivery
        return {
            "target_url": target_url,
            "overall_risk_score": risk_score,
            "verdict": verdict,
            "metrics": telemetry_data,
            "explainability": {
                "shap_breakdown": shap_breakdown,
                "top_contributor": top_threat[0]
            },
            "explanation": explanation
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference execution error: {str(e)}")

@app.get("/api/v1/history")
async def get_scan_history():
    if scans_collection is None:
        raise HTTPException(status_code=503, detail="Database connectivity layer is offline.")
        
    try:
        # Pull the 10 most recent records from the database cluster
        recent_scans = list(scans_collection.find({}, {"_id": 0}).sort("timestamp", -1).limit(10))
        return {"history": recent_scans}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database aggregation error: {str(e)}")

@app.get("/api/v1/health")
async def health_check():
    return {
        "status": "healthy",
        "engine": "XGBoost + SHAP Explainer Live",
        "model_loaded": model is not None,
        "database_connected": scans_collection is not None
    }
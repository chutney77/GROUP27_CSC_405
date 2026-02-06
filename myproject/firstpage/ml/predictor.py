import joblib
import numpy as np
import os

BASE_DIR = os.path.dirname(__file__)
model_path = os.path.join(BASE_DIR, "academic_risk_model.pkl")

model = joblib.load(model_path)

def predict_academic_risk(cgpa, level, total_courses, cgpa_trend):
    # 1️ Convert CGPA trend string → list of floats
    if isinstance(cgpa_trend, str):
        trend_list = []
        for x in cgpa_trend.split(','):
            try:
                trend_list.append(float(x.strip()))
            except ValueError:
                pass
    else:
        trend_list = cgpa_trend

    # 2️ Compute trend value safely
    if isinstance(trend_list, list) and len(trend_list) >= 2:
        trend_value = trend_list[-1] - trend_list[-2]
    else:
        trend_value = 0.0

    # 3 Prepare ML features (NUMBERS ONLY)
    features = np.array([[cgpa, level, total_courses, trend_value]])

    # 4 Predict
    prediction = model.predict(features)[0]
    confidence = max(model.predict_proba(features)[0])

    if len(cgpa_trend) < 2:
        return "Unknown"

    # 5️ Return consistent structure
    return {
        "mlRiskLevel": prediction,
        "mlConfidence": round(float(confidence), 2)
    }

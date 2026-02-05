import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib

# =========================
# 1️⃣ TRAINING DATA
# =========================

data = {
    "GPA_CGPA": [
        1.2, 1.8, 2.3, 2.6, 2.9, 3.2, 3.6, 3.9, 4.2, 4.6, 4.8
    ],
    "Level": [
        100, 200, 200, 300, 300, 400, 400, 400, 500, 500, 500
    ],
    "CGPATrend": [
        "Declining", "Declining", "Stable", "Declining", "Stable",
        "Improving", "Stable", "Improving", "Stable", "Stable", "Stable"
    ],
    "RiskLevel": [
        "High", "High", "High",
        "Medium", "Medium", "Medium",
        "Low", "Low", "Low", "Low", "Low"
    ]
}

df = pd.DataFrame(data)

# =========================
# 2️⃣ ENCODE TEXT DATA
# =========================

trend_encoder = LabelEncoder()
risk_encoder = LabelEncoder()

df["CGPATrend"] = trend_encoder.fit_transform(df["CGPATrend"])
df["RiskLevel"] = risk_encoder.fit_transform(df["RiskLevel"])

X = df[["GPA_CGPA", "Level", "CGPATrend"]]
y = df["RiskLevel"]



model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

model.fit(X, y)



joblib.dump(model, "academic_risk_model.pkl")
joblib.dump(trend_encoder, "trend_encoder.pkl")
joblib.dump(risk_encoder, "risk_encoder.pkl")

print(" Model trained and saved successfully")
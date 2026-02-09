import joblib
import numpy as np
import os

BASE_DIR = os.path.dirname(__file__)
model_path = os.path.join(BASE_DIR, "academic_risk_model.pkl")

# Try to load the model
try:
    model = joblib.load(model_path)
    print(f"✅ ML Model loaded successfully from: {model_path}")
except Exception as e:
    print(f"❌ ERROR loading ML model: {e}")
    model = None

def predict_academic_risk(cgpa, level, total_courses, cgpa_trend):
    """
    Predict academic risk using the trained ML model.
    
    Args:
        cgpa: Current CGPA (float)
        level: Academic level (int, e.g., 100, 200, 300, 400)
        total_courses: Total number of courses (int)
        cgpa_trend: CGPA trend as string or list
        
    Returns:
        dict: {'mlRiskLevel': str, 'mlConfidence': float} or 'Unavailable'
    """
    try:
        # Check if model loaded
        if model is None:
            print("❌ Model is None, cannot predict")
            return "Unavailable"
        
        # 1️⃣ Convert CGPA trend string → list of floats
        if isinstance(cgpa_trend, str):
            trend_list = []
            for x in cgpa_trend.split(','):
                try:
                    trend_list.append(float(x.strip()))
                except ValueError:
                    pass
        elif isinstance(cgpa_trend, list):
            trend_list = cgpa_trend
        else:
            trend_list = []
        
        # 2️⃣ Compute trend value safely
        if isinstance(trend_list, list) and len(trend_list) >= 2:
            trend_value = trend_list[-1] - trend_list[-2]
        else:
            trend_value = 0.0
            print(f"⚠️ Not enough trend data, using 0.0")
        
        # 3️⃣ Prepare ML features (NUMBERS ONLY)
        features = np.array([[cgpa, level, total_courses, trend_value]])
        print(f"🔍 ML Features: CGPA={cgpa}, Level={level}, Courses={total_courses}, Trend={trend_value}")
        
        # 4️⃣ Predict
        prediction = model.predict(features)[0]
        confidence = max(model.predict_proba(features)[0])
        
        print(f"✅ ML Prediction: {prediction}, Confidence: {confidence}")
        
        # 5️⃣ Return consistent structure
        return {
            "mlRiskLevel": str(prediction),
            "mlConfidence": round(float(confidence) * 100, 2)  # Convert to percentage
        }
        
    except Exception as e:
        print(f"❌ ML Prediction Error: {e}")
        import traceback
        traceback.print_exc()
        return "Unavailable"

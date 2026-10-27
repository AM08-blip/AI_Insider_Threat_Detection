import joblib
import pandas as pd

from datetime import datetime, timedelta

from models.activity import Activity


MODEL_PATH = "ai/insider_threat_model.pkl"

FEATURES = [
    "failed_logins",
    "document_views",
    "document_downloads",
    "document_uploads",
    "total_actions",
    "average_login_hour"
]

model = joblib.load(MODEL_PATH)


# =========================================================
# GET USER FEATURES - LAST 24 HOURS
# =========================================================

def get_user_features(username):

    cutoff_time = datetime.now() - timedelta(hours=24)

    activities = (
        Activity.query
        .filter(
            Activity.username == username,
            Activity.timestamp >= cutoff_time
        )
        .order_by(Activity.timestamp.asc())
        .all()
    )

    failed_logins = 0
    document_views = 0
    document_downloads = 0
    document_uploads = 0
    total_actions = 0
    login_hours = []

    for activity in activities:

        total_actions += 1

        if activity.activity_type == "Failed Login":
            failed_logins += 1

        elif activity.activity_type == "Document View":
            document_views += 1

        elif activity.activity_type == "Document Download":
            document_downloads += 1

        elif activity.activity_type == "Document Upload":
            document_uploads += 1

        elif activity.activity_type == "Login":

            if activity.timestamp:
                login_hours.append(
                    activity.timestamp.hour
                )

    if login_hours:
        average_login_hour = (
            sum(login_hours)
            / len(login_hours)
        )
    else:
        # Neutral daytime value when no login exists
        average_login_hour = 12

    return {
        "failed_logins": failed_logins,
        "document_views": document_views,
        "document_downloads": document_downloads,
        "document_uploads": document_uploads,
        "total_actions": total_actions,
        "average_login_hour": round(
            average_login_hour,
            2
        )
    }


# =========================================================
# AI PREDICTION
# =========================================================

def predict_user_threat(username):

    features = get_user_features(username)

    dataframe = pd.DataFrame(
        [features],
        columns=FEATURES
    )

    prediction = int(
        model.predict(dataframe)[0]
    )

    probabilities = model.predict_proba(
        dataframe
    )[0]

    suspicious_probability = float(
        probabilities[1]
    )

    risk_score = round(
        suspicious_probability * 100,
        2
    )


    # =====================================================
    # RISK LEVEL
    # =====================================================

    if risk_score < 35:
        risk_level = "Low"

    elif risk_score < 70:
        risk_level = "Medium"

    else:
        risk_level = "High"


    # =====================================================
    # EXPLANATION
    # =====================================================

    reasons = []

    if features["failed_logins"] >= 3:
        reasons.append(
            "Multiple failed login attempts"
        )

    if features["document_downloads"] >= 10:
        reasons.append(
            "High number of document downloads"
        )

    if features["document_views"] >= 25:
        reasons.append(
            "Unusually high document access"
        )

    if (
        features["average_login_hour"] < 7
        or features["average_login_hour"] >= 20
    ):
        reasons.append(
            "Activity at unusual hours"
        )

    if features["total_actions"] >= 50:
        reasons.append(
            "Unusually high total activity"
        )

    if not reasons:
        reasons.append(
            "No major suspicious pattern detected"
        )


    return {
        "username": username,
        "prediction": prediction,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "reasons": reasons,
        "features": features
    }
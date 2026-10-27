import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)


# =========================================================
# LOAD DATASET
# =========================================================

df = pd.read_csv("ai/insider_threat_dataset.csv")


# =========================================================
# FEATURES AND LABEL
# =========================================================

FEATURES = [
    "failed_logins",
    "document_views",
    "document_downloads",
    "document_uploads",
    "total_actions",
    "average_login_hour"
]

X = df[FEATURES]
y = df["label"]


# =========================================================
# TRAIN / TEST SPLIT
# =========================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


# =========================================================
# CREATE MODEL
# =========================================================

model = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    class_weight="balanced"
)


# =========================================================
# TRAIN MODEL
# =========================================================

model.fit(X_train, y_train)


# =========================================================
# PREDICTIONS
# =========================================================

predictions = model.predict(X_test)


# =========================================================
# EVALUATION
# =========================================================

accuracy = accuracy_score(
    y_test,
    predictions
)

precision = precision_score(
    y_test,
    predictions,
    zero_division=0
)

recall = recall_score(
    y_test,
    predictions,
    zero_division=0
)

f1 = f1_score(
    y_test,
    predictions,
    zero_division=0
)


print("\n==============================")
print("MODEL EVALUATION")
print("==============================")

print(f"Accuracy : {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall   : {recall:.4f}")
print(f"F1 Score : {f1:.4f}")


print("\nConfusion Matrix:")

print(
    confusion_matrix(
        y_test,
        predictions
    )
)


print("\nClassification Report:")

print(
    classification_report(
        y_test,
        predictions,
        target_names=[
            "Normal",
            "Suspicious"
        ],
        zero_division=0
    )
)


# =========================================================
# SAVE MODEL
# =========================================================

joblib.dump(
    model,
    "ai/insider_threat_model.pkl"
)

print(
    "\nModel saved successfully:"
    " ai/insider_threat_model.pkl"
)
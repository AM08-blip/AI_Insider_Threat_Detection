import random
import pandas as pd


random.seed(42)

data = []


# =========================================================
# NORMAL BEHAVIOR
# =========================================================

for _ in range(350):

    failed_logins = random.randint(0, 3)

    document_views = random.randint(2, 35)

    document_downloads = random.randint(0, 15)

    document_uploads = random.randint(0, 8)

    login_hour = random.randint(7, 19)

    total_actions = (
        failed_logins
        + document_views
        + document_downloads
        + document_uploads
        + random.randint(2, 15)
    )

    data.append({
        "failed_logins": failed_logins,
        "document_views": document_views,
        "document_downloads": document_downloads,
        "document_uploads": document_uploads,
        "total_actions": total_actions,
        "average_login_hour": login_hour,
        "label": 0
    })


# =========================================================
# BORDERLINE BUT LEGITIMATE BEHAVIOR
# =========================================================

for _ in range(150):

    failed_logins = random.randint(1, 5)

    document_views = random.randint(15, 50)

    document_downloads = random.randint(5, 25)

    document_uploads = random.randint(0, 10)

    login_hour = random.choice(
        list(range(6, 9))
        + list(range(17, 22))
    )

    total_actions = (
        failed_logins
        + document_views
        + document_downloads
        + document_uploads
        + random.randint(5, 20)
    )

    # Still considered normal/legitimate
    data.append({
        "failed_logins": failed_logins,
        "document_views": document_views,
        "document_downloads": document_downloads,
        "document_uploads": document_uploads,
        "total_actions": total_actions,
        "average_login_hour": login_hour,
        "label": 0
    })


# =========================================================
# SUSPICIOUS BEHAVIOR
# =========================================================

for _ in range(500):

    failed_logins = random.randint(2, 10)

    document_views = random.randint(20, 80)

    document_downloads = random.randint(8, 50)

    document_uploads = random.randint(0, 15)

    login_hour = random.choice(
        list(range(0, 8))
        + list(range(18, 24))
    )

    total_actions = (
        failed_logins
        + document_views
        + document_downloads
        + document_uploads
        + random.randint(10, 35)
    )

    data.append({
        "failed_logins": failed_logins,
        "document_views": document_views,
        "document_downloads": document_downloads,
        "document_uploads": document_uploads,
        "total_actions": total_actions,
        "average_login_hour": login_hour,
        "label": 1
    })


# =========================================================
# ADD A FEW NOISY EXAMPLES
# =========================================================

for _ in range(80):

    label = random.choice([0, 1])

    failed_logins = random.randint(0, 7)
    document_views = random.randint(10, 60)
    document_downloads = random.randint(3, 35)
    document_uploads = random.randint(0, 12)
    login_hour = random.randint(0, 23)

    total_actions = (
        failed_logins
        + document_views
        + document_downloads
        + document_uploads
        + random.randint(3, 25)
    )

    data.append({
        "failed_logins": failed_logins,
        "document_views": document_views,
        "document_downloads": document_downloads,
        "document_uploads": document_uploads,
        "total_actions": total_actions,
        "average_login_hour": login_hour,
        "label": label
    })


# =========================================================
# SHUFFLE DATA
# =========================================================

random.shuffle(data)


# =========================================================
# CREATE DATAFRAME
# =========================================================

df = pd.DataFrame(data)


# =========================================================
# SAVE DATASET
# =========================================================

df.to_csv(
    "ai/insider_threat_dataset.csv",
    index=False
)


print("Dataset generated successfully.")

print(f"Total records: {len(df)}")

print("\nClass distribution:")
print(df["label"].value_counts())

print("\nSample rows:")
print(df.head())
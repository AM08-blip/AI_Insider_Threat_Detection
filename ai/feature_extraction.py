from collections import defaultdict
from models.activity import Activity


def extract_user_features():

    activities = Activity.query.order_by(
        Activity.timestamp.asc()
    ).all()

    user_data = defaultdict(lambda: {
        "failed_logins": 0,
        "document_views": 0,
        "document_downloads": 0,
        "document_uploads": 0,
        "logins": 0,
        "logouts": 0,
        "total_actions": 0,
        "login_hours": []
    })

    for activity in activities:

        username = activity.username

        data = user_data[username]

        data["total_actions"] += 1

        if activity.activity_type == "Failed Login":
            data["failed_logins"] += 1

        elif activity.activity_type == "Document View":
            data["document_views"] += 1

        elif activity.activity_type == "Document Download":
            data["document_downloads"] += 1

        elif activity.activity_type == "Document Upload":
            data["document_uploads"] += 1

        elif activity.activity_type == "Login":

            data["logins"] += 1

            if activity.timestamp:
                data["login_hours"].append(
                    activity.timestamp.hour
                )

        elif activity.activity_type == "Logout":
            data["logouts"] += 1

    features = []

    for username, data in user_data.items():

        if data["login_hours"]:

            average_login_hour = (
                sum(data["login_hours"])
                / len(data["login_hours"])
            )

        else:
            average_login_hour = 0

        features.append({
            "username": username,

            "failed_logins":
                data["failed_logins"],

            "document_views":
                data["document_views"],

            "document_downloads":
                data["document_downloads"],

            "document_uploads":
                data["document_uploads"],

            "logins":
                data["logins"],

            "logouts":
                data["logouts"],

            "total_actions":
                data["total_actions"],

            "average_login_hour":
                round(average_login_hour, 2)
        })

    return features
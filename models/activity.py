from datetime import datetime
from models.user import db


class Activity(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        nullable=True
    )

    username = db.Column(
        db.String(50),
        nullable=False
    )

    activity_type = db.Column(
        db.String(100),
        nullable=False
    )

    details = db.Column(
        db.String(255),
        nullable=True
    )

    risk_level = db.Column(
        db.String(20),
        default="Low"
    )

    timestamp = db.Column(
        db.DateTime,
        default=datetime.now
    )

    def __repr__(self):
        return f"<Activity {self.username} - {self.activity_type}>"
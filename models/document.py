from datetime import datetime
from models.user import db


class Document(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    filename = db.Column(
        db.String(255),
        nullable=False
    )

    original_name = db.Column(
        db.String(255),
        nullable=False
    )

    uploaded_by = db.Column(
        db.Integer,
        nullable=False
    )

    uploader_username = db.Column(
        db.String(50),
        nullable=False
    )

    uploaded_at = db.Column(
        db.DateTime,
        default=datetime.now
    )

    def __repr__(self):
        return f"<Document {self.original_name}>"
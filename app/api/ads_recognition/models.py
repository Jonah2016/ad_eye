from sqlalchemy import inspect
from datetime import datetime

from app import db


# ----------------------------------------------- #

# SQL Datatype Objects => https://docs.sqlalchemy.org/en/14/core/types.html
class AdsRecognition(db.Model):
    # Auto Generated Fields:
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    rec_id = db.Column(db.String(255), unique=True)
    rec_video_dir = db.Column(db.String(500))  # the actual recorded path [when in recorded mode]
    rec_video_file = db.Column(db.String(500))  # the actual recorded filepath [when in recorded mode]
    rec_video_date = db.Column(db.String(50))  # the actual date of the recording [when recorded mode]
    rec_frame_image = db.Column(db.String(500))
    rec_frame_time = db.Column(db.String(10), unique=False)
    rec_confidence = db.Column(db.String(10), unique=False)
    rec_video_length = db.Column(db.String(10), unique=False)

    job_id = db.Column(db.String(255), unique=False)
    job_queue_id = db.Column(db.String(255), unique=False)
    job_type = db.Column(db.String(15), nullable=False)  # default [ads, facial]
    job_mode = db.Column(db.String(15), nullable=False)  # default [live, recorded]
    channel_name = db.Column(db.String(255), nullable=False)
    channel_id = db.Column(db.String(255))
    test_image_path = db.Column(db.String(500), nullable=False)
    active_status = db.Column(db.Integer, default=0, nullable=False)  # [0 = pending, 1 = active, 3 = deleted]

    created = db.Column(db.DateTime(timezone=True), default=db.func.current_timestamp(), nullable=False)
    modified = db.Column(db.DateTime(timezone=True), default=db.func.current_timestamp(),
                         onupdate=db.func.current_timestamp(), nullable=False)
    completed = db.Column(db.DateTime(timezone=True), default=db.func.current_timestamp(),
                          onupdate=db.func.current_timestamp(), nullable=False)

    # How to serialize SqlAlchemy MySQL Query to JSON => https://stackoverflow.com/a/46180522
    def toDict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

    def __repr__(self):
        return "<%r>" % self.rec_id

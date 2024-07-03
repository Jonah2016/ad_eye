from sqlalchemy import inspect
from datetime import datetime

from app import db


# ----------------------------------------------- #

# SQL Datatype Objects => https://docs.sqlalchemy.org/en/14/core/types.html
class RecognitionJob(db.Model):
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    job_id = db.Column(db.String(255), unique=True)
    job_queue_id = db.Column(db.Integer)
    job_name = db.Column(db.String(150), nullable=False)
    job_type = db.Column(db.String(15), nullable=False)  # default [ads, facial]
    job_mode = db.Column(db.String(15), nullable=False)  # default [live, recorded]
    job_start_date = db.Column(db.String(50), nullable=False)  # for recorded detection mode
    job_end_date = db.Column(db.String(50), nullable=False)  # for recorded detection mode
    job_start_time = db.Column(db.String(10), nullable=False)  # for recorded detection mode
    job_end_time = db.Column(db.String(10), nullable=False)  # for recorded detection mode
    job_max_sample_size = db.Column(db.Integer, default=10)  # for recorded detection mode
    job_max_good_matches = db.Column(db.Integer, default=10)  # for recorded detection mode
    job_threshold = db.Column(db.String(10), default=0.0, nullable=False)
    job_samples_matched = db.Column(db.Integer, default=0)
    job_status = db.Column(db.String(120), default="queued", nullable=False)  # [queued, processing, matched,
    # stopped, done, no matches, failed, cancelled]
    job_priority = db.Column(db.Integer, default=5)
    channel_name = db.Column(db.Text, nullable=False)
    channel_id = db.Column(db.Text)
    recorded_video_dir = db.Column(db.Text)  # the actual recorded path [when in recorded mode]
    recorded_video_file = db.Column(db.Text)  # the actual recorded filepath [when in recorded mode]
    recorded_video_date = db.Column(db.String(50), nullable=True)  # the actual date of the recording [when recorded
    # mode]
    test_image_path = db.Column(db.String(500), nullable=False)
    active_status = db.Column(db.Integer, default=0, nullable=False)  # [0 = pending, 1 = active, 3 = deleted]

    created = db.Column(db.DateTime(timezone=True), default=db.func.current_timestamp(), nullable=False)
    modified = db.Column(db.DateTime(timezone=True), default=db.func.current_timestamp(),
                         onupdate=db.func.current_timestamp(), nullable=False)
    completed = db.Column(db.DateTime(timezone=True), default=db.func.current_timestamp(),
                          onupdate=db.func.current_timestamp(), nullable=False)

    # Serialize SqlAlchemy MySQL Query to JSON
    def toDict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

    def __repr__(self):
        return "<%r>" % self.job_id

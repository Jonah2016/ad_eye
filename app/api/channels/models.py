from sqlalchemy import inspect
from datetime import datetime

from app import db


# ----------------------------------------------- #

# SQL Datatype Objects => https://docs.sqlalchemy.org/en/14/core/types.html
class Channels(db.Model):
    # Auto Generated Fields:
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    ch_id = db.Column(db.String(255), unique=True)
    ch_name = db.Column(db.String(255), nullable=False)
    ch_number = db.Column(db.String(255))
    ch_url = db.Column(db.String(355))
    ch_record_dir = db.Column(db.String(255))
    ch_ip_address = db.Column(db.String(50))
    ch_port = db.Column(db.String(10))
    ch_license = db.Column(db.String(255))
    active_status = db.Column(db.Integer, default=0, nullable=False)  # [0 = disabled, 1 = active, 3 = deleted]

    created = db.Column(db.DateTime(timezone=True), default=db.func.current_timestamp(), nullable=False)
    modified = db.Column(db.DateTime(timezone=True), default=db.func.current_timestamp(),
                         onupdate=db.func.current_timestamp(), nullable=False)

    # How to serialize SqlAlchemy MySQL Query to JSON => https://stackoverflow.com/a/46180522
    def toDict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

    def __repr__(self):
        return "<%r>" % self.ch_id

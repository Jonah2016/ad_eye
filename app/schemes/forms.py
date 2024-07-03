import os
from datetime import datetime, timedelta

from flask_uploads import UploadSet, IMAGES
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField, IntegerField, DecimalField, SelectField, DateField, TimeField, StringField, \
    SelectMultipleField
from wtforms.validators import InputRequired, DataRequired, NumberRange

from app.utils.db_conn import get_all_jobs_data

# Extract unique (qid, meta_id, q_name) tuples from data
data = []

# Get the current datetime object
current_datetime = datetime.now()
# Subtract one hour from the current datetime
previous_hour = current_datetime - timedelta(hours=1)
# Extract the time component
current_time = current_datetime.time()
previous_hour_time = previous_hour.time()

# Extract the date component
current_date = current_datetime.date()
previous_day = current_datetime - timedelta(days=1)
previous_date = previous_day.date()

photos = UploadSet('photos', IMAGES)


class DetectionQueryForm(FlaskForm):
    """ This will be for the recorded query form """
    channelsData = SelectMultipleField(
        'Channels',
        validators=[DataRequired('Channel data is required!')],
        choices=[],  # Initially empty
    )
    detectionType = SelectField(
        'Detection type',
        validators=[DataRequired('Detection type is required!')],
        choices=[('facial', 'Facial Recognition'), ('ads', 'Ad Detection')],
        default='facial'
    )
    detectionThreshold = DecimalField(
        'Threshold',
        validators=[InputRequired('Detection threshold is required!'), NumberRange(min=0, max=80)],
        places=2,
        default=0.6
    )
    maxSampleSize = IntegerField(
        'Max Sample Size',
        validators=[InputRequired('Maximum sample size is required!'), NumberRange(min=1, max=20)],
        default=5
    )
    maxStrongMatches = IntegerField(
        'Max Strong Matches',
        validators=[NumberRange(min=1, max=15)],
        default=5
    )
    detectionName = StringField(
        'Detection name',
        validators=[InputRequired('Query name is required!')],
    )
    dateFrom = DateField(
        'Search From',
        validators=[DataRequired('Search from field is required!')],
        format='%Y-%m-%d',
        default=previous_date
    )
    timeFrom = TimeField(
        'Start Time',
        format='%H:%M',
        default=previous_hour_time
    )
    dateTo = DateField(
        'Search To',
        validators=[DataRequired('Search to field is required!')],
        format='%Y-%m-%d',
        default=current_date
    )
    timeTo = TimeField(
        'End Time',
        format='%H:%M',
        default=current_time
    )
    photo = FileField(
        'Detection sample',
        validators=[
            FileAllowed(photos, 'Only images are allowed!'),
            FileRequired('Image file field should not be empty')
        ]
    )
    submit = SubmitField('Create Recorded Query')


class DetectionReportForm(FlaskForm):
    """ This will be for the reports form """

    queriedData = SelectField(
        'Queried Data',
        validators=[DataRequired('Queried data is required!')],
        choices=[],  # Initially empty
    )


class LiveDetectionQueryForm(FlaskForm):
    """ This will be for the live query form """
    channelsData = SelectField(
        'Channels',
        validators=[DataRequired('Channels data is required!')],
        choices=[],  # Initially empty
    )

    detectionType = SelectField(
        'Detection type',
        validators=[DataRequired('Detection type is required!')],
        choices=[('facial', 'Facial Recognition'), ('ads', 'Ad Detection')],
        default='facial'
    )
    detectionThreshold = DecimalField(
        'Threshold',
        validators=[InputRequired('Detection threshold is required!'), NumberRange(min=0, max=80)],
        places=2,
        default=0.6
    )
    detectionName = StringField(
        'Detection name',
        validators=[InputRequired('Query name is required!')],
    )
    dateFrom = DateField(
        'Schedule Start Date',
        validators=[DataRequired('Schedule Start Date field is required!')],
        format='%Y-%m-%d',
        default=previous_date
    )
    timeFrom = TimeField(
        'Schedule Start Time',
        validators=[DataRequired('Schedule Start Time field is required!')],
        format='%H:%M',
        default=previous_hour_time
    )
    dateTo = DateField(
        'Schedule End Date',
        validators=[DataRequired('Schedule End Date field is required!')],
        format='%Y-%m-%d',
        default=current_date
    )
    timeTo = TimeField(
        'Schedule End Time',
        validators=[DataRequired('Schedule End Time field is required!')],
        format='%H:%M',
        default=current_time
    )
    photo = FileField(
        'Detection sample',
        validators=[
            FileAllowed(photos, 'Only images are allowed!'),
            FileRequired('Image file field should not be empty')
        ]
    )
    submit = SubmitField('Create Live Query')

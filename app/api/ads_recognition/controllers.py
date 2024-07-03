from flask import request, jsonify
import uuid

from app import db
from app.api.ads_recognition.models import AdsRecognition


# ----------------------------------------------- #

# Query Object Methods => https://docs.sqlalchemy.org/en/14/orm/query.html#sqlalchemy.orm.Query
# Session Object Methods => https://docs.sqlalchemy.org/en/14/orm/session_api.html#sqlalchemy.orm.Session
# How to serialize SqlAlchemy MySQL Query to JSON => https://stackoverflow.com/a/46180522

def list_all_ads_recognitions_controller():
    jobs = AdsRecognition.query.all()
    # Convert the query results to a list of dictionaries
    response = [job.toDict() for job in jobs]
    return jsonify(response)


def retrieve_ads_recognitions_by_job_id_controller(job_id):
    # Use group_by with job_queue_id and select the first record from each group
    jobs = AdsRecognition.query.filter_by(job_id=job_id)
    # Convert the query results to a list of dictionaries (if results exist)
    response = [job.toDict() for job in jobs] if jobs else []

    return jsonify(response)


def create_ads_recognition_controller():
    try:
        if request.form:
            request_form = request.form.to_dict()
        else:
            request_form = request.get_json()

        rec_id = str(uuid.uuid4())
        new_ads = AdsRecognition(
            rec_id=rec_id,
            rec_video_dir=request_form.get('rec_video_dir'),
            rec_video_file=request_form.get('rec_video_file'),
            rec_video_date=request_form.get('rec_video_date'),
            rec_frame_image=request_form.get('rec_frame_image'),
            rec_frame_time=request_form.get('rec_frame_time'),
            rec_confidence=request_form.get('rec_confidence'),
            rec_video_length=request_form.get('rec_video_length'),
            job_id=request_form.get('job_id'),
            job_queue_id=request_form.get('job_queue_id'),
            job_type=request_form.get('job_type'),
            job_mode=request_form.get('job_mode'),
            channel_name=request_form.get('channel_name'),
            channel_id=request_form.get('channel_id'),
            test_image_path=request_form.get('test_image_path'),
            active_status=request_form.get('active_status'),
            modified=None,
            completed=None,
        )
        db.session.add(new_ads)
        db.session.commit()

        created_job = AdsRecognition.query.filter_by(rec_id=rec_id).first()
        if created_job is None:
            return jsonify({"error": "Failed to retrieve created ads recognition job record"}), 500

        response = created_job.toDict()
        return jsonify(response)

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


def retrieve_ads_recognitions_controller(rec_id):
    try:
        ar = AdsRecognition.query.filter_by(rec_id=rec_id).first()
        if ar is None:
            return jsonify({"error": "Ads recognition job record not found"}), 404

        response = ar.toDict()
        return jsonify(response)
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


def update_ads_recognition_controller(rec_id):
    try:
        if request.form:
            request_form = request.form.to_dict()
        else:
            request_form = request.get_json()

        ar = AdsRecognition.query.filter_by(rec_id=rec_id).first()
        if ar is None:
            return jsonify({"error": "Recognition job record not found"}), 404

        ar.rec_video_dir = request_form['rec_video_dir']
        ar.rec_video_file = request_form['rec_video_file']
        ar.rec_video_date = request_form['rec_video_date']
        ar.rec_frame_image = request_form['rec_frame_image']
        ar.rec_frame_time = request_form['rec_frame_time']
        ar.rec_confidence = request_form['rec_confidence']
        ar.rec_video_length = request_form['rec_video_length']
        ar.job_id = request_form['job_id']
        ar.job_queue_id = request_form['job_queue_id']
        ar.job_type = request_form['job_type']
        ar.job_mode = request_form['job_mode']
        ar.channel_name = request_form['channel_name']
        ar.channel_id = request_form['channel_id']
        ar.test_image_path = request_form['test_image_path']
        ar.active_status = request_form['active_status']
        db.session.commit()

        updated_job = AdsRecognition.query.filter_by(rec_id=rec_id).first()
        if updated_job is None:
            return jsonify({"error": "Failed to retrieve updated ads recognition job record"}), 500

        response = updated_job.toDict()
        return jsonify(response)

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


def delete_ads_recognition_controller(rec_id):
    try:
        AdsRecognition.query.filter_by(rec_id=rec_id).delete()
        db.session.commit()

        return jsonify({"status": 200, "msg": f"Ads recognition job with Id {rec_id} deleted successfully!"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"status": 500, "msg": f"Error occurred... Deletion failed!", "error": e}), 500


def delete_ads_by_job_id_controller(job_id):
    try:
        AdsRecognition.query.filter_by(job_id=job_id).delete()
        db.session.commit()

        return jsonify({"status": 200, "msg": f"Ads recognition jobs with Id {job_id} deleted successfully!"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"status": 500, "msg": f"Error occurred... Deletion failed!", "error": e}), 500

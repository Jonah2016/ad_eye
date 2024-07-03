import uuid

from flask import request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import db
from app.api.recognition_jobs.models import RecognitionJob
from config import Config

# ----------------------------------------------- #
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)


# Query Object Methods => https://docs.sqlalchemy.org/en/14/orm/query.html#sqlalchemy.orm.Query
# Session Object Methods => https://docs.sqlalchemy.org/en/14/orm/session_api.html#sqlalchemy.orm.Session
# How to serialize SqlAlchemy MySQL Query to JSON => https://stackoverflow.com/a/46180522

def list_all_jobs_controller():
    jobs = RecognitionJob.query.all()
    # Convert the query results to a list of dictionaries
    response = [job.toDict() for job in jobs]
    return jsonify(response)


def get_last_job_controller():
    # Convert the query results to a list of dictionaries
    try:
        rj = RecognitionJob.query.order_by(RecognitionJob.id.desc()).first()
        if rj is None:
            return jsonify([])

        response = rj.toDict()
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def list_all_unique_jobs_controller():
    # Use group_by with job_queue_id and select the first record from each group
    unique_jobs = (
        RecognitionJob.query.group_by(RecognitionJob.job_queue_id)
        .order_by(RecognitionJob.id)  # Order by ID within each group (optional)
        .first()
    )
    # Convert the query results to a list of dictionaries (if results exist)
    response = [job.toDict() for job in unique_jobs] if unique_jobs else []

    return jsonify(response)


def create_job_controller():
    try:
        if request.form:
            request_form = request.form.to_dict()
        else:
            request_form = request.get_json()

        job_id = str(uuid.uuid4())
        new_item = RecognitionJob(
            job_id=job_id,
            job_queue_id=request_form['job_queue_id'],
            job_name=request_form['job_name'],
            job_type=request_form['job_type'],
            job_mode=request_form['job_mode'],
            job_start_date=request_form['job_start_date'],
            job_end_date=request_form['job_end_date'],
            job_start_time=request_form['job_start_time'],
            job_end_time=request_form['job_end_time'],
            job_max_sample_size=request_form['job_max_sample_size'],
            job_max_good_matches=request_form['job_max_good_matches'],
            job_threshold=request_form['job_threshold'],
            job_samples_matched=request_form.get('job_samples_matched'),
            job_status=request_form['job_status'],
            channel_name=request_form['channel_name'],
            channel_id=request_form['channel_id'],
            recorded_video_file=request_form['recorded_video_file'],
            recorded_video_dir=request_form['recorded_video_dir'],
            recorded_video_date=request_form['recorded_video_date'],
            test_image_path=request_form['test_image_path'],
            active_status=request_form['active_status'],
            modified=None,
            completed=None,
        )
        db.session.add(new_item)
        db.session.commit()

        created_job = RecognitionJob.query.filter_by(job_id=job_id).first()
        if created_job is None:
            return jsonify({"error": "Failed to retrieve created recognition job record"}), 500

        response = created_job.toDict()
        return jsonify(response), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


def retrieve_job_controller(job_id):
    try:
        rj = RecognitionJob.query.filter_by(job_id=job_id).first()
        if rj is None:
            return jsonify({"error": "Recognition job record not found"}), 404

        response = rj.toDict()
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def update_job_controller(job_id):
    try:
        if request.form:
            request_data = request.form.to_dict()
        else:
            request_data = request.get_json()

        job = RecognitionJob.query.filter_by(job_id=job_id).first()
        if job is None:
            return jsonify({"error": "Recognition job record not found"}), 404

        if 'job_name' in request_data:
            job.job_name = request_data.get('job_name')
        if 'job_type' in request_data:
            job.job_type = request_data.get('job_type')
        if 'job_mode' in request_data:
            job.job_mode = request_data.get('job_mode')
        if 'job_start_date' in request_data:
            job.job_start_date = request_data.get('job_start_date')
        if 'job_end_date' in request_data:
            job.job_end_date = request_data.get('job_end_date')
        if 'job_start_time' in request_data:
            job.job_start_time = request_data.get('job_start_time')
        if 'job_end_time' in request_data:
            job.job_end_time = request_data.get('job_end_time')
        if 'job_max_sample_size' in request_data:
            job.job_max_sample_size = request_data.get('job_max_sample_size')
        if 'job_max_good_matches' in request_data:
            job.job_max_good_matches = request_data.get('job_max_good_matches')
        if 'job_threshold' in request_data:
            job.job_threshold = request_data.get('job_threshold')
        if 'job_samples_matched' in request_data:
            job.job_samples_matched = request_data.get('job_samples_matched')
        if 'job_status' in request_data:
            job.job_status = request_data.get('job_status')
        if 'channel_name' in request_data:
            job.channel_name = request_data.get('channel_name')
        if 'channel_id' in request_data:
            job.channel_id = request_data.get('channel_id')
        if 'recorded_video_file' in request_data:
            job.recorded_video_file = request_data.get('recorded_video_file')
        if 'recorded_video_dir' in request_data:
            job.recorded_video_dir = request_data.get('recorded_video_dir')
        if 'recorded_video_date' in request_data:
            job.recorded_video_date = request_data.get('recorded_video_date')
        if 'test_image_path' in request_data:
            job.test_image_path = request_data.get('test_image_path')
        if 'active_status' in request_data:
            job.active_status = request_data.get('active_status')
        if 'modified' in request_data:
            job.modified = request_data.get('modified')

        db.session.commit()

        updated_job = RecognitionJob.query.filter_by(job_id=job_id).first()
        if updated_job is None:
            return jsonify({"error": "Failed to retrieve updated recognition job record"}), 500

        response = updated_job.toDict()
        return jsonify(response)

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


def delete_job_controller(job_id):
    try:
        RecognitionJob.query.filter_by(job_id=job_id).delete()
        db.session.commit()

        return jsonify({"status": 200, "msg": f"Recognition job with Id {job_id} deleted successfully!"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"status": 500, "msg": f"Error occurred... Deletion failed!", "error": e}), 500


def get_jobs_status(job_status, job_mode):
    try:
        jobs_statuses = RecognitionJob.query.filter_by(job_status=f"{job_status}", job_mode=f"{job_mode}").all()
        jobs = []
        for job in jobs_statuses:
            jobs.append({
                'job_id': job.job_id,
                'job_queue_id': job.job_queue_id,
                'job_name': job.job_name,
                'job_type': job.job_type,
                'job_mode': job.job_mode,
                'job_start_date': job.job_start_date,
                'job_end_date': job.job_end_date,
                'job_start_time': job.job_start_time,
                'job_end_time': job.job_end_time,
                'job_max_sample_size': job.job_max_sample_size,
                'job_max_good_matches': job.job_max_good_matches,
                'job_threshold': job.job_threshold,
                'job_samples_matched': job.job_samples_matched,
                'job_status': job.job_status,
                'channel_name': job.channel_name,
                'channel_id': job.channel_id,
                'recorded_video_file': job.recorded_video_file,
                'recorded_video_dir': job.recorded_video_dir,
                'recorded_video_date': job.recorded_video_date,
                'test_image_path': job.test_image_path,
                'active_status': job.active_status,
                'created': job.created,
                'modified': job.modified,
            })
        return jsonify({"code": 200, "msg": f"{job_status} {job_mode} jobs retrieved successfully", "payload": jobs})
    except Exception as e:
        return jsonify({"code": 500, "msg": f"An error occurred: {str(e)}"})


def update_job_sample_detected(job_id):
    session = Session()
    try:
        if not job_id:
            return jsonify({"code": 400, "msg": "Job ID is required"}), 400

        # Query the job by ID
        job = session.query(RecognitionJob).filter_by(job_id=job_id).first()

        if not job:
            return jsonify({"code": 404, "msg": "Job not found"}), 404

        # Increment the job_samples_matched field
        job.job_samples_matched += 1
        session.commit()

        return jsonify({"code": 200, "msg": "Job sample matched updated successfully"}), 200
    except Exception as e:
        print(e)
        session.rollback()
        return jsonify({"code": 500, "msg": "Internal Server Error"}), 500
    finally:
        session.close()

from flask import request, Blueprint

rj_bp = Blueprint('recognition_jobs', __name__)

from app.api.recognition_jobs.controllers import (list_all_jobs_controller, create_job_controller,
                                                  retrieve_job_controller, update_job_controller, delete_job_controller,
                                                  get_jobs_status, list_all_unique_jobs_controller,
                                                  get_last_job_controller, update_job_sample_detected)


@rj_bp.route("/recognition_jobs", methods=['GET', 'POST'])
def list_create_jobs():
    if request.method == 'GET': return list_all_jobs_controller()
    if request.method == 'POST':
        return create_job_controller()
    else:
        return 'Method is Not Allowed'


@rj_bp.route("/recognition_jobs/last", methods=['GET'])
def retrieve_last_jobs():
    if request.method == 'GET':
        return get_last_job_controller()
    else:
        return 'Method is Not Allowed'


@rj_bp.route("/recognition_jobs/unique", methods=['GET'])
def list_unique_jobs():
    if request.method == 'GET':
        return list_all_unique_jobs_controller()
    else:
        return 'Method is Not Allowed'


@rj_bp.route("/recognition_jobs/<job_id>", methods=['GET', 'PUT', 'DELETE'])
def retrieve_update_destroy_job(job_id):
    if request.method == 'GET': return retrieve_job_controller(job_id)
    if request.method == 'PUT': return update_job_controller(job_id)
    if request.method == 'DELETE':
        return delete_job_controller(job_id)
    else:
        return 'Method is Not Allowed'


@rj_bp.route('/recognition_jobs/jobs_status/<job_status>/<job_mode>', methods=['GET'])
def retrieve_job_status(job_status, job_mode):
    if request.method == 'GET':
        return get_jobs_status(job_status, job_mode)
    else:
        return 'Method is Not Allowed'


@rj_bp.route('/recognition_jobs/update_job_sample_matched/<job_id>', methods=['GET', 'PUT'])
def make_update_sample_detected(job_id):
    if request.method == 'PUT':
        return update_job_sample_detected(job_id)
    else:
        return 'Method is Not Allowed'

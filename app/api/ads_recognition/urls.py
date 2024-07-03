from flask import request, Blueprint

ar_bp = Blueprint('ads_recognition', __name__)

from app.api.ads_recognition.controllers import (create_ads_recognition_controller,
                                                 list_all_ads_recognitions_controller,
                                                 retrieve_ads_recognitions_controller,
                                                 update_ads_recognition_controller,
                                                 delete_ads_recognition_controller,
                                                 retrieve_ads_recognitions_by_job_id_controller,
                                                 delete_ads_by_job_id_controller)


@ar_bp.route("/ads_recognition", methods=['GET', 'POST'])
def list_create_ads_recognition():
    if request.method == 'GET': return list_all_ads_recognitions_controller()
    if request.method == 'POST':
        return create_ads_recognition_controller()
    else:
        return 'Method is Not Allowed'


@ar_bp.route("/ads_recognition/<rec_id>", methods=['GET', 'PUT', 'DELETE'])
def retrieve_update_destroy_ads_recognition(rec_id):
    if request.method == 'GET': return retrieve_ads_recognitions_controller(rec_id)
    if request.method == 'PUT': return update_ads_recognition_controller(rec_id)
    if request.method == 'DELETE':
        return delete_ads_recognition_controller(rec_id)
    else:
        return 'Method is Not Allowed'


@ar_bp.route("/ads_recognition/group/<job_id>", methods=['GET', 'DELETE'])
def retrieve_by_job_id_ads_recognition(job_id):
    if request.method == 'GET':
        return retrieve_ads_recognitions_by_job_id_controller(job_id)
    if request.method == 'DELETE':
        return delete_ads_by_job_id_controller(job_id)
    else:
        return 'Method is Not Allowed'

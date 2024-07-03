import json
import requests

from config import Config


def save_new_jobs(data):
    # Create a new queued RecognitionJob instance
    jobs_data = []
    try:
        job_route = f"{Config.RECOGNITION_JOBS_API_ROUTE}"
        response = requests.post(job_route, json=data).json()
        if len(response) > 0:
            jobs_data = response
    except FileNotFoundError:
        pass  # Error reading queued data

    return jobs_data


def get_all_jobs_data():
    """ Read existing data from JSON file """
    db_data = []
    try:
        job_route = f"{Config.RECOGNITION_JOBS_API_ROUTE}"
        response = requests.get(job_route).json()
        if response and len(response) > 0:
            db_data = response
    except FileNotFoundError:
        pass  # # Error reading all jobs data

    return db_data


def get_last_job_data():
    """ Read last data """
    db_data = []
    try:
        job_route = f"{Config.RECOGNITION_JOBS_API_ROUTE}/last"
        response = requests.get(job_route).json()
        if response:
            db_data = response
    except FileNotFoundError:
        pass  # # Error reading all jobs data

    return db_data


def get_queued_db_data(job_mode):
    """ Read queued data from db """
    queued_data = []
    try:
        job_route = f"{Config.RECOGNITION_JOBS_API_ROUTE}/jobs_status/queued/{job_mode}"
        response = requests.get(job_route).json()
        if response and len(response['payload']) > 0:
            queued_data = response["payload"]
    except FileNotFoundError:
        pass  # Error reading queued data

    return queued_data


def get_all_unique_jobs_data():
    """ Read existing data from JSON file """
    db_data = []
    try:
        job_route = f"{Config.RECOGNITION_JOBS_API_ROUTE}/unique"
        response = requests.get(job_route).json()
        if response and len(response) > 0:
            db_data = response
    except FileNotFoundError:
        pass  # # Error reading all jobs data

    return db_data


def get_all_jobs_by_type_data(job_type):
    """ Read existing data from jobs """
    db_data = []
    try:
        job_route = f"{Config.ADS_RECOGNITION_API_ROUTE}"

        response = requests.get(job_route).json()
        if response and len(response) > 0:
            db_data = response
    except FileNotFoundError:
        pass  # # Error reading all jobs data

    return db_data


def get_all_jobs_by_type_and_id_data(job_type, job_id):
    """ Read existing data from JSON file """
    db_data = []
    try:
        job_route = f"{Config.ADS_RECOGNITION_API_ROUTE}/group/{job_id}"

        response = requests.get(job_route).json()
        if response and len(response) > 0:
            db_data = response
    except FileNotFoundError:
        pass  # # Error reading all jobs data

    return db_data


def delete_single_job_data(job_id, job_type):
    """ Delete job data from recognition_jobs table """
    db_data = []
    try:
        route = f"{Config.RECOGNITION_JOBS_API_ROUTE}/{job_id}"
        response = requests.delete(route).json()
        if response and len(response) > 0:
            # Delete from ads recognition_jobs table
            sub_route = f"{Config.ADS_RECOGNITION_API_ROUTE}/group/{job_id}"
            response = requests.delete(sub_route).json()

            db_data = response
    except FileNotFoundError:
        pass  # # Error deleting job data

    return db_data


def delete_recorded_jobs_data(job_id, job_type):
    """ Delete job data from recognition_jobs table """
    db_data = []
    try:
        # Delete from ads recognition_jobs table
        sub_route = f"{Config.ADS_RECOGNITION_API_ROUTE}/group/{job_id}"
        response = requests.delete(sub_route).json()

        db_data = response
    except FileNotFoundError:
        pass  # # Error deleting job data

    return db_data


def get_single_job_data(job_id):
    """ Get job data from recognition_jobs table """
    db_data = []
    try:
        route = f"{Config.RECOGNITION_JOBS_API_ROUTE}/{job_id}"
        response = requests.get(route).json()
        if response and len(response) > 0:
            db_data = response
    except FileNotFoundError:
        pass  # # Error getting job data

    return db_data


def get_all_channels_data():
    """ Read existing data from channels """
    db_data = []
    try:
        route = f"{Config.CHANNELS_API_ROUTE}"
        response = requests.get(route).json()
        if response and len(response) > 0:
            db_data = response
    except FileNotFoundError:
        pass  # # Error reading all channels data

    return db_data


def get_channel_data(job_id):
    """ Read channel data from channels """
    db_data = []
    try:
        route = f"{Config.CHANNELS_API_ROUTE}/{job_id}"
        response = requests.get(route).json()
        if response and len(response) > 0:
            db_data = response
    except FileNotFoundError:
        pass  # # Error reading all channels data

    return db_data


def update_current_recognition_job(data, job_id):
    # Update job status in the database
    ads_update_route = f"{Config.RECOGNITION_JOBS_API_ROUTE}/{job_id}"
    response = requests.put(ads_update_route, json=data)
    print("data", response)
    return response


def increment_job_sample_matched(job_id):
    # Update job status in the database
    ads_update_route = f"{Config.RECOGNITION_JOBS_API_ROUTE}/update_job_sample_matched/{job_id}"
    response = requests.put(ads_update_route, json={'job_id': job_id})
    return response

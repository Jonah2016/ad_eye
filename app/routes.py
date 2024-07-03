import uuid
import os
import asyncio
import time

from flask import Blueprint, render_template, send_from_directory, request, flash, redirect, url_for
from werkzeug.utils import secure_filename

from app.modules.modulator import recorded_detect_process, live_detect_process
from app.utils.async_image_processor import async_find_image
from app.schemes.forms import DetectionQueryForm, DetectionReportForm, photos, LiveDetectionQueryForm
from app.utils.db_conn import get_all_jobs_data, get_queued_db_data, save_new_jobs, get_all_jobs_by_type_data, \
    get_all_jobs_by_type_and_id_data, get_all_channels_data, get_channel_data, get_last_job_data, \
    delete_single_job_data, get_single_job_data, delete_recorded_jobs_data, update_current_recognition_job
from app.utils.handlers import escape_backslashes
from app.utils.sync_image_processor import sync_find_image

from config import Config

routes_bp = Blueprint('routes', __name__)


@routes_bp.route('/upload/<filename>')
def get_file(filename):
    return send_from_directory(Config.UPLOADED_PHOTOS_DEST, secure_filename(filename))


@routes_bp.route('/uploads/<filename>')
def get_image_url(filename):
    # Validate and sanitize the image path (optional)
    image_path = 'uploads/' + secure_filename(filename)  # Prevents path traversal attacks

    url = send_from_directory(Config.BASE_PATH, image_path, as_attachment=True)
    print("return", url)

    return url


@routes_bp.route('/jobs/<job_type>', methods=['POST', 'GET'])
def get_jobs_by_type(job_type):
    jobs_data = []
    if job_type is not None:
        jobs_data = get_all_jobs_by_type_data(job_type)

    return jobs_data


@routes_bp.route('/jobs_grouped_by_id/<job_type>/<job_id>', methods=['POST', 'GET'])
def get_jobs_by_type_and_id(job_type, job_id):
    jobs_data = []
    if job_type is not None:
        jobs_data = get_all_jobs_by_type_and_id_data(job_type, job_id)

    return jobs_data


@routes_bp.route('/')
def index():
    return render_template('index.html')


@routes_bp.route('/reports', methods=['POST', 'GET'])
def reports():
    jobs_data = get_all_jobs_data()

    form = DetectionReportForm()
    # Generate choices dynamically on first request (or when data changes)
    if not form.queriedData.choices:
        form.queriedData.choices = [(entry.get('job_id'), f"Q{entry.get('job_queue_id')} --- {entry.get('job_name')}")
                                    for entry
                                    in jobs_data]

    # Escape backslashes in the response data
    escaped_resp = escape_backslashes(jobs_data)
    return render_template('reports.html', form=form, resp=escaped_resp, job_id="")


@routes_bp.route('/reports/<job_id>', methods=['POST', 'GET'])
def specific_report(job_id):
    jobs_data = get_all_jobs_data()

    form = DetectionReportForm()
    # Generate choices dynamically on first request (or when data changes)
    if not form.queriedData.choices:
        form.queriedData.choices = [(entry.get('job_id'), f"Q{entry.get('job_queue_id')} --- {entry.get('job_name')}")
                                    for entry
                                    in jobs_data]

    # Escape backslashes in the response data
    escaped_resp = escape_backslashes(jobs_data)
    return render_template('reports.html', form=form, resp=escaped_resp, job_id=job_id)


@routes_bp.route('/statuses', methods=['POST', 'GET'])
def statuses():
    jobs_data = get_all_jobs_data()

    return render_template('statuses.html', resp=jobs_data)


@routes_bp.route('/settings', methods=['POST', 'GET'])
def app_settings():
    settings_data = []

    return render_template('settings.html', resp=settings_data)


@routes_bp.route('/recorded', methods=['POST', 'GET'])
async def recorded_upload_image():
    form = DetectionQueryForm()

    channels_data = get_all_channels_data()
    # Generate choices dynamically on first request (or when data changes)
    if not form.channelsData.choices:
        form.channelsData.choices = [
            (entry.get('ch_id'), f"{entry.get('ch_number')} --- {entry.get('ch_name')}")
            for entry
            in channels_data]

    queued_data = get_queued_db_data("recorded")
    last_job_data = get_last_job_data()

    if form.validate_on_submit():
        files = request.files.getlist('photo')
        if not files or len(files) > 5:
            flash("Please upload between 1 and 5 images.", "danger")
            return redirect(request.url)

        for file in files:
            filename = photos.save(file)
            target_image_path = os.path.join(Config.UPLOADED_PHOTOS_DEST, filename)

            frm_channel_ids = set(form.channelsData.data)
            channel_names = []
            video_directories = []
            # generate channel names for each channel id from form data
            for ch_id in frm_channel_ids:
                channel_data = get_channel_data(ch_id)
                channel_names.append(channel_data['ch_name'])
                video_directories.append(f"{Config.VIDEO_SERVER_URL}{channel_data['ch_record_dir']}")

            channel_names_str = ",".join(channel_names)
            video_directories_str = ",".join(video_directories)
            frm_channel_ids_str = ",".join(list(frm_channel_ids))

            frm_detection_type = form.detectionType.data
            frm_job_id = str(uuid.uuid4())
            frm_job_mode = "recorded"
            frm_job_status = "queued"
            frm_job_priority = 1
            frm_threshold = f"{form.detectionThreshold.data}"
            frm_max_sample_size = form.maxSampleSize.data
            frm_max_strong_matches = form.maxStrongMatches.data
            frm_date_from = form.dateFrom.data.strftime("%Y-%m-%d")
            frm_date_to = form.dateTo.data.strftime("%Y-%m-%d")
            frm_time_from = form.timeFrom.data.strftime("%H:%M")
            frm_time_to = form.timeTo.data.strftime("%H:%M")
            frm_q_name = form.detectionName.data

            last_data_entry = last_job_data['job_queue_id'] if last_job_data else 0
            frm_qid = last_data_entry + 1

            queued_records = {
                "job_id": frm_job_id,
                "job_queue_id": frm_qid,
                "job_name": frm_q_name,
                "job_type": frm_detection_type,
                "job_mode": frm_job_mode,
                "job_start_date": frm_date_from,
                "job_end_date": frm_date_to,
                "job_start_time": frm_time_from,
                "job_end_time": frm_time_to,
                "job_max_sample_size": frm_max_sample_size,
                "job_max_good_matches": frm_max_strong_matches,
                "job_samples_matched": 0,
                "job_threshold": frm_threshold,
                "job_status": frm_job_status,
                "job_priority": frm_job_priority,
                "channel_name": channel_names_str,
                "channel_id": frm_channel_ids_str,
                "recorded_video_dir": f'{video_directories_str}',
                "recorded_video_file": f'{video_directories_str}',
                "recorded_video_date": "",
                "test_image_path": target_image_path,
                "active_status": 0,
            }

            save_new_jobs(queued_records)
            flash(f"File {filename} uploaded successfully.", "success")

    return render_template('query.html', form=form, queued=queued_data)


# This is executed from js in templates query.html
@routes_bp.route('/process_recorded_uploads', methods=['GET', 'POST'])
async def process_all_recorded_uploads():
    start_time = time.time()  # time

    queued_data = get_queued_db_data("recorded")

    if len(queued_data) > 0:
        # Create a list to hold the asyncio tasks
        tasks = []

        # Iterate through temp_uploads and create an asyncio task for each upload
        for data in queued_data:
            try:
                target_image = await async_find_image(data['job_type'], data['test_image_path'])

                detect_parameters = {
                    'job_type': data['job_type'],
                    'job_threshold': data['job_threshold'],
                    'job_max_sample_size': data['job_max_sample_size'],
                    'job_max_good_matches': data['job_max_good_matches'],
                    'test_image_path': data['test_image_path'],
                    'test_target_image': target_image,
                    'recorded_video_dirs': data['recorded_video_dir'],
                    'job_start_date': data['job_start_date'],
                    'job_end_date': data['job_end_date'],
                    'job_start_time': data['job_start_time'],
                    'job_end_time': data['job_end_time'],
                    'job_queue_id': data['job_queue_id'],
                    'job_name': data['job_name'],
                    'job_id': data['job_id'],
                }

                # Use asyncio.create_task to run tasks concurrently
                task = asyncio.create_task(recorded_detect_process(detect_parameters))
                tasks.append(task)

            except Exception as e:
                print(f"Error processing upload: {e}")

        # Execute all tasks concurrently using asyncio.gather
        await asyncio.gather(*tasks)

        flash("All queued recognition jobs have been completed, check their statuses.", "success")
        msg = "All queued recognition jobs have been completed, check their statuses."

    else:
        flash("There are no queued recognition jobs to process.", "warning")
        msg = "There are no queued recognition jobs to process."

    print("------------------- %s seconds -------------------" % (time.time() - start_time))
    return msg


@routes_bp.route('/live', methods=['POST', 'GET'])
async def live_image_upload():
    live_form = LiveDetectionQueryForm()

    channels_data = get_all_channels_data()
    # Generate choices dynamically on first request (or when data changes)
    if not live_form.channelsData.choices:
        live_form.channelsData.choices = [
            (entry.get('ch_id'), f"{entry.get('ch_number')} --- {entry.get('ch_name')}")
            for entry
            in channels_data]

    queued_data = get_queued_db_data("live")
    last_job_data = get_last_job_data()

    if live_form.validate_on_submit():
        files = request.files.getlist('photo')

        if not files or len(files) < 1:
            flash("Please upload at least 1 image.", "danger")
            return redirect(request.url)

        for file in files:
            filename = photos.save(file)
            target_image_path = os.path.join(Config.UPLOADED_PHOTOS_DEST, filename)

            frm_channel_id = live_form.channelsData.data
            channel_data = get_channel_data(frm_channel_id)

            frm_channel_name = channel_data['ch_name']
            video_directory = f"{Config.VIDEO_SERVER_URL}/{channel_data['ch_record_dir']}"
            live_video_url = f"{channel_data['ch_url']}"

            frm_detection_type = live_form.detectionType.data
            frm_job_id = str(uuid.uuid4())
            frm_job_mode = "live"
            frm_job_status = "queued"
            frm_job_priority = 1
            frm_threshold = f"{live_form.detectionThreshold.data}"
            frm_date_from = live_form.dateFrom.data.strftime("%Y-%m-%d")
            frm_date_to = live_form.dateTo.data.strftime("%Y-%m-%d")
            frm_time_from = live_form.timeFrom.data.strftime("%H:%M")
            frm_time_to = live_form.timeTo.data.strftime("%H:%M")
            frm_q_name = live_form.detectionName.data

            last_data_entry = last_job_data['job_queue_id'] if last_job_data else 0
            frm_qid = last_data_entry + 1

            temp_upload = {
                "job_id": frm_job_id,
                "job_queue_id": frm_qid,
                "job_name": frm_q_name,
                "job_type": frm_detection_type,
                "job_mode": frm_job_mode,
                "job_start_date": frm_date_from,
                "job_end_date": frm_date_to,
                "job_start_time": frm_time_from,
                "job_end_time": frm_time_to,
                "job_max_sample_size": 0,
                "job_max_good_matches": 0,
                "job_samples_matched": 0,
                "job_threshold": frm_threshold,
                "job_status": frm_job_status,
                "job_priority": frm_job_priority,
                "channel_name": frm_channel_name,
                "channel_id": frm_channel_id,
                "recorded_video_dir": video_directory,
                "recorded_video_file": live_video_url,
                "recorded_video_date": "",
                "test_image_path": target_image_path,
                "active_status": 0,
            }

            save_new_jobs(temp_upload)
            flash(f"File {filename} uploaded successfully.", "success")

    return render_template('live.html', form=live_form, queued=queued_data)


# This is executed from js in templates live.html
@routes_bp.route('/process_live_uploads', methods=['GET', 'POST'])
def process_all_live_uploads():
    start_time = time.time()  # time

    queued_data = get_queued_db_data("live")

    if len(queued_data) > 0:
        # Iterate through temp_uploads and create an asyncio task for each upload
        for data in queued_data:
            try:
                target_image = sync_find_image(data['job_type'], data['test_image_path'])

                detect_parameters = {
                    'job_type': data['job_type'],
                    'job_threshold': data['job_threshold'],
                    'job_max_sample_size': data['job_max_sample_size'],
                    'job_max_good_matches': data['job_max_good_matches'],
                    'test_image_path': data['test_image_path'],
                    'test_target_image': target_image,
                    'recorded_video_dir': data['recorded_video_dir'],
                    'recorded_video_file': data['recorded_video_file'],
                    'job_start_date': data['job_start_date'],
                    'job_end_date': data['job_end_date'],
                    'job_start_time': data['job_start_time'],
                    'job_end_time': data['job_end_time'],
                    'job_queue_id': data['job_queue_id'],
                    'job_name': data['job_name'],
                    'job_id': data['job_id'],
                    'channel_name': data['channel_name'],
                    'channel_id': data['channel_id']
                }

                # Use asyncio.create_task to run tasks concurrently
                live_detect_process(detect_parameters)
            except Exception as e:
                msg = f"Error processing upload: {e}"
                print(msg)

        flash("All recognition jobs have been completed, check their statuses.", "success")
        msg = "All queued recognition jobs have been completed, check their statuses."

    else:
        flash("There are no queued recognition jobs to process.", "warning")
        msg = "There are no queued recognition jobs to process."

    print("------------------- %s seconds -------------------" % (time.time() - start_time))
    return msg


# This is executed from js in templates statuses.html
@routes_bp.route('/process_jobs_status_actions', methods=['GET', 'POST'])
async def process_jobs_actions():
    start_time = time.time()  # time

    try:
        if request.form:
            request_form = request.form.to_dict()
        else:
            request_form = request.get_json()

        action = request_form.get('action')
        job_id = request_form.get('job_id')
        job_type = request_form.get('job_type')
        job_mode = request_form.get('job_mode')

        final_result = {"status": 500, "msg": "No action was executed... Please refresh and try again later!"}

        if action == "delete":
            final_result = delete_single_job_data(job_id, job_type)

        if action == "stop":
            response = update_current_recognition_job({"job_status": "queued"}, job_id)
            if response.status_code == 200:
                final_result = {"status": 200, "msg": "Stopped job successfully."}
            else:
                final_result = {"status": 500, "msg": "Failed to stop job... Please refresh and try again later!"}

        if action == "reports":
            url = Config.SERVER_URL + 'reports/' + job_id
            # url = Config.SERVER_URL + 'reports'
            final_result = {"status": 200, "msg": "Redirecting to reports now...", "url": url}

        if action == "restart":
            # delete existing recorded jobs
            delete_recorded_jobs_data(job_id, job_type)
            # update the status and matched_samples of the current job
            update_current_recognition_job({"job_status": "queued", "job_samples_matched": 0}, job_id)
            # get the job data
            data = get_single_job_data(job_id)

            if len(data) > 0:
                if job_mode == "recorded":
                    """Execute a recorded recognition process"""
                    # Create a list to hold the asyncio tasks
                    tasks = []

                    try:
                        target_image = await async_find_image(data['job_type'], data['test_image_path'])

                        detect_parameters = {
                            'job_type': data['job_type'],
                            'job_threshold': data['job_threshold'],
                            'job_max_sample_size': data['job_max_sample_size'],
                            'job_max_good_matches': data['job_max_good_matches'],
                            'test_image_path': data['test_image_path'],
                            'test_target_image': target_image,
                            'recorded_video_dirs': data['recorded_video_dir'],
                            'job_start_date': data['job_start_date'],
                            'job_end_date': data['job_end_date'],
                            'job_start_time': data['job_start_time'],
                            'job_end_time': data['job_end_time'],
                            'job_queue_id': data['job_queue_id'],
                            'job_name': data['job_name'],
                            'job_id': data['job_id'],
                        }

                        # Use asyncio.create_task to run tasks concurrently
                        task = asyncio.create_task(recorded_detect_process(detect_parameters))
                        tasks.append(task)

                    except Exception as e:
                        print(f"Error processing upload: {e}")

                    # Execute all tasks concurrently using asyncio.gather
                    await asyncio.gather(*tasks)

                else:
                    """Execute a live recognition process"""
                    try:
                        target_image = sync_find_image(data['job_type'], data['test_image_path'])

                        detect_parameters = {
                            'job_type': data['job_type'],
                            'job_threshold': data['job_threshold'],
                            'job_max_sample_size': data['job_max_sample_size'],
                            'job_max_good_matches': data['job_max_good_matches'],
                            'test_image_path': data['test_image_path'],
                            'test_target_image': target_image,
                            'recorded_video_dir': data['recorded_video_dir'],
                            'recorded_video_file': data['recorded_video_file'],
                            'job_start_date': data['job_start_date'],
                            'job_end_date': data['job_end_date'],
                            'job_start_time': data['job_start_time'],
                            'job_end_time': data['job_end_time'],
                            'job_queue_id': data['job_queue_id'],
                            'job_name': data['job_name'],
                            'job_id': data['job_id'],
                            'channel_name': data['channel_name'],
                            'channel_id': data['channel_id']
                        }

                        # Use asyncio.create_task to run tasks concurrently
                        live_detect_process(detect_parameters)
                    except Exception as e:
                        msg = f"Error processing upload: {e}"
                        print(msg)

                flash("A recognition job has been completed, check the actual status.", "success")
                final_result = {"status": 200, "msg": "A recognition job has been processed."}
            else:
                flash("No queued recognition job to process.", "warning")
                final_result = {"status": 404, "msg": "There is no queued recognition job to process."}

        print("------------------- %s seconds -------------------" % (time.time() - start_time))
        return final_result

    except Exception as e:
        flash(f"Something went wrong.{e}", "danger")
        return {"status": 500, "msg": "Something went wrong... Please refresh the page and try again later!"}

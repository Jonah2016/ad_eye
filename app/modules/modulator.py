import asyncio
import time

from _decimal import Decimal

from app.modules.live.live_ads_recognition import process_live_ad_detection
from app.modules.recorded.recorded_ads_recognition import process_ad_detection
from app.utils.async_image_processor import async_find_image, async_get_and_encode_images
from app.utils.db_conn import update_current_recognition_job
from app.utils.sync_image_processor import sync_find_image, sync_get_and_encode_images


async def recorded_detect_ad_detection_with_restart(parameters):
    while True:
        try:
            result = await recorded_detect_ad_detection(parameters)
            return result  # Return the loop if the process completes successfully
            # break  # Exit the loop if the process completes successfully
        except OSError as e:
            if e.errno == 10038:
                print(f"OSError encountered: {e}. Restarting detection process.")
            else:
                print(f"Unhandled OSError: {e}. Restarting detection process.")
        except Exception as e:
            print(f"Unhandled exception: {e}. Restarting detection process.")
        await asyncio.sleep(1)  # Wait for a second before restarting



# ================= Recorded detection process =================
async def recorded_detect_ad_detection(parameters):
    job_type = parameters['job_type']
    job_threshold = parameters['job_threshold']
    job_max_sample_size = parameters['job_max_sample_size']
    job_max_good_matches = parameters['job_max_good_matches']
    test_image_path = parameters['test_image_path']
    test_target_image = parameters['test_target_image']
    recorded_video_dir = parameters['recorded_video_dir']
    job_start_date = parameters['job_start_date']
    job_end_date = parameters['job_end_date']
    job_start_time = parameters['job_start_time']
    job_end_time = parameters['job_end_time']
    job_queue_id = parameters['job_queue_id']
    # job_name = parameters['job_name']
    job_id = parameters['job_id']
    # video_server = parameters['video_server']

    resp = await process_ad_detection(job_id, job_type, job_threshold, job_max_sample_size,
                                      job_max_good_matches, test_image_path, test_target_image,
                                      recorded_video_dir, job_start_date, job_end_date,
                                      job_start_time, job_end_time, job_queue_id)
    return resp


async def recorded_detect_process(detect_parameters):
    job_type = detect_parameters.get('job_type')
    job_threshold = Decimal(detect_parameters.get('job_threshold', 0.6))
    job_max_sample_size = detect_parameters.get('job_max_sample_size')
    job_max_good_matches = detect_parameters.get('job_max_good_matches')
    test_image_path = detect_parameters.get('test_image_path')
    recorded_video_dirs = detect_parameters.get('recorded_video_dirs')  # This should be a list of directories
    job_start_date = detect_parameters.get('job_start_date')
    job_end_date = detect_parameters.get('job_end_date')
    job_start_time = detect_parameters.get('job_start_time')
    job_end_time = detect_parameters.get('job_end_time')
    job_queue_id = detect_parameters.get('job_queue_id')
    job_name = detect_parameters.get('job_name')
    job_id = detect_parameters.get('job_id')
    # video_server = recorded_video_dirs

    try:
        target_image = await async_find_image(job_type, test_image_path)

        # Split the string and create a dictionary in one step
        recorded_video_dirs_list = recorded_video_dirs.split(",")

        if target_image is None:
            print("Target image not loaded. Please check the path.")
            return {"code": 404, "msg": "Target image not loaded. Please check the path."}

        detected_samples = []
        for recorded_video_dir in recorded_video_dirs_list:
            parameters = {
                'recorded_video_dir': recorded_video_dir,
                'test_image_path': test_image_path,
                'test_target_image': target_image,
                'job_threshold': job_threshold,
                'job_max_sample_size': job_max_sample_size,
                'job_max_good_matches': job_max_good_matches,
                'job_start_date': job_start_date,
                'job_end_date': job_end_date,
                'job_start_time': job_start_time,
                'job_end_time': job_end_time,
                'job_queue_id': job_queue_id,
                'job_name': job_name,
                'job_type': job_type,
                'job_id': job_id,
                'video_server': recorded_video_dir,
            }

            # Create tasks list
            tasks = []

            # Add tasks to the list
            if job_type == "ads":
                print("RECORDED - ADS DETECTION PROCESS =======")
                update_current_recognition_job({"job_status": "processing"}, job_id)
                tasks.append(recorded_detect_ad_detection_with_restart(parameters))
            else:
                print("Please select the recognition type!")
                return {"code": 404, "msg": "Please select the recognition type!"}

            # Execute all tasks concurrently using asyncio.gather
            results = await asyncio.gather(*tasks)

            # Update job status in the database
            job_data = [item['update_job_data'] for item in results]
            update_job_data = job_data[0] if job_data else {}
            dts = update_job_data.get('total_detected') if update_job_data else 0
            detected_samples.append(dts)

            response = update_current_recognition_job(update_job_data, job_id)
            print(
                f"\n\n - {response.status_code} - RECORDED: Completed detection in directory: {recorded_video_dir} \n")

        # Update job status in the database
        dts_data = sum(detected_samples) if len(detected_samples) > 0 else 0
        jbs = "done" if dts_data > 0 else "no-matches"

        update_current_recognition_job({"job_status": jbs}, job_id)
        return {"code": 200, "msg": "Detection completed in all directories"}
    except Exception as e:
        update_current_recognition_job({"job_status": "failed"}, job_id)
        return {"code": 200, "msg": "Detection completed in all directories", "error": e}


# ================= Live detection process =================
def live_detect_ad_detection(parameters):
    job_type = parameters['job_type']
    job_threshold = parameters['job_threshold']
    test_image_path = parameters['test_image_path']
    test_target_image = parameters['test_target_image']
    recorded_video_dir = parameters['recorded_video_dir']
    job_start_date = parameters['job_start_date']
    job_end_date = parameters['job_end_date']
    job_start_time = parameters['job_start_time']
    job_end_time = parameters['job_end_time']
    job_queue_id = parameters['job_queue_id']
    job_name = parameters['job_name']
    job_id = parameters['job_id']
    video_server = parameters['video_server']
    channel_name = parameters['channel_name']
    channel_id = parameters['channel_id']

    resp = process_live_ad_detection(job_id, job_type, job_threshold, test_image_path, test_target_image,
                                     recorded_video_dir, job_start_date, job_end_date,
                                     job_start_time, job_end_time, job_queue_id, job_name,
                                     video_server, channel_name, channel_id)
    return resp


def live_detect_process(detect_parameters):
    job_type = detect_parameters.get('job_type')
    job_threshold = Decimal(detect_parameters.get('job_threshold', 0.6))
    test_image_path = detect_parameters.get('test_image_path')
    recorded_video_dir = detect_parameters.get('recorded_video_dir')
    recorded_video_file = detect_parameters.get('recorded_video_file')
    job_start_date = detect_parameters.get('job_start_date')
    job_end_date = detect_parameters.get('job_end_date')
    job_start_time = detect_parameters.get('job_start_time')
    job_end_time = detect_parameters.get('job_end_time')
    job_queue_id = detect_parameters.get('job_queue_id')
    job_name = detect_parameters.get('job_name')
    job_id = detect_parameters.get('job_id')
    channel_name = detect_parameters.get('channel_name')
    channel_id = detect_parameters.get('channel_id')
    video_server = recorded_video_file

    target_image = sync_find_image(job_type, test_image_path)

    if target_image is None:
        print("Target image not loaded. Please check the path.")
        return {"code": 404, "msg": "Target image not loaded. Please check the path."}

    parameters = {
        'recorded_video_dir': recorded_video_dir,
        'test_image_path': test_image_path,
        'test_target_image': target_image,
        'job_threshold': job_threshold,
        'job_start_date': job_start_date,
        'job_end_date': job_end_date,
        'job_start_time': job_start_time,
        'job_end_time': job_end_time,
        'job_queue_id': job_queue_id,
        'job_name': job_name,
        'job_type': job_type,
        'job_id': job_id,
        'video_server': video_server,
        'channel_name': channel_name,
        'channel_id': channel_id,
    }

    # Add tasks to the list
    if job_type == "ads":
        print("LIVE - ADS DETECTION PROCESS =======")
        results = live_detect_ad_detection(parameters)
    else:
        print("Please select the recognition type!")
        return {"code": 404, "msg": "Please select the recognition type!"}

    return {"code": 200, "msg": "Detection completed"}

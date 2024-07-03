import asyncio
import os
import cv2
import requests
import json
import datetime
import uuid
import threading

from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from app.utils.db_conn import update_current_recognition_job, increment_job_sample_matched
from app.utils.handlers import get_file_info_handler, get_video_filenames
from config import Config

d_s = os.sep  # Directory separator
frame_output_path = f"app{d_s}static{d_s}detected_frames{d_s}"

# Create a thread pool executor
executor = ThreadPoolExecutor()
lock = threading.Lock()


async def detect_ads(video_path, orb, des1, bf, job_threshold, job_max_sample_size, job_max_good_matches,
                    dt_data, recorded_video_dir):
    samples_detected_data = []
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return samples_detected_data

    frame_msec = 0
    samples_detected = 0
    last_detection_timestamp = None
    frame_skip_factor = 1  # Initial skipping factor (adjust based on needs)
    frames_to_skip_after_detection = 5

    while cap.isOpened() and samples_detected < job_max_sample_size:
        if last_detection_timestamp is not None:
            frame_rate = cap.get(cv2.CAP_PROP_FPS)  # Access frame rate
            frames_to_skip = int(frame_rate * 30)  # Calculate frames to skip for 30 seconds
            target_frame_position = int(cap.get(cv2.CAP_PROP_POS_FRAMES) + frame_skip_factor * frames_to_skip)
            cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame_position)
        else:
            cap.set(cv2.CAP_PROP_POS_MSEC, frame_msec)

        ret, frame = cap.read()
        if not ret:
            break

        # Preprocess target image (add code here)

        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        kp2, des2 = orb.detectAndCompute(frame_gray, None)

        if des2 is not None and des1 is not None:
            matches = bf.match(des1, des2)
            matches = sorted(matches, key=lambda x: x.distance)
            good_matches = [m for m in matches if m.distance < job_threshold]
            confidence = (len(good_matches) / len(matches)) * 100 if len(matches) > 0 else 0

            if len(good_matches) >= job_threshold:
                timestamp_ms = cap.get(cv2.CAP_PROP_POS_MSEC)
                timestamp = datetime.fromtimestamp(timestamp_ms / 1000.0)
                time_str = timestamp.strftime('%H:%M:%S')
                time_str_two = timestamp.strftime('%H_%M_%S')
                rec_id = f"{uuid.uuid4()}"

                if last_detection_timestamp is None or (
                        timestamp - last_detection_timestamp).total_seconds() >= frame_skip_factor:

                    print(f"\n [AR] Logging......: Saving detected data to disk")
                    # Update frame skipping factor after detection
                    frame_skip_factor = min(frame_skip_factor * 2, 10)  # Increase skipping, capped at 10x

                    original_str = f"{dt_data['filename']}"
                    formatted_str = original_str.replace(" ", "_")
                    frame_detected = f"{frame_output_path}detected_{formatted_str}_{time_str_two}.jpg"
                    cv2.imwrite(frame_detected, frame)

                    detection_data = {
                        'rec_id': f"{rec_id}",
                        'rec_video_dir': recorded_video_dir,
                        'rec_video_file': dt_data['filename'],
                        'rec_video_date': dt_data['actual_date'],
                        'rec_frame_image': frame_detected,
                        'rec_frame_time': time_str,
                        'rec_confidence': f'{confidence:.2f}',
                        'rec_video_length': dt_data['rec_time'],
                        'job_id': dt_data['job_id'],
                        'job_queue_id': dt_data['job_queue_id'],
                        'job_type': dt_data['job_type'],
                        'job_mode': dt_data['job_mode'],
                        'channel_name': dt_data['channel_name'],
                        'channel_id': '001',
                        'test_image_path': dt_data['test_image'],
                        'active_status': dt_data['active_status'],
                    }

                    response = requests.post(Config.ADS_RECOGNITION_API_ROUTE, json=detection_data)
                    if response.status_code == 200:
                        print(f"[AR] - {response.status_code} - Logging.........: Data saved to database successfully!")

                        # update the status of the current job
                        increment_job_sample_matched(dt_data['job_id'])

                        samples_detected_data.append(detection_data)
                        samples_detected += 1
                    last_detection_timestamp = timestamp

        # Adjust frame skipping factor based on no detection
        frame_skip_factor = max(frame_skip_factor // 2, 1)  # Reduce skipping, minimum 1x

        frame_msec += 500
    cap.release()

    # return the sample data
    return samples_detected_data


async def process_ad_detection(job_id, job_type, job_threshold, job_max_sample_size,
                               job_max_good_matches, test_image_path, target_image,
                               recorded_video_dir, job_start_date, job_end_date,
                               job_start_time, job_end_time, job_queue_id):
    try:
        # Preprocess target image (add code here)

        orb = cv2.ORB_create(scoreType=cv2.ORB_FAST_SCORE)
        kp1, des1 = orb.detectAndCompute(target_image, None)
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

        job_mode = "recorded"
        job_active_status = 1

        video_files = get_video_filenames(recorded_video_dir)  # Fetch the list of video files from the server

        loop = asyncio.get_running_loop()
        tasks = []
        for v_filename in video_files:
            if v_filename.endswith('.mp4'):
                file_data = get_file_info_handler(v_filename, recorded_video_dir)
                job_start_date_fmt = datetime.strptime(job_start_date, "%Y-%m-%d")
                job_start_time_fmt = datetime.strptime(job_start_time, "%H:%M")
                job_end_date_fmt = datetime.strptime(job_end_date, "%Y-%m-%d")
                job_end_time_fmt = datetime.strptime(job_end_time, "%H:%M")

                dt_actual_date = file_data['actualDate']
                dt_actual_date_fmt = datetime.strptime(file_data['actualDate'], "%Y-%m-%d")
                dt_start_time_fmt = datetime.strptime(file_data['startTime'], "%H:%M")
                dt_end_time_fmt = datetime.strptime(file_data['endTime'], "%H:%M")
                dt_channel_name = file_data['channelName']
                dt_rec_time = file_data['recTime']
                dt_v_filename = file_data['fileName']

                detect_data = {}

                if file_data is not None and (
                        (job_start_date_fmt <= dt_actual_date_fmt <= job_end_date_fmt) and
                        (job_start_time_fmt <= dt_start_time_fmt <= job_end_time_fmt) and
                        (job_start_time_fmt <= dt_end_time_fmt <= job_end_time_fmt)):
                    detect_data.update({
                        "job_id": f"{job_id}",
                        "job_queue_id": f"{job_queue_id}",
                        "job_type": job_type,
                        "job_mode": job_mode,
                        "test_image": f"{test_image_path}",
                        "filename": dt_v_filename,
                        "channel_name": dt_channel_name,
                        "actual_date": dt_actual_date,
                        "rec_time": dt_rec_time,
                        "active_status": job_active_status,
                    })

                    # Use run_in_executor to run detect_ads in a separate thread
                    task = loop.run_in_executor(executor, detect_ads, v_filename, orb, des1, bf, job_threshold,
                                                job_max_sample_size, job_max_good_matches, detect_data,
                                                recorded_video_dir)
                    tasks.append(task)

        # Await all tasks to complete
        results = await asyncio.gather(*tasks)

        # Flatten the results list
        samples_detected_data = [sample for result_list in results for sample in await result_list]

        # Write updated data to database
        update_job_data = {
            "job_status": "no-matches" if len(samples_detected_data) == 0 else "matched",
            "active_status": 1,
            "total_detected": len(samples_detected_data),
        }

        print(f"\n RECORDED - [AR] - End-Logging.........: Detection Done! \n")

        return {"code": 200, "job_id": job_id, "update_job_data": update_job_data}

    except Exception as e:
        print(f"\n RECORDED - [AR] - End-Logging.........: Process error! \n")
        return {"code": 200, "job_id": job_id, "msg": f"Error occurred: {e}",
                "update_job_data": {"job_status": "stopped", "active_status": 1}}
        pass


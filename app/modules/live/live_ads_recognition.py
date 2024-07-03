import os
import json
import cv2
import numpy as np
import requests
import datetime
import uuid
import time
from datetime import datetime, timedelta

from app.utils.db_conn import update_current_recognition_job, increment_job_sample_matched
from config import Config


d_s = os.sep  # Directory separator
frame_output_path = f"app{d_s}static{d_s}detected_frames{d_s}"

# Ensure GPU is available
print(cv2.cuda.getCudaEnabledDeviceCount())


def detect_ads(video_server, orb, des1, bf, job_threshold, dt_data, recorded_video_dir, inactivity_timeout=60):
    samples_detected_data = []
    cap = cv2.VideoCapture(video_server)
    if not cap.isOpened():
        return samples_detected_data

    samples_detected = 0
    frame_msec = 0
    last_frame_time = time.time()
    last_detection_timestamp = None
    frame_skip_factor = 1  # Initial skipping factor (adjust based on needs)

    while cap.isOpened():
        if last_detection_timestamp is not None:
            frame_rate = cap.get(cv2.CAP_PROP_FPS)  # Access frame rate
            frames_to_skip = int(frame_rate * 30)  # Calculate frames to skip for 30 seconds
            target_frame_position = int(cap.get(cv2.CAP_PROP_POS_FRAMES) + frame_skip_factor * frames_to_skip)
            cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame_position)

        ret, frame = cap.read()
        if not ret:
            if time.time() - last_frame_time > inactivity_timeout:
                print("[AR] Logging.........: Stream inactive, closing...")
                break
            continue

        last_frame_time = time.time()

        # Upload frame to GPU
        gpu_frame = cv2.cuda_GpuMat()
        gpu_frame.upload(frame)

        # Convert to grayscale using GPU
        gpu_frame_gray = cv2.cuda.cvtColor(gpu_frame, cv2.COLOR_BGR2GRAY)

        # Download the grayscale frame to CPU (ORB currently doesn't support CUDA directly)
        frame_gray = gpu_frame_gray.download()

        kp2, des2 = orb.detectAndCompute(frame_gray, None)

        if des2 is not None and des1 is not None:
            matches = bf.match(des1, des2)
            matches = sorted(matches, key=lambda x: x.distance)
            good_matches = [m for m in matches if m.distance < job_threshold]
            confidence = (len(good_matches) / len(matches)) * 100 if len(matches) > 0 else 0
            new_confidence = ("%.2f" % confidence)

            print(f"[AR] Logging.........: Processing data! [Good Matches: {len(good_matches)}]\n")

            if len(good_matches) > job_threshold:
                timestamp = datetime.now()
                time_str = timestamp.strftime('%H:%M:%S')
                time_str_two = timestamp.strftime('%H_%M_%S')
                rec_id = f"{uuid.uuid4()}"

                if last_detection_timestamp is None or (
                        timestamp - last_detection_timestamp).total_seconds() >= frame_skip_factor:

                    print(f"\n [AR] Logging......: Saving detected data to disk or database! [{dt_data['job_id']}] \n")

                    frame_skip_factor = min(frame_skip_factor * 2, 10)  # Increase skipping, capped at 10x

                    original_str = f"{dt_data['channel_name']}"
                    formatted_str = original_str.replace(" ", "_")
                    frame_detected = f"{frame_output_path}detected_{formatted_str}_{time_str_two}.jpg"
                    cv2.imwrite(frame_detected, frame)

                    detection_data = {
                        'rec_id': f'{rec_id}',
                        'rec_video_dir': f'{recorded_video_dir}',
                        'rec_video_file': f'{dt_data["video_server"]}',
                        'rec_video_date': f'{dt_data["current_date"]}',
                        'rec_frame_image': frame_detected,
                        'rec_frame_time': time_str,
                        'rec_confidence': f'{new_confidence}',
                        'rec_video_length': f'{dt_data["rec_time"]}',
                        'job_id': dt_data['job_id'],
                        'job_queue_id': dt_data['job_queue_id'],
                        'job_type': dt_data['job_type'],
                        'job_mode': dt_data['job_mode'],
                        'channel_name': dt_data['channel_name'],
                        'channel_id': dt_data['channel_id'],
                        'test_image_path': f'{dt_data["test_image"]}',
                        'active_status': dt_data['active_status'],
                    }

                    response = requests.post(Config.ADS_RECOGNITION_API_ROUTE, json=detection_data)
                    if response.status_code == 200:
                        print(f"[AR] - {response.status_code} - Logging.........: Data saved to database successfully!")

                        update_current_recognition_job({"job_status": "matched"}, dt_data['job_id'])
                        increment_job_sample_matched(dt_data['job_id'])

                        samples_detected_data.append(detection_data)
                        samples_detected += 1
                        last_detection_timestamp = timestamp

            # Adjust frame skipping factor based on no detection
            frame_skip_factor = max(frame_skip_factor // 2, 1)  # Reduce skipping, minimum 1x

        frame_msec += 500
    cap.release()

    return samples_detected_data


def process_live_ad_detection(job_id, job_type, job_threshold, test_image_path, target_image,
                              recorded_video_dir, job_start_date, job_end_date,
                              job_start_time, job_end_time, job_queue_id, job_name, video_server,
                              channel_name, channel_id):
    try:
        orb = cv2.ORB_create(scoreType=cv2.ORB_FAST_SCORE)

        # Convert target_image to GPU matrix and then to cv::UMat
        target_image_gpu = cv2.cuda_GpuMat()
        target_image_gpu.upload(target_image)
        target_image_umat = target_image_gpu.download()
        kp1, des1 = orb.detectAndCompute(target_image_umat, None)
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

        job_mode = "live"
        job_active_status = 1

        now = datetime.now()
        current_time = now.strftime("%H:%M")
        current_date = now.strftime("%Y-%m-%d")

        start_datetime = datetime.strptime(f"{job_start_date} {job_start_time}", "%Y-%m-%d %H:%M")
        end_datetime = datetime.strptime(f"{job_end_date} {job_end_time}", "%Y-%m-%d %H:%M")

        if now < start_datetime:
            wait_seconds = (start_datetime - now).total_seconds()
            print(f"Waiting for the start time: {job_start_time} on {job_start_date} (in {wait_seconds} seconds)")
            time.sleep(wait_seconds)
        elif now > end_datetime:
            print(f"The end time {job_end_time} on {job_end_date} has passed. Skipping detection.")
            return {"code": 200, "message": "End time has passed"}

        detect_data = {
            "job_id": f"{job_id}",
            "job_name": f"{job_name}",
            "job_queue_id": f"{job_queue_id}",
            "job_type": job_type,
            "job_mode": job_mode,
            "test_image": f"{test_image_path}",
            "video_server": video_server,
            "channel_name": channel_name,
            "channel_id": channel_id,
            "rec_time": current_time,
            "current_date": current_date,
            "active_status": job_active_status,
        }

        samples_detected_data = detect_ads(video_server, orb, des1, bf, job_threshold, detect_data, recorded_video_dir)

        update_job_data = {
            "job_samples_matched": len(samples_detected_data),
            "job_status": "done" if len(samples_detected_data) > 0 else "failed",
            "active_status": 1,
        }

        response = update_current_recognition_job(update_job_data, job_id)
        print(f"LIVE - [AR] - {response.status_code} - End-Logging.........: Detection Done!")

        return {"code": 200, "job_id": job_id, "update_job_data": update_job_data}

    except Exception as e:
        print(f"\n RECORDED - [AR] - End-Logging.........: Process error! \n")
        return {"code": 200, "job_id": job_id, "msg": f"Error occurred: {e}",
                "update_job_data": {"job_status": "stopped", "active_status": 1}}
        pass

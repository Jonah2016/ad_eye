import os
import concurrent
import pickle
import subprocess
import cv2
from imutils import paths
import asyncio


async def async_get_video_creation_date(video_path):
    creation_date = await asyncio.to_thread(_async_get_video_creation_date_blocking, video_path)
    return creation_date.strip() if creation_date else "Not Found"


def _async_get_video_creation_date_blocking(video_path):
    creation_date = subprocess.run(
        ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream_tags=creation_time', '-of',
         'default=noprint_wrappers=1:nokey=1', video_path], capture_output=True, text=True)
    return creation_date.stdout


async def async_find_image(detection_type, target_image_path):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _async_find_image_blocking, detection_type, target_image_path)


def _async_find_image_blocking(detection_type, target_image_path):
    target_image = cv2.imread(target_image_path)
    if target_image is None:
        print(f"Error loading {target_image_path}")
        return None
    if detection_type == "ads":
        target_image = cv2.imread(target_image_path, cv2.IMREAD_GRAYSCALE)  # Read the target image in grayscale
    else:
        target_image = cv2.imread(target_image_path, cv2.IMREAD_GRAYSCALE)  # Read the target image in grayscale
    return target_image



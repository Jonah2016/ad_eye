import requests

from datetime import datetime, timedelta
from urllib.parse import unquote
from bs4 import BeautifulSoup


def get_file_info_handler(filename, server_url):
    """Get the information of a video file from the file name"""
    # Split the name string by spaces
    strip_parts = filename.lstrip(server_url)

    # Decode the URL-encoded filename to get the real path
    decoded_filename = unquote(strip_parts)

    parts = decoded_filename.split()

    if len(parts) > 0:
        # Extract parameters
        date = parts[1]
        start_time = parts[2]
        total_rec_time = parts[5]

        # Convert start_time and total_rec_time to timedelta objects
        tot_rec_time_ft = datetime.strptime(total_rec_time, "%H.%M.%S.%f")
        actual_date_dt = datetime.strptime(date, "%Y-%m-%d")
        start_time_dt = datetime.strptime(start_time, "%H.%M.%S")
        total_rec_time_dt = timedelta(hours=int(total_rec_time.split('.')[0]),
                                      minutes=int(total_rec_time.split('.')[1]),
                                      seconds=int(total_rec_time.split('.')[2]))

        # Calculate end_time by adding total_rec_time to start_time
        end_time_dt = start_time_dt + total_rec_time_dt

        # Format the start_time and end_time back into string format
        start_time = start_time_dt.strftime("%H:%M")
        end_time = end_time_dt.strftime("%H:%M")
        rec_time = tot_rec_time_ft.strftime("%H:%M")
        actual_date_ft = actual_date_dt.strftime("%Y-%m-%d")

        # Join the remaining parts to get the name
        channel = ' '.join(parts[7:])  # Skip the first 7 parts and the last part
        channel = channel.replace('.mp4', '')  # Remove .mp4 from the name

        return {
            "actualDate": actual_date_ft,
            "startTime": start_time,
            "endTime": end_time,
            "recTime": rec_time,
            "channelName": channel,
            "fileName": decoded_filename
        }

    else:
        return {}


def get_video_filenames(video_directory):
    # Make a GET request to the server directory URL
    response = requests.get(video_directory)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the HTML content of the directory listing
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all <a> tags containing links to files
        links = soup.find_all('a')

        # Extract filenames from the href attributes of the links
        filenames = [link['href'] for link in links]

        # Filter out directories and other non-video files
        video_filenames = [video_directory + filename for filename in filenames if filename.endswith('.mp4')]

        return video_filenames
    else:
        # Handle unsuccessful request
        print(f"Failed to retrieve directory listing from {video_directory}")
        return []


def escape_backslashes(data):
    if isinstance(data, str):
        return data.replace("\\", "\\\\")
    elif isinstance(data, list):
        return [escape_backslashes(item) for item in data]
    elif isinstance(data, dict):
        return {key: escape_backslashes(value) for key, value in data.items()}
    return data

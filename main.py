import re
import isodate
import datetime
import requests
from bs4 import BeautifulSoup

def get_playlist_videos(playlist_url):
    videos = []
    response = requests.get(playlist_url)
    if response.status_code != 200:
        print("Error: Unable to access the playlist URL.")
        return videos

    soup = BeautifulSoup(response.text, "html.parser")
    for script in soup.find_all("script"):
        if "var ytInitialData" in script.string if script.string else "":
            data = script.string
            video_ids = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', data)
            videos.extend(video_ids)
            break

    return list(set(videos))

def get_video_durations(video_ids):
    durations = []
    video_count = 0
    for video_id in video_ids:
        print(f"\nFetching video {video_count + 1}...")
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        response = requests.get(video_url)
        if response.status_code != 200:
            print(f"Error: Unable to access video {video_id}")
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        duration_tag = soup.find("meta", itemprop="duration")
        if duration_tag:
            try:
                duration = isodate.parse_duration(duration_tag["content"])
                durations.append(duration)
                video_count += 1
            except:
                print("Error fetching video - skipping...")
                continue

    return durations

def calculate_total_duration(durations):
    total_duration = datetime.timedelta()
    for duration in durations:
        total_duration += duration
    return total_duration

def main():
    playlist_url = input("Enter YouTube playlist URL: ")

    # Extract playlist ID from URL
    playlist_id_match = re.search(r"[&?]list=([a-zA-Z0-9_-]+)", playlist_url)
    if not playlist_id_match:
        print("Invalid playlist URL.")
        return

    # Get video durations
    video_ids = get_playlist_videos(playlist_url)
    if not video_ids:
        print("No videos found in the playlist.")
        return

    durations = get_video_durations(video_ids)

    # Calculate total duration
    print("\nCalculating total duration...")
    total_duration = calculate_total_duration(durations)
    print("Total playlist duration: ", total_duration)
    print(f"\nFinished processing {len(durations)} videos!")

if __name__ == "__main__":
    main()

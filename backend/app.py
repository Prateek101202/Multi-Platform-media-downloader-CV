import os
import re
import time
import instaloader
import yt_dlp
import subprocess
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from pytubefix import YouTube
from pytubefix.cli import on_progress

app = Flask(__name__)
CORS(app, resources={r"/download": {"origins": "*"}})

# Define a directory for downloads
DOWNLOAD_DIR = "/tmp/media_downloader/"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@app.route('/download', methods=['POST'])
def download_content():
    data = request.get_json()
    video_url = data.get('url')
    platform = data.get('platform')
    delete_file = True
    if not video_url:
        return jsonify({"error": "No URL provided"}), 400

    file_path = None

    try:
        if platform == 'youtube_video':
            yt = YouTube(video_url, on_progress_callback=on_progress)
            ys = yt.streams.get_highest_resolution()
            file_path = os.path.join(DOWNLOAD_DIR, f"{sanitize_filename(yt.title)}.mp4")
            ys.download(filename=file_path)

        elif platform == 'youtube_audio':
            yt = YouTube(video_url, on_progress_callback=on_progress)
            ys = yt.streams.get_audio_only()
            file_path = os.path.join(DOWNLOAD_DIR, f"{sanitize_filename(yt.title)}.mp3")
            ys.download(filename=file_path)

        elif platform == 'instagram':
            shortcode = get_shortcode_from_url(video_url)
            if not shortcode:
                return jsonify({"error": "Invalid URL or shortcode could not be extracted."}), 400

            L = instaloader.Instaloader(
                download_videos=True, 
                download_video_thumbnails=False, 
                post_metadata_txt_pattern="",
                dirname_pattern=DOWNLOAD_DIR,
                filename_pattern="instaVideoDownloaded"  # Filename is now fixed as "instaDownloaded"
            )
            post = instaloader.Post.from_shortcode(L.context, shortcode)
            L.download_post(post, target="")
            file_path = os.path.join(DOWNLOAD_DIR, "instaVideoDownloaded.mp4")

            # Clean up unwanted files
            unwanted_files = [f for f in os.listdir(DOWNLOAD_DIR) if f.endswith(".json.xz")]
            for file in unwanted_files:
                os.remove(os.path.join(DOWNLOAD_DIR, file))

        elif platform == 'facebook':
            timestamp = str(int(time.time()))
            fixed_filename = f'fb_downloaded_video_{timestamp}.mp4'
            ydl_opts = {
                'format': 'best',
                'outtmpl': os.path.join(DOWNLOAD_DIR, fixed_filename),
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
            file_path = os.path.join(DOWNLOAD_DIR, fixed_filename)

        elif platform == 'twitter':
            timestamp = str(int(time.time()))
            fixed_filename = f'twitter_downloaded_video_{timestamp}.mp4'
            ydl_opts = {
                'outtmpl': os.path.join(DOWNLOAD_DIR, fixed_filename),
                'format': 'best',
                'noplaylist': True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
            file_path = os.path.join(DOWNLOAD_DIR, fixed_filename)

        elif platform == 'spotify':
            timestamp = str(int(time.time()))
            DOWNLOAD_DIR1 = "/tmp/"
            sanitized_filename = 'media_downloader/'
            file_path = os.path.join(DOWNLOAD_DIR1, sanitized_filename)
            before_files = set(os.listdir(file_path))
            result = subprocess.run(
                ["spotdl", video_url, "--output", file_path],
                text=True, capture_output=True
            )
            if result.returncode != 0:
                return jsonify({"error": f"Spotify download failed: {result.stderr}"}), 500
            after_files = set(os.listdir(file_path))
            new_files = after_files - before_files
            if not new_files:
                return jsonify({"error": "No new file was downloaded"}), 500

            # Get the file name (assuming one file was downloaded)
            downloaded_file_name = new_files.pop()
            file_path = os.path.join(file_path, downloaded_file_name)
            delete_file = False
        else:
            return jsonify({"error": "Unknown platform"}), 400

        if file_path:
            return send_file(file_path, as_attachment=True, download_name=os.path.basename(file_path))
        else:
            return jsonify({"error": "File path is None"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if delete_file and file_path and os.path.exists(file_path):
            os.remove(file_path)
        elif delete_file == False:
            delete_file= True

def get_shortcode_from_url(url):
    match = re.search(r'instagram\.com/(?:p|reel)/([A-Za-z0-9_-]+)', url)
    return match.group(1) if match else None


def sanitize_filename(name):
    # Remove special characters like "?" and sanitize for file systems
    return re.sub(r'[\\/*?:"<>|]', "", name)

if __name__ == '__main__':
    app.run(debug=True)

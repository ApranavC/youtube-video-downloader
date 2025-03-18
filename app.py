from flask import Flask, render_template, request, jsonify
import threading
from playlist_downloader import YouTubeDownloader

app = Flask(__name__)
downloader = YouTubeDownloader()
video_statuses = {}

@app.route('/')
def home():
    """Load the web interface."""
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    """Fetch videos from a YouTube playlist."""
    data = request.json
    url = data.get('url')

    if not url:
        return jsonify({'error': 'YouTube URL is required'}), 400

    videos = downloader.download_playlist(url)  
    for video in videos:
        video_statuses[video['url']] = "Pending"

    return jsonify({'videos': videos})

@app.route('/download', methods=['POST'])
def download():
    """Download selected videos and update their status."""
    data = request.json
    video_urls = data.get('video_urls')

    if not video_urls:
        return jsonify({'error': 'No videos selected'}), 400

    def download_videos():
        total_videos = len(video_urls)
        for index, video in enumerate(video_urls):
            video_statuses[video['url']] = "Downloading..."
            result = downloader.download_video(video['url'], "720")

            if result["status"] == "Downloaded":
                video_statuses[video['url']] = "Downloaded"
            elif result["status"] == "Already downloaded":
                video_statuses[video['url']] = "Already Downloaded"
            else:
                video_statuses[video['url']] = "Error"

            progress = int(((index + 1) / total_videos) * 100)
            downloader.update_progress(progress)

    threading.Thread(target=download_videos).start()

    return jsonify({'message': 'Download started'})

@app.route('/progress')
def get_progress():
    """Fetch current download progress."""
    return jsonify({"progress": downloader.get_progress(), "video_statuses": video_statuses})

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, render_template, request, jsonify
import threading
from playlist_downloader import YouTubeDownloader

app = Flask(__name__)

downloader = YouTubeDownloader()

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

    videos = []
    
    def update_ui_callback(videos_list):
        nonlocal videos
        videos = videos_list

    downloader.download_playlist(url, update_ui_callback)

    return jsonify({'videos': videos})

@app.route('/download', methods=['POST'])
def download():
    """Download selected videos."""
    data = request.json
    video_urls = data.get('video_urls')

    if not video_urls:
        return jsonify({'error': 'No videos selected'}), 400

    def download_videos():
        for index, video in enumerate(video_urls):
            downloader.download_video(video['url'], index, "720")

    threading.Thread(target=download_videos).start()

    return jsonify({'message': 'Download started'})

if __name__ == '__main__':
    app.run(debug=True)

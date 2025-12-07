"""
Vercel Serverless Function Entry Point
YouTube Transcript Extractor Web App
"""

from flask import Flask, render_template, request, jsonify
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from youtube_transcript_extractor import YouTubeTranscriptExtractor

app = Flask(__name__, template_folder='../templates')
extractor = YouTubeTranscriptExtractor()


@app.route('/')
def index():
    """Serve the main page."""
    return render_template('index.html')


@app.route('/extract', methods=['POST'])
def extract():
    """Extract transcript from YouTube URL."""
    data = request.get_json()
    video_url = data.get('url', '').strip()

    if not video_url:
        return jsonify({'error': 'Please provide a YouTube URL'}), 400

    try:
        # Extract transcript
        transcript = extractor.extract_transcript(video_url, languages=['en'])

        # Format transcript entries for easy copy-paste
        transcript_text = []
        for entry in transcript.transcript:
            timestamp = entry.get_timestamp_formatted()
            transcript_text.append({
                'timestamp': timestamp,
                'start_seconds': entry.start,
                'duration': entry.duration,
                'text': entry.text,
                'url_with_timestamp': f"{transcript.video_url}&t={int(entry.start)}s"
            })

        # Return structured data
        return jsonify({
            'success': True,
            'video_id': transcript.video_id,
            'video_title': transcript.video_title,
            'video_url': transcript.video_url,
            'channel_name': transcript.channel_name,
            'language': transcript.language,
            'is_generated': transcript.is_generated,
            'total_entries': len(transcript.transcript),
            'transcript': transcript_text,
            'full_json': transcript.to_dict()
        })

    except Exception as e:
        return jsonify({
            'error': f'{type(e).__name__}: {str(e)}'
        }), 400


# Vercel requires this for serverless functions
app = app


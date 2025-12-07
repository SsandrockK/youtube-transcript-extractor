# YouTube Transcript Extractor

A simple, reliable tool to extract timestamped transcripts from any YouTube video. Use it as a web app, Python library, or deploy it publicly on Vercel.

## 🌐 Live Demo

**[Try it now →](https://your-app.vercel.app)** *(Update this link after deploying)*

## ✨ Features

- 📝 Extract transcripts from any YouTube video with captions
- ⏱️ Timestamps included (HH:MM:SS format)
- 📋 One-click copy for any field
- 💾 Download as JSON or CSV
- 🔗 Supports all YouTube URL formats
- 🌍 Language selection support
- 🚀 Deploy your own instance on Vercel

## 🖥️ Use the Web App Locally

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/youtube-transcript-extractor.git
cd youtube-transcript-extractor

# Install dependencies
pip install -r requirements.txt

# Run the web app
python web_app.py
```

Then open **http://localhost:8080** in your browser.

## 🐍 Use as a Python Library

```python
from youtube_transcript_extractor import YouTubeTranscriptExtractor

extractor = YouTubeTranscriptExtractor()

# Extract transcript from any YouTube video
transcript = extractor.extract_transcript(
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    languages=['en']
)

# Access the data
print(f"Title: {transcript.video_title}")
print(f"Channel: {transcript.channel_name}")

# Get timestamped text
for entry in transcript.transcript:
    print(f"[{entry.get_timestamp_formatted()}] {entry.text}")

# Export to JSON
data = transcript.to_dict()
```

## 📤 Output Format

```json
{
  "video_id": "dQw4w9WgXcQ",
  "video_title": "Rick Astley - Never Gonna Give You Up",
  "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "channel_name": "Rick Astley",
  "language": "en",
  "is_generated": false,
  "transcript": [
    {
      "text": "We're no strangers to love",
      "start": 18.0,
      "duration": 3.5
    }
  ]
}
```

## 🚀 Deploy to Vercel

1. Fork this repository
2. Go to [vercel.com](https://vercel.com) and sign in with GitHub
3. Click **"Add New Project"** and import this repo
4. Click **Deploy**

That's it! You'll get a public URL like `youtube-transcript-extractor.vercel.app`

## 🔗 Supported URL Formats

- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://www.youtube.com/embed/VIDEO_ID`
- `https://www.youtube.com/v/VIDEO_ID`
- Just the video ID: `VIDEO_ID`

## ⚠️ Limitations

- Video must have captions (auto-generated or manual)
- Private/age-restricted videos won't work
- Some creators disable transcripts

## 📦 Dependencies

- `flask` - Web framework
- `youtube-transcript-api` - Transcript extraction
- `yt-dlp` - Video metadata (title, channel)

## 📄 License

MIT License - Use it however you want!

---

**Made with ❤️ for anyone who needs YouTube transcripts**


"""
YouTube Transcript Extractor
A reliable tool for extracting timestamped transcripts from YouTube videos.
Designed for use with RAG (Retrieval-Augmented Generation) systems.
"""

import re
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
    YouTubeRequestFailed
)
import yt_dlp


@dataclass
class TranscriptEntry:
    """Represents a single timestamped transcript entry."""
    text: str
    start: float  # Start time in seconds
    duration: float  # Duration in seconds

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    def get_timestamp_formatted(self) -> str:
        """Get timestamp in HH:MM:SS format."""
        hours = int(self.start // 3600)
        minutes = int((self.start % 3600) // 60)
        seconds = int(self.start % 60)
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        return f"{minutes:02d}:{seconds:02d}"


@dataclass
class VideoTranscript:
    """Complete video transcript with metadata."""
    video_id: str
    video_title: str
    video_url: str
    channel_name: Optional[str]
    transcript: List[TranscriptEntry]
    language: str
    is_generated: bool  # Whether transcript was auto-generated

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "video_id": self.video_id,
            "video_title": self.video_title,
            "video_url": self.video_url,
            "channel_name": self.channel_name,
            "language": self.language,
            "is_generated": self.is_generated,
            "transcript": [entry.to_dict() for entry in self.transcript]
        }

    def get_full_text(self) -> str:
        """Get complete transcript as plain text."""
        return " ".join(entry.text for entry in self.transcript)

    def get_timestamped_text(self) -> str:
        """Get transcript with timestamps."""
        lines = []
        for entry in self.transcript:
            timestamp = entry.get_timestamp_formatted()
            lines.append(f"[{timestamp}] {entry.text}")
        return "\n".join(lines)


class YouTubeTranscriptExtractor:
    """Extracts timestamped transcripts from YouTube videos."""

    def __init__(self):
        """Initialize the extractor."""
        self.transcript_api = YouTubeTranscriptApi()

    @staticmethod
    def extract_video_id(url: str) -> Optional[str]:
        """
        Extract video ID from various YouTube URL formats.

        Supports:
        - https://www.youtube.com/watch?v=VIDEO_ID
        - https://youtu.be/VIDEO_ID
        - https://www.youtube.com/embed/VIDEO_ID
        - https://www.youtube.com/v/VIDEO_ID
        """
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/|youtube\.com\/v\/)([a-zA-Z0-9_-]{11})',
            r'(?:youtube\.com\/.*[?&]v=)([a-zA-Z0-9_-]{11})',
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        # If no match, check if it's already a video ID
        if re.match(r'^[a-zA-Z0-9_-]{11}$', url):
            return url

        return None

    def get_video_metadata(self, video_id: str) -> Dict[str, str]:
        """
        Fetch video metadata using yt-dlp.

        Args:
            video_id: YouTube video ID

        Returns:
            Dictionary with video metadata
        """
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
        }

        video_url = f"https://www.youtube.com/watch?v={video_id}"

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                return {
                    'title': info.get('title', 'Unknown Title'),
                    'channel': info.get('uploader', info.get('channel', None)),
                    'url': video_url
                }
        except Exception as e:
            # Fallback if yt-dlp fails
            print(f"Warning: Could not fetch metadata with yt-dlp: {e}")
            return {
                'title': f"Video {video_id}",
                'channel': None,
                'url': video_url
            }

    def extract_transcript(
        self,
        url: str,
        languages: Optional[List[str]] = None,
        preserve_formatting: bool = False
    ) -> VideoTranscript:
        """
        Extract timestamped transcript from a YouTube video.

        Args:
            url: YouTube video URL or video ID
            languages: List of language codes to try (e.g., ['en', 'es']).
                      If None, uses default available transcript.
            preserve_formatting: Whether to preserve formatting (default: False for better RAG)

        Returns:
            VideoTranscript object containing all video and transcript data

        Raises:
            ValueError: If video ID cannot be extracted
            TranscriptsDisabled: If transcripts are disabled for the video
            NoTranscriptFound: If no transcript is available
            VideoUnavailable: If the video is unavailable
        """
        # Extract video ID
        video_id = self.extract_video_id(url)
        if not video_id:
            raise ValueError(f"Could not extract video ID from URL: {url}")

        # Get video metadata
        metadata = self.get_video_metadata(video_id)

        # Fetch transcript
        try:
            if languages:
                transcript_list = self.transcript_api.list(video_id)

                # Try to find transcript in preferred languages
                transcript_data = None
                for lang in languages:
                    try:
                        transcript_obj = transcript_list.find_transcript([lang])
                        transcript_data = transcript_obj.fetch()
                        language = lang
                        is_generated = transcript_obj.is_generated
                        break
                    except NoTranscriptFound:
                        continue

                if not transcript_data:
                    # Fallback to any available transcript
                    transcript_obj = transcript_list.find_generated_transcript(['en'])
                    transcript_data = transcript_obj.fetch()
                    language = transcript_obj.language_code
                    is_generated = transcript_obj.is_generated
            else:
                # Get default transcript - try using fetch method
                try:
                    # Try to get transcript list first for better metadata
                    transcript_list = self.transcript_api.list(video_id)
                    available = list(transcript_list)
                    if available:
                        # Use the first available transcript
                        transcript_obj = available[0]
                        transcript_data = transcript_obj.fetch()
                        language = transcript_obj.language_code
                        is_generated = transcript_obj.is_generated
                    else:
                        raise NoTranscriptFound("No transcripts available")
                except Exception:
                    # Ultimate fallback - use fetch directly
                    transcript_data = self.transcript_api.fetch(video_id)
                    language = 'unknown'
                    is_generated = True

        except TranscriptsDisabled:
            raise TranscriptsDisabled(f"Transcripts are disabled for video: {video_id}")
        except NoTranscriptFound:
            raise NoTranscriptFound(f"No transcript found for video: {video_id}")
        except VideoUnavailable:
            raise VideoUnavailable(f"Video is unavailable: {video_id}")
        except YouTubeRequestFailed as e:
            raise YouTubeRequestFailed(f"YouTube request failed: {e}")

        # Convert transcript data to TranscriptEntry objects
        transcript_entries = []
        for entry in transcript_data:
            # Handle both dict and object-based API responses
            if hasattr(entry, 'text'):
                # New API: FetchedTranscriptSnippet objects
                text = entry.text
                start = entry.start
                duration = entry.duration
            else:
                # Old API: dictionaries
                text = entry['text']
                start = entry['start']
                duration = entry['duration']

            if not preserve_formatting:
                # Clean up text for better RAG performance
                text = text.replace('\n', ' ').strip()

            transcript_entries.append(TranscriptEntry(
                text=text,
                start=start,
                duration=duration
            ))

        # Create and return VideoTranscript object
        return VideoTranscript(
            video_id=video_id,
            video_title=metadata['title'],
            video_url=metadata['url'],
            channel_name=metadata['channel'],
            transcript=transcript_entries,
            language=language,
            is_generated=is_generated
        )


def main():
    """Example usage of the YouTube Transcript Extractor."""
    extractor = YouTubeTranscriptExtractor()

    # Example URL - replace with your own
    example_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

    try:
        # Extract transcript
        video_transcript = extractor.extract_transcript(example_url, languages=['en'])

        # Print metadata
        print(f"Video ID: {video_transcript.video_id}")
        print(f"Title: {video_transcript.video_title}")
        print(f"URL: {video_transcript.video_url}")
        print(f"Channel: {video_transcript.channel_name}")
        print(f"Language: {video_transcript.language}")
        print(f"Auto-generated: {video_transcript.is_generated}")
        print(f"\nTranscript entries: {len(video_transcript.transcript)}")
        print("\nFirst 5 entries with timestamps:")

        for entry in video_transcript.transcript[:5]:
            timestamp = entry.get_timestamp_formatted()
            print(f"[{timestamp}] {entry.text}")

        # Convert to dictionary for JSON serialization
        data_dict = video_transcript.to_dict()
        print(f"\nCan be serialized to JSON: {bool(data_dict)}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()

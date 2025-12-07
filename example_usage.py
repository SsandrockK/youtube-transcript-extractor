"""
Example usage of the YouTube Transcript Extractor for RAG applications.
"""

import json
from youtube_transcript_extractor import YouTubeTranscriptExtractor


def example_basic_extraction():
    """Basic example: Extract transcript from a single video."""
    print("=" * 60)
    print("EXAMPLE 1: Basic Transcript Extraction")
    print("=" * 60)

    extractor = YouTubeTranscriptExtractor()

    # Replace with your YouTube video URL
    video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

    try:
        # Extract transcript
        video_transcript = extractor.extract_transcript(video_url, languages=['en'])

        # Display metadata
        print(f"\nVideo ID: {video_transcript.video_id}")
        print(f"Title: {video_transcript.video_title}")
        print(f"URL: {video_transcript.video_url}")
        print(f"Channel: {video_transcript.channel_name}")
        print(f"Language: {video_transcript.language}")
        print(f"Auto-generated: {video_transcript.is_generated}")
        print(f"Total transcript entries: {len(video_transcript.transcript)}")

        # Display first 3 entries
        print("\nFirst 3 transcript entries:")
        for entry in video_transcript.transcript[:3]:
            print(f"  [{entry.get_timestamp_formatted()}] {entry.text}")

    except Exception as e:
        print(f"Error: {e}")


def example_json_export():
    """Example 2: Export transcript to JSON for RAG system."""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Export to JSON for RAG")
    print("=" * 60)

    extractor = YouTubeTranscriptExtractor()
    video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

    try:
        video_transcript = extractor.extract_transcript(video_url, languages=['en'])

        # Convert to dictionary
        transcript_dict = video_transcript.to_dict()

        # Save to JSON file
        output_file = f"{video_transcript.video_id}_transcript.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(transcript_dict, f, indent=2, ensure_ascii=False)

        print(f"\nTranscript saved to: {output_file}")
        print(f"File contains {len(transcript_dict['transcript'])} timestamped entries")

    except Exception as e:
        print(f"Error: {e}")


def example_rag_chunking():
    """Example 3: Chunk transcript for RAG with time references."""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Chunking for RAG with Time References")
    print("=" * 60)

    extractor = YouTubeTranscriptExtractor()
    video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

    try:
        video_transcript = extractor.extract_transcript(video_url, languages=['en'])

        # Create chunks of ~30 seconds for RAG
        chunks = []
        current_chunk = []
        chunk_start_time = 0

        for entry in video_transcript.transcript:
            if not current_chunk:
                chunk_start_time = entry.start

            current_chunk.append(entry)

            # Create chunk every 30 seconds
            if entry.start - chunk_start_time >= 30:
                chunk_text = " ".join(e.text for e in current_chunk)
                chunks.append({
                    "video_id": video_transcript.video_id,
                    "video_title": video_transcript.video_title,
                    "video_url": video_transcript.video_url,
                    "start_time": chunk_start_time,
                    "timestamp": current_chunk[0].get_timestamp_formatted(),
                    "text": chunk_text,
                    "url_with_timestamp": f"{video_transcript.video_url}&t={int(chunk_start_time)}s"
                })
                current_chunk = []

        # Add remaining entries as final chunk
        if current_chunk:
            chunk_text = " ".join(e.text for e in current_chunk)
            chunks.append({
                "video_id": video_transcript.video_id,
                "video_title": video_transcript.video_title,
                "video_url": video_transcript.video_url,
                "start_time": chunk_start_time,
                "timestamp": current_chunk[0].get_timestamp_formatted(),
                "text": chunk_text,
                "url_with_timestamp": f"{video_transcript.video_url}&t={int(chunk_start_time)}s"
            })

        print(f"\nCreated {len(chunks)} chunks for RAG indexing")
        print("\nFirst chunk example:")
        print(f"  Timestamp: {chunks[0]['timestamp']}")
        print(f"  URL with timestamp: {chunks[0]['url_with_timestamp']}")
        print(f"  Text preview: {chunks[0]['text'][:100]}...")

        # Save chunks to JSON
        chunks_file = f"{video_transcript.video_id}_chunks.json"
        with open(chunks_file, 'w', encoding='utf-8') as f:
            json.dump(chunks, f, indent=2, ensure_ascii=False)

        print(f"\nChunks saved to: {chunks_file}")

    except Exception as e:
        print(f"Error: {e}")


def example_batch_processing():
    """Example 4: Process multiple videos."""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Batch Processing Multiple Videos")
    print("=" * 60)

    extractor = YouTubeTranscriptExtractor()

    # List of video URLs to process
    video_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        # Add more URLs here
    ]

    results = []
    failed = []

    for url in video_urls:
        try:
            print(f"\nProcessing: {url}")
            video_transcript = extractor.extract_transcript(url, languages=['en'])

            results.append(video_transcript.to_dict())
            print(f"  ✓ Success: {video_transcript.video_title}")

        except Exception as e:
            print(f"  ✗ Failed: {e}")
            failed.append({"url": url, "error": str(e)})

    print(f"\n\nProcessing complete:")
    print(f"  Successful: {len(results)}")
    print(f"  Failed: {len(failed)}")

    # Save all results
    if results:
        with open("batch_transcripts.json", 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\nAll transcripts saved to: batch_transcripts.json")


def example_timestamped_search():
    """Example 5: Get transcript with formatted timestamps (for display)."""
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Formatted Timestamped Transcript")
    print("=" * 60)

    extractor = YouTubeTranscriptExtractor()
    video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

    try:
        video_transcript = extractor.extract_transcript(video_url, languages=['en'])

        # Get timestamped text
        timestamped_text = video_transcript.get_timestamped_text()

        # Save to text file
        output_file = f"{video_transcript.video_id}_timestamped.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"Video: {video_transcript.video_title}\n")
            f.write(f"URL: {video_transcript.video_url}\n")
            f.write(f"Channel: {video_transcript.channel_name}\n\n")
            f.write(timestamped_text)

        print(f"\nTimestamped transcript saved to: {output_file}")

        # Show preview
        lines = timestamped_text.split('\n')
        print(f"\nPreview (first 5 lines):")
        for line in lines[:5]:
            print(f"  {line}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    # Run all examples
    example_basic_extraction()
    example_json_export()
    example_rag_chunking()
    example_batch_processing()
    example_timestamped_search()

    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)

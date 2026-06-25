# downloader.py — the engine that fetches TikTok content

import os
import uuid
import yt_dlp

# Folder where downloaded files are temporarily saved
DOWNLOAD_DIR = "downloads"


def extract_audio(url: str) -> str:
    """Download a TikTok link and return the path to an MP3 file."""

    # Make sure the downloads folder exists
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    # A random unique name so two users never overwrite each other's files
    file_id = uuid.uuid4().hex
    output_template = os.path.join(DOWNLOAD_DIR, f"{file_id}.%(ext)s")

    # Instructions for yt-dlp
    options = {
        "format": "bestaudio/best",          # grab the best audio available
        "outtmpl": output_template,          # where + what to name the file
        "postprocessors": [{                 # after downloading, convert it:
            "key": "FFmpegExtractAudio",     #   use ffmpeg to extract audio
            "preferredcodec": "mp3",         #   convert to MP3
            "preferredquality": "192",       #   at 192 kbps quality
        }],
        "quiet": True,                       # don't spam the terminal
        "no_warnings": True,
    }

    # Run the download
    with yt_dlp.YoutubeDL(options) as ydl:
        ydl.download([url])

    # The converted file will end in .mp3
    return os.path.join(DOWNLOAD_DIR, f"{file_id}.mp3")


def download_video(url: str) -> str:
    """Download a TikTok link as a clean (no-watermark) MP4 and return the path."""

    # Same setup: ensure folder exists, make a unique filename
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    file_id = uuid.uuid4().hex
    output_template = os.path.join(DOWNLOAD_DIR, f"{file_id}.%(ext)s")

    # Instructions for yt-dlp
    options = {
        "format": "mp4/best",        # prefer an MP4 video file
        "outtmpl": output_template,  # where + what to name it
        "quiet": True,
        "no_warnings": True,
    }

    # Download, and ask yt-dlp for the exact filename it produced
    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

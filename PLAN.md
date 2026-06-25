# TikTok Downloader — Telegram Bot Plan

A Telegram bot that takes a TikTok link and can either:

1. **Extract the audio** as an MP3, or
2. **Download the full video without the watermark** (clean MP4).

The user picks which one with inline buttons after sending a link.

## 1. Overview

```
                                              ┌─ 🎵 Audio  → ffmpeg extracts MP3 ─┐
User → sends TikTok link → Bot shows buttons ─┤                                   ├→ bot sends file back
                                              └─ 🎬 Video  → clean MP4 (no mark) ─┘
```

The bot listens for messages, detects TikTok URLs, and replies with two inline
buttons. The user taps one; the bot downloads accordingly, sends the file back,
then cleans up temp files.

**Note on the watermark:** `yt-dlp` downloads TikTok videos **without the
watermark by default** — TikTok serves a clean version through the same endpoint
yt-dlp uses, so no extra tooling or tricks are needed.

## 2. Tech Stack

| Component         | Choice                       | Why                                        |
| ----------------- | ---------------------------- | ------------------------------------------ |
| Language          | Python 3.10+                 | Best ecosystem for this                    |
| Telegram lib      | `python-telegram-bot` v21+   | Mature, async, well-documented             |
| Downloader        | `yt-dlp`                     | Most reliable TikTok extractor, maintained |
| Audio conversion  | `ffmpeg`                     | Standard tool; yt-dlp calls it automatically |
| Config            | `.env` + `python-dotenv`     | Keeps the bot token out of the code        |

## 3. Prerequisites (one-time setup)

1. **Get a bot token**: Message [@BotFather](https://t.me/BotFather) → `/newbot` → copy the token.
2. **Install Python 3.10+**: `winget install Python.Python.3.12`
3. **Install ffmpeg**: `winget install Gyan.FFmpeg` (restart terminal afterwards so it's on PATH).
4. **Python packages**: `pip install python-telegram-bot yt-dlp python-dotenv`

## 4. Project Structure

```
tiktok/
├── bot.py             # main bot logic + inline buttons
├── downloader.py      # yt-dlp: audio extraction + clean video download
├── .env               # TELEGRAM_BOT_TOKEN=xxxx  (secret, never commit)
├── .env.example       # template showing what goes in .env
├── requirements.txt   # pinned dependencies
├── .gitignore         # ignore .env, downloads/, __pycache__
└── downloads/         # temp folder for files (auto-cleaned)
```

## 5. Build Steps (in order)

### Step 1 — Config & scaffolding
- Create `requirements.txt`, `.env.example`, `.gitignore`.
- Load token from `.env`; fail clearly if missing.

### Step 2 — Downloader module (`downloader.py`)
- **`extract_audio(url) -> filepath`**: yt-dlp with format `bestaudio` + a
  postprocessor that converts to MP3 (192 kbps). Returns the `.mp3` path.
- **`download_video(url) -> filepath`**: yt-dlp with format `best` (MP4). TikTok
  serves the no-watermark version here by default. Returns the `.mp4` path.
- Both write to `downloads/` with a unique filename so concurrent users don't collide.
- Handle errors (private/region-locked/invalid URL) with clear messages.

### Step 3 — Bot handlers (`bot.py`)
- `/start` and `/help` commands → friendly instructions.
- **Message handler:**
  1. Detect a TikTok URL (regex for `tiktok.com` / `vm.tiktok.com`).
  2. Reply with two inline buttons: `🎵 Audio (MP3)` and `🎬 Video (no watermark)`.
     Store the URL keyed to this message so the callback knows what to fetch.
- **Callback handler** (fires when a button is tapped):
  1. Acknowledge the tap; edit message to "⏳ Downloading…".
  2. Call `extract_audio()` or `download_video()` depending on the button.
  3. Send the file: `send_audio` for MP3 (playable track), `send_video` for MP4.
  4. Delete the temp file.
  5. On failure, reply with a clear error.

### Step 4 — Robustness
- URL validation (reject non-TikTok links politely).
- Telegram's **50 MB** bot upload limit — audio is tiny, but **HD/long videos can
  exceed it**. Check file size before sending; if too big, send a friendly
  "video too large to upload" message (optionally offer the audio instead).
- Try/except around everything so one bad link doesn't crash the bot.
- Optional: limit concurrent downloads / simple per-user rate limit.

### Step 5 — Run & test
- `python bot.py`
- Send your bot a TikTok link, tap each button, confirm you get the MP3 and the
  clean (no-watermark) MP4 back.

## 6. Deployment (when it works locally)

- **Easiest:** keep running on your PC while testing.
- **Always-on:** a cheap VPS (Hetzner/DigitalOcean ~$5/mo) or a free tier (Railway, Fly.io). Run under `systemd` or in `screen`/`tmux` so it survives disconnects.
- **Maintenance:** run `pip install -U yt-dlp` periodically — TikTok changes break old versions.

## 7. Important Caveats

- **ToS / legal:** TikTok's terms don't allow downloading. Fine for personal/educational use; **don't** run it as a public commercial service (risk of IP bans + takedowns). Don't redistribute copyrighted audio.
- **Reliability:** Some videos (private, region-locked, deleted) won't download — that's expected.
- **Token safety:** Never share or commit your bot token. The `.env` + `.gitignore` setup handles this.

## 8. Optional Enhancements (later)

- Audio metadata (title = TikTok caption, thumbnail as cover art).
- Batch links, playlists.
- Usage logging / analytics.

---

**Estimated size:** ~150–200 lines of code total. A solid afternoon project.

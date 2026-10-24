---
name: yt-summary
description: Summarize YouTube videos via yt-dlp subtitles. Triggers on youtube.com/watch, youtu.be links, or requests like summarize this video.
version: 1.1.0
author: qam1s
license: MIT
platforms: [linux]
---

# YouTube Summary via yt-dlp

Make a summary of a YouTube video using subtitles fetched with the system yt-dlp.

## When to Use

- Message contains `youtube.com/watch`, `youtube.com/live`, `youtu.be/`.

## Prerequisites

- `yt-dlp` in PATH and `python3` with stdlib only.
- Helper script at `scripts/get_transcript.py` inside this skill.

## Procedure

1. Extract all YouTube URLs from the user message. Completion: every link listed, video IDs resolved.
2. For each URL run via the shell tool:
   ```
   python3 <skill-dir>/scripts/get_transcript.py "<url>"
   ```
   Resolve `<skill-dir>` with a file search for `get_transcript.py` if the path differs. Timeout 120000. Completion: script prints transcript text or a single `ERROR:` line.
3. On `ERROR: no subtitles found`: report that the video has no usable captions and stop for that link. On `ERROR: yt-dlp failed` or 429/403: retry once with cookies by appending `--cookies-from-browser chrome` to the script call as `python3 get_transcript.py --cookies-from-browser chrome "<url>"`. Completion: success transcript or named failure, no guessing.
4. Summarize the transcript in Russian: several bullet points with the substance, then a 2-sentence conclusion. Keep it dense, no filler. Trim transcript to ~15000 chars if longer. Transcript may be in any language, translate it in the summary. Completion: summary covers the transcript, not the title alone.
5. Multiple links: one summary block per link with the URL as heading. Completion: every requested link accounted for.

## Pitfalls

- Subtitles may be auto-generated and noisy; never invent facts missing from the transcript.
- Age or login restricted videos fail without browser cookies; say so plainly and suggest the cookies retry.

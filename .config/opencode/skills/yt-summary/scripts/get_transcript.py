#!/usr/bin/env python3
import argparse
import glob
import os
import re
import subprocess
import sys
import tempfile


def clean_vtt(path):
    with open(path, encoding="utf-8", errors="ignore") as f:
        lines = f.read().splitlines()
    out = []
    tag_re = re.compile(r"<[^>]+>")
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith("WEBVTT"):
            continue
        if "-->" in line:
            continue
        if line.startswith("NOTE"):
            continue
        line = tag_re.sub("", line).strip()
        if not line:
            continue
        if out and out[-1] == line:
            continue
        out.append(line)
    return re.sub(r"\s+", " ", " ".join(out))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--cookies-from-browser", default="")
    ap.add_argument("--max-chars", type=int, default=15000)
    args = ap.parse_args()
    with tempfile.TemporaryDirectory() as tmp:
        outtmpl = os.path.join(tmp, "%(id)s.%(ext)s")
        cmd = [
            "yt-dlp",
            "--skip-download",
            "--write-subs",
            "--write-auto-subs",
            "--sub-langs",
            "all,-live_chat",
            "--sub-format",
            "vtt/best",
            "--no-playlist",
            "--retries",
            "3",
            "--socket-timeout",
            "15",
            "--extractor-args",
            "youtube:player_client=android,mweb",
            "-o",
            outtmpl,
        ]
        if args.cookies_from_browser:
            cmd += ["--cookies-from-browser", args.cookies_from_browser]
        cmd.append(args.url)
        try:
            subprocess.run(
                cmd,
                cwd=tmp,
                timeout=90,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception as e:
            print("ERROR: yt-dlp failed: " + str(e))
            return 1
        files = sorted(glob.glob(os.path.join(tmp, "*.vtt")))
        if not files:
            print("ERROR: no subtitles found")
            return 2
        candidates = []
        for p in files:
            t = clean_vtt(p)
            if len(t) > 200:
                candidates.append(t)
        if not candidates:
            print("ERROR: empty subtitles")
            return 2
        best = max(candidates, key=len)
        print(best[: args.max_chars])
        return 0


if __name__ == "__main__":
    sys.exit(main())

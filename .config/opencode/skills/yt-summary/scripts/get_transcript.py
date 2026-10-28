import argparse
import contextlib
import glob
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import urllib.parse


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


def is_translation(entries):
    if not entries:
        return True
    url = entries[0].get("url", "")
    try:
        qs = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
    except (ValueError, AttributeError, TypeError):
        return True
    return "tlang" in qs


def build_order(manual, auto):
    order = []
    preferred = ["ru-orig", "en-orig", "ru", "en"]
    for lang in preferred:
        if lang in manual or lang in auto:
            order.append(lang)
    manual_rest = sorted(
        [k for k in manual if k not in order],
        key=lambda k: (not k.endswith("-orig"), k),
    )
    order.extend(manual_rest)
    auto_orig = []
    auto_translated = []
    for k in sorted(auto):
        if k in order or k in manual:
            continue
        entries = auto.get(k) or []
        if is_translation(entries):
            auto_translated.append(k)
        else:
            auto_orig.append(k)
    order.extend(auto_orig)
    order.extend(auto_translated)
    return order[:6]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--cookies-from-browser", default="")
    ap.add_argument("--max-chars", type=int, default=0)
    args = ap.parse_args()

    dump_cmd = [
        "yt-dlp",
        "--dump-single-json",
        "--skip-download",
        "--no-playlist",
        "--retries",
        "3",
        "--socket-timeout",
        "15",
    ]
    if args.cookies_from_browser:
        dump_cmd += ["--cookies-from-browser", args.cookies_from_browser]
    dump_cmd.append(args.url)
    try:
        proc = subprocess.run(
            dump_cmd,
            check=False,
            timeout=60,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.SubprocessError) as e:
        print("ERROR: yt-dlp failed: " + str(e))
        return 1
    if proc.returncode != 0:
        err = (proc.stderr or "").strip().splitlines()
        tail = err[-1] if err else "dump failed"
        print("ERROR: yt-dlp failed: " + tail[-300:])
        return 1
    try:
        info = json.loads(proc.stdout)
    except ValueError as e:
        print("ERROR: yt-dlp failed: bad json: " + str(e))
        return 1
    manual = info.get("subtitles") or {}
    auto = info.get("automatic_captions") or {}
    if not manual and not auto:
        print("ERROR: no subtitles found")
        return 2
    order = build_order(manual, auto)
    if not order:
        print("ERROR: no subtitles found")
        return 2
    last_err = ""
    with tempfile.TemporaryDirectory() as tmp:
        for i, lang in enumerate(order):
            if i > 0:
                time.sleep(2)
            outtmpl = os.path.join(tmp, "%(id)s.%(ext)s")
            cmd = [
                "yt-dlp",
                "--skip-download",
                "--write-subs",
                "--write-auto-subs",
                "--sub-langs",
                lang,
                "--sub-format",
                "vtt/best",
                "--no-playlist",
                "--retries",
                "3",
                "--socket-timeout",
                "15",
                "--sleep-subtitles",
                "2",
                "-o",
                outtmpl,
            ]
            if args.cookies_from_browser:
                cmd += ["--cookies-from-browser", args.cookies_from_browser]
            cmd.append(args.url)
            try:
                p = subprocess.run(
                    cmd,
                    check=False,
                    cwd=tmp,
                    timeout=90,
                    capture_output=True,
                    text=True,
                )
            except (OSError, subprocess.SubprocessError) as e:
                last_err = str(e)
                continue
            files = sorted(glob.glob(os.path.join(tmp, "*.vtt")))
            for fp in files:
                t = clean_vtt(fp)
                if len(t) > 200:
                    print(t if not args.max_chars else t[: args.max_chars])
                    return 0
            for fp in files:
                with contextlib.suppress(OSError):
                    os.remove(fp)
            err_txt = (p.stderr or "") + (p.stdout or "")
            if "429" in err_txt or "403" in err_txt:
                last_err = "rate limited on " + lang
            elif err_txt.strip():
                last_err = err_txt.strip().splitlines()[-1][:300]
    if "rate limited" in last_err:
        print(
            "ERROR: yt-dlp failed: " + last_err + " (try --cookies-from-browser chrome)"
        )
    elif last_err:
        print("ERROR: no subtitles found: " + last_err)
    else:
        print("ERROR: no subtitles found")
    return 2


if __name__ == "__main__":
    sys.exit(main())

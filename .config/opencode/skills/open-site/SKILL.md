---
name: open-site
description: Open a website, repo, or any URL in the user's system browser via xdg-open. Use when the user asks to open a site, link, or repo.
---

# Open Site

When the user asks to open a website, link, repo, do NOT use browser tabs (desktop browser is not connected in this setup). Open via the system opener.

## Procedure

1. Extract all URLs from the request. If a URL has no scheme, prepend
   `https://`.
2. For each URL run detached via `shell` so the agent does not block:
   `xdg-open "<url>" >/tmp/opencode/xdg-open.log 2>&1 &`
   For several URLs, run them in one command, each with its own redirect,
   or one by one.
3. Confirm briefly with the list of opened URLs.
4. If `xdg-open` is missing or fails (non-zero exit, error in log),
   report the error and paste the URLs as clickable fallback.

## Notes

- Prefer `/tmp/opencode` for logs, it is pre-created.
- Never use `browser.tabs.open` / `browser.preview` for this task.
- Do not download or fetch the URL content unless separately asked.

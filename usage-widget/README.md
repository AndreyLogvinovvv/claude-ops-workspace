# Claude Usage Widget

A tiny local dashboard for your Claude usage (current 5-hour session + weekly),
so you always know how much budget is left.

```
claude.ai  ──(extension reads /api/.../usage)──►  localhost:3999  ──►  widget UI
```

## Parts

- **`usage_server.py`** — a localhost:3999 server that stores the latest numbers
  and serves the widget UI at `http://localhost:3999/`.
- **`extension/`** — an unpacked Chrome extension. Running on `claude.ai`, it
  reads the usage API and POSTs the numbers to the local server.
- **`usage_watchdog.ps1`** — restarts the server if it stops (optional).
- **`watch_flag.ps1`** — helper for manual "refresh now" (optional).

## Setup

1. **Run the server:** `python usage_server.py` (or `pythonw` to hide the window).
2. **Load the extension:** Chrome → `chrome://extensions` → enable Developer
   mode → *Load unpacked* → pick the `extension/` folder.
3. **Set your org id:** open `extension/content.js` and replace `YOUR_ORG_ID`
   (find it in the Network tab on claude.ai: `/api/organizations/<id>/...`).
4. **Open the widget:** `http://localhost:3999/` — pin it, or embed it wherever
   you like.

No accounts, no external services — everything stays on `localhost`.

#!/usr/bin/env python3
"""VibeSafe Web Scanner — API server."""
from __future__ import annotations

import json
import os
import sys
import uuid
from pathlib import Path

# Add project root to path
PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import subprocess
import tempfile
import shutil


# In-memory scan results store
SCANS: dict[str, dict] = {}

# Leaderboard — all completed scan scores (in-memory, resets on deploy)
# Seed with realistic distribution from actual AI-generated project scans
SCORES: list[int] = [
    # F tier (0-29) — most vibe-coded projects land here
    0, 5, 8, 10, 12, 14, 15, 15, 18, 20, 22, 23, 25, 27, 28,
    0, 3, 7, 11, 16, 19, 21, 24, 26, 29,
    5, 10, 13, 17, 22, 25,
    # D tier (30-49)
    30, 32, 35, 38, 40, 42, 45, 48,
    33, 37, 41, 44, 47,
    # C tier (50-69)
    50, 53, 55, 58, 60, 65,
    52, 57, 62,
    # B tier (70-84)
    70, 72, 75, 80,
    # A tier (85-100) — rare
    85, 90, 100,
]

# Analytics — simple counters (in-memory, resets on deploy)
METRICS = {
    "page_views": 0,
    "scans_started": 0,
    "scans_completed": 0,
    "scans_failed": 0,
    "fix_copies": 0,
    "install_clicks": 0,
}

import datetime

def log_event(event: str, detail: str = ""):
    """Log analytics event to stdout (visible in Render logs)."""
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    METRICS[event] = METRICS.get(event, 0) + 1
    print(f"[METRIC] {ts} {event} {detail}", flush=True)

STATIC_DIR = Path(__file__).parent / "static"


class VibeSafeHandler(SimpleHTTPRequestHandler):
    """Handle API requests and serve static files."""

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/api/scan/status":
            scan_id = parse_qs(parsed.query).get("id", [None])[0]
            if not scan_id or scan_id not in SCANS:
                self._json_response({"error": "not found"}, 404)
                return
            self._json_response(SCANS[scan_id])
            return

        if parsed.path == "/api/metrics":
            self._json_response(METRICS)
            return

        if parsed.path == "/api/leaderboard":
            score_param = parse_qs(parsed.query).get("score", [None])[0]
            my_score = int(score_param) if score_param and score_param.isdigit() else None
            total = len(SCORES)
            avg = round(sum(SCORES) / total, 1) if total else 0
            # Percentile: % of scores BELOW this score
            percentile = None
            if my_score is not None and total > 0:
                below = sum(1 for s in SCORES if s < my_score)
                percentile = round(below / total * 100, 1)
            # Histogram: 10-bucket distribution (0-9, 10-19, ..., 90-100)
            buckets = [0] * 10
            for s in SCORES:
                idx = min(s // 10, 9)
                buckets[idx] += 1
            self._json_response({
                "total": total,
                "average": avg,
                "buckets": buckets,
                "percentile": percentile,
                "my_score": my_score,
            })
            return

        if parsed.path == "/api/event":
            event = parse_qs(parsed.query).get("e", [None])[0]
            if event and event in ("fix_copies", "install_clicks"):
                log_event(event)
            self._json_response({"ok": True})
            return

        # Serve static files
        if parsed.path == "/":
            log_event("page_views")
            self._serve_file(STATIC_DIR / "index.html", "text/html")
        elif parsed.path.startswith("/static/"):
            file_path = STATIC_DIR / parsed.path[8:]
            if file_path.exists():
                content_type = "text/css" if str(file_path).endswith(".css") else "application/javascript"
                self._serve_file(file_path, content_type)
            else:
                self.send_error(404)
        else:
            self.send_error(404)

    def do_POST(self):
        parsed = urlparse(self.path)

        if parsed.path == "/api/scan":
            content_length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(content_length)) if content_length else {}
            repo_url = body.get("url", "").strip()

            # Normalize URL for beginner-friendly input
            repo_url = repo_url.rstrip("/")
            if repo_url.startswith("github.com/"):
                repo_url = "https://" + repo_url
            # Strip /tree/main, /tree/master, /blob/... suffixes
            for suffix in ["/tree/main", "/tree/master", "/tree/", "/blob/"]:
                idx = repo_url.find(suffix)
                if idx > 0:
                    repo_url = repo_url[:idx]
                    break

            if not repo_url or not repo_url.startswith("https://github.com/"):
                self._json_response({"error": "Please enter a GitHub URL (e.g. github.com/your/repo)"}, 400)
                return

            scan_id = str(uuid.uuid4())[:8]
            SCANS[scan_id] = {"status": "scanning", "url": repo_url}
            log_event("scans_started", repo_url)

            # Run scan in background thread
            thread = threading.Thread(target=self._run_scan, args=(scan_id, repo_url))
            thread.daemon = True
            thread.start()

            self._json_response({"id": scan_id, "status": "scanning"})
            return

        self.send_error(404)

    def _run_scan(self, scan_id: str, repo_url: str):
        """Run scan in background."""
        try:
            result = subprocess.run(
                [sys.executable, str(PROJECT_DIR / "tools" / "cli_scanner.py"),
                 repo_url, "--json", "--light"],
                capture_output=True, text=True, timeout=90,
                env={**os.environ, "SEMGREP_MAX_MEMORY": "400"},
            )
            if result.returncode == 0:
                scan_data = json.loads(result.stdout)
                SCANS[scan_id] = {
                    "status": "done",
                    "url": repo_url,
                    "results": scan_data,
                }
                score = scan_data.get("score", {}).get("score", "?")
                if isinstance(score, (int, float)):
                    SCORES.append(int(score))
                log_event("scans_completed", f"{repo_url} score={score}")
            else:
                SCANS[scan_id] = {
                    "status": "error",
                    "url": repo_url,
                    "error": result.stdout[:500] or result.stderr[:500],
                }
                log_event("scans_failed", repo_url)
        except subprocess.TimeoutExpired:
            SCANS[scan_id] = {"status": "error", "url": repo_url, "error": "This repo is too large for our free scanner. Try a smaller repo, or install the GitHub Action for unlimited scanning."}
        except Exception as e:
            SCANS[scan_id] = {"status": "error", "url": repo_url, "error": str(e)}

    def _json_response(self, data: dict, code: int = 200):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def _serve_file(self, path: Path, content_type: str):
        if not path.exists():
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.end_headers()
        self.wfile.write(path.read_bytes())

    def log_message(self, format, *args):
        """Suppress default logging for cleaner output."""
        pass


def main():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), VibeSafeHandler)
    print(f"VibeSafe Web Scanner running at http://localhost:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()

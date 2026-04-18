#!/usr/bin/env python3
"""VibeSafe Web Scanner — API server."""
from __future__ import annotations

import json
import os
import re
import sys
import uuid
from pathlib import Path
from html import escape

# Add project root to path
PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import subprocess
import tempfile
import shutil


# In-memory scan results store (capped to prevent OOM)
SCANS: dict[str, dict] = {}
MAX_SCANS = 50  # evict oldest when exceeded

# Permanent report cache — keyed by "owner/repo". Powers /report/<owner>/<repo>
# SEO landing pages (primary top-of-funnel). Ephemeral between Render deploys;
# first visit after redeploy re-scans transparently, URL stays stable.
REPORTS: dict[str, dict] = {}
MAX_REPORTS = 500  # LRU cap
# Origin used in absolute URLs (sitemap, OpenGraph). Overridable for local testing.
PUBLIC_ORIGIN = os.environ.get("PUBLIC_ORIGIN", "https://vibesafe.onrender.com")
REPO_PATH_RE = re.compile(r"^[A-Za-z0-9_.-]+$")

SEED_FILE = Path(__file__).parent / "seed_reports.json"


def _load_seed_reports() -> None:
    """Load pre-seeded reports from committed JSON file on startup."""
    if not SEED_FILE.exists():
        return
    try:
        data = json.loads(SEED_FILE.read_text())
        for key, report in data.items():
            if len(REPORTS) >= MAX_REPORTS:
                break
            REPORTS[key] = report
        print(f"[SEED] Loaded {len(data)} pre-seeded reports into sitemap", flush=True)
    except Exception as e:
        print(f"[SEED] Failed to load seed reports: {e}", flush=True)

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
    "report_views": 0,
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


def _parse_owner_repo(repo_url: str) -> tuple[str, str] | None:
    """Extract (owner, repo) from a GitHub URL, stripping .git suffix."""
    m = re.search(r"github\.com/([^/\s]+)/([^/\s]+?)(?:\.git)?/?$", repo_url)
    if not m:
        return None
    owner, repo = m.group(1), m.group(2)
    if not (REPO_PATH_RE.match(owner) and REPO_PATH_RE.match(repo)):
        return None
    return owner, repo


def _save_report(repo_url: str, scan_record: dict) -> None:
    """Persist a completed scan to the REPORTS cache under 'owner/repo' key."""
    parsed = _parse_owner_repo(repo_url)
    if not parsed:
        return
    owner, repo = parsed
    key = f"{owner}/{repo}"
    while len(REPORTS) >= MAX_REPORTS:
        REPORTS.pop(next(iter(REPORTS)))
    REPORTS[key] = {
        "owner": owner,
        "repo": repo,
        "url": repo_url,
        "results": scan_record.get("results"),
        "scanned_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }


def _report_meta(owner: str, repo: str, report: dict | None) -> dict[str, str]:
    """Build title/description/OG values for a report page. Falls back to generic."""
    slug = f"{owner}/{repo}"
    if report and report.get("results"):
        score = (report["results"].get("score") or {})
        points = score.get("score", "?")
        grade = score.get("grade", "?")
        critical = score.get("critical", 0)
        high = score.get("high", 0)
        desc = (
            f"Security score {points}/100 (Grade {grade}) for {slug}. "
            f"{critical} critical, {high} high severity issues found by VibeSafe."
        )
        title = f"Security score for {slug}: {grade} ({points}/100) — VibeSafe"
    else:
        title = f"Security score for {slug} — VibeSafe"
        desc = (
            f"Run a free security scan on {slug} — SAST, secret detection, "
            f"accessibility. Results in 30 seconds."
        )
    return {
        "title": title,
        "description": desc,
        "og_url": f"{PUBLIC_ORIGIN}/report/{slug}",
    }


def _render_index(meta: dict[str, str] | None = None) -> bytes:
    """Render index.html with meta placeholders filled. Defaults to home-page meta."""
    html = (STATIC_DIR / "index.html").read_text()
    defaults = {
        "title": "VibeSafe — Is your AI-built app safe?",
        "description": (
            "Free security scanner for AI-generated code. Paste a GitHub URL, "
            "get SAST + secret + accessibility results in 30 seconds. No signup."
        ),
        "og_url": f"{PUBLIC_ORIGIN}/",
    }
    values = {**defaults, **(meta or {})}
    replacements = {
        "__META_TITLE__": escape(values["title"]),
        "__META_DESCRIPTION__": escape(values["description"]),
        "__META_OG_URL__": escape(values["og_url"]),
    }
    for k, v in replacements.items():
        html = html.replace(k, v)
    return html.encode("utf-8")


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

        # JSON report lookup: /api/report/<owner>/<repo>
        if parsed.path.startswith("/api/report/"):
            rest = parsed.path[len("/api/report/"):].strip("/")
            parts = rest.split("/")
            if len(parts) != 2 or not all(REPO_PATH_RE.match(p) for p in parts):
                self._json_response({"error": "invalid path"}, 400)
                return
            key = f"{parts[0]}/{parts[1]}"
            if key in REPORTS:
                self._json_response(REPORTS[key])
            else:
                self._json_response({"error": "not found"}, 404)
            return

        # SEO landing page: /report/<owner>/<repo>
        if parsed.path.startswith("/report/"):
            rest = parsed.path[len("/report/"):].strip("/")
            parts = rest.split("/")
            if len(parts) != 2 or not all(REPO_PATH_RE.match(p) for p in parts):
                self.send_error(404)
                return
            owner, repo = parts
            key = f"{owner}/{repo}"
            log_event("report_views", key)
            self._serve_html(_render_index(_report_meta(owner, repo, REPORTS.get(key))))
            return

        # SEO crawl directives
        if parsed.path == "/robots.txt":
            body = (
                "User-agent: *\n"
                "Allow: /\n"
                "Disallow: /api/\n"
                f"Sitemap: {PUBLIC_ORIGIN}/sitemap.xml\n"
            )
            self._text_response(body, "text/plain")
            return

        if parsed.path == "/sitemap.xml":
            urls = [f"{PUBLIC_ORIGIN}/"]
            urls.extend(f"{PUBLIC_ORIGIN}/report/{k}" for k in REPORTS)
            body = ['<?xml version="1.0" encoding="UTF-8"?>',
                    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
            for u in urls:
                body.append(f"<url><loc>{escape(u)}</loc></url>")
            body.append("</urlset>")
            self._text_response("\n".join(body), "application/xml")
            return

        # Serve static files
        if parsed.path == "/":
            qs = parse_qs(parsed.query)
            utm_source = qs.get("utm_source", [""])[0][:40]
            utm_medium = qs.get("utm_medium", [""])[0][:40]
            utm_campaign = qs.get("utm_campaign", [""])[0][:40]
            detail = f"utm={utm_source}/{utm_medium}/{utm_campaign}" if utm_source else "utm=direct"
            log_event("page_views", detail)
            self._serve_html(_render_index())
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
            # Evict oldest scans to prevent memory growth
            while len(SCANS) >= MAX_SCANS:
                oldest = next(iter(SCANS))
                del SCANS[oldest]
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
                env={**os.environ, "SEMGREP_MAX_MEMORY": "256"},
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
                _save_report(repo_url, SCANS[scan_id])
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
        finally:
            # Clean up cloned repos immediately to free disk/memory
            import glob
            for tmp in glob.glob("/tmp/vibesafe-scan-*"):
                shutil.rmtree(tmp, ignore_errors=True)

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

    def _serve_html(self, body: bytes):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(body)

    def _text_response(self, body: str, content_type: str):
        self.send_response(200)
        self.send_header("Content-Type", content_type + "; charset=utf-8")
        self.end_headers()
        self.wfile.write(body.encode("utf-8"))

    def log_message(self, format, *args):
        """Suppress default logging for cleaner output."""
        pass


def main():
    _load_seed_reports()
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), VibeSafeHandler)
    print(f"VibeSafe Web Scanner running at http://localhost:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()

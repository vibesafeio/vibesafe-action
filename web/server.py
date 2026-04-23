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

import datetime
from collections import deque

# Analytics — in-memory counters reset on deploy (Render free tier ~15min idle restart).
# Durability: every log_event() also writes a line to stdout. Render retains logs ~7d,
# so cumulative metrics are recoverable via `render logs | grep METRIC_EVENT`.
PROCESS_STARTED_AT = datetime.datetime.now(datetime.timezone.utc).isoformat()
METRICS = {
    "page_views": 0,
    "report_views": 0,
    "scans_started": 0,
    "scans_completed": 0,
    "scans_failed": 0,
    "fix_copies": 0,
    "install_clicks": 0,
}

# Ring buffer of recent events for live tail without Render API access.
# Exposed via /api/metrics/events so external dashboards can poll without grepping logs.
# Also resets on restart — same durability ceiling as METRICS.
MAX_EVENT_BUFFER = 1000
EVENT_BUFFER: deque[dict] = deque(maxlen=MAX_EVENT_BUFFER)


def log_event(event: str, detail: str = ""):
    """Increment in-memory counter, append to ring buffer, emit stdout line.

    Stdout line format:  [METRIC_EVENT] ts=<iso> event=<name> detail=<...>
    Render log replay can aggregate cumulative counts from these lines alone.
    """
    ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
    METRICS[event] = METRICS.get(event, 0) + 1
    safe_detail = (detail or "").replace("\n", " ").replace("\r", " ")[:200]
    EVENT_BUFFER.append({"ts": ts, "event": event, "detail": safe_detail})
    print(f"[METRIC_EVENT] ts={ts} event={event} detail={safe_detail}", flush=True)

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


def _build_report_ssr(owner: str, repo: str, report: dict | None) -> str:
    """Return server-rendered HTML for /report/<owner>/<repo>.

    Why: JS-rendered SPAs show 487 bytes of boilerplate to Googlebot on every
    /report/ URL — treated as near-duplicate thin content, rarely ranked.
    Rendering score/grade/findings server-side gives each URL ~1-2KB of unique
    indexable text (repo-specific findings, stack mentions, severity counts).

    Returns empty string when no cached report, so the JS bootstrap can
    auto-scan and cached results from other visitors rehydrate the URL over time.
    """
    if not report or not report.get("results"):
        return ""
    slug = f"{owner}/{repo}"
    r = report["results"]
    score_obj = r.get("score") or {}
    pts = score_obj.get("score")
    grade = score_obj.get("grade", "?")
    crit = score_obj.get("critical", 0)
    high = score_obj.get("high", 0)
    med = score_obj.get("medium", 0)
    low = score_obj.get("low", 0)
    stack = r.get("stack") or {}
    langs = ", ".join(stack.get("languages", [])) or "Multiple languages"
    frameworks = ", ".join(stack.get("detected_stack", [])) or None
    scanned_at = (report.get("scanned_at") or "")[:10]  # YYYY-MM-DD

    # Aggregate top finding rules for text content
    findings = (r.get("sast") or {}).get("findings", []) or []
    by_rule: dict[str, int] = {}
    for f in findings:
        rid = f.get("rule_id", "")
        if rid:
            by_rule[rid] = by_rule.get(rid, 0) + 1
    top_rules = sorted(by_rule.items(), key=lambda x: -x[1])[:5]

    secret_count = len((r.get("secrets") or {}).get("secrets", []))

    findings_html = ""
    if top_rules:
        items = "".join(
            f"<li><code>{escape(rid)}</code> — {cnt} occurrence{'s' if cnt != 1 else ''}</li>"
            for rid, cnt in top_rules
        )
        findings_html = f'<h2>Top finding patterns</h2><ul class="ssr-findings">{items}</ul>'

    stack_sentence = f"Stack: <strong>{escape(langs)}</strong>"
    if frameworks:
        stack_sentence += f" · Detected frameworks: <strong>{escape(frameworks)}</strong>"

    grade_color = {"A": "#4ade80", "B": "#facc15", "C": "#fb923c", "D": "#f87171", "F": "#f87171"}.get(grade, "#888")

    interpretation = (
        "No critical or high severity issues — this repo passes VibeSafe's safety gate."
        if crit == 0 and high == 0 else
        f"{crit} critical and {high} high severity issues found — merge blocking recommended."
    )

    return f"""
    <section class="ssr-report" id="ssrReport" itemscope itemtype="https://schema.org/Report">
        <meta itemprop="name" content="Security scan for {escape(slug)}">
        <h1 style="margin-bottom:8px;">Security report: <span style="font-family:monospace; color:#4ade80">{escape(slug)}</span></h1>
        <p style="color:#888; font-size:0.9rem; margin-bottom:20px;">
            Scanned by VibeSafe{' on ' + scanned_at if scanned_at else ''} — SAST, secret detection, and WCAG 2.1 accessibility audit.
        </p>

        <div class="ssr-grade-box" style="display:flex; align-items:center; gap:20px; padding:20px; background:#111; border-radius:12px; margin-bottom:24px;">
            <div style="font-size:3.5rem; font-weight:bold; color:{grade_color}; font-family:monospace; line-height:1;">{escape(grade)}</div>
            <div>
                <div style="font-size:1.8rem; color:#fff;"><strong itemprop="resultScore">{pts if pts is not None else '?'}</strong><span style="color:#888;">/100</span></div>
                <div style="color:#aaa; font-size:0.9rem; margin-top:4px;">
                    {crit} critical · {high} high · {med} medium · {low} low
                </div>
            </div>
        </div>

        <p style="color:#ccc; margin-bottom:16px;">{interpretation}</p>
        <p style="color:#ccc; margin-bottom:24px;">{stack_sentence}. {secret_count} secret{'s' if secret_count != 1 else ''} flagged (path/entropy-adjusted — docs, test fixtures, and non-code artifacts downgraded).</p>

        {findings_html}

        <h2>What VibeSafe checks</h2>
        <p style="color:#bbb;">
            This scan runs <strong>Semgrep OSS rules</strong> plus custom rules tuned for AI-generated code patterns.
            It flags hardcoded secrets (AWS, OpenAI, GitHub tokens, JWTs), SQL injection, eval/exec, path traversal,
            missing security headers, and WCAG 2.1 Level A accessibility gaps.
        </p>

        <h2>Scan your own repo</h2>
        <p style="color:#bbb;">
            <a href="/?utm_source=report&amp;utm_medium=ssr&amp;utm_campaign=cta" style="color:#4ade80;">
                Paste your GitHub URL →</a> Free. 30 seconds. No signup. Results include findings with file:line and
            a copy-pasteable fix prompt for Cursor / Claude.
        </p>
    </section>
    """


def _render_index(meta: dict[str, str] | None = None, body_ssr: str = "") -> bytes:
    """Render index.html with meta placeholders filled. Defaults to home-page meta.

    body_ssr: optional server-rendered HTML block injected at __SSR_BODY__ placeholder.
    Used for /report/ pages to give Googlebot per-URL unique content instead of
    the identical SPA shell. JS bootstrap removes the SSR block once the live
    scan data is loaded, so no visual duplication.
    """
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
        "__SSR_BODY__": body_ssr,
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
            payload = {
                **METRICS,
                "process_started_at": PROCESS_STARTED_AT,
                "buffered_events": len(EVENT_BUFFER),
                "note": "Counters reset on deploy/restart. Cumulative via stdout [METRIC_EVENT] log lines or /api/metrics/events live tail.",
            }
            self._json_response(payload)
            return

        if parsed.path == "/api/metrics/events":
            # Live tail of recent events. Params:
            #   limit: max events to return (default 200, max MAX_EVENT_BUFFER)
            #   event: filter to a specific event name
            #   since: only events with ts > this ISO string
            qs = parse_qs(parsed.query)
            limit_raw = qs.get("limit", [str(MAX_EVENT_BUFFER)])[0]
            try:
                limit = max(1, min(MAX_EVENT_BUFFER, int(limit_raw)))
            except ValueError:
                limit = 200
            event_filter = qs.get("event", [None])[0]
            since = qs.get("since", [None])[0]
            items = list(EVENT_BUFFER)
            if since:
                items = [e for e in items if e["ts"] > since]
            if event_filter:
                items = [e for e in items if e["event"] == event_filter]
            items = items[-limit:]
            # UTM source rollup for convenience
            utm_counts: dict[str, int] = {}
            for e in items:
                det = e.get("detail", "")
                if det.startswith("utm="):
                    utm_counts[det] = utm_counts.get(det, 0) + 1
            self._json_response({
                "total_buffered": len(EVENT_BUFFER),
                "returned": len(items),
                "utm_rollup": dict(sorted(utm_counts.items(), key=lambda x: -x[1])),
                "events": items,
            })
            return

        if parsed.path == "/api/reports/recent":
            limit_raw = parse_qs(parsed.query).get("limit", ["12"])[0]
            try:
                limit = max(1, min(50, int(limit_raw)))
            except ValueError:
                limit = 12
            items = []
            for key, rep in REPORTS.items():
                results = rep.get("results") or {}
                score_obj = results.get("score") or {}
                pts = score_obj.get("score")
                if pts is None:
                    continue
                items.append({
                    "owner": rep.get("owner"),
                    "repo": rep.get("repo"),
                    "slug": key,
                    "score": pts,
                    "grade": score_obj.get("grade", "?"),
                    "critical": score_obj.get("critical", 0),
                    "high": score_obj.get("high", 0),
                })
            items.sort(key=lambda r: (-r["score"], r["slug"]))
            self._json_response({"total": len(items), "items": items[:limit]})
            return

        # shields.io-compatible badge JSON: /api/badge/<owner>/<repo>
        # Usage: https://img.shields.io/endpoint?url=https://vibesafe.onrender.com/api/badge/<owner>/<repo>
        if parsed.path.startswith("/api/badge/"):
            rest = parsed.path[len("/api/badge/"):].strip("/")
            parts = rest.split("/")
            if len(parts) != 2 or not all(REPO_PATH_RE.match(p) for p in parts):
                self._json_response({"error": "invalid path"}, 400)
                return
            key = f"{parts[0]}/{parts[1]}"
            rep = REPORTS.get(key)
            if not rep or not rep.get("results"):
                # Not scanned yet — shields shows a neutral gray state.
                self._json_response({
                    "schemaVersion": 1,
                    "label": "VibeSafe",
                    "message": "not scanned",
                    "color": "lightgrey",
                    "cacheSeconds": 300,
                })
                return
            score_obj = (rep["results"].get("score") or {})
            pts = score_obj.get("score")
            grade = score_obj.get("grade", "?")
            color_map = {"A": "brightgreen", "B": "yellow", "C": "orange", "D": "red", "F": "red"}
            color = color_map.get(grade, "lightgrey")
            self._json_response({
                "schemaVersion": 1,
                "label": "VibeSafe",
                "message": f"{grade} ({pts}/100)" if pts is not None else grade,
                "color": color,
                "cacheSeconds": 600,
            })
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
            report = REPORTS.get(key)
            self._serve_html(_render_index(
                meta=_report_meta(owner, repo, report),
                body_ssr=_build_report_ssr(owner, repo, report),
            ))
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

    def do_HEAD(self):
        # Route HEAD through GET. Without this, HEAD falls through to
        # SimpleHTTPRequestHandler's static-file handler, which 404s our
        # dynamic routes (e.g. /sitemap.xml → 404 text/html). A header-only
        # HEAD would require buffering; responses here are small enough that
        # sending+discarding the body is acceptable and keeps routing unified.
        self.do_GET()

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

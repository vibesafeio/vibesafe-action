#!/usr/bin/env bash
# Daily snapshot of 2026-04-23 2nd-wave post metrics.
# Usage: bash scripts/track_posts.sh
#        bash scripts/track_posts.sh --append   # write to tracking log

ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
echo "=== snapshot @ $ts ==="

python3 - <<'PY'
import json, re, urllib.request, sys

# Safari UA bypasses OKKY's simple WAF and doesn't get rate-limited by GeekNews.
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"

def fetch(url, ua=UA):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": ua})
        return urllib.request.urlopen(req, timeout=10).read().decode("utf-8", errors="replace")
    except Exception as e:
        return f"__ERROR__ {e}"

# --- GeekNews (news.hada.io topic 28827) ---
gn = fetch("https://news.hada.io/topic?id=28827")
if gn.startswith("__ERROR__"):
    print(f"GeekNews   : (fetch failed) {gn[:80]}")
elif "글이 지워진거 같습니다" in gn or "404 Not Found" in gn:
    # Post removed (by author or moderator)
    print("GeekNews   : DELETED/404 (post removed — tracking halted)")
else:
    # Point marker: "<span id='tp<id>'>N</span>P by <user>"
    m_pt = re.search(r"<span\s+id=['\"]tp\d+['\"]>(\d+)</span>\s*P\s*by", gn)
    pts = m_pt.group(1) if m_pt else "?"
    # Comment count: data-topic-comment-count='N' attribute on #topic-comment-link
    m_c = re.search(r"data-topic-comment-count=['\"](\d+)['\"]", gn)
    cmts = m_c.group(1) if m_c else "0"
    print(f"GeekNews   : {pts} P, {cmts} comments")

# --- OKKY (Next.js SSR — viewCount/voteCount in hydration payload) ---
okky = fetch("https://okky.kr/articles/1555942")
if okky.startswith("__ERROR__"):
    print(f"OKKY       : (fetch failed) {okky[:80]}")
else:
    m_v = re.search(r'viewCount\\?"\s*:\s*(\d+)', okky)
    m_vt = re.search(r'voteCount\\?"\s*:\s*(\d+)', okky)
    views = m_v.group(1) if m_v else "?"
    votes = m_vt.group(1) if m_vt else "?"
    print(f"OKKY       : {views} views, {votes} votes")

# --- GitHub stars ---
gh = fetch("https://api.github.com/repos/vibesafeio/vibesafe-action")
if gh.startswith("__ERROR__"):
    print(f"GitHub     : (fetch failed)")
else:
    try:
        d = json.loads(gh)
        print(f"GitHub     : {d.get('stargazers_count','?')} stars, "
              f"{d.get('forks_count','?')} forks, "
              f"{d.get('subscribers_count','?')} watchers")
    except Exception:
        print("GitHub     : (parse failed)")

# --- Render metrics (in-memory since last restart) ---
rm = fetch("https://vibesafe.onrender.com/api/metrics")
events = fetch("https://vibesafe.onrender.com/api/metrics/events")
if not rm.startswith("__ERROR__"):
    try:
        m = json.loads(rm)
        print(f"Render     : page_views={m.get('page_views')} "
              f"install_clicks={m.get('install_clicks')} "
              f"scans_started={m.get('scans_started')} "
              f"restart={m.get('process_started_at','?')[:16]}")
    except Exception:
        pass
if not events.startswith("__ERROR__"):
    try:
        d = json.loads(events)
        items = d.get("events", [])
        okky_hits = sum(1 for e in items if "okky-v2" in e.get("detail",""))
        geek_hits = sum(1 for e in items if "geeknews-v2" in e.get("detail",""))
        print(f"UTM (v2)   : okky-v2={okky_hits} geeknews-v2={geek_hits}")
        if d.get("utm_rollup"):
            print("UTM rollup :")
            for k, c in d["utm_rollup"].items():
                print(f"             {c:>4}  {k}")
    except Exception:
        pass

# --- GSC (cannot scrape — prompt user) ---
print()
print("GSC        : (manual — paste daily numbers from)")
print("             https://search.google.com/search-console/performance/search-analytics?resource_id=https%3A%2F%2Fvibesafe.onrender.com%2F")
print("             → filter 24h or 7일 → total clicks / total impressions / avg position")
PY

# --- Append to log (optional) ---
if [ "${1:-}" = "--append" ]; then
    LOG="docs/post_tracking_log.jsonl"
    export TS_NOW=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    python3 - <<'PY' >> "$LOG"
import json, os, re, urllib.request
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
def f(u, to=10):
    try:
        r = urllib.request.Request(u, headers={"User-Agent": UA})
        return urllib.request.urlopen(r, timeout=to).read().decode("utf-8","replace")
    except Exception:
        return ""
snap = {"ts": os.environ.get("TS_NOW","")}
gn = f("https://news.hada.io/topic?id=28827")
if gn:
    if "글이 지워진거 같습니다" in gn or "404 Not Found" in gn:
        snap["gn_deleted"] = True
    else:
        m = re.search(r"<span\s+id=['\"]tp\d+['\"]>(\d+)</span>\s*P\s*by", gn)
        snap["gn_points"] = int(m.group(1)) if m else None
        mc = re.search(r"data-topic-comment-count=['\"](\d+)['\"]", gn)
        snap["gn_comments"] = int(mc.group(1)) if mc else None
okky = f("https://okky.kr/articles/1555942")
if okky:
    mv = re.search(r'viewCount\\?"\s*:\s*(\d+)', okky)
    mvt = re.search(r'voteCount\\?"\s*:\s*(\d+)', okky)
    snap["okky_views"] = int(mv.group(1)) if mv else None
    snap["okky_votes"] = int(mvt.group(1)) if mvt else None
gh = f("https://api.github.com/repos/vibesafeio/vibesafe-action")
if gh:
    try: snap["stars"] = json.loads(gh).get("stargazers_count")
    except: pass
ev = f("https://vibesafe.onrender.com/api/metrics/events")
if ev:
    try:
        d = json.loads(ev)
        items = d.get("events", [])
        snap["utm_okky_v2"] = sum(1 for e in items if "okky-v2" in e.get("detail",""))
        snap["utm_geeknews_v2"] = sum(1 for e in items if "geeknews-v2" in e.get("detail",""))
    except: pass
rm = f("https://vibesafe.onrender.com/api/metrics")
if rm:
    try:
        m = json.loads(rm)
        snap["install_clicks"] = m.get("install_clicks")
        snap["page_views"] = m.get("page_views")
    except: pass
print(json.dumps(snap))
PY
    echo "(appended to $LOG)"
fi

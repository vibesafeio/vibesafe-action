from __future__ import annotations

"""VibeSafe PR Comment — GitHub Actions 환경에서 PR에 스캔 결과를 코멘트한다."""

import json
import os
import sys
import urllib.request


SEVERITY_EMOJI = {
    "CRITICAL": "\U0001f534",
    "HIGH": "\U0001f7e0",
    "MEDIUM": "\U0001f7e1",
    "LOW": "\U0001f7e2",
    "INFO": "\u2139\ufe0f",
}
SEVERITY_ORDER = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}
SEVERITY_MAP = {"ERROR": "HIGH", "WARNING": "MEDIUM", "NOTE": "LOW", "NONE": "INFO"}
MAX_INLINE = 5     # Show top 5 inline, rest in collapsed details
MAX_FINDINGS = 20  # Absolute cap

# 룰 기반 수정 제안 매핑 (rule_id 부분 매칭 → 수정 가이드)
FIX_SUGGESTIONS: list[tuple[str, str]] = [
    # SQL Injection
    ("tainted-sql-string", "Use parameterized queries: `cursor.execute(\"SELECT ... WHERE id = ?\", (param,))`"),
    ("sql-injection", "Use parameterized queries instead of string concatenation/f-strings"),
    # Command Injection
    ("subprocess-injection", "Remove `shell=True` and use `shlex.split()`: `subprocess.run(shlex.split(cmd))`"),
    ("dangerous-subprocess", "Pass arguments as a list: `subprocess.run([\"cmd\", \"arg\"])` instead of `shell=True`"),
    ("subprocess-shell-true", "Replace `shell=True` with `subprocess.run([\"cmd\", \"arg\"])`"),
    # Code Injection
    ("eval-injection", "Replace `eval()` with `ast.literal_eval()` or a safe parser"),
    ("user-eval", "Replace `eval()` with `json.loads()` or `ast.literal_eval()`"),
    ("exec-injection", "Never pass user input to `exec()`. Use a safe alternative"),
    # Path Traversal
    ("path-traversal", "Normalize paths with `os.path.realpath()` and validate against an allowed directory"),
    # XSS
    ("xss", "Escape user input before rendering: use framework's built-in escaping (e.g., `markupsafe.escape()`)"),
    ("dangerously-set-inner-html", "Avoid `dangerouslySetInnerHTML`. Use a sanitizer like DOMPurify if HTML rendering is required"),
    ("v-html", "Avoid `v-html` with user input. Use text interpolation `{{ }}` instead"),
    # SSRF
    ("ssrf", "Validate and allowlist URLs before making requests. Block internal/private IP ranges"),
    # Debug/Config
    ("debug-enabled", "Remove `debug=True` in production: `debug=os.environ.get('FLASK_DEBUG', False)`"),
    ("app-run-param-config", "Don't bind to `0.0.0.0` — use env var for bind address in production"),
    # Secrets
    ("hardcoded_secret", "Remove secrets from code. Use environment variables (`os.environ.get()`) or a secret manager"),
    ("openai_key", "Store API key in `.env` or GitHub Secrets: `os.environ.get('OPENAI_API_KEY')`"),
    ("aws_key", "Use IAM roles or AWS Secrets Manager instead of hardcoded credentials"),
    ("github_token", "Use `${{ secrets.GITHUB_TOKEN }}` in workflows, never hardcode tokens"),
    ("stripe_key", "Store Stripe keys in environment variables, not in source code"),
    ("jwt_token", "Never hardcode JWT secrets. Use environment variables or a key management service"),
    # Config scanner findings
    ("supabase_no_rls", "Enable RLS: `ALTER TABLE your_table ENABLE ROW LEVEL SECURITY;` then add policies"),
    ("supabase_anon_key_no_rls", "Enable RLS on ALL tables. Anon key is public — RLS is the only protection"),
    ("supabase_no_migration", "Create SQL migrations with RLS policies, or verify in Supabase dashboard → Policies"),
    ("firebase_test_mode", "Replace `allow read, write: if true` with `allow read, write: if request.auth != null`"),
    ("firebase_public_read", "Restrict read: `allow read: if request.auth != null`"),
    ("unpinned_dependency", "Pin to specific version to prevent supply chain attacks"),
    # Crypto
    ("insecure-hash", "Replace MD5/SHA1 with SHA-256 or stronger: `hashlib.sha256()`"),
    ("weak-random", "Use `secrets.token_hex()` instead of `random` for security-sensitive values"),
    ("math-random", "Use `crypto.randomBytes()` or `crypto.getRandomValues()` instead of `Math.random()`"),
    # Deserialization
    ("insecure-deserialization", "Never deserialize untrusted data with `pickle`/`yaml.load()`. Use `json.loads()` or `yaml.safe_load()`"),
    ("pickle", "Replace `pickle.loads()` with `json.loads()` for untrusted data"),
    # JWT
    ("jwt-none-alg", "Always specify and validate the JWT algorithm. Reject `none` algorithm"),
    # Open Redirect
    ("open-redirect", "Validate redirect URLs against an allowlist. Don't redirect to user-supplied URLs"),
    # CORS
    ("cors-misconfiguration", "Don't use `Access-Control-Allow-Origin: *` in production. Specify allowed origins"),
]


def get_fix_suggestion(rule_id: str) -> str | None:
    """rule_id에 매칭되는 수정 제안을 반환한다."""
    rule_lower = rule_id.lower()
    for pattern, suggestion in FIX_SUGGESTIONS:
        if pattern in rule_lower:
            return suggestion
    return None

# Import shared constants (DRY — single source of truth)
try:
    from tools.shared import FRAMEWORK_CONFLICTS, NOISY_RULES
except ImportError:
    # Fallback for Docker where import path differs
    FRAMEWORK_CONFLICTS: dict[str, list[str]] = {
        "flask": ["python.django."], "django": ["python.flask."],
        "fastapi": ["python.django.", "python.flask."],
        "express": ["python.django.", "python.flask."],
        "nextjs": ["python.django.", "python.flask."],
        "react": ["python.django.", "python.flask."],
        "vue": ["python.django.", "python.flask."],
        "spring": ["python.flask.", "python.django."],
    }
    NOISY_RULES: list[str] = ["password-comparison-timing"]


def load_sarif_findings(sarif_path: str, detected_stack: list[str] | None = None) -> list[dict]:
    """SARIF 파일에서 개별 취약점 목록을 추출한다."""
    if not os.path.exists(sarif_path):
        return []
    with open(sarif_path) as f:
        data = json.load(f)

    # 프레임워크 충돌 필터: 감지된 스택 기반으로 제외할 rule prefix 목록
    exclude_prefixes: list[str] = []
    for framework in (detected_stack or []):
        exclude_prefixes.extend(FRAMEWORK_CONFLICTS.get(framework, []))

    findings: list[dict] = []
    for run in data.get("runs", []):
        # rule ID → severity, message 매핑
        rule_meta: dict[str, dict] = {}
        for rule in run.get("tool", {}).get("driver", {}).get("rules", []):
            level = rule.get("defaultConfiguration", {}).get("level", "").upper()
            # rule의 help/message 텍스트 (수정 가이드 포함)
            desc = (
                rule.get("help", {}).get("text", "")
                or rule.get("shortDescription", {}).get("text", "")
                or rule.get("fullDescription", {}).get("text", "")
            )
            rule_meta[rule["id"]] = {"level": level, "description": desc}

        for result in run.get("results", []):
            rule_id = result.get("ruleId", "unknown")

            # 프레임워크 충돌 오탐 필터링
            if any(rule_id.startswith(prefix) for prefix in exclude_prefixes):
                continue

            # Noisy rule 필터링 (고 오탐률 규칙 제거)
            if any(pattern in rule_id.lower() for pattern in NOISY_RULES):
                continue

            meta = rule_meta.get(rule_id, {})

            # severity 결정
            level = result.get("level", "").upper()
            if not level or level == "NONE":
                level = meta.get("level", "NOTE")
            severity = SEVERITY_MAP.get(level, level)
            if severity not in SEVERITY_ORDER:
                severity = "INFO"

            # 위치 정보
            locations = result.get("locations", [])
            if locations:
                phys = locations[0].get("physicalLocation", {})
                file_path = phys.get("artifactLocation", {}).get("uri", "")
                start_line = phys.get("region", {}).get("startLine", 0)
                snippet = phys.get("region", {}).get("snippet", {}).get("text", "").strip()
            else:
                file_path = ""
                start_line = 0
                snippet = ""

            # 메시지 (Semgrep message > rule description)
            message = result.get("message", {}).get("text", "") or meta.get("description", "")

            findings.append({
                "severity": severity,
                "rule_id": rule_id,
                "file": file_path,
                "line": start_line,
                "snippet": snippet,
                "message": message,
            })

    findings.sort(key=lambda f: (SEVERITY_ORDER.get(f["severity"], 99), f["file"], f["line"]))
    return findings


def load_secret_findings(secrets_path: str) -> list[dict]:
    """시크릿 스캔 결과를 findings 형식으로 변환한다."""
    if not os.path.exists(secrets_path):
        return []
    with open(secrets_path) as f:
        data = json.load(f)

    findings: list[dict] = []
    for s in data.get("secrets", []):
        findings.append({
            "severity": "CRITICAL",
            "rule_id": s.get("type", "hardcoded_secret"),
            "file": s.get("file", ""),
            "line": s.get("line", 0),
            "snippet": s.get("match", ""),
            "message": f"Hardcoded secret ({s.get('name', s.get('type', 'secret'))}) — move to environment variables or a secret manager",
        })
    return findings


def group_findings(findings: list[dict]) -> list[dict]:
    """같은 file:line의 findings를 그룹핑한다. 최고 severity 대표 1건 + related count."""
    groups: dict[str, list[dict]] = {}
    for f in findings:
        key = f"{f['file']}:{f['line']}" if f["file"] else f["rule_id"]
        groups.setdefault(key, []).append(f)

    grouped: list[dict] = []
    for _key, group in groups.items():
        # severity 순 정렬, 최고 severity가 대표
        group.sort(key=lambda x: SEVERITY_ORDER.get(x["severity"], 99))
        primary = dict(group[0])
        related = len(group) - 1
        if related > 0:
            primary["related_count"] = related
        grouped.append(primary)

    grouped.sort(key=lambda f: (SEVERITY_ORDER.get(f["severity"], 99), f["file"], f["line"]))
    return grouped


def format_findings_section(findings: list[dict]) -> str:
    """취약점 상세 목록을 마크다운으로 포맷한다. 같은 위치의 중복 탐지는 그룹핑."""
    if not findings:
        return ""

    grouped = group_findings(findings)
    total_grouped = len(grouped)
    shown = grouped[:MAX_FINDINGS]

    lines = ["", "### Findings", ""]

    def _format_one(f: dict) -> list[str]:
        """Format a single finding as markdown lines."""
        out: list[str] = []
        emoji = SEVERITY_EMOJI.get(f["severity"], "\u26aa")
        location = ""
        if f["file"]:
            location = f"  `{f['file']}"
            if f["line"]:
                location += f":{f['line']}"
            location += "`"

        related = f.get("related_count", 0)
        related_tag = f" (+{related} related)" if related > 0 else ""

        out.append(f"**{emoji} {f['severity']}** — `{f['rule_id']}`{location}{related_tag}")

        msg = f["message"].replace("\n", " ").strip()
        if len(msg) > 200:
            msg = msg[:197] + "..."
        if msg:
            out.append(f"> {msg}")
        return out

    # Show top MAX_INLINE findings inline
    inline = shown[:MAX_INLINE]
    rest = shown[MAX_INLINE:]

    for f in inline:
        lines.extend(_format_one(f))

        if f["snippet"]:
            snippet_line = f["snippet"].split("\n")[0][:120]
            lines.append(f"> ```\n> {snippet_line}\n> ```")

        fix = get_fix_suggestion(f["rule_id"])
        if fix:
            lines.append(f"> **Fix:** {fix}")

        lines.append("")

    # Collapse remaining findings
    if rest:
        lines.append(f"<details>")
        lines.append(f"<summary>+{len(rest)} more findings</summary>")
        lines.append("")
        for f in rest:
            lines.extend(_format_one(f))
            fix = get_fix_suggestion(f["rule_id"])
            if fix:
                lines.append(f"> **Fix:** {fix}")
            lines.append("")
        lines.append("</details>")
        lines.append("")

    omitted = total_grouped - len(shown)
    if omitted > 0:
        lines.append(f"<sub>+{omitted} more omitted</sub>")
        lines.append("")

    return "\n".join(lines)


def load_config_findings(config_path: str) -> list[dict]:
    """Load configuration scan findings (Supabase RLS, Firebase rules, etc.)."""
    if not os.path.exists(config_path):
        return []
    try:
        with open(config_path) as f:
            data = json.load(f)
        findings = []
        for item in data.get("findings", []):
            findings.append({
                "severity": item.get("severity", "HIGH"),
                "rule_id": item.get("type", "config_issue"),
                "file": item.get("file", ""),
                "line": item.get("line", 0),
                "snippet": "",
                "message": item.get("message", ""),
            })
        return findings
    except (json.JSONDecodeError, OSError):
        return []


def build_comment_body(score: dict, sarif_path: str = "/tmp/sast.sarif",
                       secrets_path: str = "/tmp/secrets.json",
                       stack_path: str = "/tmp/stack.json",
                       config_path: str = "/tmp/config.json") -> str:
    points = score["score"]
    grade = score["grade"]
    domain = score["domain"]
    certified = score.get("certified", False)
    block_reason = score.get("certified_block_reason") or ""

    # 스택 정보 로드 (프레임워크 충돌 필터링용)
    detected_stack: list[str] = []
    if os.path.exists(stack_path):
        try:
            with open(stack_path) as f:
                detected_stack = json.load(f).get("detected_stack", [])
        except (json.JSONDecodeError, OSError):
            pass

    # 필터링된 findings에서 실제 카운트 산출 (raw score.json 대신)
    all_findings = load_secret_findings(secrets_path) + load_sarif_findings(sarif_path, detected_stack) + load_config_findings(config_path)
    all_findings.sort(key=lambda f: (SEVERITY_ORDER.get(f["severity"], 99), f["file"], f["line"]))

    filtered_counts: dict[str, int] = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for finding in all_findings:
        sev = finding["severity"]
        if sev in filtered_counts:
            filtered_counts[sev] += 1
    critical = filtered_counts["CRITICAL"]
    high = filtered_counts["HIGH"]
    medium = filtered_counts["MEDIUM"]
    low = filtered_counts["LOW"]
    total = sum(filtered_counts.values())

    grade_emoji = {"A": "\U0001f7e2", "B": "\U0001f7e1", "C": "\U0001f7e0", "D": "\U0001f534", "F": "\U0001f534"}.get(grade, "\u26aa")
    cert_badge = " \u2705 **Certified**" if certified else ""
    cert_block = f"\n> Not certified: {block_reason}" if block_reason else ""
    grade_cap_note = ""
    if score.get("grade_capped"):
        grade_cap_note = "\n> Grade capped at **B** (1+ high severity blocks Grade A)"

    if critical > 0:
        summary = f"{critical} critical vulnerabilities found — fix immediately"
    elif high > 0:
        summary = f"{high} high vulnerabilities found — fix before merging"
    elif medium > 0:
        summary = f"{medium} medium vulnerabilities found"
    elif low > 0:
        summary = f"{low} low vulnerabilities"
    else:
        summary = "No vulnerabilities found"

    lines = [
        "## \U0001f510 VibeSafe Security Scan",
        "",
        f"{grade_emoji} **{points}/100** (Grade {grade}){cert_badge}",
        cert_block,
        grade_cap_note,
        "",
        f"> {summary}",
        "",
        "| Severity | Count |",
        "|----------|-------|",
        f"| \U0001f534 Critical | {critical} |",
        f"| \U0001f7e0 High     | {high} |",
        f"| \U0001f7e1 Medium   | {medium} |",
        f"| \U0001f7e2 Low      | {low} |",
        "",
        f"Domain: `{domain}` · {total} total",
    ]
    details = format_findings_section(all_findings)
    if details:
        lines.append(details)

    # Fix prompt for AI assistants (only when findings exist)
    if all_findings:
        fix_items = []
        grouped = group_findings(all_findings)
        for f in grouped[:10]:
            loc = f"{f['file']}:{f['line']}" if f.get("file") else ""
            fix = get_fix_suggestion(f["rule_id"]) or ""
            fix_items.append(f"- {f['severity']}: {loc} — {fix}" if fix else f"- {f['severity']}: {loc}")

        lines.extend([
            "",
            "<details>",
            "<summary>🤖 <b>Fix with AI — copy this prompt into Cursor/Claude</b></summary>",
            "",
            "```",
            "Fix these security issues in my code:",
            "",
        ])
        lines.extend(fix_items)
        lines.extend([
            "",
            "Move all hardcoded secrets to environment variables.",
            "Use parameterized queries for SQL. Never use eval() with user input.",
            "Generate a .env.example with placeholder values.",
            "```",
            "",
            "</details>",
        ])

    lines.extend([
        "",
        "<sub>Powered by [VibeSafe](https://vibesafe.dev)</sub>",
    ])
    return "\n".join(lines)


MARKER = "VibeSafe Security Scan"  # Also matches old Korean marker for backward compat


def _comment_has_marker(body: str) -> bool:
    """Check if a comment body contains the VibeSafe marker (new English or old Korean)."""
    return MARKER in body or "VibeSafe \ubcf4\uc548 \uc2a4\uce94 \uacb0\uacfc" in body


def github_api(method: str, url: str, token: str, data: dict | None = None) -> dict:
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(
        url,
        data=body,
        method=method,
        headers={
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def post_or_update_comment(token: str, repo: str, pr_number: int, body: str) -> None:
    api = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"

    comments = github_api("GET", api, token)
    existing = None
    for c in comments:
        if c.get("user", {}).get("login") == "github-actions[bot]" and _comment_has_marker(c.get("body", "")):
            existing = c
            break

    if existing:
        github_api("PATCH", existing["url"], token, {"body": body})
        print(f"Updated existing comment #{existing['id']}")
    else:
        result = github_api("POST", api, token, {"body": body})
        print(f"Created comment #{result['id']}")


def main() -> None:
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        print("No GitHub token provided, skipping PR comment.")
        return

    event_path = os.environ.get("GITHUB_EVENT_PATH", "")
    if not event_path or not os.path.exists(event_path):
        print("Not running in GitHub Actions, skipping PR comment.")
        return

    with open(event_path) as f:
        event = json.load(f)

    pr_number = event.get("pull_request", {}).get("number")
    if not pr_number:
        print("Not a pull_request event, skipping PR comment.")
        return

    repo = os.environ.get("GITHUB_REPOSITORY", "")
    if not repo:
        print("GITHUB_REPOSITORY not set, skipping PR comment.")
        return

    score_path = sys.argv[1] if len(sys.argv) > 1 else "/tmp/score.json"
    with open(score_path) as f:
        score = json.load(f)

    sarif_path = os.environ.get("VIBESAFE_SARIF", "/tmp/sast.sarif")
    secrets_path = os.environ.get("VIBESAFE_SECRETS", "/tmp/secrets.json")
    body = build_comment_body(score, sarif_path, secrets_path)
    post_or_update_comment(token, repo, pr_number, body)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
tools/scanner/secret_scanner.py
하드코딩된 API 키, 비밀번호, 토큰, 인증 정보를 탐지한다.
정규식 기반 1차 탐지 + 엔트로피 분석 2차 검증으로 오탐을 줄인다.
"""
from __future__ import annotations
import argparse
import base64
import json
import math
import re
import sys
from pathlib import Path

# ─── 시크릿 패턴 정의 ────────────────────────────────────
SECRET_PATTERNS = [
    {"id": "aws_access_key",      "name": "AWS Access Key ID",        "pattern": r"(?i)AKIA[0-9A-Z]{16}"},
    {"id": "aws_secret_key",      "name": "AWS Secret Access Key",    "pattern": r"(?i)aws[_\-\s]?secret[_\-\s]?access[_\-\s]?key\s*[=:]\s*['\"]?([A-Za-z0-9+/]{40})['\"]?"},
    {"id": "github_token",        "name": "GitHub Personal Access Token", "pattern": r"ghp_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{82}"},
    {"id": "openai_key",          "name": "OpenAI API Key",           "pattern": r"sk-(?:proj-)?[A-Za-z0-9\-_]{20,}"},
    {"id": "stripe_secret",       "name": "Stripe Secret Key",        "pattern": r"sk_live_[A-Za-z0-9]{24,}"},
    {"id": "stripe_publishable",  "name": "Stripe Publishable Key",   "pattern": r"pk_live_[A-Za-z0-9]{24,}"},
    {"id": "google_api_key",      "name": "Google API Key",           "pattern": r"AIza[0-9A-Za-z\-_]{35}"},
    {"id": "slack_token",         "name": "Slack Bot Token",          "pattern": r"xoxb-[0-9]{11,13}-[0-9]{11,13}-[A-Za-z0-9]{24}"},
    {"id": "slack_webhook",       "name": "Slack Webhook URL",        "pattern": r"https://hooks\.slack\.com/services/T[A-Z0-9]+/B[A-Z0-9]+/[A-Za-z0-9]+"},
    {"id": "jwt_token",           "name": "JWT Token",                "pattern": r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"},
    {"id": "private_key_pem",     "name": "Private Key (PEM)",        "pattern": r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----"},
    {"id": "generic_password",    "name": "Hardcoded Password",       "pattern": r"(?i)(password|passwd|pwd|secret)\s*[=:]\s*['\"]([^'\"]{8,})['\"]"},
    {"id": "generic_api_key",     "name": "Generic API Key",          "pattern": r"(?i)(api[_\-]?key|apikey)\s*[=:]\s*['\"]([A-Za-z0-9\-_]{16,})['\"]"},
    {"id": "db_url",              "name": "Database Connection String","pattern": r"(?i)(postgres|mysql|mongodb|redis)://[^:]+:[^@]+@"},
    {"id": "supabase_key",        "name": "Supabase Key",             "pattern": r"eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+"},  # Supabase anon/service keys are JWTs
]

SKIP_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".woff", ".woff2",
                   ".ttf", ".eot", ".pdf", ".zip", ".tar", ".gz", ".lock"}
SKIP_DIRS = {"node_modules", ".git", ".venv", "venv", "dist", "build", "__pycache__", ".next"}

# 저엔트로피 예시 값 (오탐 제거)
PLACEHOLDER_PATTERNS = re.compile(
    r"(?i)(your[_-]?api[_-]?key|example|placeholder|changeme|<[^>]+>|\$\{[^}]+\}|xxx+|test|demo|dummy|sample)"
)


def shannon_entropy(data: str) -> float:
    """Shannon 엔트로피 계산 — 높을수록 실제 시크릿일 가능성 높음."""
    if not data:
        return 0.0
    freq = {}
    for c in data:
        freq[c] = freq.get(c, 0) + 1
    total = len(data)
    return -sum((count / total) * math.log2(count / total) for count in freq.values())


def is_likely_real_secret(value: str) -> bool:
    """엔트로피와 패턴으로 실제 시크릿인지 판단한다."""
    if PLACEHOLDER_PATTERNS.search(value):
        return False
    if len(value) < 8:
        return False
    if shannon_entropy(value) < 3.0:  # 엔트로피 낮음 = 의미 있는 단어 = 오탐 가능
        return False
    return True


def scan_file(file_path: Path) -> list[dict]:
    """단일 파일에서 시크릿 패턴을 스캔한다."""
    findings = []
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return findings

    for line_num, line in enumerate(content.splitlines(), start=1):
        for pattern_def in SECRET_PATTERNS:
            matches = re.finditer(pattern_def["pattern"], line)
            for match in matches:
                # 매칭된 값 추출 (그룹이 있으면 그룹 1 사용)
                matched_value = match.group(1) if match.lastindex and match.lastindex >= 1 else match.group(0)

                if not is_likely_real_secret(matched_value):
                    continue

                # 마스킹 처리 (앞 4자리만 표시)
                masked = matched_value[:4] + "*" * min(len(matched_value) - 4, 20)

                findings.append({
                    "type": pattern_def["id"],
                    "name": pattern_def["name"],
                    "file": str(file_path),
                    "line": line_num,
                    "masked_value": masked,
                    "entropy": round(shannon_entropy(matched_value), 2),
                    "severity": "critical",
                    "remediation": f"Revoke this {pattern_def['name']} immediately and move it to environment variables (.env) or a secret manager.",
                })

    return findings


def scan_text(text: str) -> list[dict]:
    """문자열에서 시크릿 패턴을 스캔한다. MCP 서버 및 pre-commit에서 사용."""
    findings = []
    for line_num, line in enumerate(text.splitlines(), start=1):
        for pattern_def in SECRET_PATTERNS:
            matches = re.finditer(pattern_def["pattern"], line)
            for match in matches:
                matched_value = match.group(1) if match.lastindex and match.lastindex >= 1 else match.group(0)
                if not is_likely_real_secret(matched_value):
                    continue
                masked = matched_value[:4] + "*" * min(len(matched_value) - 4, 20)
                findings.append({
                    "type": pattern_def["id"],
                    "name": pattern_def["name"],
                    "line": line_num,
                    "masked_value": masked,
                    "entropy": round(shannon_entropy(matched_value), 2),
                    "severity": "critical",
                })
    return findings


def scan_directory(source_path: Path) -> list[dict]:
    all_findings = []

    for file_path in source_path.rglob("*"):
        if file_path.is_file():
            # 건너뛸 디렉토리 확인
            if any(skip_dir in file_path.parts for skip_dir in SKIP_DIRS):
                continue
            # 건너뛸 확장자 확인
            if file_path.suffix.lower() in SKIP_EXTENSIONS:
                continue
            # .env 파일 자체는 스캔에서 제외 (실제 비밀이 있어야 하는 곳이므로)
            if file_path.name in (".env", ".env.local", ".env.production"):
                continue

            findings = scan_file(file_path)
            all_findings.extend(findings)

    return all_findings


def main():
    parser = argparse.ArgumentParser(description="VibeSafe 시크릿 스캐너")
    parser.add_argument("--path", required=True, help="스캔 대상 경로")
    parser.add_argument("--output", default=None, help="결과 JSON 파일 저장 경로")
    args = parser.parse_args()

    source_path = Path(args.path)
    if not source_path.exists():
        print(json.dumps({"error": f"경로를 찾을 수 없습니다: {args.path}"}))
        sys.exit(1)

    findings = scan_directory(source_path)

    # 유형별 요약
    type_counts = {}
    for f in findings:
        type_counts[f["type"]] = type_counts.get(f["type"], 0) + 1

    result = {
        "status": "ok",
        "total_secrets": len(findings),
        "by_type": type_counts,
        "secrets": findings,
    }

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2))

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
from __future__ import annotations
"""
tools/report/score_calculator.py
SAST, SCA, 시크릿 스캔 결과를 종합하여 보안 점수(0-100)를 산출한다.
도메인 가중치를 적용하여 규제 위험도를 반영한다.
"""

import argparse
import json
from pathlib import Path

# ─── 도메인별 취약점 유형 가중치 ─────────────────────────
DOMAIN_WEIGHTS = {
    "ecommerce": {
        "sql_injection": 2.0, "xss": 1.5, "hardcoded_secret": 2.0,
        "missing_encryption": 1.5, "idor": 2.0, "ssrf": 1.0,
    },
    "game": {
        "sql_injection": 1.5, "xss": 1.8, "hardcoded_secret": 1.5,
        "missing_encryption": 1.0, "idor": 1.2, "ssrf": 1.0,
    },
    "platform": {
        "sql_injection": 1.5, "xss": 1.5, "hardcoded_secret": 2.0,
        "missing_encryption": 1.5, "idor": 2.5, "ssrf": 2.0,
    },
    "healthcare": {
        "sql_injection": 2.0, "xss": 1.2, "hardcoded_secret": 2.5,
        "missing_encryption": 3.0, "idor": 2.5, "ssrf": 1.5,
    },
    "fintech": {
        "sql_injection": 2.5, "xss": 1.5, "hardcoded_secret": 3.0,
        "missing_encryption": 2.5, "idor": 2.0, "ssrf": 1.5,
    },
    "education": {
        "sql_injection": 1.5, "xss": 1.5, "hardcoded_secret": 1.5,
        "missing_encryption": 1.5, "idor": 1.5, "ssrf": 1.0,
    },
}

try:
    from tools.shared import FRAMEWORK_CONFLICTS, NOISY_RULES
except ImportError:
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

# 기본 CVSS 점수 (심각도 → 점수)
BASE_CVSS = {"critical": 9.5, "high": 7.5, "medium": 5.0, "low": 2.0, "info": 0.0}

# 점수 감점 (CRITICAL 취약점 1개당 최대 감점)
PENALTY = {"critical": 20, "high": 10, "medium": 4, "low": 1, "info": 0}


def get_domain_weight(vuln_type: str, domain: str) -> float:
    """도메인과 취약점 유형에 따른 가중치를 반환한다."""
    weights = DOMAIN_WEIGHTS.get(domain, {})
    # 부분 매칭 (예: "sql_injection" 패턴이 "dast_sql_injection" 에서도 매칭)
    for key, weight in weights.items():
        if key in vuln_type.lower():
            return weight
    return 1.0


def parse_sarif_vulnerabilities(sarif_file: Path, detected_stack: list[str] | None = None) -> list[dict]:
    """SARIF 파일에서 취약점 목록을 추출한다. 프레임워크 충돌 오탐을 필터링."""
    if not sarif_file.exists():
        return []

    # 프레임워크 충돌 필터
    exclude_prefixes: list[str] = []
    for framework in (detected_stack or []):
        exclude_prefixes.extend(FRAMEWORK_CONFLICTS.get(framework, []))

    data = json.loads(sarif_file.read_text())
    vulns = []
    level_map = {"error": "high", "warning": "medium", "note": "low", "none": "info"}

    for run in data.get("runs", []):
        # 규칙 메타데이터 인덱싱
        rules = {r.get("id", ""): r for r in run.get("tool", {}).get("driver", {}).get("rules", [])}

        for result in run.get("results", []):
            rule_id = result.get("ruleId", "")

            # 프레임워크 충돌 오탐 필터링
            if any(rule_id.startswith(prefix) for prefix in exclude_prefixes):
                continue

            # Noisy rule 필터링 (고 오탐률 규칙 제거)
            if any(pattern in rule_id.lower() for pattern in NOISY_RULES):
                continue

            # result.level이 없으면 rule의 defaultConfiguration.level로 fallback
            level = result.get("level")
            if not level:
                level = (
                    rules.get(rule_id, {})
                    .get("defaultConfiguration", {})
                    .get("level", "note")
                )
            level = (level or "note").lower()
            severity = level_map.get(level, "info")

            # 규칙 기반 분류 시도
            vuln_type = "unknown"
            for known_type in ["sql_injection", "xss", "ssrf", "idor", "hardcoded_secret", "missing_encryption"]:
                if known_type.replace("_", "") in rule_id.lower().replace("_", ""):
                    vuln_type = known_type
                    break

            vulns.append({
                "type": vuln_type,
                "severity": severity,
                "rule_id": rule_id,
                "source": "sast",
            })

    return vulns


def calculate_score(
    sast_result_file: Path | None,
    sca_result_file: Path | None,
    secret_result_file: Path | None,
    domain: str,
    triage_mode: bool = False,
    raw_input: list[dict] | None = None,
    detected_stack: list[str] | None = None,
    verbose: bool = False,
) -> dict:
    """모든 스캔 결과를 종합하여 최종 보안 점수를 산출한다."""

    all_vulns = []
    deductions: list[dict] = []

    if raw_input:
        all_vulns = raw_input
    else:
        # SAST 결과
        if sast_result_file and sast_result_file.exists():
            all_vulns.extend(parse_sarif_vulnerabilities(sast_result_file, detected_stack))

        # SCA 결과
        if sca_result_file and sca_result_file.exists():
            sca_data = json.loads(sca_result_file.read_text())
            for vuln in sca_data.get("vulnerabilities", []):
                all_vulns.append({
                    "type": "dependency_vulnerability",
                    "severity": vuln.get("severity", "medium").lower(),
                    "source": "sca",
                })

        # 시크릿 결과
        if secret_result_file and secret_result_file.exists():
            secret_data = json.loads(secret_result_file.read_text())
            for s in secret_data.get("secrets", []):
                all_vulns.append({
                    "type": "hardcoded_secret",
                    "severity": s.get("severity", "critical"),
                    "source": "secret_scanner",
                })

    # 도메인 가중치 적용 및 최종 점수 계산
    score = 100
    counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}

    for vuln in all_vulns:
        severity = vuln.get("severity", "medium").lower()
        vuln_type = vuln.get("type", "unknown")
        weight = get_domain_weight(vuln_type, domain)

        base_penalty = PENALTY.get(severity, 1)
        weighted_penalty = base_penalty * weight
        score -= weighted_penalty

        deductions.append({
            "rule_id": vuln.get("rule_id", ""),
            "type": vuln_type,
            "severity": severity,
            "source": vuln.get("source", "unknown"),
            "base_penalty": base_penalty,
            "weight": round(weight, 2),
            "deduction": round(weighted_penalty, 2),
        })

        # 심각도별 카운트 (가중 적용 후 심각도 상향 조정)
        effective_cvss = min(BASE_CVSS.get(severity, 5.0) * weight, 10.0)
        if effective_cvss >= 9.0:
            counts["critical"] += 1
        elif effective_cvss >= 7.0:
            counts["high"] += 1
        elif effective_cvss >= 4.0:
            counts["medium"] += 1
        elif effective_cvss > 0:
            counts["low"] += 1
        else:
            counts["info"] += 1

    score = max(0, min(100, round(score)))

    grade = "A" if score >= 90 else "B" if score >= 75 else "C" if score >= 60 else "D" if score >= 40 else "F"

    # Grade cap: high >= 1 caps grade at B. Prevents a single high severity
    # from shipping with an A grade under domain weights that don't penalize enough.
    grade_capped = False
    if counts["high"] >= 1 and grade == "A":
        grade = "B"
        grade_capped = True

    # ─── Certified 배지 발급 조건 ─────────────────────────────────────────
    # hard gate 1: severity (점수 무관하게 critical/high 1개라도 있으면 미발급)
    # hard gate 2: rule_id 블랙리스트 (severity가 낮아도 known-dangerous 패턴)
    _DANGEROUS_RULE_PATTERNS = (
        "eval", "code-injection", "command-injection", "exec",
        "insecure-random", "weak-random", "math-random",
        "md5", "sha1", "insecure-hash", "weak-hash",
        "hardcoded-secret", "hardcoded_secret",
        "sql-injection", "sqli",
        "open-redirect",
    )
    blocked_rules = [
        v.get("rule_id", "")
        for v in all_vulns
        if any(p in v.get("rule_id", "").lower() for p in _DANGEROUS_RULE_PATTERNS)
    ]
    certified = (
        counts["critical"] == 0
        and counts["high"] == 0
        and score >= 85
        and len(blocked_rules) == 0
    )
    certified_block_reason = None
    if not certified:
        if counts["critical"] > 0:
            certified_block_reason = f"{counts['critical']} critical vulnerabilities"
        elif counts["high"] > 0:
            certified_block_reason = f"{counts['high']} high vulnerabilities"
        elif blocked_rules:
            certified_block_reason = f"dangerous pattern detected: {blocked_rules[0]}"
        elif score < 85:
            certified_block_reason = f"score below threshold ({score}/85)"

    result = {
        "score": score,
        "grade": grade,
        "grade_capped": grade_capped,
        "domain": domain,
        "total_vulnerabilities": len(all_vulns),
        **counts,
        "certified": certified,
        "certified_block_reason": certified_block_reason,
    }
    if verbose:
        result["deductions"] = sorted(deductions, key=lambda d: -d["deduction"])
    return result


def main():
    parser = argparse.ArgumentParser(description="VibeSafe 보안 점수 산출기")
    parser.add_argument("--sast-result", help="SAST SARIF 결과 파일")
    parser.add_argument("--sca-result", help="SCA JSON 결과 파일")
    parser.add_argument("--secret-result", help="시크릿 스캔 JSON 결과 파일")
    parser.add_argument("--domain", required=True, help="서비스 도메인")
    parser.add_argument("--triage", action="store_true", help="트리아지 모드 (원시 취약점 입력)")
    parser.add_argument("--input", help="트리아지 모드 입력 JSON 파일")
    parser.add_argument("--stack-file", help="스택 탐지 결과 JSON (프레임워크 충돌 필터용)")
    parser.add_argument("--verbose", action="store_true", help="per-item 차감 breakdown 포함")
    args = parser.parse_args()

    raw_input = None
    if args.triage and args.input:
        raw_input = json.loads(Path(args.input).read_text())

    detected_stack: list[str] = []
    if args.stack_file:
        try:
            detected_stack = json.loads(Path(args.stack_file).read_text()).get("detected_stack", [])
        except (json.JSONDecodeError, OSError):
            pass

    result = calculate_score(
        sast_result_file=Path(args.sast_result) if args.sast_result else None,
        sca_result_file=Path(args.sca_result) if args.sca_result else None,
        secret_result_file=Path(args.secret_result) if args.secret_result else None,
        domain=args.domain,
        triage_mode=args.triage,
        raw_input=raw_input,
        detected_stack=detected_stack,
        verbose=args.verbose,
    )

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

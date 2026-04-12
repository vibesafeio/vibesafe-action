#!/usr/bin/env python3
"""
tools/scanner/domain_rule_engine.py
도메인(이커머스, 게임, 플랫폼, 헬스케어, 핀테크, 교육)별 Semgrep 규칙셋을 매핑하고
소스 코드에서 도메인 시그널을 탐지하여 자동 분류를 수행한다.
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path

# ─── 도메인별 Semgrep 규칙셋 ────────────────────────────
DOMAIN_RULESETS = {
    "ecommerce": {
        "semgrep_configs": [
            "p/owasp-top-ten",
            "p/javascript",
            "p/sql-injection",
            "p/xss",
            "p/secrets",
        ],
        "custom_rules": "rules/ecommerce/",
        "regulations": ["PCI DSS", "GDPR", "전자상거래법"],
        "high_risk_patterns": ["sql_injection", "xss", "hardcoded_secret", "idor"],
    },
    "game": {
        "semgrep_configs": [
            "p/owasp-top-ten",
            "p/javascript",
            "p/xss",
            "p/secrets",
        ],
        "custom_rules": "rules/game/",
        "regulations": ["COPPA", "GDPR"],
        "high_risk_patterns": ["xss", "websocket_hijacking", "api_key_exposure"],
    },
    "platform": {
        "semgrep_configs": [
            "p/owasp-top-ten",
            "p/javascript",
            "p/jwt",
            "p/secrets",
            # p/nodejs-security, p/ssrf: semgrep registry 미존재 (exit 7) → 제거
            # SSRF/Node 취약점은 p/owasp-top-ten + p/javascript로 커버
        ],
        "custom_rules": "rules/platform/",
        "regulations": ["SOC2", "GDPR", "CCPA"],
        "high_risk_patterns": ["bola", "jwt_manipulation", "ssrf", "hardcoded_secret"],
    },
    "healthcare": {
        "semgrep_configs": [
            "p/owasp-top-ten",
            "p/javascript",
            "p/secrets",
            "p/sql-injection",
        ],
        "custom_rules": "rules/healthcare/",
        "regulations": ["HIPAA", "개인정보보호법"],
        "high_risk_patterns": ["missing_encryption", "access_control_bypass", "hardcoded_secret"],
    },
    "fintech": {
        "semgrep_configs": [
            "p/owasp-top-ten",
            "p/javascript",
            "p/sql-injection",
            "p/secrets",
            "p/jwt",
        ],
        "custom_rules": "rules/fintech/",
        "regulations": ["PCI DSS", "전자금융거래법"],
        "high_risk_patterns": ["hardcoded_secret", "missing_encryption", "auth_bypass", "sql_injection"],
    },
    "education": {
        "semgrep_configs": [
            "p/owasp-top-ten",
            "p/javascript",
            "p/xss",
            "p/secrets",
        ],
        "custom_rules": "rules/education/",
        "regulations": ["FERPA", "COPPA"],
        "high_risk_patterns": ["privilege_escalation", "data_over_exposure", "xss"],
    },
}

# ─── 도메인 분류 시그널 ──────────────────────────────────
DOMAIN_SIGNALS = {
    "ecommerce": {
        "file_patterns": ["cart", "checkout", "payment", "order", "product", "catalog", "shipping"],
        "packages": ["stripe", "paypal", "shopify-api", "square", "braintree", "@stripe"],
        "code_patterns": [r"price\s*[=:]\s*[\d.]", r"card_number", r"CVV", r"PCI"],
    },
    "game": {
        "file_patterns": ["game", "player", "score", "level", "inventory", "matchmaking"],
        "packages": ["socket.io", "colyseus", "phaser", "playfab"],
        "code_patterns": [r"leaderboard", r"game_state", r"respawn", r"match_id"],
    },
    "platform": {
        "file_patterns": ["tenant", "workspace", "organization", "billing", "subscription"],
        "packages": ["@auth0", "clerk", "@clerk", "supabase", "firebase-admin"],
        "code_patterns": [r"tenant_id", r"org_id", r"RBAC", r"subscription_id"],
    },
    "healthcare": {
        "file_patterns": ["patient", "diagnosis", "prescription", "medical", "health", "ehr"],
        "packages": ["fhir", "hl7", "dicom-parser"],
        "code_patterns": [r"PHI", r"HIPAA", r"patient_id", r"diagnosis_code"],
    },
    "fintech": {
        "file_patterns": ["account", "transaction", "transfer", "kyc", "aml", "ledger"],
        "packages": ["plaid", "dwolla", "moov", "tink"],
        "code_patterns": [r"account_number", r"routing_number", r"KYC", r"AML", r"balance"],
    },
    "education": {
        "file_patterns": ["student", "course", "grade", "assignment", "enrollment", "classroom"],
        "packages": ["lti", "scorm", "canvas-api"],
        "code_patterns": [r"student_id", r"grade\s*=", r"enrollment_id", r"FERPA"],
    },
}


def classify_domain(source_path: Path) -> dict:
    """소스 코드를 분석하여 각 도메인별 신뢰도 점수를 계산한다."""
    scores = {domain: 0 for domain in DOMAIN_SIGNALS}
    signal_counts = {domain: 0 for domain in DOMAIN_SIGNALS}

    # 파일 경로 시그널
    all_files = list(source_path.rglob("*"))
    for f in all_files:
        parts = f.parts
        for domain, signals in DOMAIN_SIGNALS.items():
            for pattern in signals["file_patterns"]:
                if any(pattern in part.lower() for part in parts):
                    signal_counts[domain] += 1

    # 패키지 시그널 (package.json)
    for pkg_file in source_path.rglob("package.json"):
        try:
            data = json.loads(pkg_file.read_text())
            all_deps = {
                **data.get("dependencies", {}),
                **data.get("devDependencies", {}),
            }
            for domain, signals in DOMAIN_SIGNALS.items():
                for pkg in signals["packages"]:
                    if any(dep.startswith(pkg) for dep in all_deps):
                        signal_counts[domain] += 3  # 패키지 시그널은 가중치 3
        except (json.JSONDecodeError, OSError):
            pass

    # 코드 패턴 시그널 (텍스트 파일만)
    text_extensions = {".ts", ".tsx", ".js", ".jsx", ".py", ".rb", ".go", ".java", ".kt", ".php"}
    for f in all_files:
        if f.is_file() and f.suffix.lower() in text_extensions:
            try:
                content = f.read_text(encoding="utf-8", errors="ignore")[:50000]  # 최대 50KB
                for domain, signals in DOMAIN_SIGNALS.items():
                    for pattern in signals["code_patterns"]:
                        if re.search(pattern, content, re.IGNORECASE):
                            signal_counts[domain] += 2  # 코드 패턴은 가중치 2
            except OSError:
                pass

    # 신뢰도 정규화 (0.0 ~ 1.0)
    max_signal = max(signal_counts.values()) if any(signal_counts.values()) else 1
    for domain in scores:
        scores[domain] = min(round(signal_counts[domain] / max(max_signal, 10), 2), 1.0)

    best_domain = max(scores, key=lambda d: scores[d])
    best_score = scores[best_domain]

    return {
        "scores": scores,
        "best_match": best_domain,
        "confidence": best_score,
        "auto_classify": best_score >= 0.7,
        "needs_confirmation": 0.4 <= best_score < 0.7,
        "needs_manual": best_score < 0.4,
    }


def get_ruleset(
    domain: str,
    detected_stack: list[str] | None = None,
    languages: list[str] | None = None,
    custom_rules: list[str] | None = None,
) -> dict:
    """도메인, 기술 스택, 감지된 언어에 맞는 Semgrep 규칙셋을 반환한다.
    custom_rules: 사용자가 지정한 추가 Semgrep config 경로/URL 목록."""
    if domain not in DOMAIN_RULESETS:
        # 알 수 없는 도메인 → 범용 규칙셋
        base_configs = ["p/owasp-top-ten", "p/secrets"]
        if custom_rules:
            base_configs.extend(custom_rules)
        return {
            "domain": domain,
            "semgrep_configs": base_configs,
            "custom_rules": custom_rules,
            "regulations": [],
            "fallback": True,
        }

    ruleset = dict(DOMAIN_RULESETS[domain])
    configs = set(ruleset["semgrep_configs"])

    # 감지된 언어별 규칙 추가 — 스택 감지 실패해도 언어만 있으면 커버
    langs = set(languages or [])
    if "python" in langs:
        configs.add("p/python")
    if "javascript" in langs or "typescript" in langs:
        configs.add("p/javascript")
    if "go" in langs:
        configs.add("p/golang")
    if "java" in langs:
        configs.add("p/java")
    if "ruby" in langs:
        configs.add("p/ruby")

    # 스택별 추가 규칙
    if detected_stack:
        if "nextjs" in detected_stack or "react" in detected_stack:
            configs.add("p/react")
        if "django" in detected_stack or "flask" in detected_stack:
            configs.add("p/python")
        if "prisma" in detected_stack:
            configs.add("p/javascript")

    # 사용자 커스텀 룰 추가
    if custom_rules:
        for cr in custom_rules:
            configs.add(cr)

    ruleset["semgrep_configs"] = sorted(configs)
    ruleset["domain"] = domain
    ruleset["detected_stack"] = detected_stack or []
    ruleset["languages"] = sorted(langs)
    ruleset["custom_rules"] = custom_rules or []
    return ruleset


def validate_rulesets() -> dict:
    """
    모든 도메인의 모든 semgrep_configs 팩이 실제로 Semgrep registry에 존재하는지 검증한다.
    존재하지 않는 팩(exit 7 = MISSING_CONFIG)을 목록으로 반환한다.

    사용: python domain_rule_engine.py --validate
    CI에서 릴리스 전에 실행하면 유령 팩 재진입을 구조적으로 차단한다.
    """
    import subprocess as _sp

    # 모든 도메인에서 유니크한 팩 목록 수집
    all_packs: set[str] = set()
    for ruleset in DOMAIN_RULESETS.values():
        all_packs.update(ruleset["semgrep_configs"])
    # 스택/언어 기반 추가 팩
    all_packs.update(["p/react", "p/python", "p/golang", "p/ruby", "p/java"])

    results = {}
    invalid = []

    import tempfile as _tmp
    # 빈 JS 파일 하나를 스캔 대상으로 사용 (최소한의 유효한 코드)
    with _tmp.NamedTemporaryFile(suffix=".js", mode="w", delete=False) as f:
        f.write("// vibesafe validate\n")
        scan_target = f.name

    for pack in sorted(all_packs):
        # semgrep --config {pack} --validate는 공식 지원이 없음.
        # 대신 빈 파일에 드라이런 → exit 7 = MISSING_CONFIG = 팩 미존재
        r = _sp.run(
            ["semgrep", "--config", pack, "--sarif", "--output", "/dev/null",
             "--timeout", "20", scan_target],
            stdout=_sp.PIPE,
            stderr=_sp.STDOUT,
            text=True,
            timeout=40,
        )
        ok = r.returncode in (0, 1)  # 0=clean, 1=findings
        results[pack] = "ok" if ok else f"FAIL(exit {r.returncode})"
        if not ok:
            invalid.append(pack)

    return {
        "packs_checked": len(all_packs),
        "invalid_packs": invalid,
        "valid": len(invalid) == 0,
        "results": results,
    }


def main():
    parser = argparse.ArgumentParser(description="VibeSafe 도메인 규칙 엔진")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--domain", help="규칙셋 조회할 도메인")
    group.add_argument("--classify", action="store_true", help="소스 코드 도메인 자동 분류")
    group.add_argument("--validate", action="store_true", help="모든 semgrep 팩 유효성 검증 (CI용)")
    parser.add_argument("--path", help="소스 코드 경로 (classify 시 필수)")
    parser.add_argument("--stack", help="탐지된 기술 스택 (쉼표 구분)")
    parser.add_argument("--languages", help="탐지된 언어 (쉼표 구분)")
    parser.add_argument("--custom-rules", help="추가 Semgrep configs (쉼표 구분, 예: p/react,./my-rules.yml)")
    args = parser.parse_args()

    if args.validate:
        result = validate_rulesets()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(0 if result["valid"] else 1)
    elif args.classify:
        if not args.path:
            print(json.dumps({"error": "--path required"}))
            sys.exit(1)
        result = classify_domain(Path(args.path))
    else:
        stack = [s.strip() for s in args.stack.split(",")] if args.stack else []
        langs = [l.strip() for l in args.languages.split(",")] if args.languages else []
        custom = [c.strip() for c in args.custom_rules.split(",")] if args.custom_rules else []
        result = get_ruleset(args.domain, stack, langs, custom)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

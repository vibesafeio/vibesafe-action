---
title: Hard Rules
type: engineering
confidence: high
created: 2026-03-18
updated: 2026-04-12
sources: [docs/failure-log.md, CLAUDE.md]
---

## TLDR
반복된 버그에서 추출한 절대 규칙 6개. 위반하면 프로덕션 장애.
모든 규칙은 실제 사고에서 비롯됨.

## Content

### 1. `from __future__ import annotations` on every Python file
- **이유**: Python 3.9에서 `list[str] | None` 크래시. 4번 반복됨.
- **위치**: shebang 아래, docstring 아래, import 전. 절대 1행에 넣지 않음.

### 2. No `capture_output=True` for Semgrep subprocess
- **이유**: `stderr=PIPE`가 Semgrep 원격 규칙셋 로드를 차단 (exit 7).
- **대안**: `stderr=subprocess.STDOUT` 사용.

### 3. Validate Semgrep packs before adding
- **이유**: `p/nodejs-security`, `p/ssrf` 같은 팩은 존재하지 않음.
- **검증**: `domain_rule_engine.py --validate` 실행 후 추가.

### 4. Run code immediately after writing
- **이유**: "나중에 테스트" 패턴이 12건 버그 유발 (2건 critical silent failure).
- **규칙**: 코드 작성 → 즉시 실행 → 확인.

### 5. No `${{ }}` interpolation of JSON into JS strings in GitHub Actions
- **이유**: JSON에 따옴표가 포함되면 JS 문자열이 깨짐.
- **대안**: `env:` 블록 → `process.env.*` 패턴.

### 6. git safe.directory in Docker
- **이유**: Semgrep이 `git ls-files` 사용. safe.directory 없으면 exit 128 → 0 파일 스캔 → silent 0 findings.
- **적용**: Docker에서 git 도구 사용 시 반드시 설정.

## Open Questions
- 없음. 이 규칙들은 모두 검증됨.

## Related
- [[engineering/failure-log.md]]
- [[engineering/deploy-gates.md]]

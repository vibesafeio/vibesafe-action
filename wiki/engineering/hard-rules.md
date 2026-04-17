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

### 7. Secret scanner는 test/fixture 경로 제외
- **이유**: test fixture의 가짜 키(sk-proj-abc123... 패턴)가 placeholder 정규식 통과 → critical FP → 모든 사용자 점수 왜곡. VibeSafe 자체 F/32 사고 (2026-04-17).
- **적용**: `SKIP_DIRS`에 `test, tests, __tests__, spec, specs, fixture, fixtures, example(s), sample(s), mock(s), __mocks__, demo(s), e2e, cypress, playwright` 유지.
- **Trade-off**: test 코드 진짜 유출은 놓침. 하지만 attack surface는 prod 코드 >> test 코드.

### 8. Install CTA는 `/new/main` 직접 열기 금지
- **이유**: `github.com/X/repo/new/main?...` 는 X가 해당 repo 쓰기 권한 있을 때만 동작. 남의 리포트 보는 유저한테는 무조건 404. 2026-04-17 UI 실수로 발생.
- **대안**: Marketplace URL (`github.com/marketplace/actions/vibesafe-security-scan`)로 라우팅 — GitHub 네이티브 install flow가 repo 선택 처리.

## Open Questions
- 없음. 이 규칙들은 모두 검증됨.

## Related
- [[engineering/failure-log.md]]
- [[engineering/deploy-gates.md]]

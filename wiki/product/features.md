---
title: VibeSafe Features
type: product
confidence: high
created: 2026-03-18
updated: 2026-04-12
sources: [docs/architecture.md, docs/auto_fix_design.md, docs/mcp_server_design.md]
---

## TLDR
SAST + Secret + 도메인규칙 + Fix제안 + 머지차단 + 웹스캐너 + 리더보드.
Pre-commit hook과 MCP 서버 구현 완료. SCA와 뱃지는 미구현.

## Content

### 핵심 기능
| 기능 | 설명 | 상태 |
|------|------|------|
| SAST 스캔 | Semgrep 기반 정적 분석. OWASP Top 10 | ✅ |
| Secret 탐지 | 정규식 + 엔트로피 분석. API 키, 비밀번호, 토큰 | ✅ |
| 도메인 규칙 | 이커머스/핀테크/헬스케어 등 자동 분류 → 맞춤 룰셋 | ✅ |
| 스택 감지 | 언어 + 프레임워크 자동 탐지 (import 기반) | ✅ |
| 프레임워크 필터링 | Flask/Django 충돌 등 오탐 제거 | ✅ |
| Fix 제안 | 32개 패턴 매핑 (SQL injection → parameterized query 등) | ✅ |
| PR 코멘트 | 파일:라인 + 심각도 + 수정 방법 | ✅ |
| 머지 차단 | fail-on: critical/high/medium. exit 1 → red X | ✅ |
| 점수 (0-100) | SARIF + secrets + 도메인 가중치 → 등급 A-F | ✅ |
| 웹 스캐너 | URL 입력 → 30초 스캔 → 결과 + AI 프롬프트 | ✅ |
| 리더보드 | 웜뱃 땅굴 정규분포 + 백분위 | ✅ |
| Pre-commit hook | 커밋 전 secret 탐지 | ✅ |
| MCP 서버 | Claude Code/Cursor 연동 (check_secret) | ✅ |
| 접근성 | img alt, label, lang 등 | ✅ (light) |
| SCA | 의존성 CVE 스캔 | ❌ |
| 뱃지 | README용 점수 뱃지 | ❌ |
| Diff-only | 변경된 코드만 스캔 | ❌ |

### Fix 제안 패턴 (Phase 1)
| Semgrep Rule | Fix Type | 변환 |
|---|---|---|
| tainted-sql-string | parameterized_query | f-string → placeholder + params |
| subprocess-injection | safe_subprocess | shell=True → shlex.split |
| user-eval | remove_eval | eval() → ast.literal_eval() |
| hardcoded_secret | env_variable | 리터럴 → os.environ.get() |
| path-traversal-open | path_validation | open(input) → pathlib 검증 |
| debug-enabled | remove_debug | debug=True → 제거 |

## Open Questions
- password-comparison-timing-js 규칙이 모든 === 비교를 잡음 (오탐 과다). 규칙 정제 필요.
- 접근성 규칙을 full mode에서만 돌릴 것인가, light에서도 유지할 것인가?

## Related
- [[engineering/architecture.md]]
- [[product/roadmap.md]]

---
title: VibeSafe Features
type: product
confidence: high
created: 2026-03-18
updated: 2026-04-17
sources: [docs/architecture.md, docs/auto_fix_design.md, docs/mcp_server_design.md]
---

## TLDR
SAST + SCA + Secret + Config(Supabase/Firebase) + 도메인규칙 + Fix제안 + AI Fix Prompt + 머지차단 + 웹스캐너 + CLI스캐너 + 리더보드 + PR코멘트 접기.
Pre-commit hook, MCP 서버, SCA, Config Scanner 구현 완료.

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
| 점수 (0-100) | SARIF + secrets + 도메인 가중치 → 등급 A-F. `--verbose`로 per-item 차감 breakdown. high≥1이면 A 등급 차단 (B 캡). | ✅ |
| 웹 스캐너 | URL 입력 → 30초 스캔 → 결과 + AI 프롬프트 | ✅ |
| **Per-repo SEO 랜딩** | `/report/<owner>/<repo>` 영구 URL. 캐시 miss 시 auto-scan. robots.txt + sitemap.xml 크롤링. dynamic meta + **SSR body** (per-URL 1500+ chars 고유 Googlebot-visible 콘텐츠) | ✅ |
| **Popular scans 홈 그리드** | 홈에 17 seed 카드 노출 (A-desc). sitemap을 사람이 안 읽으니 인간 진입 경로 확보 | ✅ |
| **Badge 엔드포인트** | `/api/badge/:owner/:repo` — shields.io 호환 JSON. A green / B yellow / C orange / D/F red | ✅ |
| **GitHub Marketplace 등재** | `github.com/marketplace/actions/vibesafe-security-scan` (v0.1.1 Latest) | ✅ |
| UTM attribution | 외부 링크 전수 태깅 + server-side capture ([METRIC_EVENT] stdout 파싱 포맷) | ✅ |
| 리더보드 | 픽셀아트 업라이트 바 차트 (바 위에 웜벳 마커). 홈 preview + 결과 burrow 통합. | ✅ |
| Pre-commit hook | 커밋 전 secret 탐지 | ✅ |
| MCP 서버 | Claude Code/Cursor 연동 (check_secret) | ✅ |
| 접근성 | img alt, label, lang 등 | ✅ (light) |
| SCA | pip-audit + npm audit 의존성 CVE 스캔 | ✅ |
| Config Scanner | Supabase RLS + Firebase Rules 검사 | ✅ |
| CLI 스캐너 | `python3 cli_scanner.py <url>` 즉시 스캔 | ✅ |
| AI Fix Prompt | 전체 findings → Cursor/Claude 복사용 프롬프트 생성 | ✅ |
| .env.example 생성 | 시크릿 발견 시 환경변수 템플릿 자동 생성 | ✅ |
| .gitignore 감사 | .env 미포함 시 경고 | ✅ |
| PR 코멘트 접기 | Top 5 인라인, 나머지 `<details>` 접기 | ✅ |
| Custom Rules | `custom-rules` input으로 사용자 YAML 추가 | ✅ |
| 뱃지 | shields.io dynamic badge 가이드 + `/api/badge/:owner/:repo` 엔드포인트 | ✅ |
| Diff-only | 변경된 코드만 스캔 | ❌ (Semgrep Pro 전용) |
| Certified 뱃지 UI | Share 페이지 + 뱃지 UI | ❌ (TODO) |
| Metric persistence | Render 재시작 간 누적 카운터 (현재 ephemeral + stdout [METRIC_EVENT] 로그 replay) | ⚠️ 로그 파싱 필요 |

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
- 접근성 규칙을 full mode에서만 돌릴 것인가, light에서도 유지할 것인가?

## Related
- [[engineering/architecture.md]]
- [[product/roadmap.md]]

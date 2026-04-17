---
title: Architecture
type: engineering
confidence: high
created: 2026-03-18
updated: 2026-04-17
sources: [docs/architecture.md]
---

## TLDR
GitHub Action (Docker) + 웹 스캐너 (Render) + **per-repo SEO 랜딩 페이지**. 파이프라인: 스택감지 → 도메인분류 → 규칙선택 → SAST → Secret → 점수 → PR코멘트.
웹 결과는 `/report/<owner>/<repo>` 영구 URL로 저장 (sitemap + robots.txt 크롤링 대상).
로컬 도구: pre-commit hook, MCP 서버.

## Content

### 파이프라인 (GitHub Action)
```
action_entrypoint.sh
  → sast_runner.py (Semgrep + 스택 감지)
  → secret_scanner.py (정규식 + 엔트로피)
  → domain_rule_engine.py (도메인 분류 + 규칙 선택)
  → score_calculator.py (0-100 점수)
  → pr_commenter.py (PR 코멘트 + GitHub API)
  → fail-on gate (exit 1 or 0)
```

### 데이터 흐름
1. `sast_runner.py --detect-stack` → 언어 + 프레임워크
2. `domain_rule_engine.py --classify` → 이커머스/핀테크/플랫폼 등
3. 도메인 + 스택 + 언어 → Semgrep config 리스트
4. Semgrep 실행 → SARIF 출력
5. Secret 스캔 → JSON findings
6. SARIF + secrets + 도메인 가중치 → 0-100 점수
7. PR 코멘트 생성 (파일:라인, Fix 제안)
8. score.json → fail-on 임계치 초과 시 exit 1

### 웹 스캐너
- `web/server.py`: stdlib HTTPServer
  - `SCANS`: 진행 중/완료 스캔 (LRU 50, UUID key)
  - `SCORES`: 리더보드용 점수 리스트 (seed 60 + 실 스캔)
  - `REPORTS`: **영구 리포트 캐시** (LRU 500, key=`owner/repo`) — SEO 랜딩 페이지 source
- `web/static/index.html`: 단일 페이지 SPA, 경로별 동작:
  - `/`: 홈 (스캔 입력창)
  - `/report/<owner>/<repo>`: SEO 랜딩 (자동 캐시 로드 또는 auto-scan)
- `tools/cli_scanner.py`: 웹에서 호출하는 스캔 엔트리포인트
- 배포: Render (자동, push하면 배포)
- 상태: in-memory (재배포 시 리셋). `/report/` URL은 stable — 캐시 miss 시 자동 rescan.

### SEO 라우팅 (server.py)
| 엔드포인트 | 동작 |
|-----------|------|
| `GET /` | index.html (기본 meta), page_views 카운트 + UTM 로그 |
| `GET /report/<owner>/<repo>` | index.html에 **SSR-lite dynamic meta** (title/description/og:url) 치환 후 반환. 캐시 있으면 meta에 점수 포함, 없으면 기본값. report_views 이벤트 로그. |
| `GET /api/report/<owner>/<repo>` | REPORTS 캐시 JSON 또는 404 |
| `GET /robots.txt` | `Allow: /` + `Disallow: /api/` + sitemap 링크 |
| `GET /sitemap.xml` | `/` + REPORTS 전체 URL |
| `POST /api/scan` | 스캔 시작. 완료 시 `_save_report()`가 REPORTS에 저장 → sitemap 자동 포함 |

### 퍼널
```
Google 검색 ("next.js security score" 등)
    ↓
/report/<owner>/<repo> 랜딩 (점수 + findings + 웜벳 분포)
    ↓ 하단 CTA: "Install from Marketplace"
GitHub Marketplace (vibesafe-security-scan)
    ↓ GitHub 네이티브 install flow (유저가 자기 repo 선택)
GitHub Action 설치 + 매 PR 자동 실행
```

### 핵심 파일
| 파일 | 용도 |
|------|------|
| action.yml | GitHub Action 정의 (Marketplace 등재됨) |
| action_entrypoint.sh | 오케스트레이터 |
| Dockerfile.action | Docker 이미지 (Python 3.11 + Semgrep + git) |
| tools/scanner/sast_runner.py | Semgrep 래퍼 + 스택 감지 |
| tools/scanner/secret_scanner.py | 시크릿 탐지 (test/fixture 경로 제외) |
| tools/scanner/domain_rule_engine.py | 도메인 분류 + 규칙 선택 |
| tools/report/score_calculator.py | 점수 계산 (`--verbose` breakdown, high≥1→B cap) |
| tools/report/pr_commenter.py | PR 코멘트 |
| web/server.py | 웹 스캐너 + SEO 라우팅 + REPORTS 캐시 + sitemap |
| web/static/index.html | SPA + `/report/` 부트스트랩 + 업라이트 burrow 차트 |
| tools/mcp_server.py | MCP 서버 |

## Open Questions
- REPORTS 캐시를 Render 재배포 간 영속화? (현재는 ephemeral → rescan on miss. 데이터량 상승 후 Supabase/Upstash KV 고려)
- Render free tier의 메모리/CPU 한계로 대형 repo 스캔 시 타임아웃 (90초)
- Sitemap 크기 상한 (50MB/50K URL) — 현재 규모에서는 걱정 없음, 후일 분할 필요 가능성

## Related
- [[engineering/hard-rules.md]]
- [[product/features.md]]

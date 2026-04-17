---
title: VibeSafe Roadmap
type: product
confidence: high
created: 2026-03-18
updated: 2026-04-17
sources: [docs/auto_fix_design.md, docs/mcp_server_design.md, docs/vc-response.md]
---

## TLDR
Phase 1 (현재): 사용자 확보. **전략 pivot: 일회성 포스트 → 영구 SEO 자산 (per-repo 랜딩 페이지)**. Marketplace 등재 + UTM 측정 + Install CTA 단일화 완료.
Phase 2: 코딩 시점 보안 — MCP 서버 + pre-commit hook (구현됨).
Phase 3: 비즈니스 모델 검증 — 사용자 기반 확보 후 결정.

## Content

### 현재 상태 (2026-04-17)
| 기능 | 상태 |
|------|------|
| GitHub Action (SAST + Secrets + SCA + Config) | ✅ 출시 |
| PR 코멘트 (파일+라인+수정제안) | ✅ 출시 |
| 도메인별 자동 규칙 선택 | ✅ 출시 |
| 프레임워크 오탐 필터링 | ✅ 출시 |
| fail-on 머지 차단 | ✅ 출시 |
| 웹 스캐너 (URL 입력) | ✅ 출시 (vibesafe.onrender.com) |
| 업라이트 바 차트 리더보드 | ✅ 출시 |
| pre-commit hook | ✅ 구현 |
| MCP 서버 | ✅ 구현 (check_secret) |
| 접근성 스캔 | ✅ 구현 (light mode) |
| **GitHub Marketplace 등재** | ✅ 출시 (v0.1.1 Latest) |
| **Per-repo SEO 랜딩 페이지** | ✅ 출시 (/report/owner/repo + sitemap + robots.txt) |
| **UTM 전수 태깅 + server capture** | ✅ 출시 |
| score_calculator `--verbose` + grade cap | ✅ 출시 |
| 뱃지 엔드포인트 | ❌ 미구현 |
| diff-only 스캔 | ❌ 미구현 (Semgrep Pro 전용, OSS 대안 리서치 필요) |
| Share 페이지 + Certified 뱃지 UI | ❌ 미구현 |

### 다음 할 것 (2026-04-17 기준 우선순위)
1. **Day+3 측정 (2026-04-20)**: install_clicks, page_views, Stars, Marketplace UTM 분포 → 다음 결정 input
2. Awesome Lists PR (awesome-actions, awesome-security) — 반영구 compound
3. Show HN / Reddit (r/selfhosted, r/programming) — 한 방 lottery, 데이터 hook으로 ("We scanned N AI-coded repos, median grade D")
4. Cold DM 10명 vibe-coded repo 오너
5. 뱃지 엔드포인트 (공유 가능한 artifact — SEO pages에 뱃지 노출)
6. diff-only 스캔 OSS 대안 리서치

### 안 할 것 (재확인 2026-04-17)
- ~~Twitter/LinkedIn 단독 launch 포스트~~ (0 audience에서 follower-based = dead. [[decisions/rejected.md]])
- 엔터프라이즈 타겟
- 유료 기능 (사용자 기반 전)
- 컨테이너 스캔

## Open Questions
- Awesome Lists 머지 성공률? (curator 기준 제각각)
- Show HN 시간대 최적화 (화-목 8-10am PT 가정)
- REPORTS ephemeral → 영속화 전환 시점 (N > 500? 또는 Render 재시작 빈도?)
- diff-only 스캔을 Semgrep OSS로 구현 가능한가? (--baseline-commit은 Pro 전용)

## Related
- [[product/features.md]]
- [[engineering/architecture.md]]
- [[future/vibecost.md]]

---
title: VibeSafe Roadmap
type: product
confidence: high
created: 2026-03-18
updated: 2026-04-12
sources: [docs/auto_fix_design.md, docs/mcp_server_design.md, docs/vc-response.md]
---

## TLDR
Phase 1 (현재): 사용자 확보 — 웹 스캐너 + GitHub Action + 마케팅.
Phase 2: 코딩 시점 보안 — MCP 서버 + pre-commit hook.
Phase 3: 비즈니스 모델 검증 — 사용자 기반 확보 후 결정.

## Content

### 현재 상태 (2026-04-12)
| 기능 | 상태 |
|------|------|
| GitHub Action (SAST + Secrets) | ✅ 출시 |
| PR 코멘트 (파일+라인+수정제안) | ✅ 출시 |
| 도메인별 자동 규칙 선택 | ✅ 출시 |
| 프레임워크 오탐 필터링 | ✅ 출시 |
| fail-on 머지 차단 | ✅ 출시 |
| 웹 스캐너 (URL 입력) | ✅ 출시 (vibesafe.onrender.com) |
| 웜뱃 땅굴 리더보드 | ✅ 출시 |
| pre-commit hook | ✅ 구현 |
| MCP 서버 | ✅ 구현 (check_secret) |
| 접근성 스캔 | ✅ 구현 (light mode) |
| SCA (의존성 스캔) | ❌ 미구현 |
| 뱃지 엔드포인트 | ❌ 미구현 |
| diff-only 스캔 | ❌ 미구현 (최대 moat 기회) |

### 다음 할 것 (우선순위)
1. LinkedIn 콘텐츠로 공유 유도 (리더보드 데이터 활용)
2. 웹 스캐너 → Action 설치 전환 퍼널 최적화
3. diff-only 스캔 (가장 큰 기술적 moat)
4. 뱃지 엔드포인트 (공유 가능한 결과)

### 안 할 것
- 엔터프라이즈 타겟 (사용자 0명에서 의미 없음)
- 유료 기능 (아직 사용자 기반 없음)
- 컨테이너 스캔 (scope 밖)

## Open Questions
- diff-only 스캔을 Semgrep OSS로 구현 가능한가? (--baseline-commit은 Pro 전용)
- 뱃지 엔드포인트: 스캔 결과를 얼마나 캐시할 것인가?

## Related
- [[product/features.md]]
- [[engineering/architecture.md]]
- [[future/vibecost.md]]

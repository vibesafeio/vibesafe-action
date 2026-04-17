---
title: Market Validation
type: market
confidence: high
created: 2026-03-20
updated: 2026-04-17
sources: [docs/market_validation_2026-03-20.md, docs/vc-response.md]
---

## TLDR
시장은 존재한다 (경쟁사 5+개 = 수요 증명). "관심→행동" 전환이 카테고리 전체의 미해결 문제.
2026-04-17 첫 실제 유저 피드백 확보 — **바이브 코딩 프로젝트는 a11y 이슈가 security보다 많다**는 non-obvious insight.

## Content

### 수요 신호
- 5+ 펀딩/활성 경쟁사 존재 = 시장 검증됨
- "I Scanned 100 Vibe-Coded Apps" 류 콘텐츠 바이럴 (DEV.to 10K+ 뷰 추정)
- "53% of AI Code Has Security Holes" 기사 확산
- OKKY에서 "크로스 체크 필수" 공감 댓글
- YouTube에 securing AI-generated code 튜토리얼 등장

### 불편한 진실
1. **바이브 코더는 보안에 관심 없다** — 사고가 터지기 전까지
2. **"관심→행동" 전환이 전체 카테고리의 문제** — 모든 경쟁사가 겪고 있음
3. **무료 도구의 한계** — 사용자가 돈 안 내면 비즈니스 모델 없음
4. **Moat 없음** — YAML + Semgrep = 주말이면 복제 가능

### 현재 지표 (2026-04-17 20:46 KST)
| 지표 | 값 | 비고 |
|------|----|----|
| GitHub Stars | **6** | P0 배포 직후 baseline |
| GitHub Forks | 1 | |
| OKKY 뷰 | 772 | 댓글 3개 + 1 추가 (2026-04-02 경 "코딩숙") |
| dev.to | 반응 없음 | 댓글 0, 좋아요 0 |
| LinkedIn | 미시도 | 기각 ([[decisions/rejected.md]]) |
| Render page_views | 3 | P0 배포 직전 기준 |
| install_clicks | 0 | Day+3 (2026-04-20) 측정 예정 |
| Marketplace | ✅ live | v0.1.1 Latest, 2026-04-17 등재 |

### 사용자 증언 (2026-04-17)
**OKKY 댓글 — "코딩숙" (+1 upvote, 2026-04-02 경)**:
> "이거 써봤는데 스크린 리더 항목도 걸려서 보안은 아니고 접근성 문제도 함께 잡네요 **제 바이브 코딩 프로젝트는 보안성보다는 다 이쪽으로 걸렸습니다**"

**signal extraction:**
1. **제품 실제 동작 검증** (n=1, 첫 실제 사용 증거)
2. **예상 못한 가치 발견**: "보안" 기대 → "a11y" 경험 → 긍정적으로 수용
3. **세그먼트 인사이트**: 바이브 코딩 프로젝트 = **a11y 이슈 > security 이슈**
4. **포지셔닝 정당화**: 2026-03-22 "Safety 확장" 결정이 사후 검증됨

### 전략: "도구 홍보 X, 데이터 공유 O"
- 도구를 광고하지 말고, 실험 데이터를 공유하라
- "AI 생성 코드 10개 스캔 결과 평균 23점" → 시니어가 공유
- 도구는 마지막 한 줄: "참고로 스캔은 이걸로 했습니다"

## Open Questions
- 추가 유저 증언 확보 (n=1 → n≥3)
- SEO 페이지 통한 Google 유입 시작 시점 (인덱싱 latency)
- Awesome Lists / Show HN 반응
- Day+3 (2026-04-20) 측정 결과 vs baseline

## Related
- [[market/segments.md]]
- [[marketing/channels.md]]
- [[marketing/results.md]]

---
title: Marketing Results & KPI Tracking
type: marketing
confidence: high
created: 2026-03-20
updated: 2026-04-12
sources: [docs/vc-response.md]
---

## TLDR
Phase 1 KPI 목표: Stars 100, Installs 50, Re-run 50%.
현재: OKKY 772뷰가 유일한 유의미한 지표. 나머지 미측정 또는 0.

## Content

### Phase 1 KPI
| Metric | Target | Current | Gap |
|--------|--------|---------|-----|
| Stars | 100 / 4주 | **4** | 96 부족 |
| Action installs | 50 repos / 4주 | **0** | 50 부족 |
| Re-run rate | 50%+ | N/A | 데이터 없음 |

### 채널별 성과
| 채널 | 지표 | 날짜 |
|------|------|------|
| OKKY | 772뷰, 댓글 3개 | 2026-04-11 |
| dev.to | 0 반응 | 2026-04-12 |
| GeekNews | 게시 완료, 대기 중 | 2026-04-12 |
| 웹 스캐너 | 1 page view, 0 scans (재배포 리셋) | 2026-04-12 |
| GitHub | 19 views, 22 clones (14d) | 2026-04-12 |

### 메트릭 대시보드
- 웹: `vibesafe.onrender.com/api/metrics`
- 이벤트: page_views, scans_started, scans_completed, fix_copies, install_clicks
- GitHub: `gh api repos/vibesafeio/vibesafe-action` (stars, forks, clones)

### 리더보드 데이터
- Seed: 60개 점수 (평균 34.8)
- 분포: 0-29점 대에 31개 집중 (현실적)
- 실 스캔 점수가 추가되면서 분포 업데이트됨

## Open Questions
- 현재 정확한 Stars/Installs/Clones 수?
- Render 메트릭 마지막 확인 시점?
- 리더보드 seed 데이터와 실제 데이터의 비율?

## Related
- [[marketing/channels.md]]
- [[market/validation.md]]

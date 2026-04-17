---
title: VibeSafe Positioning
type: product
confidence: medium
created: 2026-03-19
updated: 2026-04-17
sources: [docs/competitive_analysis.md, docs/market_validation_2026-03-20.md]
---

## TLDR
"Security Scanner" → "Safety Scanner for Vibe-Coded Apps"로 확장.
2026-04-17 **사용자 피드백으로 a11y 포지셔닝 검증됨**: 바이브 코딩 프로젝트는 security보다 a11y 이슈가 더 많이 걸림.
퍼널: **Google 검색 → per-repo SEO 페이지 → Marketplace 설치** (일회성 포스트에서 영구 자산으로 전환).

## Content

### 포지셔닝 문장
**For vibe coders** who build apps with AI but don't know if they're safe,
**VibeSafe** is a free safety scanner that checks your code in 30 seconds
and tells your AI exactly how to fix every issue.
**Unlike** Snyk, CodeQL, or manual security audits,
VibeSafe requires zero security knowledge — paste a URL, get results, copy the fix prompt.

### 퍼널 구조
```
웹 스캐너 (체험, 무료, 즉시)
    ↓ "Want this on every PR?"
GitHub Action 설치 (원클릭 YAML)
    ↓ 반복 사용
습관화 → 입소문
```

### 타겟 메시지
| 대상 | 메시지 | 채널 |
|------|--------|------|
| 바이브 코더 (초보) | "AI가 만든 코드, 안전한지 확인해봤나?" | OKKY, Reddit |
| 시니어/리드 | "AI 코드 보안 실태 데이터" | LinkedIn |
| 보안 담당자 | "AI 코드 위험 통계" | dev.to, r/netsec |

### 실험 결과
- OKKY (한국): 772뷰, 댓글 3개 (긍정적). "크로스 체크 필수" 공감.
- dev.to (영어): 반응 없음. 경쟁 콘텐츠가 너무 많음.
- LinkedIn: 미시도. 0-audience에서 follower-based 플랫폼은 기각 ([[decisions/rejected.md]]).

### 사용자 검증 (2026-04-17)
OKKY 유저 "코딩숙" 댓글 (+1 upvote):
> "이거 써봤는데 스크린 리더 항목도 걸려서 보안은 아니고 접근성 문제도 함께 잡네요 **제 바이브 코딩 프로젝트는 보안성보다는 다 이쪽으로 걸렸습니다**"

**시사점**:
1. 첫 실제 유저 validation
2. 바이브 코딩 = security < **a11y** 이슈 지배적 (n=1 anecdotal이나 direction 강함)
3. "Security Scanner" 프레이밍은 **undersell**. 현실은 a11y가 더 많이 걸리는데 유저는 security 기대하고 옴 = 기대-경험 misalignment
4. "Safety" 확장 전략이 사후 검증됨 ([[decisions/log.md]] 2026-03-22 a11y 추가 결정)

### 포지셔닝 조정 액션 (검토 중)
| 노출 지점 | 현재 | 제안 |
|----------|------|------|
| README 첫 문장 | "Is it safe to ship?" | 유지 (이미 safety) |
| Marketplace description | "SAST + secret detection" | "+ WCAG 2.1 accessibility" 추가 |
| Home subtitle | "Find out in 30 seconds" | "Security + accessibility audit in 30 seconds" (A/B 검토) |

## Open Questions
- Marketplace 설명에 a11y 추가 시 install_clicks 변화? (측정 필요)
- Home subtitle 바꾸면 scans_started 전환율 변화? (A/B 테스트)
- 추가 유저 testimonial 확보 필요 (n=1 → n≥3)

## Related
- [[product/vision.md]]
- [[marketing/channels.md]]
- [[marketing/messages.md]]

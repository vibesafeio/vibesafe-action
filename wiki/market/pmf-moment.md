---
title: PMF Moment
type: market
confidence: medium
created: 2026-03-20
updated: 2026-04-23
sources: [docs/market_validation_2026-03-20.md]
---

## TLDR
진짜 PMF = "실제 사용자 데이터를 다루기 시작한 솔로 개발자"가 VibeSafe를 발견하는 순간.
결제 연동, 회원가입 구현 시점에서 불안감이 극대화된다.

## Content

### PMF 가설
바이브 코더가 VibeSafe를 필요로 하는 정확한 순간:
1. 사이드 프로젝트에 **실제 사용자**가 생김
2. **결제** 또는 **개인정보**를 다루기 시작
3. "이거 해킹당하면 어떡하지?" 불안감 발생
4. → 이 순간 "무료 보안 스캔" 검색

### 트리거 이벤트
- Stripe/토스페이먼츠 연동
- 회원가입/로그인 구현
- Supabase/Firebase에 사용자 데이터 저장
- 첫 번째 "실제 사용자" 가입

### 이 순간 VibeSafe에 도달하는 경로 (2026-04-23 기준)
| 경로 | 상태 | 블로커 |
|------|------|--------|
| Google 검색 ("flask security check" 등) | SEO 기반 구축됨 (17 seed + SSR body). 3개월 GSC 데이터 = 1 impression / 1 click | 인덱싱 latency. seed 풀 작아서 long-tail 커버리지 제한적 |
| GitHub Marketplace 검색 | ✅ v0.1.1 등재 (2026-04-17) | 검색어 전환율 미측정 |
| 도구 디렉토리 (awesome-lists) | 초안 완료 (docs/awesome_lists_prs.md), PR 미제출 | user action 대기 |
| 커뮤니티 포스트 (HN/Reddit) | 초안 완료 (docs/hn_reddit_post_draft.md), 미게시 | user action 대기 |
| 직접 referral (OKKY 등) | OKKY 1건 (2026-04-11, 772뷰) | 반복 게시 시 반응 체감 감소 |

### 근본 병목 (2026-04-23)
3개월간 GSC impression 1건 = **유입 자체가 없다.** stars 6일째 정체.
근본 원인: SEO 자산은 있는데 "검색 품질 → 랭킹" 고리가 작동하지 않음.
- thin-content (487 chars)이었음 → 2026-04-23 SSR로 해결 (1500+ chars, per-URL 고유)
- 백링크 0 → Awesome Lists PR로 해결 예정 (user action)

## Open Questions
- SSR 배포 후 GSC impression 증가 latency? (1-4 weeks 예상)
- "결제 연동" 키워드로 SEO 가능한가? (현재 seed에는 payment 관련 콘텐츠 없음)
- Lovable/Bolt 커뮤니티에서 이 순간의 질문이 올라오는가?

## Related
- [[market/segments.md]]
- [[marketing/messages.md]]
- [[engineering/architecture.md]] — SSR body 구현

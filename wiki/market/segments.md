---
title: User Segments
type: market
confidence: high
created: 2026-03-19
updated: 2026-04-12
sources: [docs/market_validation_2026-03-20.md, docs/vc-response.md]
---

## TLDR
Primary: B세그먼트 (AI-assisted 솔로 빌더). 보안 지식 없지만 실제 사용자 데이터를 다루기 시작한 개발자.
A(비개발자), C(팀), D(엔터프라이즈)는 현재 단계에서 제외.

## Content

### 세그먼트 MECE 분류
| 세그먼트 | 설명 | VibeSafe 적합도 |
|----------|------|----------------|
| A. 완전 비개발자 | Lovable/Bolt로 처음 만드는 사람 | ❌ GitHub 안 씀 |
| **B. AI-assisted 솔로 빌더** | **Cursor/Claude로 만드는 개인 개발자** | **✅ Primary** |
| C. 소규모 팀 | 2-5명, AI 적극 사용 | ⚠️ Phase 2 |
| D. 엔터프라이즈 | 보안팀 있음 | ❌ Snyk/Wiz 사용 |

### B세그먼트 상세
- **페르소나**: Cursor/Claude로 사이드 프로젝트 만드는 개발자
- **보안 인식**: "보안? 나중에" → 사용자가 생기면 갑자기 불안해짐
- **PMF 순간**: "실제 사용자 데이터를 다루기 시작한 순간" (결제 연동, 회원가입 구현 등)
- **행동 패턴**: GitHub 사용, PR 워크플로 이해, AI 도구에 의존

### TAM 계산
```
전체 개발자: ~28M (GitHub)
AI 코딩 도구 사용 (84%): ~23.5M
보안 의식 있음 (30%): ~7M
무료 도구 시도 의향 (50%): ~3.5M
= Immediate TAM: ~3.5M
```

### B세그먼트 하위 분류 (2026-04-17 추가)
| 하위 | 설명 | 전략 |
|------|------|------|
| B1. 불안형 | Moltbook/Lovable 기사 읽고 불안 | 충격 콘텐츠 → "확인하는 데 30초" |
| B2. 무관심형 | "내 앱은 작아서 괜찮다" | 직접 스캔 결과 보여주기 (URL 스캔) |
| B3. 행동형 | 이미 보안 도구 검색 중 | Marketplace + SEO |

- B3가 현재 유입 (123 clones)
- B2가 가장 큰 풀. URL 스캔으로 B2→B1 전환이 핵심
- 진짜 PMF 트리거: "사용자가 생겼다"가 아니라 **"사용자의 데이터를 받기 시작한 순간"** (회원가입 폼, 결제 연동)

### 가장 큰 경쟁자 = "아무것도 안 하는 것"
B 세그먼트는 Snyk을 고려한 적이 없다. 경쟁은 "VibeSafe vs Snyk"이 아니라 **"30초 투자 vs 아무것도 안 함"**.

## Open Questions
- 한국 vs 글로벌 B세그먼트의 행동 차이?
- URL 스캔 → Action 설치 전환율은?

## Related
- [[market/validation.md]]
- [[market/pmf-moment.md]]
- [[marketing/messages.md]]

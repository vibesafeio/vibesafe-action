---
title: Security Incidents in AI-Generated Code
type: market
confidence: high
created: 2026-03-19
updated: 2026-04-12
sources: [docs/market_research_2026-03-19.md]
---

## TLDR
실제 사고 3건이 "AI 코드 = 위험"을 증명. Lovable 18K 유저, Moltbook 1.5M 키, Escape 5600 앱.
이 데이터가 VibeSafe 존재 이유의 핵심 근거.

## Content

### 주요 사고
| 사건 | 규모 | 취약점 |
|------|------|--------|
| Lovable | 18,000 유저 노출 | 16개 취약점 (6 critical) |
| Moltbook | 1.5M API 키 + 35K 이메일 유출 | 하드코딩된 시크릿 |
| Escape | 5,600개 앱 → 2,000+ 취약점 | 400+ 시크릿 노출 |

### 통계
- AI 생성 코드의 24.7%에 보안 결함 (2026)
- GitHub 커밋의 51%+가 AI 생성/보조 (2026 Q1)
- CodeRabbit: AI 코드 리뷰 시 취약점 2.74x 더 발견

### Palo Alto Unit 42 인용
> "Coding agents optimize for making code run, not making code safe"

## Open Questions
- 2026 Q2 이후 새로운 대형 사고?
- 한국 내 AI 코드 보안 사고 사례?

## Related
- [[product/vision.md]]
- [[market/validation.md]]

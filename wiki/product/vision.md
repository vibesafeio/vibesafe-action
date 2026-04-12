---
title: VibeSafe Vision
type: product
confidence: high
created: 2026-03-18
updated: 2026-04-12
sources: [docs/competitive_analysis.md, docs/vc-response.md]
---

## TLDR
VibeSafe는 AI로 만든 앱의 보안을 자동으로 검사하는 무료 오픈소스 도구.
"Safety Scanner for Vibe-Coded Apps" — PR마다 보안 점수 + 수정 방법을 알려준다.
코딩을 모르는 바이브 코더도 30초 안에 보안 상태를 확인할 수 있다.

## Content

### 왜 존재하는가
- AI 생성 코드의 24.7%에 보안 결함이 있다 (2026 데이터)
- AI는 "코드가 돌아가게" 최적화하지, "코드가 안전하게"는 신경 안 쓴다 (Palo Alto Unit 42)
- 바이브 코더는 보안 지식이 없어서 취약점이 있는지조차 모른다
- 실제 사고: Lovable 18K 유저 노출, Moltbook 1.5M API 키 유출

### 핵심 가치 제안
1. **무료** — $0. 경쟁사는 API 비용 또는 $35K+
2. **30초 설치** — 24줄 YAML. 경쟁사는 pip + API 키 또는 빌드 설정
3. **행동 가능** — "뭐가 틀렸다"가 아니라 "이렇게 고쳐라" + AI에 붙여넣을 프롬프트
4. **PR 네이티브** — 코드 리뷰 흐름에 자연스럽게 통합

### 5-Gap Framework
| Gap | 문제 | VibeSafe 해결 |
|-----|------|-------------|
| Setup | 설치가 어렵다 | 24줄 YAML, 원클릭 |
| Awareness | 위험을 모른다 | 자동 스캔 + 점수 |
| Actionability | 뭘 고쳐야 하는지 모른다 | Fix 제안 32패턴 + AI 프롬프트 |
| Timing | PR 때는 늦다 | MCP 서버 (코딩 시점) + pre-commit hook |
| Trust | 도구를 믿을 수 있나 | Semgrep 기반 (Snowflake, Dropbox 사용) |

## Open Questions
- "Safety Scanner"로의 포지셔닝 확장 (보안 → 보안+접근성+비용)이 혼란을 줄 수 있는가?

## Related
- [[product/positioning.md]]
- [[market/validation.md]]
- [[market/incidents.md]]

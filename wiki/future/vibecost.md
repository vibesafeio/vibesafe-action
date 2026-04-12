---
title: VibeCost
type: future
confidence: low
created: 2026-03-20
updated: 2026-04-12
sources: [docs/vc-response.md]
---

## TLDR
코드 비용 패턴 스캐너. 설계 완료. 시장 검증 미완. 대기 중.
별도 repo: ~/Desktop/vibecost/

## Content

### 컨셉
AI가 생성한 코드에서 비용 폭탄 패턴을 탐지:
- N+1 쿼리
- 무한 루프 API 호출
- 캐시 없는 반복 DB 조회
- 과도한 로깅

### 설계 원칙
- 달러 추정치 제공하지 않음 (정확하지 않아서)
- 높은 정확도 규칙만 포함 (오탐 최소화)
- VibeSafe와 같은 구조 (Semgrep 기반)

### 현재 상태
- 설계 문서 완료
- 구현 미시작
- VibeSafe 사용자 확보 후 재검토

## Open Questions
- 비용 공포가 실제 사용자 행동을 바꾸는가?
- VibeSafe에 통합할 것인가, 별도 프로덕트로 갈 것인가?

## Related
- [[decisions/rejected.md]]
- [[product/roadmap.md]]

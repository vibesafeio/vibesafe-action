---
title: Rejected Decisions
type: decision
confidence: high
created: 2026-03-19
updated: 2026-04-12
sources: [docs/vc-response.md]
---

## TLDR
고려했지만 선택하지 않은 것들과 그 이유.

## Content

### VibeCost 즉시 개발 → 보류
**왜 안 했나:** 비용 공포가 실제 사용자 행동을 바꾸는지 미검증. VibeSafe 사용자 0명인 상태에서 두 번째 프로덕트 시작은 리소스 분산.
**재고 조건:** VibeSafe 사용자 100+ 확보 후

### 엔터프라이즈 타겟 → 제외
**왜 안 했나:** 사용자 0명에서 엔터프라이즈 영업 불가. Snyk/Wiz가 이미 장악.
**재고 조건:** B2C 또는 B2B2C로 사용자 기반 확보 후

### 유료 기능 즉시 출시 → 보류
**왜 안 했나:** 바이브 코더는 보안에 돈 안 냄 (지불 의향 ≈ 0). 무료로 사용자 확보 선행.
**재고 조건:** 사용자 1000+, 명확한 premium 수요 확인 시

### Wall of Shame 리더보드 → 거부
**왜 안 했나:** 타인 repo를 공개적으로 까는 건 법적 리스크 + 커뮤니티 반감
**재고 조건:** 재고하지 않음

### B2C 구독 ($9/month) → 보류
**왜 안 했나:** 바이브 코더가 보안에 월 구독 할 동기 없음. Private repo 스캔이 전환 트리거가 될 수 있으나 미검증.
**재고 조건:** 웹 스캐너에서 private repo 요청이 반복될 때

## Related
- [[decisions/log.md]]
- [[product/roadmap.md]]

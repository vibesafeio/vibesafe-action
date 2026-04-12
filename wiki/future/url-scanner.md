---
title: URL Scanner
type: future
confidence: high
created: 2026-03-26
updated: 2026-04-12
sources: [docs/iteration-log.md]
---

## TLDR
구현 완료. vibesafe.onrender.com에서 운영 중.
URL 입력 → 30초 스캔 → 점수 + 취약점 목록 + AI Fix 프롬프트 + 웜뱃 땅굴 리더보드.

## Content

### 현재 상태: ✅ 운영 중
- vibesafe.onrender.com
- GitHub public repo URL 입력
- cli_scanner.py --json --light 실행
- 90초 타임아웃 (대형 repo는 Action 설치 유도)
- 결과: 점수 + 등급 + 취약점 + Fix 프롬프트 + 리더보드

### 개발 이력
- 10차 이터레이션으로 완성 (docs/iteration-log.md 참조)
- JSON 파싱 오류, /tmp/ 경로 노출, 오탐 등 해결
- password-comparison-timing-js 규칙 오탐 문제 미해결

### 퍼널 역할
```
웹 스캐너 (체험) → "Want this on every PR?" → Action 설치
```

## Open Questions
- password-comparison-timing-js 오탐 해결?
- Render free tier sleep 문제 (첫 요청 느림)

## Related
- [[engineering/architecture.md]]
- [[product/positioning.md]]

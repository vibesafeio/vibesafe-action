---
title: Ideas Parking Lot
type: future
confidence: low
created: 2026-04-12
updated: 2026-04-12
sources: []
---

## TLDR
평가 전 아이디어 모음. 우선순위 미정.

## Content

### 제품
- **뱃지 엔드포인트**: README에 "VibeSafe Score: A" 뱃지. 공유 + 신뢰 신호.
- **diff-only 스캔**: 변경 코드만 스캔. 가장 큰 기술적 moat 기회. Semgrep OSS로 가능한지 검증 필요.
- **Supabase RLS 전용 규칙**: Supabase 사용 바이브 코더 타겟.
- **score_calculator.py --verbose**: 항목별 감점 상세 내역.
- **high >= 1이면 B 이상 불가**: 등급 캡 규칙.
- **공유 페이지 + Certified 뱃지 UI**: 스캔 결과 공유 전용 페이지.

### 마케팅
- **"AI 생성 코드 10개 스캔" 실험 콘텐츠**: LinkedIn 공유용 데이터.
- **Cursor vs Claude vs Copilot 보안 점수 비교**: 인플루언서가 공유할 콘텐츠.
- **Before/After 명예의 전당**: F→A+ 달성 프로젝트 하이라이트.
- **한국어 전용 마케팅**: OKKY 반응 좋음. 한국 시장 선점.

### 통합
- **MCP 서버 scan_file, scan_diff**: 현재 check_secret만 구현. IDE 통합 확장.
- **GitHub Marketplace 등록**: 발견 가능성 증대.
- **OpenClaw 전용 규칙**: CVE-2026-25253 대응.

## Open Questions
- 우선순위 평가 기준? (사용자 영향 × 구현 비용?)

## Related
- [[product/roadmap.md]]
- [[decisions/rejected.md]]

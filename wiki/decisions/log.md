---
title: Decision Log
type: decision
confidence: high
created: 2026-03-18
updated: 2026-04-12
sources: []
---

## TLDR
주요 결정 기록. 왜 그렇게 했는지, 대안은 뭐였는지.

## Content

### 2026-04-12: 웜뱃 땅굴 리더보드 추가
**결정:** 스캔 결과에 정규분포 시각화 (웜뱃 땅굴 모양) + 백분위 표시
**이유:** 공유 동기 부여 ("상위 X%") + LinkedIn 콘텐츠로 활용 가능
**대안:** 단순 숫자 리더보드 (재미 없음), Wall of Shame (법적 리스크)
**되돌릴 수 있나:** 예
**관련 페이지:** [[product/features.md]]

### 2026-04-12: 리더보드 seed 데이터 60개 추가
**결정:** 배포 즉시 분포가 보이도록 현실적인 AI 프로젝트 점수 60개를 seed
**이유:** total < 2이면 burrow 섹션이 안 보임. 첫 사용자 경험 중요.
**대안:** 빈 상태로 시작 (첫 사용자가 분포 못 봄)
**되돌릴 수 있나:** 예
**관련 페이지:** [[engineering/schema-notes.md]]

### 2026-03-26: 웹 스캐너 (URL 입력) 추가
**결정:** GitHub URL 입력 → 30초 스캔 → 결과 페이지
**이유:** 체험 → Action 설치 퍼널. "써보지도 않고 설치하라"는 안 됨.
**대안:** Action만 제공 (전환율 낮음)
**되돌릴 수 있나:** 예
**관련 페이지:** [[product/positioning.md]]

### 2026-03-22: 접근성 스캔 추가
**결정:** img alt, label, lang 등 접근성 규칙 VibeSafe에 포함
**이유:** "Security" → "Safety" 확장. ADA 소송 4,000+건/년 = 실제 리스크.
**대안:** 보안만 집중 (scope 좁음)
**되돌릴 수 있나:** 예
**관련 페이지:** [[future/accessibility.md]]

### 2026-03-20: 웜벳 마스코트 확정
**결정:** 픽셀 웜벳. 땅 파는 애니메이션 (스캔 로딩).
**이유:** 웜벳 = 땅을 파서 안전한 굴을 만드는 동물 = 보안 메타포
**대안:** 방패 아이콘 (generic), 로봇 (AI 클리셰)
**되돌릴 수 있나:** 예
**관련 페이지:** [[product/positioning.md]]

### 2026-03-19: 외부 repo 자동 PR 중단 (사고 후)
**결정:** 외부 repo에 자동 PR/이슈 생성 절대 금지
**이유:** firetix, VibesDIY, mpaepper에 자동 PR → 2건 거절, 1건 Vercel 배포 (비용 발생)
**대안:** 계속 자동 PR (사용자 신뢰 파괴)
**되돌릴 수 있나:** 아니오 (이미 신뢰 손상)
**관련 페이지:** [[engineering/failure-log.md]]

## Related
- [[decisions/rejected.md]]

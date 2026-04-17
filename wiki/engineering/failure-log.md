---
title: Failure Log
type: engineering
confidence: high
created: 2026-03-18
updated: 2026-04-17
sources: [docs/failure-log.md]
---

## TLDR
프로덕션 버그 7건 기록. 가장 위험한 패턴: 에러 없이 빈 결과를 반환하는 silent failure.
모든 버그에 방어 조치 추가됨.

## Content

### 2026-04-17: Render 웹서비스 OOM (메모리 초과 재시작)
- **원인**: (1) SCANS dict 무한 증가 — 스캔 결과를 메모리에 계속 쌓고 삭제 안 함. (2) Semgrep 메모리 400MB 설정이 Render free tier 512MB에서 여유 없음. (3) OOM kill 시 /tmp 클론 디렉토리 미정리.
- **결과**: 웹 스캐너 반복 재시작, 사용자 스캔 중단
- **교훈**: in-memory 저장소는 반드시 상한선 필요. 외부 서비스의 메모리 제한을 코드에 반영해야 함.
- **방어**: MAX_SCANS=50 LRU 삭제, SEMGREP_MAX_MEMORY 256MB, finally 블록에 /tmp 정리 추가

### 2026-04-12: from __future__ import annotations가 shebang 위에 위치
- **원인**: domain_rule_engine.py, secret_scanner.py 1행에 future import가 shebang 위에 있음
- **결과**: Python SyntaxError → 하네스 테스트 3개 실패
- **교훈**: future import는 docstring 뒤, shebang 아래에 위치해야 함
- **방어**: 수정 완료 + 하네스 통과 확인

### 2026-03-20: Semgrep --baseline-commit requires Pro
- **원인**: --baseline-commit가 OSS에서 동작한다고 가정
- **결과**: SAST exit 2, findings 0, PR 코멘트 미생성
- **교훈**: CLI 기능의 무료/유료 여부 반드시 확인
- **방어**: try-catch + baseline 실패 시 full scan fallback

### 2026-03-19: Action exit code always 0
- **원인**: action_entrypoint.sh가 항상 exit 0
- **결과**: README에 "머지 차단" 기능이라고 적었지만 실제로 차단 안 됨
- **교훈**: 핵심 보안 기능은 E2E 테스트 필수. README와 동작 일치 확인.
- **방어**: fail-on input 추가 (기본: critical). 임계치 초과 시 exit 1.

### 2026-03-19: 외부 repo에 자동 PR 전송 (Priority 1-2 위반)
- **원인**: KPI 압박 → firetix, VibesDIY, mpaepper repo에 자동 PR
- **결과**: 2건 거절, 1건이 Vercel 배포 트리거 (타인 인프라 비용 발생)
- **교훈**: 되돌릴 수 없는 외부 행동은 절대 자동화 금지
- **방어**: Priority 1-2 규칙 CLAUDE.md에 추가. 3건 모두 사과와 함께 닫음.

### 2026-03-18: Flask app triggers Django false positives
- **원인**: detect_stack이 requirements.txt만 확인 → import 기반 프레임워크 미감지
- **결과**: Flask 프로젝트에서 Django 관련 오탐 4건
- **교훈**: 의존성 파일 없는 프로젝트 많음. 코드 내용 기반 감지 필요.
- **방어**: Python import 스캔 추가 (sast_runner.py)

### 2026-03-18: git safe.directory not set → Semgrep 0 findings
- **원인**: Docker에서 /github/workspace를 trust하지 않음 → git ls-files exit 128
- **결과**: Semgrep이 0 파일 스캔 → 0 findings → "안전합니다" 표시 (치명적 오류)
- **교훈**: Docker + git = 반드시 safe.directory 설정. Semgrep은 이 실패에 exit 0 반환 (silent failure).
- **방어**: action_entrypoint.sh에 `git config --global --add safe.directory` 추가

### 2026-04-15: password-comparison-timing-js 전역 오탐
- **원인**: Semgrep의 `password-comparison-timing-js` 규칙이 모든 `===` 비교를 잡음. 실제 비밀번호 비교와 무관한 코드까지 critical로 보고.
- **결과**: 클린 프로젝트에서도 거짓 경고 발생 → 리더보드 점수 왜곡
- **교훈**: 고 오탐률 규칙은 NOISY_RULES 필터에 등록하는 구조적 방어가 필요.
- **방어**: `tools/shared.py`의 NOISY_RULES에 `password-comparison-timing` 등록 (커밋 9409553).

## Open Questions
- (없음)

## Related
- [[engineering/hard-rules.md]]
- [[engineering/deploy-gates.md]]

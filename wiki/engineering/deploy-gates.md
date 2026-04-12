---
title: Deploy Gates
type: engineering
confidence: high
created: 2026-03-18
updated: 2026-04-12
sources: [docs/harness-protocol.md]
---

## TLDR
커밋 전 5개 게이트 통과 필수. 하나라도 실패하면 push 금지.
3회 수정 실패 시 중단 + failure-log 기록.

## Content

### 5개 게이트
| # | 게이트 | 명령 | 언제 |
|---|--------|------|------|
| 1 | 실행 검증 | `python3 <file> --help` + `test/e2e_pipeline_test.py` | 항상 |
| 2 | Docker 빌드 | `docker build -f Dockerfile.action -t vibesafe-test .` | tools/ 변경 시 |
| 3 | Docker 스캔 | vulnerable fixture → critical >= 1, clean → score >= 90 | tools/ 변경 시 |
| 4 | 룰 검증 | `domain_rule_engine.py --validate` | 항상 |
| 5 | 오탐 검증 | ambiguous fixture → false positive 없음 | tools/ 변경 시 |

### Quick 모드
`test/harness.sh quick` — Gate 2, 3, 5 스킵. 코드만 검증.

### Failure Protocol
1. 실패 → 최대 3회 자동 수정 시도
2. 3회 실패 → 멈추고 failure-log에 기록
3. 같은 파일 3회+ 수정 (doom loop) → 접근 방법 재고

### Silent Failure Check
가장 위험한 버그 = 에러 없이 빈 결과 반환:
- subprocess가 빈 결과 반환해도 에러 안 남
- 파일 미존재 → 빈 리스트 기본값
- JSON 키 누락 → 빈 값으로 대체

## Open Questions
- 없음

## Related
- [[engineering/hard-rules.md]]
- [[engineering/failure-log.md]]

---
title: Schema Notes
type: engineering
confidence: medium
created: 2026-03-18
updated: 2026-04-12
sources: []
---

## TLDR
현재 데이터베이스 없음. 모든 상태 in-memory (server.py).
리더보드 seed 데이터 60개. 재배포 시 리셋.

## Content

### 현재 데이터 구조
| 변수 | 타입 | 용도 | 영속성 |
|------|------|------|--------|
| SCANS | dict[str, dict] | 스캔 결과 (scan_id → result) | 메모리 (재배포 리셋) |
| SCORES | list[int] | 리더보드 점수 | 메모리 (seed 60개 + 런타임 추가) |
| METRICS | dict[str, int] | 분석 카운터 | 메모리 (재배포 리셋) |

### Render 배포
- 자동 배포: master push → Render 자동 빌드
- Free tier: 메모리 제한, 비활성 시 sleep
- 영속 저장소 없음 (파일 시스템도 ephemeral)

## Open Questions
- Render에 persistent disk 추가할 것인가? ($7/month)
- SQLite로 전환 시 이점? (리더보드 데이터 보존)
- 스캔 결과를 GitHub Gist 등 외부에 저장하는 방안?

## Related
- [[engineering/architecture.md]]

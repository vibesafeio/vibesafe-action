---
title: Schema Notes
type: engineering
confidence: medium
created: 2026-03-18
updated: 2026-04-17
sources: []
---

## TLDR
데이터베이스 없음. 모든 상태 in-memory (server.py). 리더보드 seed 60개, REPORTS 캐시 LRU 500.
재배포 시 리셋. `/report/` URL은 캐시 miss 시 auto-rescan으로 stable-feeling.

## Content

### 현재 데이터 구조
| 변수 | 타입 | 용도 | 영속성 | 상한 |
|------|------|------|--------|------|
| SCANS | dict[str, dict] | 진행 중/완료 스캔 (scan_id → result) | 메모리 (재배포 리셋) | LRU 50 |
| SCORES | list[int] | 리더보드 점수 | 메모리 (seed 60 + 런타임 추가) | 무제한 (메모리 상 OK) |
| REPORTS | dict[str, dict] | Per-repo 영구 캐시 (`owner/repo` key) | 메모리 (재배포 리셋) | **LRU 500** |
| METRICS | dict[str, int] | 분석 카운터 (page_views, report_views, scans_*, fix_copies, install_clicks) | 메모리 (재배포 리셋) | 고정 키 집합 |

### REPORTS 캐시 — SEO 페이지 source
- key: `"owner/repo"` (github URL에서 추출, 대소문자/확장자 정규화)
- value: `{owner, repo, url, results, scanned_at}`
- 쓰기: 스캔 완료 시 `_save_report()` 자동 호출
- 읽기: `GET /api/report/...` 또는 `/report/...` 페이지 렌더 시
- **크롤링**: `/sitemap.xml`이 `REPORTS.keys()` 순회
- **Miss 시 동작**: 프론트엔드가 자동 re-scan 트리거 → 유저는 URL이 stable한 것처럼 경험

### Render 배포
- 자동 배포: master push → Render 자동 빌드
- Free tier: 메모리 제한 (512MB), 비활성 시 sleep
- 영속 저장소 없음 (파일 시스템도 ephemeral)
- **결과**: REPORTS + SCORES + METRICS가 재배포마다 리셋. 현재 단계(소규모 트래픽)에서 허용 가능.

## Open Questions
- REPORTS 영속화 전환 시점? (N > 500 또는 재배포 빈도 문제 될 때)
- 후보: Supabase 무료 tier, Upstash Redis, Render persistent disk ($7/mo), GitHub Gist (hacky)
- SCORES 복원: 현재 seed 60 고정 → 실 데이터 점점 쌓이는데 재배포로 소실. 영속화 1순위 후보.
- Sitemap 크기 상한 (50MB/50K URL) — 현재 규모에서는 무관, 수만 URL 넘어가면 분할 고려

## Related
- [[engineering/architecture.md]]

---
title: Marketing Results & KPI Tracking
type: marketing
confidence: high
created: 2026-03-20
updated: 2026-04-12
sources: [docs/vc-response.md]
---

## TLDR
Phase 1 KPI 목표: Stars 100, Installs 50, Re-run 50%.
현재: OKKY 772뷰가 유일한 유의미한 지표. 나머지 미측정 또는 0.

## Content

### Phase 1 KPI
| Metric | Target | Current (2026-04-17 20:46 KST) | Gap |
|--------|--------|--------------------------------|-----|
| Stars | 100 / 4주 | **6** | 94 부족 |
| Action installs | 50 repos / 4주 | **0 (install_clicks)** | 50 부족 |
| Re-run rate | 50%+ | N/A | 데이터 없음 |

### Baseline Snapshot (2026-04-17 20:46 KST)
P0 (UTM + Marketplace + Install CTA) 배포 직후 측정. Day+3 (2026-04-20) 비교 기준.

| 지표 | 값 |
|------|-----|
| Stars | 6 |
| Forks | 1 |
| Watchers | 0 |
| Render `page_views` (생애) | 3 |
| Render `scans_started` | 2 |
| Render `scans_completed` | 1 |
| Render `install_clicks` | **0** |
| Render `fix_copies` | 0 |
| GitHub Marketplace | ✅ HTTP 200 (listing live) |
| Marketplace "Latest" tag | ✅ v0.1.1 (사용자가 UI에서 수정 완료, 2026-04-17) |

### 2026-04-17 세션 작업 요약 (프로덕트 레벨 변경)

**전략 pivot**: 일회성 포스트 유입 → **영구 SEO 자산** (per-repo 랜딩 페이지)

| 변경 | 커밋 | KPI 연결 |
|------|------|----------|
| score_calculator `--verbose` + high≥1→B cap | 900fd15 | (품질) 유저가 감점 원인 이해 |
| UTM 태깅 + server capture | c370c04 | 유입 소스 측정 가능 |
| Marketplace 등재 (v0.1.1 Latest) | — (UI) | 무료 distribution 채널 오픈 |
| Marketplace 뱃지 + baseline | b6cf524 | README 신뢰 |
| Next.js manifests 제거 | 6e73fd9 | Dependabot 28 vulns 소멸 |
| **Per-repo SEO 랜딩 + sitemap + robots.txt** | e10c6f5 | **SEO 자산 복리화** |
| secret_scanner test-path 제외 (self-scan F→A) | 49e7ae6 | 모든 사용자 점수 왜곡 수정 |
| 분포 차트 통합 (preview + burrow) | 31d2ebb | UX 일관성 |
| 업라이트 바 차트 전환 | e5ac2d3 | 차트 가시성 |
| 중복 Install CTA 제거 (3→1) + 404 버튼 제거 | e5ac2d3, 7a6ac3e | 첫 방문자 혼란 해소 |

### 채널별 성과
| 채널 | 지표 | 날짜 |
|------|------|------|
| OKKY | 772뷰, 댓글 4개 (+"코딩숙" a11y 피드백) | 2026-04-11 |
| dev.to | 0 반응 | 2026-04-12 |
| GeekNews | 게시 완료, 대기 중 | 2026-04-12 |
| 웹 스캐너 | 3 page views, 2 scans 시도 (1 성공, 1 실패) | 2026-04-17 |
| GitHub | 19 views, 22 clones (14d) | 2026-04-12 |
| Marketplace | 등재 완료 + v0.1.1 Latest | 2026-04-17 |
| **SEO 페이지** (`/report/...`) | live, sitemap 크롤링 대기 | 2026-04-17 |

### 채널별 성과
| 채널 | 지표 | 날짜 |
|------|------|------|
| OKKY | 772뷰, 댓글 3개 | 2026-04-11 |
| dev.to | 0 반응 | 2026-04-12 |
| GeekNews | 게시 완료, 대기 중 | 2026-04-12 |
| 웹 스캐너 | 3 page views, 2 scans 시도 (1 성공, 1 실패) | 2026-04-17 |
| GitHub | 19 views, 22 clones (14d) | 2026-04-12 |
| Marketplace | 등재 완료 | 2026-04-17 |

### 메트릭 대시보드
- 웹: `vibesafe.onrender.com/api/metrics`
- 이벤트: page_views, scans_started, scans_completed, fix_copies, install_clicks
- GitHub: `gh api repos/vibesafeio/vibesafe-action` (stars, forks, clones)

### 리더보드 데이터
- Seed: 60개 점수 (평균 34.8)
- 분포: 0-29점 대에 31개 집중 (현실적)
- 실 스캔 점수가 추가되면서 분포 업데이트됨

### Day+3 측정 계획 (2026-04-20)

| 메트릭 | Baseline (04-17) | Target (04-20) | 체크 방법 |
|--------|------------------|----------------|-----------|
| Stars | 6 | ≥ 10 | `curl api.github.com/repos/vibesafeio/vibesafe-action` |
| Render `page_views` | 3 | ≥ 20 | `curl vibesafe.onrender.com/api/metrics` |
| Render `install_clicks` | 0 | ≥ 1 | 같음 |
| UTM 분포 (top 3 소스) | N/A | 식별 | Render 로그 `grep "[METRIC].*utm=" | sort | uniq -c` |
| Marketplace traffic | 시작 | 측정 시작 | Marketplace analytics (사용자 수동 확인) |
| SEO 페이지 인덱싱 | 0 | sitemap 크롤링 확인 | Google Search Console (사용자 필요) |

## Open Questions
- SEO 페이지 Google 인덱싱 latency? (사이트맵 제출 후 N일)
- Marketplace 유입이 실제 install로 전환되는 비율?
- "코딩숙" 같은 anecdotal 피드백 누적 → testimonial 활용 시점?

## Related
- [[marketing/channels.md]]
- [[market/validation.md]]

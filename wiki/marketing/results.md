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

### Day+3 측정 계획 (2026-04-20) — 결과

| 메트릭 | Baseline (04-17) | Target (04-20) | 실측 (04-23) | 결과 |
|--------|------------------|----------------|---------------|------|
| Stars | 6 | ≥ 10 | **6** | ❌ miss (Δ=0) |
| Render `page_views` | 3 | ≥ 20 | 0 (ephemeral) | ❌ 측정 불가 |
| Render `install_clicks` | 0 | ≥ 1 | 0 (ephemeral) | ❌ 측정 불가 |
| UTM 분포 | N/A | 식별 | 데이터 없음 | n/a |
| Marketplace traffic | 시작 | 측정 시작 | 미확인 | user 수동 확인 필요 |
| SEO 페이지 인덱싱 | 0 | sitemap 크롤링 확인 | **17 URL 인덱싱됨, 3개월 1 impression** | ❌ 유입 없음 |

**진단**: 배포 인프라 완성, 유입 채널 전무. stars 증가 0의 근본 원인 = 외부 유입 경로 미활성 (HN/Reddit/Awesome Lists 포스팅 대기).

### 2026-04-19 세션: a11y 규칙 구조 수정

| 변경 | 커밋 | 배경 |
|------|------|------|
| Popular scans 홈 그리드 (17 seed 카드) | d3a6ba9 | SEO 페이지를 사람 유입 경로로 노출. sitemap은 사람이 안 봄. |
| `[METRIC_EVENT]` stdout parseable 포맷 | d3a6ba9 | Render 로그 replay로 누적 메트릭 복원 가능 |
| `/api/badge/:owner/:repo` (shields.io 호환) | d2c4a7e | README 뱃지 유입 경로 |
| a11y 규칙 WARNING → INFO | d2c4a7e | 4 F 레포 (continue/payload/trpc/shadcn) 원인 = `a11y-input-missing-label` FP (htmlFor 패턴 미감지). 구조적 FP → severity 다운그레이드로 점수 살림. |
| 재seed 17 repo | ae2fec5 | F 소멸: A:12 / B:2 / C:3 |
| HEAD routing → do_GET alias | 04ea0ff | `curl -I /sitemap.xml` 404 text/html 버그 (SimpleHTTP static handler fallthrough) |
| Google Search Console verify meta | d2c4a7e | user action 미실행 시점에서 선행 준비 |
| Awesome Lists PR 초안 x3 | 7866e87 | user 수동 제출 대기 |
| HN/Reddit 데이터 포스트 초안 | 7866e87 | user 수동 게시 대기 |

### 2026-04-23 세션: SEO content quality

| 변경 | 커밋 | 근거 |
|------|------|------|
| `/report/` SSR body | adfaf57 | GSC 실측: 3개월 1 impression. 원인 = 17 URL이 JS SPA 때문에 Googlebot에 487 chars duplicate. SSR로 per-URL 1500+ chars 고유 콘텐츠 (score + stack + findings + keywords). |

## Open Questions
- SSR 배포 후 GSC impression 증가 시점? (1-4 weeks 예상, 2026-05-07까지 재측정)
- 유입이 없으면 KPI 측정 자체가 의미 없음 — user action 타임라인?
- 메트릭 ephemeral 문제: Render 로그 7일 retention → 로그 aggregation 스크립트 필요 시점 판단

## Related
- [[marketing/channels.md]]
- [[market/validation.md]]

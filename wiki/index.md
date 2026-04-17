---
title: VibeSafe Knowledge Index
type: index
updated: 2026-04-17
---

# VibeSafe Wiki Index

이 파일을 세션 시작 시 가장 먼저 읽는다.
질문이 오면 여기서 관련 페이지를 찾고, 해당 페이지만 읽는다.

## Current State (2026-04-17)
- **Phase:** Post-launch, P0 distribution 배포 완료. 일회성 포스트 → 영구 SEO 자산 전환.
- **Stack:** GitHub Action + Docker + Semgrep + Custom Rules + Web Scanner (Render) + **Per-repo SEO 랜딩 페이지**
- **Channels:**
  - OKKY (772뷰, 댓글 4개 — 2026-04-17 "코딩숙" 실제 유저 피드백 확보)
  - dev.to (반응 없음)
  - GeekNews (발행)
  - **GitHub Marketplace (2026-04-17 등재, v0.1.1 Latest)**
  - **Per-repo SEO (sitemap + robots.txt live, 인덱싱 대기)**
  - ~~Twitter/LinkedIn~~ (기각: 0-audience에서 follower-based = dead)
- **KPI (2026-04-17 20:46 KST baseline):** Stars **6**, install_clicks **0**, page_views **3**. Day+3 (2026-04-20) 재측정 예정.
- **Mascot:** 픽셀 웜벳 (확정). 분포 차트는 **업라이트 바 차트**로 전환 (가시성 우선).
- **Comms style:** SV (Action + Owner + Deadline + Metric) + Musk 제1원칙 (facts first). CLAUDE.md에 고정.

## Page Directory

### Product
| Page | What | Confidence |
|------|------|------------|
| [[product/vision.md]] | 왜 VibeSafe가 존재하는지. "Safety Scanner for Vibe-Coded Apps" | high |
| [[product/roadmap.md]] | 현재 상태 + 다음 할 것 + 안 할 것 | high |
| [[product/features.md]] | SAST+SCA+Secret+CustomRules+FixSuggestions+MergeBlocking+PreCommit+MCP+Badge 상태 | high |
| [[product/positioning.md]] | "보안 스캐너" → "Safety Scanner" 확장. URL 스캔 → Action 퍼널 | medium |

### Market
| Page | What | Confidence |
|------|------|------------|
| [[market/segments.md]] | B세그먼트(AI-assisted 솔로 빌더) = Primary. A/C/D 제외 이유 | high |
| [[market/competitors.md]] | VibeWrench, Secto, VibeEval 등 10+ 도구 비교. 차별점: PR 자동화+머지 차단 | high |
| [[market/validation.md]] | "관심→행동" 전환이 카테고리 전체의 미해결 문제. acknowledge and ship | high |
| [[market/incidents.md]] | Moltbook 1.5M 토큰, Lovable 18K 유저, CodeRabbit 2.74x 통계 | high |
| [[market/pmf-moment.md]] | 진짜 PMF = "실제 사용자 데이터를 다루기 시작한 솔로 개발자" | medium |

### Engineering
| Page | What | Confidence |
|------|------|------------|
| [[engineering/architecture.md]] | SAST→Secret→SCA→Score→PR Comment 파이프라인 | high |
| [[engineering/failure-log.md]] | 버그 이력 12건+ 근본 원인 + 방어 | high |
| [[engineering/hard-rules.md]] | Python 3.9, subprocess, Semgrep pack 등 절대 규칙 | high |
| [[engineering/deploy-gates.md]] | E2E + Docker + 스캔 + 룰 검증 + 오탐 = 5개 게이트 | high |
| [[engineering/schema-notes.md]] | 데이터 구조 (in-memory), Render 배포, 영속성 미존재 | medium |

### Marketing
| Page | What | Confidence |
|------|------|------------|
| [[marketing/channels.md]] | OKKY/dev.to 발행. GeekNews 3/26 대기. Reddit karma 부족 | high |
| [[marketing/messages.md]] | 두 메시지: "AI 코드가 위험하다"(유입) + "사용자 생기면 네 책임"(전환) | medium |
| [[marketing/results.md]] | 2026-04-17 baseline (Stars 6, page_views 3, install_clicks 0). Day+3 측정 계획. | high |

### Decisions
| Page | What | Confidence |
|------|------|------------|
| [[decisions/log.md]] | URL 스캔 추가 결정, 접근성 확장, 웜벳 마스코트 확정 등 | high |
| [[decisions/rejected.md]] | VibeCost 보류 (비용 공포 미검증), 엔터프라이즈 타겟 제외 | high |

### Future
| Page | What | Confidence |
|------|------|------------|
| [[future/vibecost.md]] | 코드 비용 패턴 스캐너. 설계 완료. 시장 검증 미완. 대기 | low |
| [[future/accessibility.md]] | img alt, label, lang 등 접근성 룰 VibeSafe에 추가 계획 | medium |
| [[future/url-scanner.md]] | URL 붙여넣기 → 즉시 스캔. 체험 → Action 설치 퍼널. ✅ 운영 중 | high |
| [[future/ideas.md]] | 아이디어 파킹 (뱃지, diff-only, Supabase RLS 등) | low |

## Key Relationships
- market/validation ↔ market/segments: "관심→행동" 문제가 세그먼트 선택에 영향
- market/pmf-moment ↔ marketing/messages: PMF 순간이 메시지 전략을 결정
- engineering/failure-log ↔ engineering/hard-rules: 버그가 규칙을 만든다
- product/positioning ↔ future/accessibility: "Security" → "Safety" 확장. 2026-04-17 유저 피드백으로 validation ("a11y > security" in vibe-coded projects).
- marketing/results ↔ decisions/log: 측정된 KPI가 다음 결정의 input
- engineering/architecture ↔ marketing/results: SEO 페이지(/report/)가 유입 → install 퍼널의 top

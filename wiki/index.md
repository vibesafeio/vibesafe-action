---
title: VibeSafe Knowledge Index
type: index
updated: 2026-04-12
---

# VibeSafe Wiki Index

이 파일을 세션 시작 시 가장 먼저 읽는다.
질문이 오면 여기서 관련 페이지를 찾고, 해당 페이지만 읽는다.

## Current State (2026-04-12)
- **Phase:** Post-launch. OKKY 772뷰. 웹 스캐너 운영 중. 리더보드 추가.
- **Stack:** GitHub Action + Docker + Semgrep + Custom Rules + Web Scanner (Render)
- **Channels:** OKKY (772뷰, 댓글 3), dev.to (반응 없음), GeekNews (발행), LinkedIn (미시도)
- **KPI:** Stars ?, Installs ?, OKKY 772뷰
- **Mascot:** 픽셀 웜벳 (확정. 땅 파는 애니메이션 + 땅굴 리더보드)

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
| [[marketing/results.md]] | Views 5, Clones 406, Stars 0. 트래픽 문제. | high |

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
- product/positioning ↔ future/accessibility: "Security" → "Safety" 확장

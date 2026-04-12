---
title: Competitor Analysis
type: market
confidence: high
created: 2026-03-19
updated: 2026-04-12
sources: [docs/competitive_analysis.md, docs/market_research_2026-03-19.md]
---

## TLDR
직접 경쟁사 5개, 인접 경쟁사 4개. VibeSafe만의 차별점: 무료 + 24줄 설치 + 도메인 규칙 + Fix 제안.
하지만 moat는 없다 (주말이면 복제 가능). 속도만이 전략.

## Content

### 직접 경쟁사 (Vibe Coding Security)
| 도구 | 방식 | Stars | 강점 | 약점 |
|------|------|-------|------|------|
| SecureVibes | Claude 멀티에이전트 (5개) | ~200+ | 11언어, DAST, exploit chain | API 비용, 설정 복잡 |
| VibeSecurity | 웹 스캐너 (Go) | - | 웹 UI | Action 아님, CI 연동 없음 |
| VibePenTester | AI 펜테스터 | 159 | DAST | 정적 분석 아님 |
| ZeriFlow | 상용 스캐너 | - | 80+ 체크 | 클로즈드 소스, 가격 불명 |
| vibe-security-skill | Claude Code 스킬 | 201 | IDE 실시간 | MCP 경쟁 |

### 인접 경쟁사 (범용 SAST)
| 도구 | 특징 | VibeSafe 대비 |
|------|------|-------------|
| Semgrep Action | 무료(10인), PR 코멘트(유료) | VibeSafe가 내부 사용. 차별: 도메인 규칙 |
| CodeQL | 공개 레포 무료 | 빌드 설정 15분+ vs VibeSafe 30초 |
| Codacy | 코드 품질 중심 | VibeSafe는 보안 전문 |
| Gitleaks | Secret 전용, 24K stars | PR 코멘트 없음 |

### VibeSafe 차별점
1. **24줄 YAML, 30초 설치** — 경쟁사 중 유일
2. **도메인별 규칙 자동 선택** — 경쟁사 없음
3. **프레임워크 오탐 필터링** — 경쟁사 없음
4. **Fix 제안 32패턴** — 무료로 제공하는 곳 없음
5. **$0** — SecureVibes: API 비용, Snyk: $35K+

### 위협
1. SecureVibes가 GitHub Action 출시 → 직접 경쟁 (AI 비용이 장벽)
2. Semgrep이 도메인 규칙 추가 → 차별점 소멸 (엔터프라이즈 포커스라 가능성 낮음)
3. GitHub Copilot Autofix 확대 → Fix 제안 차별점 소멸

### 기회
1. **MCP 서버** — vibe-security-skill 201 stars가 수요 증명
2. **pre-commit hook** — 경쟁사 중 제공하는 곳 없음
3. **한국 시장** — 한국어 지원 바이브 코딩 보안 도구 없음
4. **diff-only 스캔** — 모든 경쟁사가 전체 repo 스캔. 이게 최대 moat

## Open Questions
- SecureVibes의 GitHub Action 출시 계획이 있는가?
- vibe-security-skill (201 stars)의 실제 활성 사용자 수?

## Related
- [[product/positioning.md]]
- [[market/validation.md]]

---
title: Decision Log
type: decision
confidence: high
created: 2026-03-18
updated: 2026-04-17
sources: []
---

## TLDR
주요 결정 기록. 왜 그렇게 했는지, 대안은 뭐였는지.

## Content

### 2026-04-23: `/report/` SSR body — thin-content 해결
**결정:** `/report/<owner>/<repo>` 페이지 body를 서버 렌더. 기존 JS SPA는 유지하되 initial HTML에 score/grade/stack/findings 포함.
**이유:** GSC 3개월 데이터 = 1 impression / 1 click. 17 URL이 동일한 487 char SPA shell만 노출 → Google duplicate/thin 판정. 실측 불일치 + SEO 구조적 원인 = 유일한 고침. 각 페이지가 1500+ chars 고유 콘텐츠 (score, stack 키워드, rule_id 패턴, cwe 언급).
**대안:** (1) 전체 SSR 전환 — JS 경로 재작성 비용 큼 (2) JS pre-render 서비스 (Render 추가 비용) (3) 무시하고 awaiting 인덱싱 — 증거 부재, 도박
**되돌릴 수 있나:** 예 (`body_ssr=""` 기본값으로 회귀)
**관련:** [[marketing/results.md]] 2026-04-23 세션, [[engineering/architecture.md]]

### 2026-04-19: a11y 규칙 severity WARNING → INFO
**결정:** `a11y-img-missing-alt`, `a11y-input-missing-label` 규칙 severity를 WARNING (= medium, 4점) → INFO (= low, 1점) 다운그레이드. 플래그는 유지, 점수 영향만 약화.
**이유:** 4 F 레포 분석 결과 전부 a11y-input-missing-label이 지배 (shadcn-ui 21개, payload 32개, trpc 27개). 규칙이 `aria-label`만 체크하고 `<Label htmlFor=...>` sibling 패턴 미감지 = 구조적 FP (shadcn/MUI/Tailwind 모두 이 패턴 사용). "Security scanner인데 a11y로 F" = 기대 불일치 + credibility 손상.
**대안:** (1) 규칙 삭제 — OKKY "코딩숙" validation과 모순 (a11y 중요) (2) 규칙 재작성해 htmlFor sibling 감지 — HTML parser 필요, Semgrep pattern-regex로 어려움 (3) 유지 — 모든 사용자에게 F 표시 문제 지속
**되돌릴 수 있나:** 예 (WARNING 복구)
**관련:** [[engineering/failure-log.md]] 2026-04-19, [[product/features.md]]

### 2026-04-17: Per-repo SEO 랜딩 페이지 (`/report/<owner>/<repo>`)
**결정:** 스캔 결과를 영구 URL로 노출. sitemap.xml + robots.txt + dynamic meta. 완료된 스캔은 REPORTS 캐시에 저장되어 sitemap에 자동 포함.
**이유:** 일회성 포스트(OKKY/dev.to/GeekNews)는 48시간이면 트래픽 끊김. SEO 페이지는 시간 지날수록 compound. Snyk 전략 (npm 패키지마다 페이지).
**대안:** Twitter/LinkedIn 포스트 집중 (기각 — follower-based = 0 audience에서 dead), Awesome Lists만 (병행 예정)
**되돌릴 수 있나:** 예 (server.py 라우트만 제거)
**관련:** [[engineering/architecture.md]], [[product/positioning.md]]

### 2026-04-17: Install CTA 단일화 — Marketplace 1개만
**결정:** 결과 페이지 Install CTA 3개 → 1개 (맨 아래 "Install from Marketplace"). 중복 Scan 입력창도 제거.
**이유:** "Copy YAML & open GitHub" 버튼이 404 유발 (남의 repo에 `/new/main` 연결). 중복 CTA = 첫 방문자 혼란. 맨 아래 한 개는 GitHub 네이티브 install flow 사용 → 유저가 자기 repo 선택 가능.
**대안:** 3개 유지 (UX 혼란), 직접 YAML 배포 (권한 문제 재발)
**되돌릴 수 있나:** 예
**관련:** [[engineering/hard-rules.md]] Rule 8, [[product/features.md]]

### 2026-04-17: 웜벳 분포 차트 업라이트 전환
**결정:** 기존 "땅굴" 메타포 (grass 위, 구멍이 아래로 카빙) → **업라이트 바 차트** (grass 아래, 바가 위로). 픽셀아트 + 웜벳 마커는 유지.
**이유:** 첫 방문자가 "이게 막대 그래프구나" 인지하는 데 2-3초 이상 걸림. "깊이 = 카운트"는 반직관 (차트 상식: "키 = 양"). 기능 > 메타포.
**대안:** 땅굴 유지 (브랜드 우선), 완전 generic bar chart (브랜드 손실)
**되돌릴 수 있나:** 예 (drawBurrow 복구)
**관련:** [[product/features.md]]

### 2026-04-17: Secret scanner test/fixture 경로 제외 (Hard Rule 7)
**결정:** `SKIP_DIRS`에 test/fixture/sample/mock/e2e 등 추가. VibeSafe 자체가 F(32) 사고 원인.
**이유:** test fixture의 가짜 시크릿이 critical로 카운트되어 모든 사용자 점수 왜곡. SEO 랜딩 페이지 배포 직후 자기 자신 F 표시 = credibility bomb.
**대안:** 값-기반 placeholder 정교화 (실패함 — "sk-proj-abc123" 같은 현실적 fake 못 거름), downgrade (복잡)
**되돌릴 수 있나:** 예
**관련:** [[engineering/failure-log.md]] 2026-04-17, [[engineering/hard-rules.md]] Rule 7

### 2026-04-17: Next.js web/ scaffold 부분 제거 (package.json만)
**결정:** `web/package.json` + `package-lock.json`만 삭제 → Dependabot 28 vulns 소멸. `src/app/api/`, `prisma/` 설계 코드는 유지 (미래 영속화 마이그레이션 참고자료).
**이유:** 28 high/medium 알림이 퍼블릭 repo에 떠 있어 credibility 저해. 하지만 src/prisma는 실제 구현체 (WIP) → 전면 삭제는 정보 손실 큼.
**대안:** A1 전면 삭제 (41 files, 정보 손실), A3 gitignore 숨김 (숨기기는 비추천)
**되돌릴 수 있나:** 예 (git revert)
**관련:** [[decisions/rejected.md]] "Next.js 전면 삭제"

### 2026-04-17: GitHub Marketplace 등재
**결정:** v0.1.1을 Latest로 지정하여 `github.com/marketplace/actions/vibesafe-security-scan` 등재.
**이유:** 0-audience 상태에서 가장 큰 무료 distribution 채널. GitHub Action 검색 유입.
**대안:** 등재 안 하고 README만 (수동 설치만 가능 — 전환율 낮음)
**되돌릴 수 있나:** 예 (Delist action)
**관련:** [[marketing/results.md]], [[product/features.md]]

### 2026-04-17: UTM 전수 태깅 + server-side capture
**결정:** 외부 link 전수 UTM (README 배지, 스캐너 CTA, release notes). server.py가 `/` 방문 시 utm_source/medium/campaign을 Render 로그에 기록.
**이유:** 이전까지 유입 소스 측정 불가 = 맹점. 제1원칙: 측정 없이 최적화 불가.
**대안:** GA/PostHog 등 analytics SaaS (과함, cost), UTM 생략 (측정 없음)
**되돌릴 수 있나:** 예
**관련:** [[marketing/results.md]]

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

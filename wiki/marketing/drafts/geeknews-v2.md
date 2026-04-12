---
title: GeekNews Draft v2
type: marketing
confidence: medium
created: 2026-04-12
updated: 2026-04-12
sources: [docs/geeknews_draft.md]
---

# Show GN: GitHub에서 "vibe coding" 프로젝트 10개를 보안 스캔해봤습니다

바이브 코딩이 유행이라 저도 Cursor로 앱을 만들어봤습니다.
20분 만에 동작하는 Flask 앱이 나왔는데, 문득 궁금해졌습니다. "이거 보안은 괜찮은 건가?"

Semgrep 기반 스캐너로 돌려봤더니 **0/100점**. SQL Injection, 하드코딩된 API 키, Command Injection이 그대로 있었습니다.

한 개만 그런 건지 궁금해서 GitHub에서 "vibe coding"으로 검색되는 프로젝트 10개를 스캔해봤습니다.

---

## 결과 (실제 스캔 데이터)

| # | 프로젝트 | 스택 | 점수 | 등급 | 주요 발견 |
|---|---------|------|------|------|----------|
| 1 | Vibe-Skills | Python/TypeScript | 0 | F | **MD5 해시 사용, autoescape 비활성화, 시크릿 노출** |
| 2 | vibe-kanban | React/TypeScript | 0 | F | 접근성 미비 25건 (input label 없음) |
| 3 | vibedev | JavaScript | 20 | F | **하드코딩된 시크릿 4개 (Critical)** |
| 4 | Product-Brainstorm | React/Express/Socket.io | 76 | B | 접근성 6건 |
| 5 | motif | React/TypeScript | 76 | B | 접근성 6건 |
| 6 | VibeSecurity | FastAPI/Go | 88 | A | CORS *, TLS MinVersion 미설정 |
| 7 | mcphub | Go/Next.js/React | 88 | A | Docker user 미지정, 접근성 |
| 8 | Vibe-Coder | Next.js/Prisma/React | 96 | A | 접근성 1건 |
| 9 | ctx-cloud | TypeScript/React | 96 | A | 접근성 1건 |
| 10 | Portfolio | Next.js/Express/React | 96 | A | 접근성 1건 |

**평균: 63.6점. 10개 중 3개가 F등급.**

---

## 발견한 패턴

흥미로운 건 **프로젝트 종류에 따라 점수가 극단적으로 갈린다**는 점입니다.

**F등급 (0~29점) — 백엔드 로직이 있는 앱:**
- 하드코딩된 시크릿 (API 키를 코드에 직접 삽입)
- MD5 같은 약한 해시 알고리즘
- 템플릿 엔진의 autoescape 비활성화 (XSS 가능)
- AI가 "돌아가게" 만들면서 보안 설정을 빼먹음

**A등급 (85~100점) — 프론트엔드 중심 앱:**
- 정적 사이트, 포트폴리오, 단순 UI는 취약점이 거의 없음
- 접근성 이슈(input에 label 없음)가 유일한 감점 요인
- 즉, **DB/API/인증이 들어가는 순간 위험해진다**

실제로 위험한 건 "로직이 복잡해지는 시점"입니다. OKKY에서도 비슷한 반응이 있었는데, "보안 지침을 줘도 어길 때가 있어서 크로스 체크는 필수"라는 댓글이 핵심을 찌릅니다.

---

## 직접 확인해보세요

웹에서 바로: https://vibesafe.onrender.com
GitHub URL 붙여넣으면 30초 안에 점수가 나옵니다. 가입이나 설치 필요 없습니다.

매 PR마다 자동 체크하고 싶으면: https://github.com/vibesafeio/vibesafe-action
24줄 YAML 추가하면 됩니다.

오픈소스이고, 코드는 스캔 중에만 서버에 있다가 즉시 삭제됩니다.

---

*Semgrep 기반 정적 분석 + 시크릿 탐지. 비즈니스 로직이나 런타임 취약점은 못 잡습니다.*

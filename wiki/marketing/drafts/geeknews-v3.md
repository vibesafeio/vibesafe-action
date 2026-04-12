---
title: GeekNews Draft v3 (뉴비톤)
type: marketing
confidence: medium
created: 2026-04-12
updated: 2026-04-12
sources: [실제 스캔 데이터 10개]
---

# Show GN: 바이브 코딩으로 만든 앱이 해킹당할 수 있는지 궁금해서 직접 스캔해봤습니다

비전공자인데 요즘 Cursor로 이것저것 만들고 있습니다.

며칠 전 Flask로 쇼핑몰 비슷한 걸 만들었는데 "이거 누가 해킹하면 어쩌지?" 싶어서 보안 스캐너라는 걸 돌려봤습니다.

결과: **0/100점**. F등급.

SQL Injection이 뭔지도 몰랐는데 제 코드에 있다고 나오더라구요. eval()이 위험하다는 것도 이때 처음 알았습니다.

그래서 "나만 이런 건가?" 싶어서 GitHub에서 비슷한 프로젝트 10개를 더 스캔해봤습니다.

---

## 결과

| 프로젝트 | 뭘로 만들었나 | 점수 | 뭐가 나왔나 |
|---------|-------------|------|-----------|
| Vibe-Skills | Python + TypeScript | 0점 | MD5 해시, 시크릿 노출 |
| vibe-kanban | React | 0점 | 접근성 미비 25건 |
| vibedev | JavaScript | 20점 | **하드코딩된 API 키 4개** |
| Product-Brainstorm | React + Express | 76점 | 접근성 누락 |
| motif | React | 76점 | 접근성 누락 |
| VibeSecurity | FastAPI + Go | 88점 | CORS 설정 문제 |
| mcphub | Go + Next.js | 88점 | Docker 설정 |
| Vibe-Coder | Next.js | 96점 | 접근성 1건 |
| ctx-cloud | TypeScript | 96점 | 접근성 1건 |
| Portfolio | Next.js | 96점 | 접근성 1건 |

평균 63점. 근데 **백엔드가 있는 프로젝트는 대부분 F등급**이었습니다.

포트폴리오나 프론트엔드만 있는 건 거의 만점인데, DB 연결하거나 API 키 쓰기 시작하면 갑자기 0점 근처로 떨어지더라구요.

---

## 제가 배운 것

1. **API 키를 코드에 직접 쓰면 안 된다** — `.env` 파일에 넣어야 한다는 걸 처음 알았습니다
2. **AI한테 "보안 신경 써"라고 해도 잘 안 된다** — 실험해봤는데 일부만 고쳐줌
3. **프론트만 있으면 괜찮은데 백엔드 붙이면 위험해진다** — 결제나 로그인 만들 때가 진짜 위험한 시점

---

## 스캔 도구

직접 만들어봤습니다. GitHub URL 넣으면 30초 안에 점수 나옵니다.

https://vibesafe.onrender.com

가입 필요 없고 무료입니다. 저 같은 뉴비가 최소한 "내 코드가 얼마나 위험한지" 알 수 있게 만들었습니다. 결과 나오면 AI한테 복사해서 붙여넣으면 고쳐줍니다.

소스코드: https://github.com/vibesafeio/vibesafe-action

피드백 주시면 감사합니다.

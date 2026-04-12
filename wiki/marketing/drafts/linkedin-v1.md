---
title: LinkedIn Draft v1
type: marketing
confidence: medium
created: 2026-04-12
updated: 2026-04-12
---

GitHub에서 "vibe coding" 프로젝트 10개를 보안 스캔해봤습니다.

결과가 재밌었습니다:
- 프론트엔드만 있는 프로젝트: 평균 92점
- 백엔드(DB, API, 인증)가 있는 프로젝트: 평균 7점

같은 AI가 만든 코드인데 왜 이렇게 다를까?

AI는 "돌아가는 코드"를 만들지, "안전한 코드"를 만들지 않습니다.
프론트엔드는 틀릴 게 별로 없어서 괜찮은데,
DB 연결하고 API 키 쓰고 인증 붙이는 순간 보안 구멍이 생깁니다.

가장 흔한 실수 3가지:
1. API 키를 코드에 직접 하드코딩 (10개 중 3개)
2. CORS를 전체 허용 (Access-Control-Allow-Origin: *)
3. MD5 같은 취약한 해시 알고리즘 사용

바이브 코딩으로 MVP 만들고 있다면,
백엔드 붙이는 시점에 한 번은 스캔해보세요.

직접 만든 무료 스캐너: vibesafe.onrender.com
GitHub URL 넣으면 30초 안에 결과 나옵니다.

#vibecoding #aisecurity #webdev #개발자

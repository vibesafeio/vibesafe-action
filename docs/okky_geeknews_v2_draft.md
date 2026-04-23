# OKKY + GeekNews 2차 포스팅 초안 (2026-04-23)

**목적**: 1차 포스팅(OKKY 772뷰, 2026-04-11) 이후 2주 경과. 새 데이터 hook = 17개 유명 repo 스캔 결과 + 구조적 FP 발견 스토리. 같은 도구 홍보가 아닌 **후속 실험 리포트** 포지션.

**핵심 전략**: 1차에서 "코딩숙"님이 남긴 validation ("바이브 코딩은 보안보다 a11y가 더 걸림")이 유명 오픈소스에서도 재현되는지 확인 → 결과 공유. 커뮤니티 내부 conversation 이어가기.

UTM: 모든 링크에 `?utm_source=okky-v2` 또는 `?utm_source=geeknews-v2`.

---

## OKKY 2차 포스팅 초안

### 제목 옵션 (후킹 순 정렬)

1. **"유명 오픈소스 17개를 보안 스캔했더니 전부 A가 아니었습니다"** ← 추천
2. "fastapi, shadcn-ui, trpc… 보안 점수 매겨봤습니다 (A 12개 / B 2개 / C 3개)"
3. "'AI 코드는 a11y가 더 걸린다'를 유명 오픈소스 17개로 확인해봤습니다"

제목 1번이 가장 강력: 구체적 숫자 + 반전 ("전부 A가 아니었다"). 검색어와 매칭도 높음.

### 본문 (권장, 약 500자)

```
2주 전에 여기에 "AI 만든 앱 보안 점수 0점" 얘기 올렸을 때
코딩숙님이 댓글 남겨주셨었죠 —
"제 바이브 코딩 프로젝트는 보안성보다는 다 접근성 쪽으로 걸렸다"고.

이 관찰이 유명 오픈소스에서도 재현되는지 궁금해서 17개 돌려봤습니다.

대상: fastapi, flask, express, shadcn-ui, trpc, payload, continue,
      drizzle-orm, tailwindcss, anthropic-sdk-python, openai-python 등

결과 (A-F, VibeSafe 기준):
  A (12개): flask, express, streamlit, gradio, reflex, tailwindcss 등
  B (2개):  fastapi(80/100), shadcn-ui(79/100)
  C (3개):  payload(68), continue(64), trpc(60)
  F: 없음

흥미로웠던 건 C 받은 3개가 **전부 보안 이슈가 아니라 a11y 때문**이었습니다.
<input> 태그에 aria-label 안 붙어있는 패턴. 코딩숙님 관찰 그대로.

처음 스캔했을 때는 이 3개가 다 F 나왔는데,
shadcn/MUI/Tailwind 같은 라이브러리들이 쓰는 <Label htmlFor="id"> 패턴을
제 스캐너가 못 잡는 구조적 FP여서 severity 내렸습니다.
그래도 플래그는 유지 (코딩숙님 말대로 실제 gap이니까).

각 repo 결과 보기:
https://vibesafe.onrender.com/report/tiangolo/fastapi?utm_source=okky-v2
https://vibesafe.onrender.com/report/shadcn-ui/ui?utm_source=okky-v2
...등

자기 repo 스캔해보고 싶으시면 (무료, 30초):
https://vibesafe.onrender.com?utm_source=okky-v2

혹시 이상한 결과 나오거나 건지 못 하는 패턴 있으면 알려주세요.
특히 htmlFor + Label 감지는 아직 못 풀었습니다 (HTML parser 수준 작업).
```

### Length check
- 약 800-900자. 1차 포스팅보다 짧음.
- 후킹: 첫 문장 "2주 전에 올렸을 때 코딩숙님이…" = 같은 스레드 암시 → 반복 도구 홍보 인식 낮춤
- 데이터: 구체적 레포 이름 + 점수 범위 (A-F 분포)
- 도구 링크는 본문 중반+말미에 2번만

### 댓글 유도
- "해보고 이상한 결과 알려주세요" = 반복 방문/재참여 유도
- "특히 htmlFor + Label 감지는 못 풀었다" = 기술적 도움 요청 → 개발자 커뮤니티 응답 자극

---

## GeekNews 2차 포스팅 초안

GeekNews는 링크 + 짧은 설명 포맷. 한 번 올린 URL은 재등록 불가. **새 URL 필요**.

### 링크 선택

**Option A — 전체 결과 페이지 (홈)**:
`https://vibesafe.onrender.com?utm_source=geeknews-v2`
- 기존에 올린 URL과 같을 수 있어 재등록 거부 가능

**Option B — 특정 보고서 페이지 (새 URL)** ← 추천:
`https://vibesafe.onrender.com/report/tiangolo/fastapi?utm_source=geeknews-v2`
- 1차에 없던 URL, 완전 새 리소스
- 제목에 "fastapi" 같은 구체적 이름이 들어가면 클릭률 ↑

### 제목 옵션

1. **"fastapi, shadcn-ui, trpc 보안 점수 자동 스캔 — 17개 오픈소스 결과"** ← 추천
2. "VibeSafe: 유명 오픈소스 17개 보안/접근성 자동 평가 결과"
3. "GitHub repo URL만 넣으면 30초 보안 스캔 — 17개 유명 프로젝트 실험 결과"

### 본문 (GeekNews 스타일, 3-5줄)

```
AI가 만든 코드 보안 스캐너 VibeSafe로 유명 오픈소스 17개를 돌려봤습니다.

결과:
- A 12개 (fastapi 80, shadcn-ui 79 등 B 포함 시 제외)
- B 2개 (fastapi 80, shadcn-ui 79)
- C 3개 (payload 68, continue 64, trpc 60) — 전부 접근성(a11y) 이슈 지배

구조적 발견: <Label htmlFor="id"> 패턴을 쓰는 현대 컴포넌트 라이브러리가 많아
              Semgrep 규칙 severity를 조정해야 했습니다.

각 repo 결과 페이지: https://vibesafe.onrender.com/report/<owner>/<repo>
GitHub: https://github.com/vibesafeio/vibesafe-action
```

### GeekNews 제출 방식

- 링크 URL: `/report/tiangolo/fastapi?utm_source=geeknews-v2` (또는 shadcn-ui/ui)
- 제목: 옵션 1
- 본문: 위 3-5줄
- 카테고리: 개발도구 / 오픈소스

---

## 실행 체크리스트

| Step | Owner | Deadline | Metric |
|------|-------|----------|--------|
| OKKY 로그인 → 기존 글 확인 → 2차 게시 | **user** | 오늘 저녁 or 내일 | OKKY post URL |
| OKKY 댓글 응답 (첫 24h) | user | 게시 후 24h | 댓글 수 |
| GeekNews 제출 | user | 오늘 | GeekNews post URL |
| 24h 후 UTM 측정 | Claude | 2026-04-25 | `curl /api/metrics/events \| grep okky-v2 \| wc -l` |

### 24h 측정 명령

```bash
# UTM rollup — 모든 채널 한번에
curl -s "https://vibesafe.onrender.com/api/metrics/events" \
  | python3 -c "import json,sys; d=json.load(sys.stdin); [print(f'{c:>4}  {k}') for k,c in d['utm_rollup'].items()]"

# OKKY-v2 유입만
curl -s "https://vibesafe.onrender.com/api/metrics/events?event=page_views" \
  | python3 -c "import json,sys; d=json.load(sys.stdin); okky=[e for e in d['events'] if 'okky-v2' in e.get('detail','')]; print(f'OKKY-v2 hits: {len(okky)}')"

# install_clicks since post time
curl -s "https://vibesafe.onrender.com/api/metrics/events?event=install_clicks&since=2026-04-23T12:00:00+00:00" \
  | python3 -c "import json,sys; print(json.load(sys.stdin)['returned'])"
```

## 리스크 & 완화

| 리스크 | 완화 |
|--------|------|
| "또 도구 홍보?" 반감 | 첫 문장이 코딩숙 댓글 인용 = 커뮤니티 내 continuation 톤 |
| 1차와 동일 내용이면 중복 게시 지적 | 2차는 **데이터 리포트** — 17개 이름/점수/발견 스토리로 차별 |
| Render 재시작으로 측정 unit buffer 리셋 | 게시 직후 ring buffer 스냅샷 tee 저장 권장 (게시 시각부터 24h 누적 집계 가능) |
| htmlFor 패턴 얘기가 비개발자에게 어려움 | OKKY는 개발자 커뮤니티라 괜찮음. GeekNews도 동일. |

## 왜 지금 하는가 (근거)

- 1차 포스팅 2주 경과 (충분한 cooldown)
- 데이터 신규성: 17 seed + SSR + a11y 분석은 1차에 없던 콘텐츠
- KPI baseline stars 6일째 정체 → 외부 유입 재점화 필요
- SSR 배포(2026-04-23) → 링크 클릭 후 랜딩 페이지 품질도 1차 대비 향상

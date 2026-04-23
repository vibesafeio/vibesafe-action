# 2차 포스팅 트래킹 (2026-04-23)

게시: 2026-04-23 ~21:36 UTC (KST 2026-04-24 ~06:36)

| 채널 | URL | 자동 트래킹 | 근거 |
|------|-----|-----|------|
| OKKY | https://okky.kr/articles/1555942 | ❌ WAF 403 | 뷰/댓글 수 → user 수동 보고 or UTM 간접 |
| GeekNews | https://news.hada.io/topic?id=28827 | ✅ HTML 200 | `▲ ... N P by ... | 댓글과 토론` 패턴 파싱 |
| GitHub repo | vibesafeio/vibesafe-action | ✅ API | stars/forks/watchers |
| Render UTM | /api/metrics/events | ✅ | utm_source=okky-v2/geeknews-v2 rollup |

## Baseline snapshot (2026-04-23 21:36 UTC)

| 지표 | 값 |
|------|----|
| OKKY 뷰 | (manual) — 게시 직후 |
| OKKY 댓글 | 0 (게시 직후) |
| GeekNews 점수 | **1 P** (자기 추천만) |
| GeekNews 댓글 | 0 |
| GitHub Stars | **6** |
| Forks | 1 |
| Watchers | 0 |
| Render page_views (since restart) | 2 (curl from me) |
| Render install_clicks | 0 |
| UTM okky-v2 | **0** |
| UTM geeknews-v2 | **0** |

## 24h 측정 명령어 (북마크용)

```bash
# 전체 스냅샷 한 번에
bash scripts/track_posts.sh    # ← 작성 예정

# 개별:
# GeekNews 점수+댓글
curl -sL "https://news.hada.io/topic?id=28827" -A "Mozilla/5.0" \
  | grep -oE "[0-9]+ P by|댓글과 토론" | head -2

# GitHub stars
curl -s https://api.github.com/repos/vibesafeio/vibesafe-action \
  | python3 -c "import json,sys; print(json.load(sys.stdin)['stargazers_count'])"

# UTM okky-v2 hits
curl -s "https://vibesafe.onrender.com/api/metrics/events?event=page_views" \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print(len([e for e in d['events'] if 'okky-v2' in e.get('detail','')]))"

# 전체 UTM rollup
curl -s "https://vibesafe.onrender.com/api/metrics/events" \
  | python3 -c "import json,sys; d=json.load(sys.stdin); [print(f'{c:>4}  {k}') for k,c in d['utm_rollup'].items()]"
```

## 체크포인트

| 시점 | 타겟 | 미션 |
|------|------|------|
| +1h | UTM 유입 시작 확인 | okky-v2 ≥ 1, geeknews-v2 ≥ 1 |
| +6h | 초기 momentum | OKKY 뷰 ≥ 100, GeekNews ≥ 3 P |
| +24h | 도달 평가 | Stars Δ ≥ +3, install_clicks ≥ 1 |
| +72h | 롱테일 평가 | SEO 2차 유입 시작 (referrer 링크) |

## 실패 시그널

- +6h에 UTM okky-v2 = 0 → OKKY 뷰는 있는데 링크 클릭 0 = 메시지 hook이 안 통함
- +24h에 Stars Δ=0 → 트래픽 있는데 액션 없음 = 제품/랜딩 품질 문제
- GeekNews +6h에 1 P 정체 → frontpage 못 올라감, dead

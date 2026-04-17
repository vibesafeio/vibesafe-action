# PM Pulse — Weekly Product Health

매주 1회 실행. 제품의 건강 상태를 PM 관점에서 점검한다.

## Steps

1. wiki/marketing/results.md에서 KPI 읽기
2. GitHub API로 최신 stars, clones, views 가져오기 (GITHUB_TOKEN 필요)
3. wiki/market/validation.md에서 핵심 가정 확인
4. 아래 형식으로 출력

## Output
- **Acquisition**: 이번 주 새 방문자 몇 명? 어디서 왔나?
- **Activation**: 방문 → 설치 전환율? (views → clones → installs)
- **Retention**: 설치한 레포 중 2회 이상 실행한 비율?
- **가장 위험한 가정**: 지금 검증 안 된 가장 큰 가정 1개
- **이번 주 해야 할 것**: 1개만. 가장 임팩트 큰 행동.

## Rules
- 숫자가 없으면 "측정 불가 — 측정 방법 필요"라고 쓴다
- "잘 되고 있다" 금지. 숫자로만 말한다
- 좋은 소식보다 나쁜 소식을 먼저 쓴다

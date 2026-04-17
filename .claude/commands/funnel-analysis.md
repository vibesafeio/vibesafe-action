# Funnel Analysis

사용자 획득부터 활성화까지의 퍼널을 분석한다.

## Funnel Stages
1. **Awareness**: 글을 봤다 (GeekNews 뷰, dev.to 뷰, OKKY 뷰)
2. **Interest**: 레포를 방문했다 (GitHub views)
3. **Evaluation**: 레포를 클론했다 (GitHub clones)
4. **Activation**: GitHub Action을 설치했다 (workflow 파일 추가)
5. **Retention**: 2회 이상 실행했다 (같은 레포에서 재실행)

## Steps
1. 각 단계의 숫자를 수집 (가능한 것만, GITHUB_TOKEN 필요)
2. 단계 간 전환율 계산
3. 가장 큰 이탈 지점 식별
4. 이탈 원인 가설 제시 (최대 3개)
5. 각 가설에 대한 실험 제안

## Output Format
```
Awareness  → Interest:   X% (N → N)
Interest   → Evaluation: X% (N → N)
Evaluation → Activation: X% (N → N)
Activation → Retention:  X% (N → N)
Biggest drop: [단계]
Hypotheses: ...
Experiment: ...
```

## Rules
- 측정 불가능한 단계는 "측정 불가"로 표시하고, 측정 방법을 제안
- 전환율이 0%인 단계가 있으면 그게 1순위 문제

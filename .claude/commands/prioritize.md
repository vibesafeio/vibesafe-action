# Prioritization — ICE + Constraint

기능/작업의 우선순위를 결정한다.

## Framework: ICE + 1 Constraint

| 기준 | 질문 | 점수 |
|------|------|------|
| Impact | 이게 핵심 KPI를 얼마나 움직이나? | 1-10 |
| Confidence | 이게 실제로 효과가 있다는 증거가 있나? | 1-10 |
| Ease | 얼마나 빨리 만들 수 있나? | 1-10 |
| **Constraint** | **지금 이게 가장 큰 병목인가?** | Yes/No |

## Steps
1. 후보 작업 목록을 받는다
2. 각 작업에 ICE 점수를 매긴다
3. Constraint = Yes인 것을 최상위로 올린다
4. ICE × Constraint로 정렬
5. wiki/product/roadmap.md를 업데이트한다

## Rules
- "전부 중요하다"는 답이 아니다. 반드시 1개를 고른다
- Confidence가 3 이하면 "먼저 검증 필요"로 표시
- 사용자 0명인 상태에서 Impact 10은 없다. 최대 7.

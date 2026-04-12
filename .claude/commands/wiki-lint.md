# Wiki Lint

위키의 건강 상태를 점검하는 워크플로우.

## Checks

1. **고아 페이지**: index.md에서 링크되지 않은 페이지
2. **오래된 정보**: updated 날짜가 30일 이상 된 high-confidence 페이지
3. **깨진 참조**: [[존재하지 않는 페이지]] 링크
4. **빈 페이지**: TLDR만 있고 Content가 비어있는 페이지
5. **시크릿 패턴**: API 키, 토큰, 비밀번호 패턴 탐지
6. **confidence 불일치**: sources가 없는데 confidence: high인 것

## Output
```
Wiki Health Report
- Total pages: N
- Healthy: N
- Orphans: N (list)
- Stale: N (list)
- Broken refs: N (list)
- Empty: N (list)
- Secrets found: N (CRITICAL)
```

## Auto-fix (--fix 옵션)
- 깨진 참조 -> 스텁 페이지 생성
- 오래된 high -> medium으로 다운그레이드
- 고아 -> index.md에 추가

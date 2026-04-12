# Wiki Ingest

새로운 자료를 위키에 통합하는 워크플로우.

## Steps

1. `raw/` 폴더에서 새로 추가된 파일을 확인한다
2. `wiki/index.md`를 읽고 관련 페이지를 찾는다
3. 각 관련 페이지를 읽는다
4. 새 정보가 기존 내용과 충돌하면 충돌을 명시한다:
   ```
   > CONFLICT: 기존: "X". 새 자료(raw/filename): "Y". 해결 필요.
   ```
5. 위키 페이지를 업데이트하거나 새 페이지를 만든다
6. 모든 페이지의 frontmatter `updated:` 날짜를 갱신한다
7. `wiki/index.md`의 Page Directory를 갱신한다
8. confidence 레벨 설정:
   - high: 원본에 명시적으로 있음
   - medium: 원본에서 합리적으로 추론
   - low: 추측이 포함됨

## Output
변경된 페이지 목록 + 각 변경 요약 (1줄씩)

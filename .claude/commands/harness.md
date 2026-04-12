# Harness — Self-Verification

코드 변경 후 커밋 전에 반드시 실행하는 검증 루프.

## Gates (전부 통과 필수)

1. **실행 검증**
   ```bash
   python3 <changed_file.py> --help
   python3 test/e2e_pipeline_test.py
   ```

2. **Docker 빌드** (tools/ 또는 Dockerfile 변경 시)
   ```bash
   docker build -f Dockerfile.action -t vibesafe-test . -q
   ```

3. **Docker 스캔 테스트**
   ```bash
   # vulnerable fixture -> critical >= 1
   # clean fixture -> score >= 90
   ```

4. **룰 검증**
   ```bash
   python3 tools/scanner/domain_rule_engine.py --validate
   ```

5. **오탐 검증**
   ```bash
   # ambiguous fixture -> false positive 없음
   ```

## Failure Protocol
- 실패 시 최대 3회 자동 수정
- 3회 실패 -> 멈추고 wiki/engineering/failure-log.md에 기록
- 같은 파일 3회+ 수정 (doom loop) -> 접근 재고

## Output
```
## Harness Report
- Gate 1 (run): pass/fail
- Gate 2 (docker): pass/fail/N/A
- Gate 3 (scan): pass/fail/N/A
- Gate 4 (rules): pass/fail
- Gate 5 (FP): pass/fail
- Fragile: (one line)
- Unchecked: (one line)
```

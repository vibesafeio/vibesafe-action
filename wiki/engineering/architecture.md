---
title: Architecture
type: engineering
confidence: high
created: 2026-03-18
updated: 2026-04-12
sources: [docs/architecture.md]
---

## TLDR
GitHub Action (Docker) + 웹 스캐너 (Render). 파이프라인: 스택감지 → 도메인분류 → 규칙선택 → SAST → Secret → 점수 → PR코멘트.
로컬 도구: pre-commit hook, MCP 서버.

## Content

### 파이프라인 (GitHub Action)
```
action_entrypoint.sh
  → sast_runner.py (Semgrep + 스택 감지)
  → secret_scanner.py (정규식 + 엔트로피)
  → domain_rule_engine.py (도메인 분류 + 규칙 선택)
  → score_calculator.py (0-100 점수)
  → pr_commenter.py (PR 코멘트 + GitHub API)
  → fail-on gate (exit 1 or 0)
```

### 데이터 흐름
1. `sast_runner.py --detect-stack` → 언어 + 프레임워크
2. `domain_rule_engine.py --classify` → 이커머스/핀테크/플랫폼 등
3. 도메인 + 스택 + 언어 → Semgrep config 리스트
4. Semgrep 실행 → SARIF 출력
5. Secret 스캔 → JSON findings
6. SARIF + secrets + 도메인 가중치 → 0-100 점수
7. PR 코멘트 생성 (파일:라인, Fix 제안)
8. score.json → fail-on 임계치 초과 시 exit 1

### 웹 스캐너
- `web/server.py`: stdlib HTTPServer, in-memory SCANS/SCORES
- `web/static/index.html`: 단일 페이지, 웜뱃 애니메이션 + 땅굴 리더보드
- `tools/cli_scanner.py`: 웹에서 호출하는 스캔 엔트리포인트
- 배포: Render (자동, push하면 배포)
- 상태: in-memory (재배포 시 리셋). 리더보드 seed 데이터 60개.

### 핵심 파일
| 파일 | 용도 |
|------|------|
| action.yml | GitHub Action 정의 |
| action_entrypoint.sh | 오케스트레이터 |
| Dockerfile.action | Docker 이미지 (Python 3.11 + Semgrep + git) |
| tools/scanner/sast_runner.py | Semgrep 래퍼 + 스택 감지 |
| tools/scanner/secret_scanner.py | 시크릿 탐지 |
| tools/scanner/domain_rule_engine.py | 도메인 분류 + 규칙 선택 |
| tools/report/score_calculator.py | 점수 계산 |
| tools/report/pr_commenter.py | PR 코멘트 |
| web/server.py | 웹 스캐너 서버 |
| tools/mcp_server.py | MCP 서버 |

## Open Questions
- in-memory 상태를 영구 저장소로 전환할 필요가 있는가? (리더보드 데이터 손실)
- Render free tier의 메모리/CPU 한계로 대형 repo 스캔 시 타임아웃 (90초)

## Related
- [[engineering/hard-rules.md]]
- [[product/features.md]]

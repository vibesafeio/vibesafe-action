# VibeSafe Wiki System — 설치 가이드

Claude Code에서 아래를 실행하세요.

## 1. 디렉토리 생성

```bash
# Wiki 구조
mkdir -p raw/{articles,benchmarks,screenshots,feedback}
mkdir -p wiki/{product,market,engineering,marketing,decisions,future}

# Claude Code Skills
mkdir -p .claude/commands
```

## 2. CLAUDE.md 배치

vibesafe-claude-md-wiki.md 내용을 프로젝트 루트의 CLAUDE.md로 복사.

## 3. Wiki Index 배치

wiki-index.md 내용을 wiki/index.md로 복사.

## 4. Skills 배치

vibesafe-skills.md의 각 섹션을 개별 파일로:

```
.claude/commands/wiki-ingest.md
.claude/commands/wiki-query.md
.claude/commands/wiki-lint.md
.claude/commands/wiki-status.md
.claude/commands/wiki-decision.md
.claude/commands/harness.md
.claude/commands/retro-weekly.md
```

## 5. 기존 지식 마이그레이션

현재 이 대화에서 나온 분석들을 raw/에 넣고 ingest:

```
raw/articles/market-validation.md     ← 시장 검증 결과 문서
raw/articles/user-segments.md         ← 사용자 세그먼트 분석
raw/articles/competitor-analysis.md   ← 경쟁사 10+ 비교
raw/articles/vibesafe-positioning.md  ← 포지셔닝 + 불편한 진실
raw/articles/vibecost-design.md       ← VibeCost 설계 + 비판적 검토
```

Claude Code에서:
```
/wiki-ingest
```
→ AI가 raw/를 읽고 wiki/ 페이지를 생성/업데이트

## 6. 일상 워크플로우

### 매일
- 새 자료 발견 → raw/에 저장
- `/wiki-ingest` → 위키 업데이트
- 코드 변경 → `/harness` → 커밋

### 매주
- `/retro-weekly` → 주간 회고
- `/wiki-lint` → 위키 건강 점검
- `/wiki-status` → 현재 상태 확인

### 결정할 때
- `/wiki-decision` → 결정 기록

## 7. Git으로 버전 관리

```bash
git add wiki/
git commit -m "wiki: update after ingest session"
```

wiki/ 변경 이력이 git에 쌓이므로:
- 언제 어떤 지식이 추가/변경됐는지 추적
- 잘못된 업데이트를 revert 가능
- 팀 협업 시 wiki/ 변경을 PR로 리뷰 가능

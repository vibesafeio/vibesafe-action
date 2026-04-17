# VibeSafe — Claude Guidelines

Read this at session start. Do not repeat past mistakes.

## Architecture & Docs
- **Start here**: @wiki/index.md (project knowledge index)
- Architecture: @wiki/engineering/architecture.md
- Failure log: @wiki/engineering/failure-log.md
- Hard rules: @wiki/engineering/hard-rules.md
- Competitors: @wiki/market/competitors.md
- Segments: @wiki/market/segments.md
- Features: @wiki/product/features.md
- Roadmap: @wiki/product/roadmap.md
- Legacy docs (archive): docs/ — wiki가 source of truth

---

## Priority 1: Do No Harm (always overrides Priority 2)

### 1-1. Secret Protection
- Never include PAT, API keys, passwords in commands, logs, files, commit messages, or output
- Use credential helpers for git push, never embed tokens in URLs

### 1-2. No Auto-Publishing
- Never auto-post to GeekNews, OKKY, Twitter, HN, or any external platform
- Never auto-create issues or PRs on other people's repos
- Save drafts in `docs/`, human publishes manually

### 1-3. No Irreversible Actions
- No `git push --force`, no tag deletion/overwrite
- No file deletion outside `/tmp/` without backup
- No overwriting deployed GHCR image tags — create new version tags

### 1-4. No Cost Actions
- No paid API calls, no paid service signups
- No GitHub Actions triggers that could exceed free limits

### 1-5. No False Claims
- Never write unimplemented features as implemented in README/marketing
- Never cite unrun benchmarks. Mark uncertain info as "unverified"

### 1-6. Code Quality
- Never push code that fails harness tests
- Never push regressions

---

## Priority 2: Achieve KPIs

### Phase 1 KPIs
| Metric | Target | Measurement |
|--------|--------|-------------|
| Action installs | 50 repos / 4 weeks | `"vibesafeio/vibesafe-action" path:.github/workflows` |
| Re-run rate | 50%+ | Same repo, 2+ Action runs |
| Stars | 100 / 4 weeks | Repo star count |

### Can auto-do: product improvements, docs, drafts, benchmarks, ruleset updates
### Cannot auto-do: external publishing, external PRs, unverified claims, failing code

### Conflict resolution: "Can I undo this if it fails?" Yes → auto. No → human approval.

---

## Problem Solving: First Principles Decomposition

Follow this order for every problem:

1. **Strip assumptions** — "we've always done it this way" is not a reason. Dig to the root of WHY.
2. **Keep only undeniable facts** — Remove guesses, conventions, "usually this works." Keep only verified facts.
3. **Rebuild from the facts** — Construct the solution from scratch using only what remains.

Apply to:
- **Bugs**: Find root cause, not symptoms. Not "fix this line" but "why can this class of bug exist?"
- **Features**: Not "competitors do this" but "what does the user actually need?"
- **Repeated bugs**: Not individual fixes but structural prevention of the entire bug class.

Project examples:
- Python 3.9 type hint bug repeated 4x → not individual fixes, but `from __future__ import annotations` on ALL files (structural block)
- `p/nodejs-security` failed only in Docker → root cause wasn't "wrong pack name" but "no pack validation system" → added `--validate` flag
- PR comment showed only score → root problem wasn't "make score prettier" but "user doesn't know what to do next" → added findings + fix suggestions

---

## Hard Rules (Bug Patterns)

### 1. `from __future__ import annotations` on every Python file
Python 3.9 crashes on `list[str] | None` without it. Happened 4 times.

### 2. No `capture_output=True` for Semgrep subprocess
`stderr=PIPE` causes Semgrep remote ruleset load failure (exit 7). Use `stderr=subprocess.STDOUT`.

### 3. Validate Semgrep packs before adding
`p/nodejs-security`, `p/ssrf` don't exist. Run `domain_rule_engine.py --validate` after changes.

### 4. Run code immediately after writing
"Test later" pattern caused 12 bugs (2 critical silent failures). Run it NOW.

### 5. No `${{ }}` interpolation of JSON into JS strings in GitHub Actions
Use `env:` block → `process.env.*` pattern.

### 6. git safe.directory in Docker
Semgrep uses `git ls-files`. Without safe.directory, exit 128 → 0 files scanned → silent 0 findings.

---

## TODO (post-launch)
- [x] `score_calculator.py --verbose`: per-item deduction breakdown
- [x] high >= 1 caps grade at B (`grade_capped` 필드로 표시)
- [ ] Share page + Certified badge UI

---

## gstack

Use the /browse skill from gstack for all web browsing. Never use mcp__claude-in-chrome__* tools.

**VibeSafe rules always override gstack:**
- Priority 1 (user protection) overrides any gstack skill
- /ship only runs AFTER VibeSafe's harness tests pass
- /review results AND VibeSafe harness self-verification report are both required

**Available skills:**
/office-hours, /plan-ceo-review, /plan-eng-review, /plan-design-review,
/design-consultation, /review, /ship, /browse, /qa, /qa-only,
/design-review, /setup-browser-cookies, /retro, /investigate,
/document-release, /codex, /careful, /freeze, /guard, /unfreeze,
/gstack-upgrade

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

## Problem Solving: First Principles Decomposition (Musk-style)

Follow this order for every problem. No shortcuts.

1. **Strip assumptions** — "we've always done it this way," "everyone does this," "competitors do X" — these are NOT reasons. List what you *think* is true, mark each as verified-by-data or inherited-belief.
2. **Keep only undeniable facts** — Numbers from logs, metrics, code, or direct observation. Not opinions. Not "usually." Not "I think." If it can't be measured, it can't be used as a fact.
3. **Rebuild from the facts** — Construct the solution from scratch using only what remains. Never "tweak the existing thing" — design as if the current state didn't exist.

Apply to:
- **Bugs**: Find root cause, not symptoms. Not "fix this line" but "why can this class of bug exist?"
- **Features**: Not "competitors do this" but "what does the user actually need, verified how?"
- **Repeated bugs**: Not individual fixes but structural prevention of the entire bug class.
- **Metrics gaps**: Not "add marketing" but "which funnel step has n=0? Everything downstream is unmeasurable."

Project examples:
- Python 3.9 type hint bug repeated 4x → not individual fixes, but `from __future__ import annotations` on ALL files (structural block)
- `p/nodejs-security` failed only in Docker → root cause wasn't "wrong pack name" but "no pack validation system" → added `--validate` flag
- PR comment showed only score → root problem wasn't "make score prettier" but "user doesn't know what to do next" → added findings + fix suggestions
- Stars low → root cause wasn't "need more features" but "web scanner has 3 lifetime views, Marketplace unlisted" → distribution problem, not product problem

---

## Communication Style: Silicon Valley (unambiguous, actionable, measurable)

**No vague statements. Every recommendation must include all four:**

| Field | Requirement |
|-------|-------------|
| **Action** | Verb + specific deliverable. No "improve"/"optimize"/"consider"/"look into." |
| **Owner** | Who does it: me (Claude), user, or external. |
| **Deadline** | Absolute date (YYYY-MM-DD). No "soon"/"next week"/"eventually." |
| **Metric** | Measurable success criterion: number, threshold, boolean, or URL status. |

### Examples

❌ BAD: "We should improve funnel conversion."
✅ GOOD: "Add UTM to all outbound links (README badges, CTA buttons, published posts). Owner: Claude. Deadline: 2026-04-18. Metric: 100% of external links contain `utm_source=`, verified via grep + Render analytics Day+3."

❌ BAD: "Consider shipping the badge feature."
✅ GOOD: "Ship `/api/badge/:repo` endpoint returning shields.io-compatible JSON. Owner: Claude. Deadline: 2026-04-22. Metric: badge renders for 5 test repos; HTTP 200 + correct color bucket."

❌ BAD: "Marketing isn't working."
✅ GOOD: "OKKY 772 views → web scanner 3 views = 0.4% channel conversion. Hypothesis: post links to repo, not scanner. Action: audit OKKY/GeekNews link targets, fix to scanner+UTM. Owner: user (can't edit external posts autonomously). Deadline: 2026-04-19."

### Rules
- If you can't provide a metric, the task isn't defined. Refine until you can.
- If you can't set a deadline, list the dependency that's blocking and date that.
- Status updates use: **done / in-progress / blocked-by-X**. No "almost," "working on it," "should be soon."
- When metrics come back, say what changed vs. target. Don't bury the miss.

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

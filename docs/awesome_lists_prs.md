# Awesome Lists PR Drafts

Three PRs to compound-SEO lists. User submits; each curator runs on their own clock.

**UTM**: every link uses `?utm_source=awesome-X&utm_medium=list&utm_campaign=launch` so we can attribute inbound in Render logs (`[METRIC_EVENT] ... detail=utm=awesome-...`).

---

## PR 1 — sdras/awesome-actions

**Repo**: https://github.com/sdras/awesome-actions
**File**: `README.md`
**Section**: `Linting` (subsection under `Static Analysis`)
**Target line**: alphabetical insert; find existing Semgrep/security entries

**Line to add** (alphabetical by action name):
```markdown
- [VibeSafe](https://github.com/vibesafeio/vibesafe-action?utm_source=awesome-actions&utm_medium=list&utm_campaign=launch) - Security + accessibility scanner for AI-generated code. SAST, secret detection, WCAG 2.1 a11y. PR comments with file:line + fix prompts. 24-line YAML install.
```

**PR title**: `Add VibeSafe — security + a11y scanner for AI-generated code`

**PR body**:
```
Adds VibeSafe to the Static Analysis / Linting section.

What it does:
- Semgrep-based SAST (OWASP Top 10) with domain-aware rule selection
- Secret detection (AWS, GitHub, Stripe, OpenAI, JWT, etc.) with entropy + path context
- WCAG 2.1 accessibility checks (img alt, input labels, html lang)
- Posts PR comments with file:line references + ready-to-paste fix prompts for Cursor/Claude

Why it fits this list:
- Pure GitHub Action — 24-line YAML, no external service dependencies
- MIT licensed, OSS, free
- Listed on GitHub Marketplace: https://github.com/marketplace/actions/vibesafe-security-scan

Repo: https://github.com/vibesafeio/vibesafe-action
Live demo (web scanner): https://vibesafe.onrender.com
```

**Submission checklist**:
- [ ] Fork sdras/awesome-actions
- [ ] Insert line alphabetically in the right subsection
- [ ] Open PR with body above
- [ ] Link PR number back here

---

## PR 2 — sbilly/awesome-security

**Repo**: https://github.com/sbilly/awesome-security
**File**: `README.md`
**Section**: `Tools / Static Analyzer` or `DevSecOps`
**Check policy**: contributor guide requires "active, maintained, open-source" — we qualify (commits daily, MIT)

**Line to add**:
```markdown
* [VibeSafe](https://github.com/vibesafeio/vibesafe-action?utm_source=awesome-security&utm_medium=list&utm_campaign=launch) - Security + accessibility scanner built for AI-generated code. SAST + secret detection + WCAG 2.1 a11y. GitHub Action with automatic PR comments and merge blocking.
```

**PR title**: `Add VibeSafe — OSS security scanner for AI-generated code`

**PR body**:
```
Adds VibeSafe to Static Analyzer / DevSecOps.

What it does:
- Static analysis (Semgrep), secret scanning, accessibility audit in one Action
- Domain-aware rule selection (fintech/healthcare/ecommerce weights)
- Framework conflict filter (Flask/Django false-positive suppression)
- Merge-blocking via fail-on input (critical/high/medium)

Differentiator:
- Focuses on the AI-generated code class: low false-positive rate, actionable
  fix prompts users can paste back into Cursor/Claude
- Tutorial/example-path aware secret detection (docs/, *.test.ts, *.md → downgraded)

MIT, OSS, active: https://github.com/vibesafeio/vibesafe-action
Marketplace: https://github.com/marketplace/actions/vibesafe-security-scan
```

---

## PR 3 — returntocorp/semgrep-rules (NOT a PR — dedicated listing on semgrep.dev)

**Reality check**: `returntocorp/semgrep-rules` accepts rule contributions, not "products built on Semgrep." Skip.

**Replacement PR 3 — analysis-tools-dev/static-analysis**

**Repo**: https://github.com/analysis-tools-dev/static-analysis
**File**: `data/tools/vibesafe.toml` (this repo is data-driven; PRs add a tool file)
**Method**: fork, create the TOML file, open PR

**File contents** (`data/tools/vibesafe.toml`):
```toml
name = "VibeSafe"
categories = ["program-analysis"]
languages = ["javascript", "typescript", "python", "go", "java", "ruby", "html"]
other_names = ["vibesafe-action"]
homepage = "https://vibesafe.onrender.com/?utm_source=analysis-tools-dev&utm_medium=list&utm_campaign=launch"
source = "https://github.com/vibesafeio/vibesafe-action"
license = "mit"
tags = ["semgrep-based", "sast", "secret-detection", "accessibility", "ai-generated-code"]
discussion = ""
deprecated = false
description = "Security + accessibility scanner for AI-generated code. GitHub Action built on Semgrep with domain-aware rule selection, secret detection (entropy + path context), WCAG 2.1 a11y checks, and auto PR comments with fix prompts for Cursor/Claude."
plans.oss = true
plans.free = true
```

**PR title**: `Add VibeSafe`

**PR body**:
```
Adds VibeSafe — a security + accessibility scanner for AI-generated code.

- OSS, MIT, free
- Languages: JS/TS, Python, Go, Java, Ruby, HTML
- Categories: static analysis, secret detection, accessibility audit
- Integration: GitHub Action + web scanner (https://vibesafe.onrender.com)

Repo: https://github.com/vibesafeio/vibesafe-action
```

---

## Execution plan

| Step | Owner | Deadline | Metric |
|------|-------|----------|--------|
| Fork 3 repos | user | 2026-04-20 | 3 forks exist |
| Submit 3 PRs using bodies above | user | 2026-04-21 | 3 PRs open |
| Track merges in Render logs | Claude | 2026-04-28 (wait 1 week) | `grep utm=awesome-` → count inbound visits per channel |
| If merged → LinkedIn/HN announce | user | on merge | shares + stars delta |

## Why these three

| List | Stars | Merge bar | Expected latency |
|------|-------|-----------|------------------|
| awesome-actions | ~20K | Medium (curator reviews) | 1-4 weeks |
| awesome-security | ~10K | Medium | 1-3 weeks |
| analysis-tools-dev | ~3K | Low (data-file format) | 3-7 days |

Compound value: each list averages ~100-500 referral visits/month long-tail. 3 lists × 200 visits/month × indefinite = real compounding SEO.

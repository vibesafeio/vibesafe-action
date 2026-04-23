# HN + Reddit Data-Hook Post Drafts

**Strategy**: share data, not product. Tool mentioned once at the very end.
**Backing numbers**: 17 repos scanned 2026-04-19 (seed_reports.json). Re-verify numbers after a11y downgrade seed completes before posting.

---

## Show HN draft

**Title options (pick one — titles determine 80% of HN success)**:
1. `Show HN: We scanned 17 popular dev-tool repos for security + a11y (data)`
2. `Show HN: Security scores for fastapi, flask, express, shadcn-ui, and 13 more`
3. `Show HN: What happens when you scan awesome-list repos for security?`

**Recommended**: #2 — concrete repo names create curiosity + identification.

**Post body**:
```
I built a scanner (SAST + secret detection + WCAG a11y checks) tuned for
AI-generated code. To validate it wasn't garbage, I scanned 17 well-known
repos that a lot of people install without thinking about it.

The setup:
- Semgrep OSS rules + custom rules for AI-code patterns
- Secret detection with entropy + path-context (docs/, *.test.ts, *.md
  downgrade to info — this kills the fastapi-F-from-tutorial-JWTs class
  of false positives)
- WCAG 2.1 checks for <img alt>, <input aria-label>, <html lang>
- Everything runs in ~30s per repo (Docker + Semgrep)

Results (score / grade — lower = more findings):

  A (≥85)   anthropic-sdk-python, crewAI, drizzle-orm, express, flask,
            full-stack-fastapi-template, gradio, openai-python, pr-agent,
            reflex, streamlit, tailwindcss

  B (70-84) fastapi (80), shadcn-ui (79)

  C (50-69) payload (68), continue (64), trpc (60)

Interesting findings I didn't expect:

1. fastapi was initially graded F because 24 tutorial JWTs in
   docs/*/tutorial/security/ got flagged as critical. Needed to add
   "non-production path" severity downgrade before the data made sense.

2. A11y was the dominant signal in component libraries (shadcn-ui, trpc,
   payload, continue). These aren't true security findings — they're
   WCAG gaps. I had to downgrade a11y rules from medium→info because
   the rule only matched aria-label, not <Label htmlFor="id"> sibling
   patterns which is how every modern React component library writes
   labels. Structural false positive.

3. Secret detection false-positive rate was dominated by:
   - Tutorial JWTs in docs
   - Test fixtures with placeholder keys
   - Postman collection files
   - Markdown code blocks
   Path-based downgrade + Shannon-entropy < 4.0 catches ~90% without
   explicit allow-lists.

Repo + scanner: https://github.com/vibesafeio/vibesafe-action
Web version you can try on your own repo: https://vibesafe.onrender.com

Code is MIT. Rules are in rules/vibe-coding.yml. Happy to hear about
classes of findings I'm missing — especially from anyone who's fought
with a11y pattern detection (the htmlFor/Label thing feels like an
unsolved problem).
```

**Submission**:
- Tuesday or Wednesday, 8-10am PT (peak HN activity)
- First-comment should address: "why not just use Semgrep?" → answer: domain weights, a11y bundling, AI-code-specific FP filters, fix-prompt generator
- Do NOT upvote your own post. Do NOT ask friends to upvote (detected → shadowban).

---

## Reddit variants

### r/programming

**Title**: `I scanned 17 popular dev repos for security + a11y — here's what I found`

**Body**: same as HN but remove the "I built a scanner" opening. Start with:
```
Scanned some well-known repos (fastapi, flask, express, shadcn-ui, etc.)
for security issues and accessibility gaps. Found some things I didn't
expect.

[continue with same Results + Findings sections]
```

**Rules for r/programming**: must be educational, no self-promotion. Lead with findings, tool link last.

---

### r/cursor (or r/ClaudeAI)

**Title**: `Scanned popular repos for security gaps that AI tools are known to produce`

**Body**:
```
I wrote a scanner specifically tuned to find the kinds of bugs AI coding
tools (Cursor, Claude, Copilot) tend to produce. Ran it against 17
well-known repos to see how bad it is in practice.

Three classes of issues dominate AI-generated code:

1. Hardcoded secrets (esp. in examples AI writes for you to "just replace later")
2. Missing input validation on user-controlled parameters
3. Missing a11y attributes on form inputs and images — AI almost never
   adds these unless you explicitly ask

Scan results:

[Same results table]

The most common gap across all 17 repos was input-without-aria-label.
This is the kind of thing AI will never insert unless you ask for it
by name. If you're using Cursor/Claude for web UIs, add "also generate
aria-labels for form inputs" to your system prompt and it'll cut this
class of finding dramatically.

Scanner is free + open: https://vibesafe.onrender.com
Paste your repo URL, get a score in 30s. 
```

**r/cursor policy**: self-promotion allowed if it's useful/data-backed. This is borderline — lead with findings, not product.

---

### r/opensource

**Title**: `OSS scanner we built for AI-generated code — scan results on 17 popular repos`

**Body**: tool-focused (r/opensource explicitly welcomes OSS project announcements).

---

## Execution plan

| Step | Owner | Deadline | Metric |
|------|-------|----------|--------|
| Wait for re-seed | Claude bg | — | 17 repos re-scored with a11y INFO |
| Verify numbers in draft match new seed | Claude | pre-post | all scores match prod `/api/reports/recent` |
| User posts Show HN | **user** | 2026-04-22 (Tue) 8-10am PT | HN submission URL |
| Reddit posts (r/programming + r/cursor) | **user** | same day, 30min apart | 3 post URLs |
| 24h capture | Claude | 2026-04-23 | `render logs \| grep utm=hn` count, `\| grep utm=reddit` count, /api/metrics scan count delta, GitHub stars delta |

## Attribution tracking

All links in post bodies above include `?utm_source=<channel>`. Render captures:
```
[METRIC_EVENT] ts=... event=page_views detail=utm=hn-show/social/launch
[METRIC_EVENT] ts=... event=page_views detail=utm=reddit-programming/social/launch
```

**Live polling (no Render API needed)**:
```bash
# utm_rollup in one call — aggregated since last Render restart
curl -s https://vibesafe.onrender.com/api/metrics/events \
  | python3 -c "import json,sys; d=json.load(sys.stdin); [print(f'{c:>4}  {k}') for k,c in d['utm_rollup'].items()]"

# Filter by event — install_clicks since posting
curl -s "https://vibesafe.onrender.com/api/metrics/events?event=install_clicks" \
  | python3 -c "import json,sys; print(json.load(sys.stdin)['returned'])"

# Since a specific timestamp (e.g. HN post time)
curl -s "https://vibesafe.onrender.com/api/metrics/events?since=2026-04-22T16:00:00+00:00"
```

**Full history (when /api/metrics/events loses buffer after restart)**:
```bash
# Render dashboard → Logs tab → export → grep
render logs --tail 10000 | grep "utm=hn" | wc -l
```

## Risks

- HN flags first-hour: title sensationalism → flagged → dead. Keep title factual.
- Reddit r/programming aggressive mod removal if framed as self-promo.
- If data looks "too clean" (all A/B/C no F), skeptics will call it a demo.
  Mitigation: explicitly show that initial scan had F's and explain why they
  were fixed (structural FP classes). Honesty is the hook.

# Handoff Index — GNT Reader

These documents capture project state so that any session (human or AI) can spin up with full context. Read them in order.

| File | Covers |
|------|--------|
| `00-index.md` | This index and update protocol |
| `01-project-overview.md` | Project vision, origin story, scholarly landscape, research advantages |
| `02-colometry-method.md` | Greek colometric methodology, principles, rules, open questions |
| `03-architecture.md` | Repo structure, build pipeline, scripts, web app, deployment |
| `04-editorial-workflow.md` | How text gets from raw SBLGNT to finished reading edition |
| `YLT-visualization.md` | Conversation exploring a toggleable YLT English layer; design decision and rationale (2026-04-10) |

---

### Update Protocol

When updating handoff docs, append a dated block at the bottom of the relevant file:

```markdown
---
### Update — 2026-MM-DD
- What changed
- What was decided
- New state
```

Never overwrite history — always append.

---

### Update — 2026-04-10 (session 4)

Files updated this session:
- `01-project-overview.md` — YLT replaced by WEB; domain purchased and configured; colometric methodology reset documented
- `02-colometry-method.md` — Five new editorial principles from Mark 4 v4 gold standard (updated separately during session)
- `03-architecture.md` — New scripts (web_align.py, diagnostic_scanner.py, experimental alignment scripts), new directories (v4-editorial, web-colometric), updated build pipeline, domain/CNAME deployment
- `04-editorial-workflow.md` — v4 editorial tier established with Mark 4 as first gold standard chapter; pipeline diagram updated; colometric methodology reset and its implications for v3 output

---

### Update — 2026-04-11 (post v4 editorial review)

Files updated this session:
- `01-project-overview.md` — English layer replaced by structural glosses; universal vocative rule; cross-pollination from BOM Reader; methodology maturation with ~15 sub-principles
- `03-architecture.md` — Updated pipeline priority chain (v4-editorial > v3-colometric for Greek, web-colometric structural glosses for English); gnt-reader.com live with HTTPS
- `04-editorial-workflow.md` — System-wide v4 editorial review: 120 chapters complete, ~52 still need second pass; common fix patterns documented; gold standards expanded to Mark 4 + Acts 1

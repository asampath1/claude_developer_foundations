# Progress Tracker

The one file you write in. Everything the adaptive rules need lives here: your scores, your current difficulty level, and the tags you keep missing.

When you ask me to run a session or build a reinforcement set, point me at this file and I'll pick up where you left off.

---

## Current status

| Field | Value |
|---|---|
| Current difficulty level | L2 Applied |
| Sessions completed | 0 of 8 |
| Mock exams taken | 0 of 4 |
| Latest readiness score | — |
| Exam date | — |
| Next action | Session 1 — Applications and Integration |

Update this block after every session or mock. It's the first thing I read.

---

## Session log

Record every coaching session. The **Next level** column applies the difficulty rule: above 80% go up one level, 60–80% stay, below 60% go down one level with expanded explanations.

| Date | Session | Level run | Score | % | Weakest tags this session | Next level |
|---|---|---|---|---|---|---|
| | 1 — Applications and Integration | | /15 | | | |
| | 2 — Model Selection and Optimization | | /14 | | | |
| | 3 — Agents and Workflows | | /13 | | | |
| | 4 — Prompt and Context Engineering | | /12 | | | |
| | 5 — Tools and MCP | | /12 | | | |
| | 6 — Security and Safety | | /12 | | | |
| | 7 — Claude Code | | /10 | | | |
| | 8 — Eval, Testing, and Debugging | | /10 | | | |

Example of a filled row, for format:

| 2026-09-12 | 3 — Agents and Workflows | L2 | 10/13 | 77% | `agents.construction`, `agents.patterns` | L2 (hold) |

Repeat a session rather than moving on when you score below 60%. Mocks measure; sessions teach.

---

## Mock exam log

| Mock | Date | Raw score | % | Weighted readiness | Domains under 70% |
|---|---|---|---|---|---|
| 1 | | /50 | | | |
| 2 | | /50 | | | |
| 3 | | /50 | | | |
| 4 | | /50 | | | |

### Domain breakdown across mocks

Fill in the percentage per domain per mock. The trend across a row matters more than any single cell — a domain that stays flat after reinforcement needs a different approach, not another mock.

| Domain | Weight | M1 | M2 | M3 | M4 |
|---|---|---|---|---|---|
| Applications and Integration | 33.1% | | | | |
| Model Selection and Optimization | 16.8% | | | | |
| Agents and Workflows | 14.7% | | | | |
| Prompt and Context Engineering | 11.0% | | | | |
| Tools and MCP | 10.6% | | | | |
| Security and Safety | 8.1% | | | | |
| Claude Code | 3.1% | | | | |
| Eval, Testing, and Debugging | 2.6% | | | | |

Weighted readiness = Σ (domain % × domain weight). Bands: 85%+ ready to sit, 75–84% nearly ready, 65–74% real gaps, below 65% not yet.

---

## Weak areas

Add a row the first time you miss a tag. A tag becomes **active** (drilled in reinforcement sets) at two misses, or immediately if its domain scored under 70% on a mock.

| Tag | Misses | Status | Where it came from | Revise | Cleared |
|---|---|---|---|---|---|
| | | | | | |

Status values: `watching` (one miss), `active` (two or more — appears in reinforcement sets), `clearing` (answered correctly once since going active), `cleared` (correct twice in a row — stops appearing).

Example rows, for format:

| `apps.api-mechanics` | 3 | active | S1 Q7, M1 Q22, M1 Q41 | `2_applications_and_integration.md` → Claude API Mechanics | |
| `sec.hooks` | 2 | clearing | S6 Q4, M1 Q13 | `5_eval_debugging_security.md` → Hooks as enforcement | 1 of 2 |

Write down *why* you missed it, not just that you did. "Confused adaptive with extended thinking" is actionable; a tick in a box is not.

---

## Reinforcement sets

Drill only what you're actually getting wrong:

> Generate a 10-question reinforcement set from my active weak areas in the tracker, at L2, questions only — hold the answers until I've finished.

| Date | Tags drilled | Questions | Score | Tags moved to clearing/cleared |
|---|---|---|---|---|
| | | | | |

Rules the sets follow:
- Only `active` tags are drawn from.
- Fresh scenarios every time — no reuse of session or mock questions.
- A tag needs two consecutive correct answers to clear, and one miss sends it back to `active` with the counter reset.

---

## Readiness snapshot

Fill this in before booking the exam.

| Check | Target | Yours |
|---|---|---|
| All eight sessions completed | 8/8 | |
| Latest mock weighted readiness | 85%+ | |
| Applications and Integration (33.1% of the exam) | 80%+ | |
| No domain below | 70% | |
| Active weak-area tags remaining | 0–2 | |
| Mock exam 4 taken timed and closed-book | Yes | |

Applications and Integration gets its own line because it's a third of the exam on its own. Strong scores everywhere else can't compensate for a weak score there.

---

## Notes to self

Anything worth remembering between sessions — a distinction that keeps slipping, a scenario that caught you out, a gotcha you want to see once more the morning of the exam.

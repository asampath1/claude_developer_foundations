# Claude Developer Exam Coach — CCDV-F

A domain-by-domain training program for the [Claude Certified Developer – Foundations](https://anthropic-partners.skilljar.com/claude-certified-developer-foundations-certification) exam (**CCDV-F**), built entirely from this repository's notes and Anthropic's official documentation.

Eight coaching sessions covering every exam domain at its official weight, four non-overlapping mock exams, and an adaptive tracker that decides what you study next based on what you actually got wrong.

---

## What's here

| File | What it's for |
|---|---|
| [`progress_tracker.md`](progress_tracker.md) | Your score log, weak-areas list, and current difficulty level. The one file you write in. |
| [`sessions/`](sessions/) | Eight coaching sessions, one per domain, in study order |
| [`mock_exams/blueprint.md`](mock_exams/blueprint.md) | How the mock exams are built, how to score them, and when to take each |
| [`mock_exams/mock_exam_1.md`](mock_exams/mock_exam_1.md) … [`mock_exam_4.md`](mock_exams/mock_exam_4.md) | Four full 50-question exams, 200 unique questions, no repetition |
| [`analogies/`](analogies/) | Plain-language walkthroughs of a source chapter through one sustained analogy, for when the mechanisms won't stick from the notes alone |

Source material lives in the repository root — the five domain files, [`exam_sections.md`](../exam_sections.md), and [`study_cheat_sheet.md`](../study_cheat_sheet.md). Everything in this program traces back to those.

## The eight sessions

Ordered by exam weight, so your first hours go where the marks are.

| # | Session | Weight | Questions | Official domains covered |
|---|---|---|---|---|
| 1 | [Applications and Integration](sessions/session_1_applications_and_integration.md) | 33.1% | 15 | Domain 2 |
| 2 | [Model Selection and Optimization](sessions/session_2_model_selection_and_optimization.md) | 16.8% | 14 | Domain 5 |
| 3 | [Agents and Workflows](sessions/session_3_agents_and_workflows.md) | 14.7% | 13 | Domain 1 |
| 4 | [Prompt and Context Engineering](sessions/session_4_prompt_and_context_engineering.md) | 11.0% | 12 | Domain 6 |
| 5 | [Tools and MCP](sessions/session_5_tools_and_mcp.md) | 10.6% | 12 | Domain 8 |
| 6 | [Security and Safety](sessions/session_6_security_and_safety.md) | 8.1% | 12 | Domain 7 |
| 7 | [Claude Code](sessions/session_7_claude_code.md) | 3.1% | 10 | Domain 3 |
| 8 | [Eval, Testing, and Debugging](sessions/session_8_eval_testing_and_debugging.md) | 2.6% | 10 | Domain 4 |

98 questions across the eight sessions, plus 200 across the mock exams.

Sessions 7 and 8 carry more questions than their exam weight justifies. That's deliberate: Claude Code and debugging concepts show up inside scenario questions belonging to other domains, so the material is worth more than its 5.7% combined weighting suggests.

## How to run a session

Each session is written to work two ways.

**Self-study.** Read Section A, answer Section B's questions on paper without looking ahead, then score yourself against the answer key and fill in Section C. Roughly 10–15 minutes.

**Coached.** Ask me to run it live:

> Run coaching session 3. Give me Section A, then ask me the questions one at a time and wait for my answer before revealing anything.

Coached mode is better for weak areas, because I can follow up on a wrong answer immediately rather than leaving you to read an explanation. Self-study is better for a fast pass over material you mostly know.

## Session format

**Section A — Domain Overview.** What the domain actually tests, the key patterns and decision rules, the mistakes that cost people marks, and worked exam-style scenarios.

**Section B — Questions.** 10–15 multiple-choice questions, four options each, single best answer. The answer key follows the questions rather than sitting under each one, so you can work through the set without spoiling yourself. Every answer entry gives the correct option, why it's correct, why each other option is wrong, a difficulty rating, and the exact repo section to revise.

**Section C — Score and Analysis.** A scoring table, a weak-area map that turns your specific misses into a revision list, and the adaptive next step based on your percentage.

## Adaptive learning

All three modes are active across the program. The rules are mechanical on purpose — no judgment calls about whether you're "ready."

### Difficulty scaling

| Your session score | Next session runs at | What changes |
|---|---|---|
| Above 80% | One level harder | More multi-step scenarios, more constraints that override the obvious answer, distractors separated by a single detail |
| 60–80% | Same level | Steady mix |
| Below 60% | One level easier, with expanded explanations | More recall and single-rule questions, and every answer entry explains the underlying mechanism, not just the choice |

Three levels: **L1 Foundations** (recall and single-rule application), **L2 Applied** (short scenarios, adjacent-mechanism discrimination), **L3 Production** (multi-step scenarios, integrative constraints, structural reasoning). Sessions ship at L2. Record your current level in the tracker; when you ask me to run a session, tell me the level or point me at the tracker.

### Weak-area reinforcement

Every question carries a tag. When you miss one, log its tag in the tracker's weak-areas table. A tag becomes a **weak area** when you miss it twice, or when any domain scores under 70% on a mock exam.

To drill them, ask:

> Generate a 10-question reinforcement set from my current weak areas in the tracker, at L2, questions only — hold the answers until I've finished.

Reinforcement sets draw only from tagged weak areas, use fresh scenarios, and retire a tag once you clear it twice in a row.

### Progressive scenario depth

The program moves through three stages as you work through it, independent of difficulty level:

| Stage | Question shape | Where it appears |
|---|---|---|
| 1. Recall | Name the mechanism, read the table row, define the boundary | Early questions in each session |
| 2. Applied | One scenario, one decision, one rule to apply | Middle of each session, most of mock exams 1–2 |
| 3. Production | Multi-step agent/tool/MCP scenarios, JSON-schema and structured-output validation, tool-calling and message-block sequencing, safety constraints that override the operationally convenient answer | End of each session, the Hard band of every mock, and mock exam 4 throughout |

## Tag taxonomy

Tags map to the official skill breakdown in [`exam_sections.md`](../exam_sections.md), so a weak area points at a specific place in the notes.

| Tag | Skill | Revise in |
|---|---|---|
| `apps.requirements` | Understanding Requirements | `2_applications_and_integration.md` |
| `apps.lifecycle` | Systems Life Cycle | `2_applications_and_integration.md` |
| `apps.api-mechanics` | Claude API Mechanics | `2_applications_and_integration.md` |
| `apps.swe` | Software Engineering Foundations | `2_applications_and_integration.md` |
| `apps.design` | Claude Application Design | `2_applications_and_integration.md` |
| `apps.config` | Configuration Management | `2_applications_and_integration.md` |
| `mso.llm-fundamentals` | LLM Fundamentals | `4_model_selection_prompting_context.md` |
| `mso.technical` | Technical Fundamentals | `4_model_selection_prompting_context.md` |
| `mso.model-choice` | Model Selection and Tradeoffs | `4_model_selection_prompting_context.md` |
| `mso.cost` | Cost and Token Management | `4_model_selection_prompting_context.md` |
| `agents.architecture` | Agent Architecture | `1_agents_and_workflows.md` |
| `agents.construction` | Agent Construction with Claude | `1_agents_and_workflows.md` |
| `agents.patterns` | Agent Patterns and Frameworks | `1_agents_and_workflows.md` |
| `prompt.context` | Context Engineering | `4_model_selection_prompting_context.md` |
| `prompt.prompting` | Prompt Engineering | `4_model_selection_prompting_context.md` |
| `prompt.output` | Output Handling | `4_model_selection_prompting_context.md` |
| `tools.implementation` | Tool Implementation | `3_claude_code_tools_mcp.md` |
| `tools.mcp` | MCP Server Development | `3_claude_code_tools_mcp.md` |
| `tools.customization` | Agentic Customization | `3_claude_code_tools_mcp.md` |
| `sec.appsec` | AI Application Security | `5_eval_debugging_security.md` |
| `sec.guardrails` | Guardrails and Safe Deployment | `5_eval_debugging_security.md` |
| `sec.hooks` | Claude Hooks | `5_eval_debugging_security.md` |
| `sec.secrets` | Identity, Secrets, and Key Management | `5_eval_debugging_security.md` |
| `cc.operation` | Claude Code Operation | `3_claude_code_tools_mcp.md` |
| `eval.debugging` | Debugging and Error Handling | `5_eval_debugging_security.md` |

## Recommended order

1. Sessions 1 → 4, in order. These are 75.6% of the exam.
2. **Mock exam 1** as a baseline. Expect gaps in domains you haven't reached yet; that's the point.
3. Sessions 5 → 8.
4. **Mock exam 2** — your first honest full-blueprint measurement.
5. A reinforcement set on your top three weak-area tags, then re-run any session whose domain scored under 70%.
6. **Mock exam 3** to confirm the reinforcement took.
7. **Mock exam 4**, timed and closed-book, as the final rehearsal. Its readiness score is your go/no-go signal.

Take the mocks cold and timed. A mock taken with the notes open measures your reading speed, not your readiness.

## Ground rules

- Everything in this program comes from this repository's notes plus Anthropic's official documentation. No invented features, parameters, or model behaviors.
- The blueprint in [`exam_sections.md`](../exam_sections.md) is Exam Guide v1.0, effective July 2026. Re-check for a version bump before your exam date — if the weights move, the session order and mock distributions should move with them.
- Where the notes flag a number as "verify at build time" (pricing, context windows, per-tier limits, feature availability), the exam-relevant fact is the mechanism and the tradeoff, not the number. Questions here are written accordingly.
- These are original practice questions written from the public blueprint and paraphrased course material. They are not reproductions of real exam items, which are confidential.

## Checking the question files

`python3 tools/check_questions.py` verifies every question file in one pass: question and answer-entry counts, answer-letter balance, difficulty spread, per-domain counts against [`mock_exams/blueprint.md`](mock_exams/blueprint.md), that no answer entry is missing its explanation, difficulty, domain, tag, or revise pointer, and that no two stems across the sessions, the mocks, and [`study_practice_questions.md`](../study_practice_questions.md) are near-duplicates. Run it after editing or adding any question — a reworded stem can quietly collide with one three files away.

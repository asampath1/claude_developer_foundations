# Session 8 — Eval, Testing, and Debugging (2.6%)

Domain 4 of the CCDV-F blueprint. Smallest weight on the exam, largest leverage on everything else: evals gate model and prompt promotion in Applications, and error classification shows up in every integration scenario.

Source: [`5_eval_debugging_security.md`](../../5_eval_debugging_security.md). Level: **L2 Applied**. Time: 10–15 minutes.

---

## Section A — Domain Overview

### What this domain actually tests

The blueprint lists one skill — Debugging and Error Handling (2.6%): identifying error types, selecting recovery strategies, analyzing traces, and isolating integration-layer failures from model-output failures. The eval material sits alongside it because it's what produces the signal you debug against.

### Key patterns

**An eval turns "done" from a feeling into a number.** A fixed set of input cases, each with a written expected behavior, run through the feature and graded. Write it **before** the feature, so success is defined rather than rationalized afterward. A minimal pipeline is three functions: run one case, grade one output, loop and average.

A low first score is normal. What matters is whether it moves when you **change one thing at a time** — prompt, tools, *or* model, never two at once. And read the **per-case breakdown**, not just the average: a steady average can hide a change that fixed three cases and broke three others.

**Match the grading method to the output shape:**

| Output shape | Method | Blind to |
|---|---|---|
| One correct label or value | Exact/string match | Any valid paraphrase or reordering |
| Structured output or code | Code-graded check (parses, valid syntax, in range, required field present) | Whether the content is any *good* |
| Open-ended quality | LLM-as-judge | Nothing a code rule can express — but noisy and costly until calibrated |

Exact-match and code checks run locally and effectively free, so run thousands per commit. A judge is a second model call per case — a 1,000-case judged eval is 1,000 extra API calls every run — so reserve it for a scheduled quality pass rather than the inner loop. Calibrate a judge by asking for `strengths`/`weaknesses`/`reasoning` **before** the score (without reasoning-first, judges drift to a safe middle score regardless of quality), then measure agreement against a human-labeled set before trusting the number.

**Coverage beats a small perfect set:** 20 cases including irregular and edge inputs catch more than 3 carefully-chosen ones.

**Four test levels, each catching what the others miss:**

| Level | Isolates | Cannot catch |
|---|---|---|
| Unit | One function alone | How components fit together |
| Functional | One Claude call returning the expected shape | Failures in the system around that call |
| Integration | The **seam** where two components hand off | Whole-flow behavior |
| End-to-end | The full flow as a user runs it | *Where* the break is |

**Most silent production breaks live at the integration seam**, because each side passes its own test while the handoff is broken — the standard example being `retrieve()` returning chunk dicts where `build_prompt()` expected a string, so the model answered from memory instead of the retrieved policy.

**A test says a failure exists; a trace says where.** A timeline of each step's prompt, tool calls, intermediate outputs, and timing turns "something's wrong" into "step 4's parser raised a `KeyError` on a field the model didn't return." The failure *category* from a trace directs the next fix: formatting failures point at output instructions, factual failures on retrieved content point at retrieval, failures that appear only on long input point at context handling.

**Retriable or terminal?** One question gates everything: would waiting and retrying the identical request plausibly work?

| Status | Retriable |
|---|---|
| 429 rate limit | Yes — honor `retry-after` |
| 529 overloaded | Yes |
| 500 / 502 / 503 / 504 | Yes — transient server-side |
| 400 bad request | No |
| 401 authentication | No |
| 403 permission | No |
| 404 missing resource | No |

**When unsure, default to terminal.** A failure misclassified as terminal fails loudly and gets fixed; one misclassified as retriable hammers a service and hides the real problem.

Three details that catch people out:

1. **Check what the SDK already retries** before writing your own loop. The client libraries retry transient failures with progressive delay up to a configurable count — stacking your own loop on top multiplies attempts against the same rate limit instead of capping them.
2. **A refusal is not a retriable error and the status-code classifier won't catch it** — it returns **HTTP 200** with `stop_reason: "refusal"`. Raise it, log it, never silently retry.
3. **Tool errors must return to Claude explicitly** with `is_error: true` on the `tool_result`. A tool that swallows its error and returns an empty result produces a confident, wrong answer built on missing data.

**Integration layer or model output?** The isolating question this domain tests. A malformed request, a mismatched `tool_use_id`, a broken format contract at a handoff, or a hook silently denying a call are integration-layer failures — diagnosed from the raw request/response and the trace, not by re-prompting. A `stop_reason` of `refusal` or `max_tokens` on a clean, well-formed request points at *what was asked for*, not at the request-construction code.

### Common mistakes

- **Validating shape and calling it correctness.** The field-extraction incident: a message containing two dates yielded a well-formed, populated, *wrong* date. Validation confirms a value is the right shape; only a graded case with human-checked expected output confirms it's the right value.
- **Changing prompt and model together** and then wondering which helped.
- **Trusting a judge score before measuring agreement with human labels.**
- **Writing no error path because development traffic never hit a rate limit**, then retrying in a tight loop when production does.
- **Asserting exact strings** against non-deterministic output.
- **Re-prompting to fix an integration-layer bug.**

### Real exam-style scenarios

**Scenario A.** A parser unit test passes. A functional test of the Claude call passes. The end-to-end test fails, and the model's answers ignore the retrieved policy.

The reasoning: both passing tests are irrelevant — the unit worked and the functional call worked on well-formed input. The break is at the seam, where `retrieve()` handed a list of dicts to something expecting a string, so the model received malformed context and answered from memory. Only a test driving the actual handoff with real retrieved data surfaces this, which is why the integration level exists.

**Scenario B.** The first production traffic spike returns 429s. The unhandled exception takes down the request, and the developer's instinct is to retry immediately in a loop, which makes it worse.

The reasoning: 429 is retriable, so the fix is classification plus discipline — back off with a cap, honor `retry-after` over guessing, and check whether the SDK is already retrying before adding a loop of your own. Effort isn't the missing ingredient; classification is.

---

## Section B — Questions

10 questions, four options each, single best answer.

### Q1

What distinguishes an eval from "I tried it a few times and it looked right", and when should it be written?

A. An eval is a production monitoring dashboard, built after launch once real traffic exists
B. An eval is a fixed set of input cases with written expected behavior, run and graded to produce a score — and it should be written before the feature, so success is defined rather than rationalized afterward
C. An eval is a load test measuring latency under concurrency, written during the deploy phase
D. An eval is a one-time acceptance check performed at handover and then retired

### Q2

A feature returns a JSON object your code consumes. You want a check cheap enough to run on every commit. Which grading method, and what won't it tell you?

A. LLM-as-judge, which will report both format and content quality
B. Exact string match, which is the only method suitable for JSON
C. A code-graded check — does it parse, are required fields present, are values in range — which says nothing about whether the content is any good
D. No automated grading is possible for structured output; it requires manual review

### Q3

A team wants to run a 1,000-case eval on every commit and is considering LLM-as-judge for all of it. What's the correct assessment?

A. Correct — a judge is the most accurate method, so it should be used wherever possible
B. Incorrect — judges can't evaluate structured output at all
C. Correct, provided the judge runs on a cheaper model tier
D. A judge is a second model call per case, so 1,000 cases means 1,000 extra API calls every run — grade format and structure with code in the inner loop and reserve the judge for a slower, scheduled quality pass

### Q4

An eval score moves from 62% to 71% after a change in which the team swapped the model tier and rewrote the system prompt. What's the problem, and what else should they check?

A. They can't attribute the gain to either change — one variable per iteration — and they should read the per-case breakdown, because a steady or improved average can hide cases that regressed
B. Nothing; a 9-point gain justifies keeping both changes
C. The score is invalid because model and prompt changes can't be evaluated by the same suite
D. They should re-run the eval several times and average, since the score itself is non-deterministic

### Q5

A retrieval-augmented feature has passing unit tests for its parser and passing functional tests for its Claude call, yet the model answers from memory instead of the retrieved policy. Which test level would have caught this, and why did the others miss it?

A. Unit tests, with better mocking of the retrieval function
B. End-to-end tests, which are the only level that exercises real data
C. Integration tests, which drive the seam where one component hands off to another — the unit worked in isolation and the functional call worked on well-formed input, so neither could see a broken handoff
D. Functional tests, run against a larger sample of inputs

### Q6

An eval case fails. What does a trace add that the failing score doesn't?

A. A statistical confidence interval for the score
B. A timeline of each step's prompt, tool calls, intermediate outputs, and timing — turning "something's wrong" into which step failed and how
C. An automatic retry of the failing case with a higher effort level
D. A comparison against the previous model version's output for the same case

### Q7

Which of these should your client treat as retriable?

A. 400 and 403, since both can succeed on a second attempt once the service settles
B. 401, because credentials are often propagating at the moment of the call
C. 404, because a resource may not have finished being created
D. 429 and 529 — plus 500/502/503/504 — because they're rate-limit or transient server-side faults, whereas 400/401/403/404 fail identically on an identical retry

### Q8

A developer adds a retry loop with exponential backoff around every Claude call, on top of the SDK's own retry behavior. What's the consequence?

A. Attempts multiply against the same rate limit rather than being capped — decide explicitly whether the SDK owns transient retries or your code does, and honor `retry-after` over guessing at backoff
B. Nothing measurable; the SDK detects an outer retry loop and disables its own
C. Latency improves because the two mechanisms interleave attempts
D. The SDK's retries only cover connection errors, so the outer loop is always required

### Q9

A response arrives with HTTP 200 and `stop_reason: "refusal"`. How should the application treat it?

A. As a transient failure — retry with backoff, since the status code is a success
B. As a 400-class error, converted and returned to the caller as a bad request
C. As a content decision, not a transient fault: raise it to the caller and log it, never silently retry it or treat it as valid output — and note the status-code classifier won't catch it, because the HTTP status is 200
D. As valid output, since the request completed successfully at the transport level

### Q10

A tool's implementation catches its own exceptions and returns an empty result so the agent doesn't crash. What does this cause?

A. The agent halts, because an empty tool result fails request validation
B. A confident but wrong downstream answer — the model treats the empty result as valid data and reasons on top of it, which is why a failing tool should return `is_error: true` on the `tool_result`
C. An automatic retry of the tool call by the SDK, up to the configured attempt count
D. Nothing harmful; empty results are the standard way to signal tool failure

---

### Answer Key and Explanations

#### Q1 — Answer: B

- **Why B is correct:** An eval is a fixed, graded case set with written expected behavior, and writing it first forces success to be defined before implementation rather than rationalized from whatever the model produced.
- **Why not A:** Production monitoring is valuable but isn't an eval, and building it after launch loses the pre-implementation definition.
- **Why not C:** Load testing measures performance, not output quality.
- **Why not D:** An eval is the ongoing gate on prompt and model changes, not a one-time acceptance check.
- **Difficulty:** Easy
- **Tag:** `eval.debugging/eval-basics`
- **Revise:** `5_eval_debugging_security.md` → The core idea

#### Q2 — Answer: C

- **Why C is correct:** Structured output is graded by code checks — parses, valid syntax, required field present, value in range — which run locally and effectively free, and which say nothing about content quality.
- **Why not A:** A judge can assess quality but costs an API call per case, which is exactly what you don't want on every commit.
- **Why not B:** Exact match is for a single unambiguous label or value, and breaks on any valid reordering.
- **Why not D:** Automated grading of structured output is straightforward; it's *quality* grading that needs a judge.
- **Difficulty:** Medium
- **Tag:** `eval.debugging/grading-methods`
- **Revise:** `5_eval_debugging_security.md` → Matching the grading method to the output shape

#### Q3 — Answer: D

- **Why D is correct:** Each judged case is an extra model call, so a large judged suite is expensive on every run. Grade format and structure with code in the tight loop and reserve the judge for what only a judge can assess, on a slower scheduled pass.
- **Why not A:** A judge is noisy and costly, and produces a confident-looking number that means nothing until calibrated against human labels.
- **Why not B:** A judge *can* assess structured output; it's just the wrong tool when a code check suffices.
- **Why not C:** A cheaper judge reduces unit cost but doesn't change the structural problem, and a weaker judge is harder to calibrate.
- **Difficulty:** Medium
- **Tag:** `eval.debugging/judge-cost`
- **Revise:** `5_eval_debugging_security.md` → Matching the grading method to the output shape

#### Q4 — Answer: A

- **Why A is correct:** Two changes in one iteration make attribution impossible, and the average can conceal offsetting per-case movement — which is why the per-case breakdown matters as much as the mean.
- **Why not B:** Keeping both changes means never learning which one worked, and carrying the other's risk.
- **Why not C:** The same suite is exactly what should evaluate both kinds of change — one at a time.
- **Why not D:** Repeated runs address sampling noise but not the attribution problem.
- **Difficulty:** Medium
- **Tag:** `eval.debugging/iteration-discipline`
- **Revise:** `5_eval_debugging_security.md` → The core idea

#### Q5 — Answer: C

- **Why C is correct:** Most silent production breaks live at the integration seam. The unit test passed because the unit worked; the functional test passed because the call worked on well-formed input. Only a test driving the actual handoff with real retrieved data surfaces the type mismatch.
- **Why not A:** Better mocking makes the unit test pass more convincingly while the real handoff stays broken.
- **Why not B:** The end-to-end test did fail here — it just can't tell you *where*, which is the point of the integration level.
- **Why not D:** More inputs to a functional test still bypasses the handoff.
- **Difficulty:** Hard
- **Tag:** `eval.debugging/test-levels`
- **Revise:** `5_eval_debugging_security.md` → Four test levels

#### Q6 — Answer: B

- **Why B is correct:** A trace is a timeline of each step — prompt, tool calls, intermediate outputs, timing — which converts a failed case into a specific failing step and a specific cause.
- **Why not A:** Traces localize failures; they don't do statistics.
- **Why not C:** Nothing about a trace retries anything.
- **Why not D:** Version comparison is a separate practice from tracing a single run.
- **Difficulty:** Medium
- **Tag:** `eval.debugging/tracing`
- **Revise:** `5_eval_debugging_security.md` → Tracing

#### Q7 — Answer: D

- **Why D is correct:** 429 and 529 are the canonical retriable cases, along with 500/502/503/504 as transient server-side faults. 400, 401, 403, and 404 fail identically on an identical retry.
- **Why not A:** A bad request and a permission problem can't be fixed by waiting.
- **Why not B:** An authentication failure is terminal; retrying won't produce valid credentials.
- **Why not C:** A missing resource is terminal for the identical request.
- **Difficulty:** Medium
- **Tag:** `eval.debugging/error-classification`
- **Revise:** `5_eval_debugging_security.md` → Failure handling

#### Q8 — Answer: A

- **Why A is correct:** The client libraries already retry transient failures with progressive delay. An outer loop multiplies attempts against the same limit rather than capping them, so ownership has to be an explicit decision — and `retry-after` beats guessing when the service tells you when capacity returns.
- **Why not B:** There's no such detection or auto-disable.
- **Why not C:** More attempts against a rate limit deepen the problem rather than improving latency.
- **Why not D:** SDK retries cover transient failures generally, not only connection errors.
- **Difficulty:** Hard
- **Tag:** `eval.debugging/retry-strategy`
- **Revise:** `5_eval_debugging_security.md` → Failure handling

#### Q9 — Answer: C

- **Why C is correct:** A refusal is a content decision returned with HTTP 200 and `stop_reason: "refusal"`. It should be raised and logged, never retried silently or passed downstream as valid output — and a status-code-only classifier will miss it entirely.
- **Why not A:** Retrying an identical refused request just refuses again.
- **Why not B:** It isn't a malformed request, so recasting it as a 400 misrepresents the failure.
- **Why not D:** Transport success doesn't make the content usable.
- **Difficulty:** Medium
- **Tag:** `eval.debugging/refusal-handling`
- **Revise:** `5_eval_debugging_security.md` → Failure handling

#### Q10 — Answer: B

- **Why B is correct:** A swallowed tool error returns an empty result the model treats as valid data, producing a confident answer built on nothing. Setting `is_error: true` on the `tool_result` surfaces the failure so the model can react.
- **Why not A:** An empty result is structurally valid; it's semantically misleading, which is worse.
- **Why not C:** No automatic tool-call retry happens on an empty result.
- **Why not D:** It's specifically the harmful pattern this section warns against.
- **Difficulty:** Medium
- **Tag:** `eval.debugging/tool-errors`
- **Revise:** `5_eval_debugging_security.md` → Failure handling

---

## Section C — Score and Analysis

### Score

| | |
|---|---|
| Correct | ___ / 10 |
| Percentage | ___ % |
| Difficulty level run | L2 Applied |

| Band | Reading |
|---|---|
| 9–10 (90%+) | Strong. You've finished all eight sessions — move to the mock exams. |
| 7–8 (70–80%) | Solid. Re-read the error-code table, then move to the mocks. |
| 5–6 (50–60%) | Re-read the failure-handling section, then repeat at L1. |
| Below 5 | Repeat at L1. This domain is small on the exam but its error-classification content appears inside integration scenarios in the larger domains. |

### Weak-area map

Every question here tags to `eval.debugging`, so track the sub-tag:

| Missed | Sub-tag | Revise |
|---|---|---|
| Q1, Q4 | `/eval-basics`, `/iteration-discipline` | `5_eval_debugging_security.md` → The core idea |
| Q2, Q3 | `/grading-methods`, `/judge-cost` | `5_eval_debugging_security.md` → Matching the grading method |
| Q5, Q6 | `/test-levels`, `/tracing` | `5_eval_debugging_security.md` → Four test levels, Tracing |
| Q7–Q10 | `/error-classification`, `/retry-strategy`, `/refusal-handling`, `/tool-errors` | `5_eval_debugging_security.md` → Failure handling |

### Recommended next steps

1. Memorize the retriable/terminal table, including the two cases the status code alone won't tell you: a refusal arrives as HTTP 200, and a tool failure only reaches the model if you set `is_error: true`.
2. Keep the isolating question ready for every debugging scenario on the exam: integration layer, or model output? Malformed requests, mismatched IDs, broken handoffs, and silently denying hooks are the former; a wrong or oddly-shaped response to a well-formed request is the latter.
3. Update the tracker. All eight sessions are now complete — take **Mock Exam 2** as your first honest full-blueprint measurement, then drill your active weak-area tags before Mock Exam 3.

**Next domain or repeat this one?**

# Session 4 — Prompt and Context Engineering (11.0%)

Domain 6 of the CCDV-F blueprint. Diagnostic thinking is what's being tested here: not "write a better prompt" but "identify which structural piece is missing."

Source: [`4_model_selection_prompting_context.md`](../../4_model_selection_prompting_context.md). Level: **L2 Applied**. Time: 10–15 minutes.

---

## Section A — Domain Overview

### What this domain actually tests

| Skill | Weight | The question behind the questions |
|---|---|---|
| Context Engineering | 3.8% | Managing the whole token budget: pruning, compaction, subagent isolation |
| Prompt Engineering | 4.6% | Diagnosing a failure to the missing technique, not rewording |
| Output Handling | 2.6% | Structured outputs, defensive parsing, skepticism toward confident output |

### Key patterns

**Context engineering is the superset.** Prompt engineering is about *what you say*; context engineering is about *curating the full set of tokens* available at each inference call — prompt, history, tool definitions, tool outputs, injected documents.

**Two bloat-control techniques that solve different problems:**

| Technique | Use when | Cost |
|---|---|---|
| Tool output pruning / clearing | The bloat is re-fetchable tool output — a big file read, verbose command output | Cheap and lossless: no LLM call, and the agent can just re-call the tool |
| Compaction | The bloat is dialogue and reasoning that **can't** be cheaply re-fetched | An LLM call to summarize; preserves non-recoverable context |

The Agent SDK compacts automatically as the window fills, emitting a `compact_boundary` event. A `PreCompact` hook can archive the full transcript first. Because compaction can lose specific early instructions, **persistent rules belong in CLAUDE.md** — re-injected every request — rather than only in the opening prompt.

**Subagent isolation** is the third lever: a fresh context per subagent, with only the final response returning to the parent.

**The four prompt techniques, indexed by failure signature.** This table is the highest-yield thing in the domain:

| Symptom | Missing technique |
|---|---|
| Output comes back in the wrong *shape* — prose where you wanted a label, text where you wanted JSON | Output constraint |
| Content is off — scope drifts, tone shifts, quality decays deeper into the conversation | System prompt, or a more specific one |
| Task is right but the structure is invented | Few-shot examples |
| Clean on tested inputs, breaks on a variant or edge case | A constraint covering that variant |

Rewording changes how you say something; it doesn't add a missing technique. **If a prompt keeps getting longer with each iteration and still fails, that's the signal you're padding instead of diagnosing.** Five failed re-prompts means stop and classify the failure.

The worked classification pattern stacks three techniques because each does a job the others can't: a **system prompt** sets the output contract, **XML tags** mark where each few-shot example begins and ends so Claude doesn't read them as live instructions, and **few-shot pairs** show exact casing and format. Stacking is right for a clearly-defined output contract with edge cases; it's over-engineering on a task that needs one technique.

**Structured outputs move the guarantee from the prompt into the API** via constrained decoding — the model can only emit tokens that keep the output valid against your schema, so an invalid response literally can't be generated.

| Mechanism | Constrains |
|---|---|
| JSON outputs (`output_config.format`, `json_schema`) | The final response your code consumes |
| Strict tool use (`strict: true` on a tool definition) | The arguments Claude passes to your tools, before your code runs |

What structured outputs cost, and what they still don't guarantee: the first request on a new schema pays a grammar-compile latency (compiled grammars cached **24 hours** from last use); token cost rises slightly because the API injects a format-describing system prompt; they're **incompatible with message prefilling**; and a **refusal** (`stop_reason: "refusal"`) or a **truncation** (`stop_reason: "max_tokens"`) still won't parse. Always check `stop_reason` first.

### Common mistakes

- **Rewording instead of diagnosing.** The single most common failure in this domain.
- **Stacking all four techniques by reflex.** A "summarize this paragraph" prompt doesn't need an output schema and worked examples.
- **Compacting when pruning would do.** Compaction costs an LLM call; re-fetchable tool output should just be cleared.
- **Putting must-not-drift rules only in the opening prompt.** Compaction can summarize them away.
- **Trusting a schema to guarantee success.** It guarantees shape, not delivery — check `stop_reason`.
- **Reading fluency as correctness.** Validate structure and meaning separately; meaning needs a graded eval, not an assertion.

### Real exam-style scenarios

**Scenario A.** An agent's tool selection degrades reliably around turn 8 in production, though it was fine in development. The team starts rewriting tool descriptions.

The reasoning: this is the context-overflow incident in disguise. Development fixtures averaged ~800 tokens per tool result; production inputs averaged ~3,200, so accumulated tool output crowded out the system prompt and early instructions telling the agent which tool to use. **When tool selection degrades after a consistent number of turns, check whether the window is filling before you debug the schema.** The fix is pruning or compaction plus measuring against the largest realistic production input, not better descriptions.

**Scenario B.** A field-extraction endpoint returns valid JSON on every case the team tested, then returns a stray sentence before the JSON on an unusual input, and the parser throws.

The reasoning: a prompt-level "return only JSON" instruction holds on tested cases and slips on untested ones. Structured outputs enforce the schema on every token, which rules the failure out at generation time rather than catching it afterward. The residual risk to handle in code is `stop_reason` — a refusal or truncation still won't parse.

---

## Section B — Questions

12 questions, four options each, single best answer.

### Q1

How does the material distinguish context engineering from prompt engineering?

A. They're synonyms; context engineering is the newer term
B. Prompt engineering is about what you say; context engineering is the superset — curating the full set of tokens available at each inference call, including history, tool definitions, and tool outputs
C. Prompt engineering applies to the API; context engineering applies only to Claude Code
D. Context engineering concerns the system prompt specifically, and prompt engineering the user turn

### Q2

A long-running agent's context is dominated by many turns of dialogue and intermediate reasoning that can't be regenerated cheaply, and the window is nearly full. Which technique applies, and what should happen first?

A. Pruning the dialogue, which is lossless and requires no LLM call
B. Starting a fresh session, since dialogue history can't be condensed
C. Raising `max_tokens` so the model has more room to work with
D. Compaction — summarizing older history into a condensed form via an LLM call — with a `PreCompact` hook archiving the full transcript before it's summarized away

### Q3

An agent's tool selection is reliably fine for the first several turns and degrades from roughly turn 8 onward in production, though it never did in development. What should be checked before rewriting the tool schemas?

A. Whether accumulated, never-pruned tool output has filled the window and crowded out the system prompt and early instructions
B. Whether the model version was silently upgraded mid-session
C. Whether `temperature` drifted upward across turns
D. Whether the tools were registered in a different order in production

### Q4

A team keeps a must-not-violate path restriction in the first message of every Claude Code session. It's occasionally ignored in long sessions. Where should the rule live, and why?

A. In a `PostToolUse` hook, since that's the only enforcement point available
B. Repeated in every user turn, so it's always the most recent instruction
C. In CLAUDE.md, which is re-injected every request — compaction can summarize away specific instructions given early in a session
D. Nowhere different; the rule should simply be worded more forcefully

### Q5

A support assistant answers the first few turns exactly as specified, then gradually widens its scope, adopts a different tone, and starts answering adjacent questions it wasn't asked. Which technique is missing?

A. Few-shot examples showing the desired answer shape
B. Structured outputs with a JSON schema
C. A constraint covering the edge-case inputs
D. A system prompt, or a more specific one — the behavioral contract was too vague to hold across turns

### Q6

Claude performs the requested extraction correctly, but returns it in a structure the team never specified and didn't want. Which technique addresses this most directly?

A. Few-shot examples — a description alone can't pin down an exact structure, but an example shows it
B. A longer system prompt restating the task
C. Raising the effort level so the model reasons more about formatting
D. Switching to a more capable model tier

### Q7

In the worked classification pattern, few-shot examples are wrapped in XML tags. What job do the tags do?

A. They compress the examples so they cost fewer tokens
B. They mark where each example starts and ends, so Claude doesn't read the examples as part of the live instruction
C. They are required syntax for any prompt containing more than one example
D. They enable constrained decoding against the label set

### Q8

A team's prompt does one thing: summarize a paragraph in two sentences. A reviewer suggests adding a system prompt, XML structure, few-shot examples, and an output schema, on the grounds that the worked pattern used all four. What's the correct assessment?

A. Correct — the four techniques should always be applied together for consistency
B. Correct, provided the eval score improves at all
C. Over-engineering — stacking is for a clearly-defined output contract with edge cases few-shot can cover; a simple summarization task doesn't need an output schema and worked examples
D. Incorrect for a different reason: summarization tasks can't use system prompts

### Q9

What makes structured outputs a stronger guarantee than a prompt instruction to "respond only with JSON"?

A. Constrained decoding: the model is restricted token by token to emissions that keep the output valid against the schema, so an invalid response can't be generated
B. The API retries internally until a response parses, up to a fixed attempt count
C. The schema is appended to the system prompt with elevated priority
D. Responses are validated after generation and regenerated if they fail

### Q10

An agentic loop crashes intermittently when Claude passes a malformed argument to a tool. Which mechanism targets this specifically?

A. JSON outputs via `output_config.format`, which constrains the final response
B. Message prefilling, which fixes the opening of the tool call
C. A `PostToolUse` hook that repairs arguments after the fact
D. Strict tool use — `strict: true` on the tool definition — which constrains the arguments Claude passes, validated against the input schema before your code runs

### Q11

A team enables JSON outputs with a schema and removes all their parse-failure handling. What can still break, and what should they check?

A. Nothing can break; a schema guarantees a parseable response
B. A refusal (`stop_reason: "refusal"`) or a truncation (`stop_reason: "max_tokens"`) still won't parse — check `stop_reason` before assuming the response is valid
C. Only network failures, which the SDK retries automatically
D. The schema can be silently ignored on requests that also include tools

### Q12

Which pair of costs applies when structured outputs are enabled?

A. A per-request schema-validation fee, and a hard limit of one schema per API key
B. Doubled output token cost, and incompatibility with streaming
C. First-request grammar-compile latency with compiled grammars cached for 24 hours from last use, and a slight token-cost rise from the format-describing system prompt the API injects
D. A required beta header, and loss of tool-use support on the same request

---

### Answer Key and Explanations

#### Q1 — Answer: B

- **Why B is correct:** Context engineering is explicitly the superset — curating every token available at inference, since context is a finite shared resource — while prompt engineering concerns the wording.
- **Why not A:** They're related but distinct scopes, not synonyms.
- **Why not C:** Both apply across interfaces.
- **Why not D:** Neither is defined by which message role it targets.
- **Difficulty:** Easy
- **Tag:** `prompt.context/definition`
- **Revise:** `4_model_selection_prompting_context.md` → Context Engineering

#### Q2 — Answer: D

- **Why D is correct:** Compaction is the technique for bloat that can't be cheaply re-fetched — it costs an LLM call but preserves non-recoverable context, and a `PreCompact` hook archives the full transcript before summarization.
- **Why not A:** Pruning is for re-fetchable tool output; dialogue and reasoning aren't recoverable by re-calling a tool.
- **Why not B:** Starting fresh discards exactly the context that can't be regenerated.
- **Why not C:** `max_tokens` caps the response, not the window.
- **Difficulty:** Medium
- **Tag:** `prompt.context/compaction`
- **Revise:** `4_model_selection_prompting_context.md` → Context Engineering

#### Q3 — Answer: A

- **Why A is correct:** This is the documented incident: accumulated tool outputs crowded out the system prompt and early instructions, and the symptom presented as degraded tool selection. If selection degrades after a consistent number of turns, check the window before debugging the schema.
- **Why not B:** Pinned versions don't change mid-session, and a version change wouldn't produce a consistent turn-count threshold.
- **Why not C:** Temperature doesn't drift across turns, and the newest models reject the parameter entirely.
- **Why not D:** Registration order isn't what drives tool selection; descriptions and available context are.
- **Difficulty:** Hard
- **Tag:** `prompt.context/overflow-misdiagnosis`
- **Revise:** `4_model_selection_prompting_context.md` → Context Engineering gotcha

#### Q4 — Answer: C

- **Why C is correct:** CLAUDE.md is re-injected on every request, which is why persistent rules belong there rather than in an opening prompt that compaction can summarize away.
- **Why not A:** `PostToolUse` runs after the call and can't block it; enforcement would be `PreToolUse`, and the question is about where the rule lives.
- **Why not B:** Repeating a rule every turn is token-expensive and still fragile.
- **Why not D:** Wording strength doesn't survive summarization.
- **Difficulty:** Medium
- **Tag:** `prompt.context/persistent-rules`
- **Revise:** `4_model_selection_prompting_context.md` → Context Engineering

#### Q5 — Answer: D

- **Why D is correct:** Scope drift, tone shift, and decay deeper into the conversation is the system-prompt signature — the behavioral contract was too vague to hold across turns.
- **Why not A:** Few-shot fixes an invented structure, not drifting content.
- **Why not B:** A schema constrains shape, not scope or tone.
- **Why not C:** An edge-case constraint addresses a specific input variant, not gradual drift.
- **Difficulty:** Easy
- **Tag:** `prompt.prompting/diagnostic-table`
- **Revise:** `4_model_selection_prompting_context.md` → Prompt Engineering

#### Q6 — Answer: A

- **Why A is correct:** Right task, invented structure is the few-shot signature: a description can't pin an exact structure, an example can.
- **Why not B:** More words describing the same thing is rewording, not a missing technique.
- **Why not C:** Reasoning depth doesn't determine output structure.
- **Why not D:** Model capability isn't the gap when the task itself is being done correctly.
- **Difficulty:** Medium
- **Tag:** `prompt.prompting/diagnostic-table`
- **Revise:** `4_model_selection_prompting_context.md` → Prompt Engineering

#### Q7 — Answer: B

- **Why B is correct:** The tags delimit each example so Claude reads them as demonstrations rather than as part of the live instruction.
- **Why not A:** Tags add tokens; they don't compress anything.
- **Why not C:** There's no syntactic requirement — it's a clarity technique.
- **Why not D:** Constrained decoding comes from structured outputs, not from XML tags in the prompt.
- **Difficulty:** Medium
- **Tag:** `prompt.prompting/xml-structure`
- **Revise:** `4_model_selection_prompting_context.md` → Prompt Engineering

#### Q8 — Answer: C

- **Why C is correct:** Stack all four against a clearly-defined output contract with edge cases few-shot can cover. A two-sentence summary needs none of that machinery, and adding it costs tokens on every call for no gain.
- **Why not A:** The material explicitly warns against adding all four to a task needing one.
- **Why not B:** "Any improvement" ignores the cost side of a quality/cost tradeoff.
- **Why not D:** Summarization tasks can absolutely use system prompts.
- **Difficulty:** Hard
- **Tag:** `prompt.prompting/when-to-stack`
- **Revise:** `4_model_selection_prompting_context.md` → When to stack vs. simplify

#### Q9 — Answer: A

- **Why A is correct:** Structured outputs work by constrained decoding — the API restricts generation token by token to what keeps the output schema-valid, so an invalid response can't be produced.
- **Why not B:** There's no internal retry loop making the guarantee.
- **Why not C:** A schema in the prompt would be exactly the prompt-level request this replaces.
- **Why not D:** Post-generation validation is what you'd write yourself; the API prevents the invalid output instead.
- **Difficulty:** Easy
- **Tag:** `prompt.output/constrained-decoding`
- **Revise:** `4_model_selection_prompting_context.md` → Output Handling

#### Q10 — Answer: D

- **Why D is correct:** Strict tool use constrains the arguments Claude passes to your tools, validated against the tool's input schema before your code runs — exactly the agentic-loop failure described.
- **Why not A:** JSON outputs constrain the final response, not tool arguments.
- **Why not B:** Prefilling doesn't validate arguments, and it's incompatible with JSON outputs anyway.
- **Why not C:** A hook could reject a bad call, but the mechanism designed for this is a schema constraint at generation time.
- **Difficulty:** Medium
- **Tag:** `prompt.output/strict-tool-use`
- **Revise:** `4_model_selection_prompting_context.md` → Output Handling

#### Q11 — Answer: B

- **Why B is correct:** A guaranteed schema is not a guaranteed success. A refusal and a truncation both return responses that won't parse, so `stop_reason` has to be checked before assuming validity.
- **Why not A:** That's the assumption the material explicitly warns against.
- **Why not C:** Transport failures are a separate concern from these two content-level cases.
- **Why not D:** Schemas aren't silently dropped when tools are present.
- **Difficulty:** Hard
- **Tag:** `prompt.output/stop-reason`
- **Revise:** `4_model_selection_prompting_context.md` → Output Handling

#### Q12 — Answer: C

- **Why C is correct:** The API compiles your schema into a grammar before it can constrain output — a first-request latency cost, with compiled grammars cached 24 hours from last use — and injects a format-describing system prompt that's billed like any other input.
- **Why not A:** There's no per-request validation fee or per-key schema limit.
- **Why not B:** Output tokens aren't doubled; the documented incompatibility is with prefilling, not streaming.
- **Why not D:** No beta header is required and tool use isn't lost.
- **Difficulty:** Medium
- **Tag:** `prompt.output/structured-output-costs`
- **Revise:** `4_model_selection_prompting_context.md` → Costs to weigh before enabling structured outputs

---

## Section C — Score and Analysis

### Score

| | |
|---|---|
| Correct | ___ / 12 |
| Percentage | ___ % |
| Difficulty level run | L2 Applied |

| Band | Reading |
|---|---|
| 10–12 (83%+) | Strong. Move up a level next session. |
| 8–9 (67–75%) | Hold level; clear the tags below. |
| 6–7 (50–58%) | Re-read the four-technique diagnostic table and the Output Handling section, then repeat at L1. |
| Below 6 | Repeat at L1. Learn the diagnostic table first — half this domain is that table applied to a scenario. |

### Weak-area map

| Missed | Tag | Revise |
|---|---|---|
| Q1–Q4 | `prompt.context` | `4_model_selection_prompting_context.md` → Context Engineering |
| Q5–Q8 | `prompt.prompting` | `4_model_selection_prompting_context.md` → Prompt Engineering |
| Q9–Q12 | `prompt.output` | `4_model_selection_prompting_context.md` → Output Handling |

### Recommended next steps

1. Reproduce the symptom → missing-technique table from memory. If you can do that cold, most Prompt Engineering questions answer themselves.
2. If you missed Q11 or Q12, note that "structured outputs still need error handling" is a favorite trap: the schema constrains shape, not delivery.
3. Update the tracker with your score, level, and next level.
4. You've now covered 75.6% of the exam. **Take Mock Exam 1** before session 5 — expect gaps in the four domains you haven't studied, and use it as a baseline rather than a verdict.

**Next domain or repeat this one?**

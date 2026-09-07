# Session 2 — Model Selection and Optimization (16.8%)

The second-largest domain. Domain 5 of the CCDV-F blueprint, and the one where a wrong assumption carried over from an older model generation costs you marks.

Source: [`4_model_selection_prompting_context.md`](../../4_model_selection_prompting_context.md). Level: **L2 Applied**. Time: 10–15 minutes.

---

## Section A — Domain Overview

### What this domain actually tests

| Skill | Weight | The question behind the questions |
|---|---|---|
| LLM Fundamentals | 5.2% | Tokens, context windows, sampling, non-determinism, thinking modes, shot count |
| Technical Fundamentals | 6.1% | SDKs over REST, and the four request patterns: sync, streaming, async, batch |
| Model Selection and Tradeoffs | 2.7% | Tier positioning, reasoning-mode support, and deciding by eval rather than instinct |
| Cost and Token Management | 2.8% | Prompt caching mechanics and economics, usage tracking, cost modeling |

Technical Fundamentals is the heaviest skill here at 6.1% — heavier than the model-tier comparison everyone studies first. Know the four request patterns cold.

### Key patterns

**Tokens are the unit of everything**, and the characters-per-token ratio is a property of the model's tokenizer, which changes across generations. Never hardcode a constant. Everything draws on the same context budget: system prompt, full conversation history, tool definitions, tool results, injected documents, and the model's own output.

**Two distinct context-overflow failures** — the exam separates them deliberately:

| Situation | Result |
|---|---|
| Input is already larger than the window | Request rejected with a validation error *before* generation starts |
| Input fits, generation hits the ceiling mid-response | Model stops and returns partial output with stop reason `model_context_window_exceeded` |

**Sampling and non-determinism.** The model samples from a probability distribution at each step, so the same prompt can return different-but-equally-correct wording. On the newest models (Fable 5, Opus 5, Sonnet 5) `temperature`, `top_p`, and `top_k` are **not accepted and return a 400** — steering happens through prompting. Even where temperature is accepted, `temperature: 0` is more repeatable, not identical. This is why tests assert on properties (a field is present, a value is in range, the output parses) instead of exact strings.

**Shot count is a cost/quality dial.** Zero-shot when the task and output shape are obvious; one or multi-shot when structure, casing, or an edge case keeps getting missed. Examples aren't training data — they sit in the prompt and cost tokens on every single call. A more capable model often succeeds zero-shot where a smaller one needs examples, which means examples can be what lets a cheaper tier do the job.

**Four request patterns, four different problems:**

| Pattern | Use when | Watch for |
|---|---|---|
| Synchronous | Short response, backend job, nobody watching | Blocks until complete |
| Streaming | Long response or a user is watching; server-sent events over the same connection | Your code reassembles pieces; tool calls need full accumulation |
| Async client | You want concurrency across many in-flight requests | Buys concurrency, **not** lower latency or lower cost. Python has `AsyncAnthropic`; the TypeScript client is Promise-based already, with no separate async class |
| Message Batches | Bulk, offline, latency-tolerant | Up to 24 hours, lower per-token cost, poll for completion |

**The model lineup**, with the one detail people get backwards:

| Tier | Context | Reasoning mode | Positioning |
|---|---|---|---|
| Fable 5 | 1M | Adaptive, always on | Most capable; long-running agents; slower |
| Opus 5 | 1M | Adaptive | Complex agentic coding, enterprise |
| Sonnet 5 | 1M | Adaptive | Best speed/intelligence balance — the default |
| Haiku 4.5 | 200K | **Extended** thinking, not adaptive | Fastest and cheapest, near-frontier |

Reasoning depth on adaptive models is tuned with `effort` (`low`, `medium`, `high`, `xhigh`, `max`). The older `budget_tokens` control is deprecated and returns a **400** on the newest generations. Defaults for `effort` have changed across releases and differ by surface — confirm per model rather than assuming.

**Prompt caching economics.** Writes cost a premium over base input (roughly 1.25x at the 5-minute TTL, 2x at 1-hour); reads cost roughly 0.1x. Caching only pays when reads outnumber writes. Up to 4 explicit breakpoints per request, a 20-block lookback window, and a minimum token threshold (about 1,024 tokens on current models) below which nothing caches at all. A single changed character before the breakpoint invalidates the prefix and forces a fresh, paid write.

### Common mistakes

- **Defaulting to the most capable model.** Called out as the most common and most expensive model-selection mistake in production. Start at Sonnet; move up when an eval shows the quality bar isn't met, down when an eval shows the drop is acceptable. Include the cost of a wrong answer in the calculation — a cheaper tier that creates downstream errors isn't a saving.
- **Assuming the flagship supports extended thinking.** It's the reverse: the top three use adaptive thinking, and Haiku 4.5 is the one with extended thinking.
- **Carrying sampling parameters across a migration.** `temperature` on a newest-generation model is a 400, not a no-op.
- **Hardcoding chars-per-token.** Tokenizers change between generations; Fable 5's produces roughly 30% more tokens for the same text than pre-4.7 models.
- **Turning caching on and expecting a saving.** A prefix written once and never re-read is a pure loss, because you paid the write premium and never collected the read discount.
- **Confusing concurrency with batching.** Fanning out async requests doesn't reduce per-token cost; only the Batch API does that.

### Real exam-style scenarios

**Scenario A.** An agent pauses between steps, calling the same 30K-token system prompt and tool schema roughly every 20 minutes. The team enabled caching and saw no saving.

The reasoning: the default TTL is 5 minutes from last read. A 20-minute gap means the cache has expired before every call, so each request pays the write premium and never collects a read discount. The 1-hour TTL exists for exactly this bursty-but-infrequent shape — it costs more per write and turns a net loss into a net saving.

**Scenario B.** A nightly job scores 3,000 eval cases. The team proposes fanning them out with the async client to finish faster.

The reasoning: async fan-out is a real option and will finish sooner, but it pays full per-token price and pushes against rate limits. Nothing is waiting on the result before morning, which is the definition of a latency-tolerant workload — the Message Batches API completes within 24 hours at a lower per-token rate. Concurrency and batching solve different problems, and this workload's constraint is cost, not turnaround.

---

## Section B — Questions

14 questions, four options each, single best answer.

### Q1

A team estimates whether a request will fit the context window by counting the user's message plus the expected reply. Their long-running sessions keep overflowing anyway. What are they failing to count?

- **A.** Only the conversation history, which is the sole additional consumer
- **B.** Nothing — the window applies to input only, so their method is sound
- **C.** The response, which is billed but does not occupy the window
- **D.** The system prompt, the full conversation history, every tool definition, every tool result, and injected documents — all of it draws from the same shared budget

### Q2

A request is accepted and the model begins generating, then stops partway through with a partial response. What stop reason indicates the generation hit the context ceiling, and how does this differ from an oversized input?

- **A.** `max_tokens` — identical to the oversized-input case, which also returns a partial response
- **B.** `refusal` — the model declined to continue once the window filled
- **C.** `model_context_window_exceeded` — the request was valid on submission, so you get partial output rather than the up-front validation error an oversized input triggers
- **D.** There is no distinct stop reason; the connection is closed without one

### Q3

A team migrates a classification service to Sonnet 5 and keeps `temperature: 0.2` in the request, which worked on their previous model. What happens, and what's the correct approach?

- **A.** A 400 error — the newest models don't accept non-default sampling parameters, and output is steered through prompting instead
- **B.** The parameter is silently ignored and output is unchanged
- **C.** It works normally; temperature support is unchanged across all Claude generations
- **D.** The request succeeds but output becomes fully deterministic, since 0.2 rounds to 0

### Q4

Which statement about few-shot examples is correct?

- **A.** They fine-tune the model on your data for the duration of the session
- **B.** They live in the prompt and cost tokens on every call, which makes shot count a quality/cost tradeoff rather than a free improvement
- **C.** They are cached automatically and therefore cost nothing after the first request
- **D.** They are only supported on models with adaptive thinking

### Q5

A team runs a document-tagging task on a top-tier model with a zero-shot prompt because a smaller model produced inconsistent output shapes. Cost is now a problem. What does the material suggest trying?

- **A.** Nothing — output shape is a capability property, so the top tier is required
- **B.** Raising `temperature` on the smaller model to widen its output distribution
- **C.** Removing the output-format instruction so the smaller model has less to follow
- **D.** Adding a few examples to the smaller model's prompt: examples can pin the structure a description keeps missing, which is often what lets a cheaper tier clear the bar

### Q6

What is the relationship between an official Anthropic SDK and the REST API?

- **A.** The SDK is a thin convenience layer over the same REST API, handling auth, request construction, retries, and parsing — same endpoint, same model
- **B.** The SDK connects over a persistent websocket while REST is request/response
- **C.** The SDK routes to a different, SDK-optimized model deployment
- **D.** The SDK is required for tool use; raw REST supports text completion only

### Q7

A user-facing assistant returns long answers and users complain about staring at a blank screen. Which request pattern addresses this, and how does it work?

- **A.** The Message Batches API, which returns results as they complete
- **B.** The async client, which reduces time-to-first-token
- **C.** Streaming, which delivers the response in pieces over the same HTTP connection via server-sent events, with your code reassembling them
- **D.** Synchronous calls with a lower `max_tokens`, since shorter answers arrive sooner

### Q8

A TypeScript team asks which import gives them the async client, having seen `AsyncAnthropic` in a Python example. What's the answer?

- **A.** `AsyncAnthropic` is exported from the TypeScript SDK under the same name
- **B.** There is no separate async client class — the standard TypeScript client is already Promise-based, so you just `await` calls
- **C.** TypeScript requires the REST API directly for concurrent calls
- **D.** Async support in TypeScript requires enabling a beta header

### Q9

A nightly job grades 3,000 eval cases. Results are needed by morning and cost is the main concern. A developer proposes fanning the calls out concurrently with the async client. What's the correct assessment?

- **A.** Async fan-out is correct — concurrency is the standard way to reduce bulk-processing cost
- **B.** Neither works; eval runs must be executed synchronously to preserve case ordering
- **C.** Async fan-out is correct because batch submissions can't return structured results
- **D.** Async fan-out finishes sooner but pays full per-token price; the workload is latency-tolerant with nobody waiting, which is exactly the Message Batches API's design point — up to 24 hours at a lower per-token rate

### Q10

A team's standing policy is to use the most capable available model everywhere "so quality is never the problem." How does the material characterize this?

- **A.** Correct practice — capability headroom is the cheapest insurance against quality complaints
- **B.** Acceptable only for customer-facing features, and wasteful for internal ones
- **C.** The most common and most expensive model-selection mistake in production: start at Sonnet, move up only when an eval shows the quality bar isn't met, and move down when an eval shows the drop is acceptable
- **D.** Irrelevant, since per-token pricing is broadly aligned across tiers

### Q11

Reasoning depth on adaptive-thinking models is tuned with `effort`. Which description matches the documented levels?

- **A.** Five levels — `low` for lookups and listing, `medium` for routine edits, `high` for thorough analysis such as refactors and debugging, `xhigh` for extended depth on complex coding, `max` for multi-step problems needing the deepest analysis
- **B.** Three levels — `off`, `on`, and `max` — with `on` as the universal default
- **C.** A numeric scale from 1 to 5, each level mapping to a fixed reasoning token budget
- **D.** A single boolean flag, since depth is decided entirely by the model on adaptive-thinking tiers

### Q12

A team sets a `cache_control` breakpoint on a 400-token system prompt and sees no cache hits at all. Why?

- **A.** Breakpoints only work on tool definitions, never on system prompts
- **B.** Caching applies only above a minimum token threshold — around 1,024 tokens on current models — so a short prompt won't cache even with a breakpoint set
- **C.** The system prompt must be the last block in the request to be cacheable
- **D.** Cache hits only register after the tenth identical request

### Q13

After enabling prompt caching, a team's bill goes up. Their traffic is a large volume of one-off requests, each with a different long document placed before the breakpoint. What happened?

- **A.** Cache reads are billed at a premium over standard input tokens
- **B.** Caching increases token counts because the API adds a describing system prompt
- **C.** Enabling caching disabled their existing batch discount
- **D.** Every request wrote a fresh cache entry that was never read again — writes cost more than base input, and the economics only work when reads outnumber writes

### Q14

A cost model sums the `usage` block's input tokens into a single "input" line. What does this get wrong once caching is in play?

- **A.** Nothing — cached and uncached input tokens are billed identically
- **B.** Output tokens would be double-counted in the same total
- **C.** Cache writes, cache reads, and regular input tokens are priced differently, so a single input total misstates cost — they have to be tracked separately
- **D.** Usage data isn't available per request, so cost can only be reconciled from the monthly invoice

---

### Answer Key and Explanations

#### Q1 — Answer: D

- **Why D is correct:** The context window is a single shared budget. System prompt, full history, tool definitions, tool results, injected documents, and the model's own output all draw from it.
- **Why not A:** History is one consumer among several; tool definitions and tool results are frequently the largest.
- **Why not B:** Generated output occupies the window too, which is why a request can fit on submission and still hit the ceiling mid-response.
- **Why not C:** The response both costs money and consumes window.
- **Difficulty:** Easy
- **Tag:** `mso.llm-fundamentals/context-window`
- **Revise:** `4_model_selection_prompting_context.md` → LLM Fundamentals

#### Q2 — Answer: C

- **Why C is correct:** Two distinct failure modes. Oversized input is rejected with a validation error before generation; a valid request whose generation hits the ceiling stops and returns partial output with `model_context_window_exceeded`.
- **Why not A:** `max_tokens` is the output-limit stop reason, and the oversized-input case never produces a partial response at all.
- **Why not B:** A refusal is a content decision, unrelated to window size.
- **Why not D:** There is a specific stop reason, and recognizing it is the point of the distinction.
- **Difficulty:** Medium
- **Tag:** `mso.llm-fundamentals/context-overflow`
- **Revise:** `4_model_selection_prompting_context.md` → LLM Fundamentals

#### Q3 — Answer: A

- **Why A is correct:** The newest Claude models don't accept non-default sampling parameters — `temperature`, `top_p`, or `top_k` returns a 400. Output is steered by prompting instead.
- **Why not B:** It's a hard error, not a silent no-op, which is what makes it a migration hazard.
- **Why not C:** Parameter support has explicitly changed across generations; always confirm in the API reference.
- **Why not D:** No rounding behavior exists, and even where temperature is accepted, 0 doesn't guarantee identical output.
- **Difficulty:** Medium
- **Tag:** `mso.llm-fundamentals/sampling`
- **Revise:** `4_model_selection_prompting_context.md` → Sampling and non-determinism

#### Q4 — Answer: B

- **Why B is correct:** Examples are prompt content, not training data. They're re-sent and re-billed on every call, which makes shot count a deliberate quality/cost tradeoff.
- **Why not A:** Nothing about in-context examples updates model weights.
- **Why not C:** Examples can be cached like any other prefix, but that isn't automatic and doesn't make them free.
- **Why not D:** Shot count is independent of reasoning mode.
- **Difficulty:** Easy
- **Tag:** `mso.llm-fundamentals/shot-count`
- **Revise:** `4_model_selection_prompting_context.md` → Prompting modes

#### Q5 — Answer: D

- **Why D is correct:** A description alone often can't pin an output structure, which is exactly what an example does. A more capable model may succeed zero-shot where a smaller one needs examples — so adding examples is frequently what lets the cheaper tier meet the bar.
- **Why not A:** The failure described is output-shape consistency, which few-shot targets directly.
- **Why not B:** Higher temperature increases variability, the opposite of what's needed — and the newest models reject the parameter outright.
- **Why not C:** Removing constraints makes shape drift worse.
- **Difficulty:** Hard
- **Tag:** `mso.llm-fundamentals/shot-count`
- **Revise:** `4_model_selection_prompting_context.md` → Prompting modes

#### Q6 — Answer: A

- **Why A is correct:** Claude is reached over an HTTP REST API. The SDKs are convenience layers over that same API handling auth, request construction, retries, and parsing — same endpoint, same model.
- **Why not B:** The SDK speaks the same HTTP protocol; streaming uses server-sent events, not websockets.
- **Why not C:** There is no separate SDK-only deployment.
- **Why not D:** Tool use is an API feature available to any HTTP client.
- **Difficulty:** Easy
- **Tag:** `mso.technical/sdk-vs-rest`
- **Revise:** `4_model_selection_prompting_context.md` → Technical Fundamentals

#### Q7 — Answer: C

- **Why C is correct:** Streaming exists for exactly this: output appears as it's generated, delivered as server-sent events over the same HTTP connection, with the client reassembling the pieces.
- **Why not A:** Batch is for offline work with nobody waiting — the opposite situation.
- **Why not B:** Async buys concurrency across requests; it does nothing for time-to-first-token on one request.
- **Why not D:** Truncating answers degrades the product rather than fixing the wait.
- **Difficulty:** Medium
- **Tag:** `mso.technical/streaming`
- **Revise:** `4_model_selection_prompting_context.md` → Technical Fundamentals

#### Q8 — Answer: B

- **Why B is correct:** The Python SDK exposes `AsyncAnthropic` for non-blocking calls; the TypeScript SDK's standard client is already Promise-based, so there's no separate async class to import.
- **Why not A:** That class is Python-specific.
- **Why not C:** The standard TypeScript client handles concurrency fine.
- **Why not D:** No beta header is involved.
- **Difficulty:** Medium
- **Tag:** `mso.technical/async`
- **Revise:** `4_model_selection_prompting_context.md` → Technical Fundamentals

#### Q9 — Answer: D

- **Why D is correct:** Bulk, offline, latency-tolerant, cost-sensitive with nobody waiting is the Message Batches API's design point — a different submission model, up to 24 hours, at a lower per-token rate.
- **Why not A:** Concurrency changes turnaround, not per-token price.
- **Why not B:** There's no ordering requirement that rules out batch; batch results come back in arbitrary order and are matched by `custom_id`.
- **Why not C:** Batch returns the same structured responses the synchronous endpoint does.
- **Difficulty:** Hard
- **Tag:** `mso.technical/batch-vs-async`
- **Revise:** `4_model_selection_prompting_context.md` → Technical Fundamentals

#### Q10 — Answer: C

- **Why C is correct:** Reaching for the most capable model by default, with no eval forcing the question, is named as the most common and most expensive model-selection mistake. The workflow is Sonnet first, then move in whichever direction an eval justifies.
- **Why not A:** It buys capability you may not need at a price you definitely pay.
- **Why not B:** The decision is empirical per workload, not a customer-facing/internal split.
- **Why not D:** Per-token rates differ meaningfully across tiers; it's platform pricing that's broadly aligned.
- **Difficulty:** Medium
- **Tag:** `mso.model-choice/default-workflow`
- **Revise:** `4_model_selection_prompting_context.md` → Model Selection and Tradeoffs

#### Q11 — Answer: A

- **Why A is correct:** Those are the five documented levels and their intended uses, from `low` for lookups through `max` for the deepest multi-step analysis. Reasoning earns its cost on hard problems and is wasted on lookups and classification.
- **Why not B:** There's no on/off effort switch; adaptive thinking is always the mode on those tiers, with `effort` tuning depth.
- **Why not C:** Numeric reasoning budgets are the deprecated `budget_tokens` model, which returns a 400 on the newest generations.
- **Why not D:** The model does decide when and how much to think, but `effort` is the setting that tunes it — and its default varies by model and surface.
- **Difficulty:** Medium
- **Tag:** `mso.model-choice/effort-levels`
- **Revise:** `4_model_selection_prompting_context.md` → Model Selection and Tradeoffs

#### Q12 — Answer: B

- **Why B is correct:** Caching is subject to a minimum token threshold per block — about 1,024 tokens on most current models — so short prefixes never cache, breakpoint or not.
- **Why not A:** Breakpoints work on system prompts, tool definitions, and message content alike.
- **Why not C:** Position rules concern what falls inside the cached prefix, not a requirement to be last.
- **Why not D:** There's no request-count threshold before hits register.
- **Difficulty:** Medium
- **Tag:** `mso.cost/caching-mechanics`
- **Revise:** `4_model_selection_prompting_context.md` → Cost and Token Management

#### Q13 — Answer: D

- **Why D is correct:** Cache writes cost more than base input (roughly 1.25x at 5-minute TTL, 2x at 1-hour) while reads cost roughly 0.1x. With a unique document before the breakpoint on every request, every request is a write and none is a read — a pure loss.
- **Why not A:** Reads are the cheap side of the deal; writes are the premium.
- **Why not B:** That describes structured outputs' injected format prompt, not caching.
- **Why not C:** Caching and batch pricing are independent.
- **Difficulty:** Hard
- **Tag:** `mso.cost/caching-economics`
- **Revise:** `4_model_selection_prompting_context.md` → Cost and Token Management

#### Q14 — Answer: C

- **Why C is correct:** Cache writes, cache reads, and regular input tokens carry different prices. Collapsing them into one input total will misstate cost in either direction.
- **Why not A:** They are explicitly priced differently — that's the entire basis of caching economics.
- **Why not B:** Output tokens are reported separately and aren't the issue.
- **Why not D:** Usage and cost fields come back per request, including `total_cost_usd` in the Agent SDK's `ResultMessage`.
- **Difficulty:** Medium
- **Tag:** `mso.cost/usage-tracking`
- **Revise:** `4_model_selection_prompting_context.md` → Cost and Token Management

---

## Section C — Score and Analysis

### Score

| | |
|---|---|
| Correct | ___ / 14 |
| Percentage | ___ % |
| Difficulty level run | L2 Applied |

| Band | Reading |
|---|---|
| 12–14 (86%+) | Strong. Move up a level next session. |
| 9–11 (64–79%) | Hold level; clear the tags below before the first mock. |
| 7–8 (50–57%) | Re-read the model lineup and caching sections, then repeat at L1. |
| Below 7 | Repeat at L1. Most misses here are stale assumptions from older model generations — read the two "gotchas worth knowing cold" paragraphs first. |

### Weak-area map

| Missed | Tag | Revise |
|---|---|---|
| Q1–Q5 | `mso.llm-fundamentals` | `4_model_selection_prompting_context.md` → LLM Fundamentals |
| Q6–Q9 | `mso.technical` | `4_model_selection_prompting_context.md` → Technical Fundamentals |
| Q10, Q11 | `mso.model-choice` | `4_model_selection_prompting_context.md` → Model Selection and Tradeoffs |
| Q12–Q14 | `mso.cost` | `4_model_selection_prompting_context.md` → Cost and Token Management |

### Recommended next steps

1. If you missed Q3 or Q11, memorize the reasoning-mode table: adaptive on Fable 5 / Opus 5 / Sonnet 5, extended on Haiku 4.5, `effort` replacing the deprecated `budget_tokens`. Every one of those is a single-detail distractor waiting to happen.
2. If you missed Q12 or Q13, work through the cheat sheet's Prompt Caching block until the four numbers (4 breakpoints, 20-block lookback, minimum threshold, two TTLs) are automatic.
3. Update the tracker with your score, level, and next level.

**Next domain or repeat this one?**

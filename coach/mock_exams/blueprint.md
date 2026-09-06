# Mock Exam Blueprint

How the four mock exams are built, why each question sits where it does, and how to score them. Read this once; then take the exams cold.

---

## Exam shape

Each mock exam mirrors the real CCDV-F sitting:

| Property | Real exam (Guide v1.0, July 2026) | Mock exam |
|---|---|---|
| Items | 53 | 50 |
| Time | 120 minutes | 115 minutes (same ~2.26 min/item pace) |
| Pass mark | 720 on a 720/1000-scaled score | 72% raw as the working proxy, 80% as the confidence target |
| Format | Single-best-answer multiple choice | Single-best-answer multiple choice |

The scaled score on the real exam is not a raw percentage, and Anthropic does not publish the scaling curve. Treat 72% as "borderline" and 80%+ as "comfortable" rather than assuming a raw 72% converts to a scaled 720.

---

## Domain distribution

Question counts follow the official weighting. Rounding is rotated across the four exams so the four-exam total lands close to the published percentages.

| Domain | Official weight | E1 | E2 | E3 | E4 | Total | Effective |
|---|---|---|---|---|---|---|---|
| Applications and Integration | 33.1% | 17 | 16 | 17 | 16 | 66 | 33.0% |
| Model Selection and Optimization | 16.8% | 8 | 9 | 8 | 8 | 33 | 16.5% |
| Agents and Workflows | 14.7% | 7 | 7 | 8 | 7 | 29 | 14.5% |
| Prompt and Context Engineering | 11.0% | 6 | 6 | 5 | 6 | 23 | 11.5% |
| Tools and MCP | 10.6% | 5 | 5 | 5 | 6 | 21 | 10.5% |
| Security and Safety | 8.1% | 4 | 4 | 4 | 4 | 16 | 8.0% |
| Claude Code | 3.1% | 2 | 2 | 2 | 2 | 8 | 4.0% |
| Eval, Testing, and Debugging | 2.6% | 1 | 1 | 1 | 1 | 4 | 2.0% |
| **Total** | 100% | **50** | **50** | **50** | **50** | **200** | 100% |

Claude Code is slightly over-weighted and Eval slightly under-weighted because a 50-item exam can't render 3.1% and 2.6% exactly without dropping a domain to zero on some exams. Both domains are covered in full by their dedicated coaching sessions, where the question count is set by teaching need rather than exam weight.

## Difficulty mix

Each exam targets roughly:

| Difficulty | Share | What it looks like |
|---|---|---|
| Easy | ~30% | Direct recall of a named mechanism, table row, or definition |
| Medium | ~45% | A short scenario where you apply one rule, or distinguish two adjacent mechanisms |
| Hard | ~25% | Multi-step scenarios: a constraint that overrides the obvious answer, a misdiagnosis to see through, JSON/schema or tool-call structure to reason about, or two plausible answers separated by one detail |

## No-repetition rule

- No question stem, scenario, or answer set repeats across the four mock exams.
- No mock question reuses a stem from the repo's existing `study_practice_questions.md` (58 questions).
- A given underlying fact may appear at most twice across all four exams, and the second appearance must test a different decision (for example: one question asks which mechanism to choose, the other asks why the obvious choice fails under a stated constraint).

The topic allocation below is what enforces this. Each exam draws its questions from its own anchor list.

---

## Topic allocation

Anchors are the specific facts each exam owns. Every anchor traces to a section of the repo notes.

### Applications and Integration

**Exam 1** — functional vs. infrastructure requirements; the design→build gate; Messages API statelessness and who owns conversation state; base64 image re-send vs. Files API reuse; accumulating `input_json` before acting on a streamed `tool_use`; batch vs. synchronous for an overnight job; `custom_id` and arbitrary result ordering; choosing between the first-party API and Bedrock; alias vs. pinned model ID; async concurrency vs. latency; evals in CI; instruction persistence in Claude Code vs. the raw API; tool-schema change as a breaking change; settings.json precedence; plugin command namespacing; session hygiene; the requirements record as a defensible artifact.

**Exam 2** — deriving the four infrastructure dimensions (latency, scale, residency, identity) from a business problem; why the operate phase is never finished; PDFs as `document` blocks; Files API beta unavailability on Bedrock/Vertex; the visual-token patch formula; extended vs. adaptive thinking at the API-mechanics level; Microsoft Foundry's two hosting forms; Vertex AI's model-in-URL and `anthropic_version` body field; batch size limits (100,000 requests / 256MB); packaging an engagement build for reuse; prompt versioning as production configuration; plugin dependency resolution at install; content boundaries as a design-time decision; code review scope for prompt and schema diffs; the residency-discovered-late rebuild incident; CLAUDE.md as a versioned artifact.

**Exam 3** — mapping a functional requirement onto an infrastructure choice; lifecycle phase placement of eval-suite construction; `tool_result` pairing inside a multi-turn Messages exchange; image `url` source tradeoffs; a stream that breaks mid-response as a transient failure; realtime vs. batch when a user is waiting; Claude Platform on AWS vs. Claude in Amazon Bedrock; legacy Bedrock `InvokeModel`/`Converse` and ARN pinning; partner retirement dates differing from Anthropic's; dateless-but-pinned 4.6+ model IDs; retaining the prior pin for rollback; REST/JSON fundamentals behind the SDK; large-scale refactoring from workflow to agent architecture; schema design as an application API contract; the five settings scopes and the permissions-accumulate exception; Claude Desktop/claude.ai instruction persistence; measuring latency from the customer's region.

**Exam 4** — a business goal that is not yet a requirement; gates under deadline pressure; the four-part content-block response shape; thinking blocks omitted by default; prompt caching at the API-mechanics level (breakpoints, TTL); chunking a loop is not batching; residency confirmed per model rather than per platform; version promotion gated on an eval against a pinned baseline; the moving-alias production incident; the iterate phase feeding production findings back into requirements; small-scale refactoring of a tool surface; plugin vs. project-local configuration; marketplace `.claude-plugin/marketplace.json` distribution; model-version pinning as configuration management; treating all four config artifacts with code-level rigor; an unbounded session's cost and drift.

### Model Selection and Optimization

**Exam 1** — tokens as the unit of pricing and budget; input larger than the window rejected before generation; non-determinism and property-based assertions; zero-shot vs. few-shot cost tradeoff; synchronous vs. streaming; starting at Sonnet and moving on eval evidence; `effort: low` for lookups; 5-minute vs. 1-hour cache TTL economics.

**Exam 2** — everything that draws on the shared context budget (tool definitions, tool results, output); `model_context_window_exceeded` as a mid-generation partial response; sampling parameters returning 400 on the newest models; adding examples so a cheaper tier clears the bar; `AsyncAnthropic` buying concurrency, not lower latency; Haiku 4.5 supporting extended rather than adaptive thinking; `budget_tokens` deprecated in favour of `effort`; cache write premium vs. read discount and why reads must outnumber writes; tracking cache-read/write/regular input tokens separately in a cost model.

**Exam 3** — tokenizer changes across model generations breaking a hardcoded chars-per-token estimate; `temperature: 0` not guaranteeing identical output; the TypeScript SDK having no separate async client; Message Batches' 24-hour window and lower per-token rate; Fable 5's always-on adaptive thinking and 1M window; a cheap classifier routing heterogeneous traffic; `xhigh`/`max` effort on genuinely hard problems; automatic vs. explicit cache breakpoints.

**Exam 4** — the SDK as a thin convenience layer over the same REST API; multi-shot when a description keeps missing the output structure; Opus 5's positioning against Sonnet 5 as default; `effort` defaults differing by model and surface; reading the migration guide before bumping a pin; the 4-breakpoint limit, 20-block lookback, and ~1,024-token minimum; a cached prefix serving stale content; reasoning depth wasted on classification and lookups.

### Agents and Workflows

**Exam 1** — the workflow-vs-agent decision criteria; prompt chaining vs. routing; what counts as one turn in the agent loop; `max_turns` vs. `max_budget_usd` and their `ResultMessage` subtypes; a human gate before a destructive tool call; in-context memory failing on a changed session shape; LangGraph's defining characteristic.

**Exam 2** — "not sure" defaulting to an agent with workflow patterns extracted later; evaluator-optimizer; the supervisor/leader-worker structure; self-hosted sandboxes as the middle ground; a `PreToolUse` denial short-circuiting the loop; external-storage memory; PydanticAI's positioning.

**Exam 3** — parallelization by sectioning vs. voting; orchestrator-workers as dynamic decomposition; the ~15x token multiplier and the tightly-coupled counterexample; context isolation as a subagent benefit; `SystemMessage`/`AssistantMessage`/`ResultMessage` sequence; Managed Agents ruled out by a PHI/ZDR requirement; `PreCompact` and `SubagentStart`/`SubagentStop`; Strands Agents and Bedrock.

**Exam 4** — choosing the wrong pattern as the most critical early mistake, including the observability tradeoff; the hierarchical multi-level variant; what a harness owns (including resuming after a hit limit); programmatic `AgentDefinition` vs. filesystem `.claude/agents/`; the `Workflow` tool for orchestration beyond turn-by-turn delegation; stateless memory; the Agent SDK as a provider-native primitive vs. cross-provider frameworks.

### Prompt and Context Engineering

**Exam 1** — pruning vs. compaction; wrong output shape pointing at a missing output constraint; scope drift pointing at the system prompt; XML tags delimiting few-shot examples; JSON outputs vs. strict tool use; checking `stop_reason` before assuming a structured response parses.

**Exam 2** — what compaction preserves that pruning can't, and archiving via `PreCompact`; clean-on-tested-inputs failures pointing at a missing constraint; re-prompting five times as a diagnosis failure; grammar-compile latency and the 24-hour compiled-schema cache; structured outputs being incompatible with prefilling; validating structure separately from meaning.

**Exam 3** — context engineering as the superset of prompt engineering; subagents as a context-isolation technique; few-shot fixing an invented structure; strict tool use protecting an agentic loop from malformed arguments; the 40K-cap incident whose symptom looked like tool-selection failure.

**Exam 4** — persistent rules belonging in CLAUDE.md because compaction can drop early instructions; tool-output pruning as the lossless, LLM-free option; when stacking all four techniques is over-engineering; the system prompt as the whole-session behavioral contract; the token cost of structured outputs and why a prompt-only instruction slips; skepticism toward fluent, confident output.

### Tools and MCP

**Exam 1** — built-in tool vs. custom tool vs. Skill vs. MCP server; adding an exclusion sentence to a tool description; `tool_result` in the immediately following user turn matched by ID; stdio vs. HTTP transport; OAuth for a remote server where user identity matters.

**Exam 2** — an MCP-discovered tool being indistinguishable from a manually registered one; resources vs. tools as the right primitive; a committed `.mcp.json` stdio server still needing the runtime on every teammate's machine; dependent tool calls belonging in separate turns; `${VAR}` references plus a `PreToolUse` hook as the two halves of secret hygiene.

**Exam 3** — over-marking schema fields `required` causing fabricated arguments; thinking blocks returned unchanged or the signature breaks; `mcp__server__tool` granularity with deny overriding allow; `defer_loading`/`mcp_toolset` and the connector's remote-only limitation; classical RAG vs. agentic search.

**Exam 4** — merging two tools behind a `type` parameter when descriptions can't be separated; preserving the `text` block when appending an assistant turn that also contains `tool_use`; `readOnlyHint` and sequential execution of state-mutating tools; the prompts primitive as server-maintained wording; OAuth redirect URIs registered per host breaking staging→production; Skills teaching what to do vs. MCP reaching the data, and the layers being additive.

### Security and Safety

**Exam 1** — the indirect-injection defense pattern (isolate as data plus enforcement); least privilege bounding the blast radius; a `PreToolUse` hook needing exit code 2 to deny; HIPAA BAA coverage excluding Console/Workbench/beta/consumer plans.

**Exam 2** — why trusting your own users doesn't address injection; `deny > ask > allow` precedence; a committed secret requiring rotation because history persists; EU residency routing through Bedrock/Vertex rather than the direct API.

**Exam 3** — jailbreak vs. prompt injection as different targets; OS-level sandboxing covering what a hook's explicit checks miss; the agent's own auth configuration being a privileged target; the three authorized FedRAMP routes and the AWS Marketplace exclusion.

**Exam 4** — the trust boundary at an inter-component seam; JSON-encoding untrusted content and never placing your own instructions in a tool result; an API key shown once at creation and federated short-lived credentials; the attorney-client-privilege configuration, including Anthropic not capturing conversation content by default on direct API traffic.

### Claude Code

**Exam 1** — `--bare` for deterministic CI runs; `dontAsk` auto-denying anything off the allow list.
**Exam 2** — CLAUDE.md dilution as the size failure mode; rules files scoped by a `paths` glob in frontmatter, not by directory placement.
**Exam 3** — built-in `Explore`/`Plan` subagents skipping CLAUDE.md and git status; `plan` mode holding the session in the explore phase.
**Exam 4** — the same SKILL.md behaving differently across the four runtimes; `$CLAUDE_PROJECT_DIR` and `${CLAUDE_PLUGIN_ROOT}` for portable plugin scripts.

### Eval, Testing, and Debugging

**Exam 1** — the integration seam as where silent breaks live.
**Exam 2** — matching the grading method to the output shape.
**Exam 3** — retriable vs. terminal classification, and SDK retries that your own loop multiplies.
**Exam 4** — changing one thing per iteration and reading the per-case breakdown rather than the average.

---

## Scoring

1. Mark each answer against the answer key. One point per question, no partial credit.
2. Fill in the domain breakdown table printed at the end of each exam.
3. Compute the weighted readiness score:

```
Readiness = Σ (domain score % × official domain weight)
```

Using official weights rather than the raw count means a miss in Applications and Integration costs you more than a miss in Eval — the same way the real exam prices it.

| Readiness | Reading | Next step |
|---|---|---|
| 85%+ | Ready to sit | Keep one weekly mock to stay warm; revise only flagged weak areas |
| 75–84% | Nearly ready | Two focused sessions on your two weakest domains, then the next mock |
| 65–74% | Real gaps | Re-run coaching sessions for every domain scoring under 70%, then the next mock |
| Below 65% | Not yet | Return to the source notes for the weakest domains before more mocks; mocks measure, they don't teach |

Record every result in `../progress_tracker.md`. A domain scoring under 70% on any mock goes on the weak-areas list regardless of the overall total.

## Recommended sequencing

| Mock | When | Purpose |
|---|---|---|
| Exam 1 | After coaching sessions 1–4 | Baseline; expect gaps in the domains you haven't studied yet |
| Exam 2 | After all eight coaching sessions | First honest full-blueprint measurement |
| Exam 3 | After clearing your top three weak areas | Confirms the reinforcement worked |
| Exam 4 | Final rehearsal, timed, no notes | Predicts your sitting; treat the readiness score as the go/no-go signal |

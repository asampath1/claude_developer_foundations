# Session 3 — Agents and Workflows (14.7%)

Domain 1 of the CCDV-F blueprint. The domain with the most named vocabulary to keep straight, and the one where the right answer is often "the simpler pattern."

Source: [`1_agents_and_workflows.md`](../../1_agents_and_workflows.md). Level: **L2 Applied**. Time: 10–15 minutes.

---

## Section A — Domain Overview

### What this domain actually tests

| Skill | Weight | The question behind the questions |
|---|---|---|
| Agent Architecture | 4.5% | Workflow vs. agent, the five named patterns, supervisor hierarchies, what subagents buy |
| Agent Construction with Claude | 5.3% | The Agent SDK loop, custom harnesses, three deployment paths, hooks |
| Agent Patterns and Frameworks | 4.9% | Tool-use loops, memory scopes, context management, LangGraph/PydanticAI/Strands |

### Key patterns

**The line between workflow and agent.** A workflow follows a **predefined code path** — orchestration lives in your code. An agent **dynamically directs its own process and tool use**. If you can map the exact steps, build a workflow and keep the predictability. If you can't, build an agent and accept non-determinism bounded by the registered toolset. If you're not sure, **start with an agent and extract workflow patterns as they emerge from real usage** rather than guessing at a structure up front.

The progression that keeps this honest: single API call → workflow → agent. Move up only when the simpler pattern can't handle the variability the task actually has. Choosing the wrong pattern at the start is named as the single most critical agent-development mistake — an agent where a workflow would do adds behavioral complexity with no capability gain and trades standard operational logging for transcript-level observability.

**The five named workflow patterns** (Anthropic's own vocabulary, and the exam uses it):

| Pattern | Defining characteristic |
|---|---|
| Prompt chaining | Sequential LLM calls, each processing the previous step's output |
| Routing | Classify the input, then dispatch to a specialized handler |
| Parallelization | Simultaneous subtasks — *sectioning* (independent pieces, for speed) or *voting* (multiple attempts at the same task, for confidence) |
| Orchestrator-workers | A central LLM decomposes a task into subtasks **it can't predict in advance** and delegates each |
| Evaluator-optimizer | One LLM generates, a second evaluates and feeds back for iterative refinement |

Orchestrator-workers is the bridge between workflow and agent: dynamic decomposition, bounded worker tasks. Its cost is real — Anthropic's own multi-agent research system ran at roughly **15x** the token cost of a single-agent chat, and that multiplier only buys something when the work genuinely splits into independent parts. On tightly-coupled work like coding, subagents mostly wait on each other and you pay the fan-out for nothing.

**The supervisor (leader-worker) pattern** is the most common multi-agent structure: a central supervisor holds a list of workers, delegates, and aggregates — usually without executing work itself. The **hierarchical** variant adds levels when one supervisor would have too many direct workers.

**Subagents buy three things**, independent of architecture: context isolation (only the final summary returns to the parent), parallelization (finish in the slowest subtask's time, not the sum), and specialization (narrow prompts, scoped tools, smaller blast radius).

**The agent loop** — receive prompt, evaluate and respond, execute tools and feed results back, repeat until no tool calls remain, return result. Each full cycle is one **turn**. The SDK yields a `SystemMessage` (`subtype: "init"`), `AssistantMessage`s, `UserMessage`s carrying tool results, and finally a `ResultMessage` with text, usage, cost, and session ID. `max_turns` and `max_budget_usd` cap runaway loops, and when either hits you get a `ResultMessage` with an `error_max_turns` / `error_max_budget_usd` subtype — not an exception thrown mid-loop.

**Three wiring paths, same loop:**

| | Raw Messages API loop | Agent SDK (self-hosted) | Managed Agents |
|---|---|---|---|
| Who runs the loop | Your code | The SDK, in your process | Anthropic, plus the sandbox |
| Choose when | Full control, or a constraint no library accommodates | You want Claude Code's loop/context/tool scaffolding in your own environment | Long-running execution, managed sandbox, no loop to build |
| Watch for | Every SDK convenience becomes your code | Set `setting_sources` explicitly — don't rely on a default | Server-side stateful sessions: **not currently ZDR or HIPAA-BAA eligible**; public beta header required |

**Self-hosted sandboxes** are the middle ground: orchestration stays on Anthropic's side, tool execution moves into infrastructure you control.

**Memory has three scopes** — in-context (all state in the live conversation), external storage (written at session end, read at session start), and stateless (fresh every time). The production failure is choosing in-context because development used one long session, then meeting production's many-short-sessions shape where injected history alone exceeds tens of thousands of tokens before the first tool call.

**Hooks** run in *your application process*, not in the model's context, so they cost no tokens. `PreToolUse` can deny a call outright or modify its input; a denial short-circuits the loop and Claude sees the rejection as the tool result. This is the deterministic guarantee a prompt instruction can never be.

### Common mistakes

- **Building an agent because agents are more capable.** More flexible is not automatically better; it costs testing, guardrails, and observability.
- **Fanning out because a task feels slow.** Reach for orchestrator-workers only when an eval or the task's structure confirms genuine parallel decomposability.
- **Assuming `settingSources` has a helpful default in the Agent SDK.** Skills, hooks, and CLAUDE.md silently don't load when it isn't set.
- **Picking Managed Agents for a PHI or ZDR workload.** The governing constraint overrides operational fit.
- **Treating hooks as advisory.** A `PreToolUse` denial is enforcement; a system-prompt rule is a request.
- **Choosing a memory scope from the development session shape** rather than measuring expected state size per production session.

### Real exam-style scenarios

**Scenario A.** A support agent works well in a 12-turn dev session. In production the same work spreads over four short sessions a day, each seeded with accumulated history. By the fourth session the agent returns incomplete results, and the team starts debugging tool schemas.

The reasoning: the symptom points at tool selection, the cause is memory architecture. Injected history was consuming over 40K tokens before the first tool call. In-context memory suits one long session; many accumulating short ones need external storage with only the relevant subset injected. Measure expected state size against the context limit at design time — retrofitting is a much more expensive fix.

**Scenario B.** A team needs an agent that runs for hours, wants someone else to operate the sandbox, and handles PHI under an existing BAA.

The reasoning: everything operational points at Managed Agents, and the compliance constraint overrides all of it. Server-side stateful sessions currently rule out ZDR and HIPAA-BAA coverage, so the answer is the Agent SDK or a raw loop on a BAA-covered configuration. When a governing constraint and an operational preference disagree on this exam, the constraint wins.

---

## Section B — Questions

13 questions, four options each, single best answer.

### Q1

A pipeline generates a marketing summary with one model call, then passes it to a second call that critiques it against a rubric and returns feedback, and loops until the critique passes. Which named pattern is this?

A. Prompt chaining
B. Orchestrator-workers
C. Evaluator-optimizer
D. Parallelization by voting

### Q2

A team can't decide whether a new document-handling task needs a workflow or an agent — the inputs seem varied but they aren't certain the steps are genuinely unpredictable. What does Anthropic's guidance recommend?

A. Start with an agent, then extract deterministic workflow patterns as they emerge from real usage
B. Always default to a workflow, since predictability is never the wrong tradeoff
C. Build both and route traffic between them based on input length
D. Defer the decision until an eval suite exists, since architecture can't be chosen without one

### Q3

A team runs the same risk-assessment prompt three times on each input and takes the majority answer. Which pattern and variant is this, and what does it buy?

A. Prompt chaining — accuracy through focused attention per step
B. Routing — different handlers for different categories
C. Parallelization by sectioning — speed, by splitting independent subtasks
D. Parallelization by voting — confidence, by running multiple attempts at the same task

### Q4

A central agent receives every request, maintains a list of specialist worker agents, delegates to them, and reviews and aggregates their output without doing the work itself. As the worker count grows, mid-level coordinators are introduced between the top agent and the workers. Name the structure and the variant.

A. Evaluator-optimizer, extended into a chain
B. The supervisor (leader-worker) pattern, extended into its hierarchical variant
C. Routing, extended into cascading routes
D. Orchestrator-workers, extended into voting

### Q5

In the Agent SDK's execution loop, what counts as one **turn**?

A. One full cycle of Claude responding and the SDK executing any requested tools and feeding the results back
B. One user message, regardless of how many tool calls it triggers
C. One tool execution
D. One complete session, from init through `ResultMessage`

### Q6

An agent is configured with `max_budget_usd`. The run exceeds the cap partway through. What does the application observe?

A. An exception raised mid-loop, which the harness must catch to avoid crashing
B. The loop continues to completion and the overage is billed as normal
C. A `ResultMessage` with an `error_max_budget_usd` subtype, returned rather than raised
D. A silent truncation, with no signal distinguishing it from a normal completion

### Q7

A team wants Claude Code's loop, context management, and tool scaffolding without rebuilding it, running inside their own Python service where they execute the tools themselves. Which path fits, and what's the configuration trap?

A. Managed Agents — and the trap is forgetting the beta header
B. The Agent SDK, self-hosted — and the trap is relying on a default for `setting_sources`, which gates whether CLAUDE.md, skills, and hooks load at all
C. A raw Messages API loop — and the trap is forgetting to append tool results
D. Claude Desktop — and the trap is per-user configuration drift

### Q8

A regulated customer will accept Anthropic running the agent's orchestration, but the agent's code, filesystem, and network egress must stay inside infrastructure they control. What fits?

A. Managed Agents, since the sandbox is fully managed
B. A raw Messages API loop, which is the only compliant option
C. The Agent SDK with `permission_mode` set to `dontAsk`
D. Self-hosted sandboxes — orchestration stays on Anthropic's side while tool execution runs in the customer's own environment

### Q9

Why is a `PreToolUse` hook a stronger control than a system-prompt instruction saying "never delete files outside the working directory", and what does it cost in context?

A. It runs in your application process as deterministic code rather than a model-followed instruction, and consumes no context-window tokens at all
B. It is injected into the system prompt with higher priority, at the cost of a few hundred tokens per request
C. It retrains the model against the disallowed action for the remainder of the session, at no token cost
D. It is equivalent in strength; the only difference is that hooks are easier to version-control

### Q10

An assistant helps the same engineer across many separate 15-minute sessions spread over weeks, and each session needs to know what happened previously. Which memory scope fits?

A. In-context memory, keeping the whole history in the live conversation
B. Stateless, since each session is short and independently scoped
C. External storage — write state at session end, read it back at session start, injecting only the relevant subset
D. No scope fits; the work must be restructured into one continuous session

### Q11

A team needs to coordinate dozens of agents on a long-running data-migration program — far more than a handful of delegated tasks per turn. What does the SDK offer beyond ordinary subagent delegation?

A. Increasing `max_turns` until every agent fits in one conversation
B. Registering each agent as an MCP server so they can call one another
C. Nothing — subagent delegation is the only supported orchestration mechanism
D. The `Workflow` tool, which moves orchestration into a script executed outside the conversation's own context rather than inside the manager agent's turn-by-turn loop

### Q12

Which third-party framework is characterized by Python-first type safety and schema validation, without heavy multi-agent orchestration machinery?

A. Strands Agents
B. PydanticAI
C. LangGraph
D. The Claude Agent SDK

### Q13

An exploratory agent reads dozens of files to answer one question, and the main conversation's context is filling up. Why does delegating the exploration to a subagent help, and what actually returns to the parent?

A. The subagent runs against a larger context window reserved for delegated work, and returns its full transcript
B. The subagent compresses every tool result automatically, returning a compacted version of each
C. The subagent starts with a fresh context — no parent history, no accumulated tool output — and only its final response returns to the parent as a tool result
D. Nothing returns to the parent; the subagent writes its findings to disk for the parent to read separately

---

### Answer Key and Explanations

#### Q1 — Answer: C

- **Why C is correct:** One LLM generates, a second evaluates and gives feedback for iterative refinement — the defining shape of evaluator-optimizer, and it suits tasks with clear evaluation criteria.
- **Why not A:** Prompt chaining passes output forward through sequential steps; it has no critique-and-refine loop.
- **Why not B:** Orchestrator-workers is about dynamic decomposition into unpredictable subtasks.
- **Why not D:** Voting runs multiple attempts at the same task and picks among them; it doesn't critique and refine.
- **Difficulty:** Easy
- **Tag:** `agents.architecture/workflow-patterns`
- **Revise:** `1_agents_and_workflows.md` → The five named workflow patterns

#### Q2 — Answer: A

- **Why A is correct:** The stated rule for the uncertain case is to start with an agent and extract deterministic workflow patterns as they emerge from real usage, rather than guessing a structure up front.
- **Why not B:** Defaulting to a workflow produces a system that breaks the moment input deviates from the predetermined path.
- **Why not C:** Building both doubles the work and resolves nothing.
- **Why not D:** Evals gate quality and version promotion; they aren't a prerequisite for choosing an architecture.
- **Difficulty:** Medium
- **Tag:** `agents.architecture/workflow-vs-agent`
- **Revise:** `1_agents_and_workflows.md` → Workflow vs. agent

#### Q3 — Answer: D

- **Why D is correct:** Parallelization has two variants: sectioning splits independent subtasks for speed, voting runs multiple attempts at the same task for confidence. Majority-vote risk assessment is voting.
- **Why not A:** Nothing here is sequential.
- **Why not B:** There's no classification-then-dispatch step.
- **Why not C:** Sectioning would split the assessment into different subtasks, not repeat the same one.
- **Difficulty:** Medium
- **Tag:** `agents.architecture/workflow-patterns`
- **Revise:** `1_agents_and_workflows.md` → The five named workflow patterns

#### Q4 — Answer: B

- **Why B is correct:** A central supervisor holding a worker list, delegating, and aggregating without executing is the supervisor/leader-worker pattern; adding mid-level supervisors is its hierarchical variant, used when one supervisor would track too many direct workers.
- **Why not A:** Evaluator-optimizer is a two-role generate/critique loop.
- **Why not C:** Routing dispatches by input category, with no ongoing supervision or aggregation.
- **Why not D:** Voting is a parallelization variant, not a multi-level delegation structure.
- **Difficulty:** Medium
- **Tag:** `agents.architecture/supervisor-hierarchies`
- **Revise:** `1_agents_and_workflows.md` → Manager/supervisor hierarchies

#### Q5 — Answer: A

- **Why A is correct:** A turn is one full cycle of the loop: Claude responds, the SDK executes any requested tools and feeds results back. The cycle repeats until Claude returns a response with no tool calls.
- **Why not B:** A single user message can drive many turns.
- **Why not C:** One turn can contain several tool executions, including parallel ones.
- **Why not D:** A session is many turns.
- **Difficulty:** Easy
- **Tag:** `agents.construction/agent-loop`
- **Revise:** `1_agents_and_workflows.md` → The Claude Agent SDK and the agent loop

#### Q6 — Answer: C

- **Why C is correct:** When `max_turns` or `max_budget_usd` is hit, the SDK returns a `ResultMessage` carrying an `error_max_turns` or `error_max_budget_usd` subtype rather than raising mid-loop — which is what lets a harness decide whether to resume with a higher limit.
- **Why not A:** No exception is thrown at the cap.
- **Why not B:** The cap is enforced; that's its purpose, and it also covers subagent spend.
- **Why not D:** The subtype is exactly the signal that distinguishes it from `success`.
- **Difficulty:** Medium
- **Tag:** `agents.construction/loop-limits`
- **Revise:** `1_agents_and_workflows.md` → Agent Construction with Claude

#### Q7 — Answer: B

- **Why B is correct:** The self-hosted Agent SDK is the path that gives you the loop, context management, and tool registration inside your own process. The documented trap is `settingSources`/`setting_sources` — set it explicitly, because relying on a default is why a skill that worked in Claude Code silently does nothing under the SDK.
- **Why not A:** Managed Agents hands the loop and sandbox to Anthropic, which isn't what's described.
- **Why not C:** A raw loop means writing the scaffolding they explicitly don't want to rebuild.
- **Why not D:** Claude Desktop isn't a programmatic deployment path.
- **Difficulty:** Medium
- **Tag:** `agents.construction/deployment-paths`
- **Revise:** `1_agents_and_workflows.md` → Managed agent deployment models

#### Q8 — Answer: D

- **Why D is correct:** Self-hosted sandboxes are precisely this middle ground — Anthropic keeps orchestration, tool execution moves into your infrastructure, so code, filesystem, and network egress never leave your environment.
- **Why not A:** Managed Agents runs the sandbox on Anthropic's side, which is what the constraint forbids.
- **Why not B:** A raw loop would satisfy the constraint but isn't the only option, and the customer explicitly accepts Anthropic-run orchestration.
- **Why not C:** A permission mode governs approval behavior, not where execution physically happens.
- **Difficulty:** Hard
- **Tag:** `agents.construction/self-hosted-sandboxes`
- **Revise:** `1_agents_and_workflows.md` → Managed agent deployment models

#### Q9 — Answer: A

- **Why A is correct:** Hooks are callbacks running in your application process at defined loop points. They're code, not instructions the model may or may not follow, and because they don't live in the model's context they cost no tokens.
- **Why not B:** Hooks aren't injected into the prompt at all.
- **Why not C:** Nothing about a hook changes the model.
- **Why not D:** The whole reason hooks exist is that a prompt-level rule isn't a reliable guarantee.
- **Difficulty:** Medium
- **Tag:** `agents.construction/hooks`
- **Revise:** `1_agents_and_workflows.md` → Hooks for deterministic actions

#### Q10 — Answer: C

- **Why C is correct:** The same user or task continuing across many separate, shorter sessions is the external-storage case: persist at session end, read back at session start, and inject only what's relevant.
- **Why not A:** This is the documented production failure — accumulated injected history crowds out the working context before the first tool call.
- **Why not B:** Stateless suits fully independent jobs, and here each session depends on previous ones.
- **Why not D:** Restructuring the user's working pattern isn't the fix; changing the memory architecture is.
- **Difficulty:** Medium
- **Tag:** `agents.patterns/memory-scopes`
- **Revise:** `1_agents_and_workflows.md` → Agent memory

#### Q11 — Answer: D

- **Why D is correct:** Subagents suit a handful of delegated tasks per turn. Beyond that, the SDK exposes a separate `Workflow` tool that moves orchestration into a script executed outside the conversation's own context.
- **Why not A:** Raising the turn cap doesn't address the context and coordination cost of dozens of agents in one loop.
- **Why not B:** MCP exposes tools to clients; it isn't an agent-orchestration mechanism.
- **Why not C:** There is a documented mechanism beyond subagent delegation.
- **Difficulty:** Medium
- **Tag:** `agents.patterns/scaling-orchestration`
- **Revise:** `1_agents_and_workflows.md` → Sub-agents as a scaling mechanism

#### Q12 — Answer: B

- **Why B is correct:** PydanticAI is the Python-first framework built around type safety and schema validation without heavy orchestration machinery — the pick when validated, typed inputs and outputs matter more than multi-agent coordination.
- **Why not A:** Strands Agents is AWS's model-driven framework, tightly integrated with Bedrock.
- **Why not C:** LangGraph is graph-based orchestration for complex stateful workflows.
- **Why not D:** The Agent SDK is the provider-native primitive, not a third-party framework.
- **Difficulty:** Easy
- **Tag:** `agents.patterns/frameworks`
- **Revise:** `1_agents_and_workflows.md` → Third-party agentic frameworks

#### Q13 — Answer: C

- **Why C is correct:** A subagent starts with a fresh context window carrying no parent history or accumulated tool output, and only its final response comes back to the parent as a tool result. That's why subagents are the primary architectural lever against unbounded context growth.
- **Why not A:** There's no larger reserved window, and the transcript stays with the subagent.
- **Why not B:** No automatic per-result compression happens; the isolation is what saves context.
- **Why not D:** The final response does return to the parent — that's the delegation contract.
- **Difficulty:** Hard
- **Tag:** `agents.patterns/context-management`
- **Revise:** `1_agents_and_workflows.md` → The role of subagents

---

## Section C — Score and Analysis

### Score

| | |
|---|---|
| Correct | ___ / 13 |
| Percentage | ___ % |
| Difficulty level run | L2 Applied |

| Band | Reading |
|---|---|
| 11–13 (85%+) | Strong. Move up a level next session. |
| 8–10 (62–77%) | Hold level; clear the tags below. |
| 6–7 (46–54%) | Re-read the pattern table and the three deployment paths, then repeat at L1. |
| Below 6 | Repeat at L1. Start with the five named patterns — most of this domain's questions are pattern identification in disguise. |

### Weak-area map

| Missed | Tag | Revise |
|---|---|---|
| Q1–Q4 | `agents.architecture` | `1_agents_and_workflows.md` → Agent Architecture |
| Q5–Q9 | `agents.construction` | `1_agents_and_workflows.md` → Agent Construction with Claude |
| Q10–Q13 | `agents.patterns` | `1_agents_and_workflows.md` → Agent Patterns and Frameworks |

### Recommended next steps

1. If you missed a pattern-identification question, write the five patterns from memory with one defining sentence each. They recur inside scenario questions in other domains.
2. If you missed Q7 or Q8, redraw the three-path table from memory including the "watch for" row — the compliance caveat on Managed Agents is a favorite constraint-overrides-convenience setup.
3. Update the tracker with your score, level, and next level.

**Next domain or repeat this one?**

# Session 5 — Tools and MCP (10.6%)

Domain 8 of the CCDV-F blueprint. Two halves: getting a single tool call structurally right, and deciding which extension mechanism a capability belongs in.

Source: [`3_claude_code_tools_mcp.md`](../../3_claude_code_tools_mcp.md). Level: **L2 Applied**. Time: 10–15 minutes.

---

## Section A — Domain Overview

### What this domain actually tests

| Skill | Weight | The question behind the questions |
|---|---|---|
| Tool Implementation | 4.4% | Schemas, descriptions, block pairing, parallel calls, dispatch and approval patterns |
| MCP Server Development | 2.1% | Primitives, transports, configuration scopes, authentication |
| Agentic Customization | 4.1% | Built-in tool vs. custom tool vs. Skill vs. MCP server |

### Key patterns

**Claude never sees your implementation** — only the tool's name, description, and `input_schema`, plus whatever result you return. With the default `tool_choice: {"type": "auto"}`, it calls a tool when the request maps to the described capability and the answer isn't already in context. That makes **description writing a design task**: write it in two parts, when to use it *and when not to*. A vague or overlapping description directly causes wrong-tool and no-tool-call failures, and if two descriptions can't be cleanly separated even with exclusion conditions, merge the tools behind a `type` parameter instead of lengthening both.

In the schema, mark a field `required` only when the call is meaningless without it. Marking everything required forces Claude to fabricate values it has no basis for.

**The message-block pairing rules are validated before generation, so no prompt can fix them:**

| Block | Rule |
|---|---|
| `text` | Can appear alongside `tool_use` in the same assistant turn — preserve the whole content array when appending to history |
| `tool_use` | Must be answered by a `tool_result` in the **immediately following** user turn, matched by ID |
| `tool_result` | `tool_use_id` must match exactly; optional `is_error: true` |
| `thinking` | Must be passed back **unchanged** — the signature verifies it, and any edit (even a summary) gets the request rejected |

**Parallel tool use** is the default when subtasks are independent: several `tool_use` blocks in one turn, with matching `tool_result` blocks returned together. Read-only tools run concurrently; state-mutating ones run sequentially, and a custom tool opts into concurrency via `readOnlyHint`. When one tool's output feeds the next call's input, that's **separate turns** — or `disable_parallel_tool_use` when a workflow requires strictly one call per turn.

**What MCP solves:** without it, three applications needing the same external service maintain three copies of the same integration. MCP turns the tool definition into a standalone server any client can connect to and discover tools from. Once discovered, an MCP tool is **indistinguishable** to Claude from one you registered manually — only ownership differs.

| Primitive | What it is |
|---|---|
| Tools | Actions the model can call |
| Resources | Read-only data fetched by address straight into context, no tool call (support varies by client) |
| Prompts | Server-maintained instruction templates invoked by name |

| Transport | Use when |
|---|---|
| stdio | Local process on the same machine; can't be shared across a team |
| HTTP | Recommended for anything not local |
| SSE | Legacy, superseded — treat as historical |

Configuration scopes mirror settings.json: local (`~/.claude.json` per project), user, project (`.mcp.json`, committed), enterprise (managed). Note the project-scope catch: a committed stdio server still spawns a local subprocess on every teammate's machine, so each of them needs the runtime installed.

**Permissions get finer than the server level:** a rule can target `mcp__server__tool`, and **a deny on one tool overrides an allow on the whole server**.

**The four-way choice** the blueprint names explicitly:

| | Reach for it when |
|---|---|
| Built-in tools | The task is generic and the built-in already does it |
| Custom tools | One app needs one specific internal function, with no reuse elsewhere |
| Skills | A repeatable process or judgment call, no new live data access needed |
| MCP servers | Multiple apps need the same live data or action, maintained independently |

**MCP connects Claude to data; Skills teach Claude what to do with that data.** The layers are additive, never substitutive — built-in tools remain available regardless of what you add, and a production setup commonly uses all of them, bundled and distributed as a plugin.

### Common mistakes

- **Fixing tool-selection failures with prompt patches.** If selection failures are systematic, the fix belongs in the schema and description.
- **Marking every schema field required.** It doesn't make calls more complete; it makes Claude invent arguments.
- **Chaining dependent tool calls in one turn.** The second call can't be built correctly until the first result is back.
- **Editing or summarizing a thinking block before sending it back.** The signature breaks and the request is rejected — redacted blocks follow the same rule.
- **Reaching for MCP for a single app-specific function.** That's a custom tool; MCP is for capabilities several independently-maintained clients need.
- **Expecting a Skill to fetch live data.** A Skill is procedural knowledge; it needs a tool or MCP server underneath to reach anything.

### Real exam-style scenarios

**Scenario A.** Two tools — `search_docs` ("use this to find information about the product") and `get_context_summary` ("use this to retrieve relevant information from the current session") — and Claude keeps picking the wrong one on ambiguous inputs.

The reasoning: from Claude's side both descriptions say "find information." The fix is one exclusion sentence per description naming when *not* to call it. One caveat worth remembering: exclusion conditions referencing "earlier in this conversation" only work if the full history is actually passed on each request — truncate prior turns and the exclusion logic silently stops working.

**Scenario B.** An MCP server exposes ten tools including a destructive one. The team wants one read tool callable freely while everything else still prompts.

The reasoning: permission rules can target `mcp__server__tool`, so an allow rule on the single read tool leaves the rest under whatever rule otherwise applies. And if someone later adds a broad server-level allow, a deny on the destructive tool still wins — deny beats allow at every scope and in every mode.

---

## Section B — Questions

12 questions, four options each, single best answer.

### Q1

When Claude decides whether to call a tool, what does it actually read?

A. The tool's implementation source, so behavior can be inferred from the code
B. The tool's name only, which is why naming matters more than documentation
C. The tool's name, description, and `input_schema` — never the implementation — plus whatever result you return
D. The tool's most recent execution logs, to judge reliability

### Q2

A developer marks every field in a tool's `input_schema` as `required`, reasoning that complete arguments produce better results. What actually happens?

A. Claude fabricates values for fields it has no basis for, because the call can't be made without them
B. The API rejects any request where a required field's value is uncertain
C. Nothing changes; `required` is advisory metadata
D. Claude stops calling the tool entirely and asks the user to fill in the fields

### Q3

An application appends an assistant turn containing a `tool_use` block, then sends the next request without a matching `tool_result`. What happens, and can prompting fix it?

A. Claude re-issues the tool call automatically on the next turn
B. The result is treated as empty, and Claude continues with degraded accuracy
C. The request succeeds but the tool's output is dropped from context
D. Request validation fails — a `tool_use` must be answered by a matching `tool_result` in the immediately following user turn, and no prompt-level instruction can recover from a structural mismatch

### Q4

An application using extended thinking summarizes each `thinking` block before appending it to history, to save tokens. Requests start being rejected. Why?

A. Thinking blocks may only appear in the first turn of a conversation
B. Thinking blocks carry a signature verifying they haven't been edited — any modification, including a summary, breaks it and the request is rejected
C. Summarized thinking must be re-encoded as a `text` block, which the application didn't do
D. Thinking blocks must be removed from history entirely, and keeping a summary is what fails

### Q5

A workflow needs `get_customer_id` to run first, because `fetch_orders` takes that ID as its input. How should this be structured?

A. Both tools in one turn, with Claude resolving the ordering internally
B. Both in one turn with `readOnlyHint` set on the first, which forces it to complete first
C. As separate turns — the second call can't be built correctly until the first result is back — or with `disable_parallel_tool_use` if the workflow requires strictly one call per turn
D. As a single merged tool, since dependent calls are not supported

### Q6

Three separate applications each need to query the same internal inventory service. What problem does building an MCP server solve here?

A. The tool definition lives once in a standalone server that any MCP client can connect to and discover tools from, instead of the same integration being rebuilt and maintained in all three applications
B. It reduces per-token cost by moving tool schemas out of the request
C. It gives Claude direct database access without an intermediate service
D. It is the only mechanism by which Claude can call an internal API

### Q7

A team is deploying an MCP server that a whole team will reach over the network. Which transport, and what should they know about the alternatives?

A. stdio, because it's the most widely supported
B. SSE, because it's designed for shared remote servers
C. Either stdio or SSE; the choice is a style preference
D. HTTP — recommended for anything not local; stdio is for a local process on the same machine and can't be shared, and SSE is legacy and superseded

### Q8

A team commits a `.mcp.json` at the repo root registering an `npx`-launched stdio server, so the whole team picks it up on clone. Two teammates report it fails to start. What's the likely cause?

A. `.mcp.json` only applies to the repository owner's machine
B. A project-scoped stdio server still spawns a local subprocess on each teammate's machine, so every one of them needs the runtime installed — Node, in this case
C. stdio servers cannot be registered at project scope at all
D. The server must be re-registered per user in `~/.claude.json` before it will start anywhere

### Q9

An internal expense application needs Claude to call one specific function — `submit_expense_line` — that exists only in that application and will never be reused elsewhere. Which mechanism fits?

A. An MCP server, so the capability is available if another team ever needs it
B. A Skill describing how to submit expense lines
C. A custom tool defined with a schema in that application
D. A built-in tool, since expense submission is a generic operation

### Q10

A skill that works in Claude Code stops working when the same `SKILL.md` is sent with a Messages API request. Its steps shell out to a local validation script. Why does it break?

A. On the Messages API the skill's steps run inside Anthropic's code-execution container, not on your machine, so a skill assuming local files and tools has nothing to reach
B. Skills are not supported on the Messages API in any form
C. The skill's frontmatter requires a `runtime` field that Claude Code sets automatically
D. Messages API skills only execute if `disable-model-invocation` is set to false

### Q11

A production setup uses an MCP server for a live deployment system, two custom tools for app-specific functions, and a Skill encoding the team's release-review procedure. A reviewer asks whether the Skill makes the MCP server redundant. What's correct?

A. Yes — a Skill can describe the same operations, so the MCP server duplicates it
B. Yes, provided the Skill's description names the deployment system explicitly
C. No, but only because Skills can't run in Claude Code alongside MCP servers
D. No — MCP connects Claude to the data and actions, Skills teach Claude what to do with them, and the layers are additive; a Skill saying "look up deployment status" can't itself reach the deployment system

### Q12

An MCP server has a broad server-level allow rule, and a separate deny rule targeting `mcp__deploy__delete_environment`. What happens when Claude tries to call that specific tool?

A. The allow rule wins, because server-level rules take precedence over tool-level ones
B. The call is denied — a deny on one tool overrides an allow covering the whole server
C. The rules cancel out and the user is prompted for approval
D. The configuration is invalid and the server fails to load

---

### Answer Key and Explanations

#### Q1 — Answer: C

- **Why C is correct:** Claude sees the name, description, and JSON input schema, and the result you return — never the implementation. That's why the description carries the selection decision.
- **Why not A:** The implementation is never exposed to the model.
- **Why not B:** The name matters, but selection is driven mainly by how well the request matches the *description*.
- **Why not D:** Execution history isn't part of what the model reads to select a tool.
- **Difficulty:** Easy
- **Tag:** `tools.implementation/what-claude-reads`
- **Revise:** `3_claude_code_tools_mcp.md` → Tool Implementation

#### Q2 — Answer: A

- **Why A is correct:** Marking everything required forces Claude to supply values it has no basis for. Mark a field required only when the call is meaningless without it; leave the rest optional where a default or absence carries meaning.
- **Why not B:** The API validates shape, not whether Claude had grounds for a value.
- **Why not C:** `required` genuinely constrains what a valid call looks like.
- **Why not D:** The model fills the fields rather than refusing the call.
- **Difficulty:** Medium
- **Tag:** `tools.implementation/schema-design`
- **Revise:** `3_claude_code_tools_mcp.md` → Schema anatomy

#### Q3 — Answer: D

- **Why D is correct:** The pairing rule is enforced at request validation, before generation starts. A missing or mismatched `tool_result` fails the request, and there's no prompt-level recovery from a structural mismatch.
- **Why not A:** Nothing re-issues the call for you.
- **Why not B:** There's no lenient fallback that treats the result as empty.
- **Why not C:** The request doesn't succeed at all.
- **Difficulty:** Medium
- **Tag:** `tools.implementation/block-pairing`
- **Revise:** `3_claude_code_tools_mcp.md` → Message block structure

#### Q4 — Answer: B

- **Why B is correct:** Thinking blocks must be passed back unchanged; the signature verifies they haven't been edited, and any modification — including a summary — breaks it. Redacted thinking blocks follow the same rule despite being unreadable.
- **Why not A:** They can appear across turns; the constraint is integrity, not position.
- **Why not C:** Re-encoding as text doesn't preserve the signature.
- **Why not D:** The requirement is to return them intact, not to strip them.
- **Difficulty:** Hard
- **Tag:** `tools.implementation/thinking-blocks`
- **Revise:** `3_claude_code_tools_mcp.md` → Message block structure

#### Q5 — Answer: C

- **Why C is correct:** Parallel calls are for independent subtasks. When one tool's output is the next call's input, that's separate turns, and `disable_parallel_tool_use` forces one call per turn when a workflow needs it.
- **Why not A:** Issuing both in one turn means the second is built before the first result exists.
- **Why not B:** `readOnlyHint` opts a custom tool into concurrency; it isn't an ordering primitive.
- **Why not D:** Dependent calls are entirely supported — as separate turns.
- **Difficulty:** Medium
- **Tag:** `tools.implementation/parallel-calls`
- **Revise:** `3_claude_code_tools_mcp.md` → Subtask dependency and parallel calls

#### Q6 — Answer: A

- **Why A is correct:** That duplication is the problem MCP was designed for: define the capability once as a standalone server, and every MCP client discovers it through the handshake without re-implementing anything.
- **Why not B:** MCP schemas still cost context — which is why definitions are deferred by default.
- **Why not C:** An MCP server is a process exposing tools; it doesn't grant direct database access.
- **Why not D:** A custom tool can call an internal API perfectly well; MCP is about reuse across clients.
- **Difficulty:** Easy
- **Tag:** `tools.mcp/what-it-solves`
- **Revise:** `3_claude_code_tools_mcp.md` → MCP Server Development

#### Q7 — Answer: D

- **Why D is correct:** Transport is matched to where the server runs. HTTP is recommended for anything not local; stdio is a local same-machine process that can't be shared; SSE predates HTTP transport and is not recommended for new servers.
- **Why not A:** stdio can't serve a team over a network.
- **Why not B:** SSE is the legacy option, explicitly superseded.
- **Why not C:** It isn't a style preference — it's determined by where the server runs.
- **Difficulty:** Medium
- **Tag:** `tools.mcp/transports`
- **Revise:** `3_claude_code_tools_mcp.md` → Transport

#### Q8 — Answer: B

- **Why B is correct:** Project scope distributes the *configuration*, not a running service. A stdio server spawns a local subprocess per teammate, so each machine needs the runtime the launch command depends on.
- **Why not A:** A committed `.mcp.json` applies to everyone who clones the repo.
- **Why not C:** stdio servers are commonly registered at project scope; that's exactly the case with this catch.
- **Why not D:** Per-user re-registration isn't required, and it wouldn't install a missing runtime.
- **Difficulty:** Hard
- **Tag:** `tools.mcp/configuration-scopes`
- **Revise:** `3_claude_code_tools_mcp.md` → Configuration scope

#### Q9 — Answer: C

- **Why C is correct:** One app, one specific internal function, no reuse elsewhere is the custom-tool case exactly.
- **Why not A:** MCP is for capabilities multiple applications need, maintained independently — overkill for a single one-off function.
- **Why not B:** A Skill is procedural knowledge and can't reach an external system by itself.
- **Why not D:** Built-in tools cover generic capabilities, not a proprietary internal operation.
- **Difficulty:** Medium
- **Tag:** `tools.customization/four-way-choice`
- **Revise:** `3_claude_code_tools_mcp.md` → Agentic Customization

#### Q10 — Answer: A

- **Why A is correct:** The same `SKILL.md` behaves differently per runtime. On the Messages API it runs inside Anthropic's code-execution container, so anything assuming local files or local commands breaks — and it breaks silently, because the skill still loads.
- **Why not B:** Skills are supported on the Messages API with the appropriate beta headers.
- **Why not C:** No such runtime field exists.
- **Why not D:** `disable-model-invocation` controls whether a skill can be auto-triggered, not where it executes.
- **Difficulty:** Medium
- **Tag:** `tools.customization/skills-across-runtimes`
- **Revise:** `3_claude_code_tools_mcp.md` → Skills across four runtimes

#### Q11 — Answer: D

- **Why D is correct:** MCP connects Claude to data and actions; Skills encode what to do with them. A Skill is text — it can't reach the deployment system, so it needs the MCP server (or a custom tool) underneath. The layers are additive.
- **Why not A:** Describing an operation isn't performing it.
- **Why not B:** A more explicit description still can't make text reach an external system.
- **Why not C:** Skills and MCP servers coexist in Claude Code routinely; that's the typical production setup.
- **Difficulty:** Hard
- **Tag:** `tools.customization/layering`
- **Revise:** `3_claude_code_tools_mcp.md` → Agentic Customization

#### Q12 — Answer: B

- **Why B is correct:** MCP permissions can target a single tool as `mcp__server__tool`, and a deny on one tool overrides an allow covering the whole server — consistent with deny beating allow everywhere else.
- **Why not A:** Precedence runs the other way: the specific deny wins.
- **Why not C:** Deny is decisive; it doesn't fall back to prompting.
- **Why not D:** Combining a server-level allow with a tool-level deny is a supported, intended configuration.
- **Difficulty:** Medium
- **Tag:** `tools.implementation/approval-patterns`
- **Revise:** `3_claude_code_tools_mcp.md` → Dispatch patterns

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
| 6–7 (50–58%) | Re-read the block-pairing table and the four-way choice table, then repeat at L1. |
| Below 6 | Repeat at L1. The two tables above account for most of this domain's marks. |

### Weak-area map

| Missed | Tag | Revise |
|---|---|---|
| Q1–Q5, Q12 | `tools.implementation` | `3_claude_code_tools_mcp.md` → Tool Implementation |
| Q6–Q8 | `tools.mcp` | `3_claude_code_tools_mcp.md` → MCP Server Development |
| Q9–Q11 | `tools.customization` | `3_claude_code_tools_mcp.md` → Agentic Customization |

### Recommended next steps

1. If you missed Q3 or Q4, re-read the block-structure table until the pairing and signature rules are automatic — these are structural facts no prompt can work around, and the exam likes that framing.
2. If you missed Q9, Q10, or Q11, write out the built-in / custom / Skill / MCP table from memory with the "not the right fit when" row included; the wrong answers in those questions are all "right mechanism, wrong situation."
3. Update the tracker with your score, level, and next level.

**Next domain or repeat this one?**

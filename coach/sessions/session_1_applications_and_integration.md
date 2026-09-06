# Session 1 — Applications and Integration (33.1%)

The largest domain on the exam by a wide margin: a third of your marks live here. Domain 2 of the CCDV-F blueprint.

Source: [`2_applications_and_integration.md`](../../2_applications_and_integration.md). Level: **L2 Applied**. Time: 10–15 minutes.

---

## Section A — Domain Overview

### What this domain actually tests

| Skill | Weight | The question behind the questions |
|---|---|---|
| Understanding Requirements | 3.4% | Can you tell a business goal from a requirement, and a functional requirement from an infrastructure one? |
| Systems Life Cycle | 2.8% | Do you know which phase a decision belongs in, and what a gate refuses to let through? |
| Claude API Mechanics | 6.8% | Messages, tools, streaming, vision, thinking, caching, batch — and the realtime/batch tradeoff |
| Software Engineering Foundations | 7.4% | Ordinary engineering discipline applied to prompts, schemas, and evals |
| Claude Application Design | 8.6% | Instruction interpretation per interface, content boundaries, schema contracts, session hygiene, plugins |
| Configuration Management | 4.1% | CLAUDE.md, settings.json, model pinning, prompt versioning, plugin dependencies |

Notice where the weight actually sits: Application Design and Software Engineering Foundations together are 16% — more than the entire Model Selection domain. The exam is more interested in whether you can design and operate a Claude application than in whether you can recite API parameters.

### Key patterns

**A business problem is not a requirement.** "Help support agents answer faster" is a goal. The functional requirement derived from it — "classify each ticket into one of four queues; draft a reply citing the relevant policy; never auto-send without human approval" — is specific enough to become a line in an eval. The infrastructure requirements are the non-functional constraints the goal implies but never states, and there are four to ask about every time:

| Dimension | The question to ask |
|---|---|
| Latency | How fast, measured from where the user actually is? |
| Scale | How many requests, at what peak? |
| Residency | Where must data be processed, under which regulation? |
| Identity | Who acts, under what credentials, and what has to be auditable? |

These four usually decide the deployment platform. Capture them during scoping, because the alternative is discovering one at a security review after the build is finished.

**Requirements map onto infrastructure choices.** "Summarize 10,000 documents overnight, cost-sensitive" maps to the Message Batches API. "Respond to a live chat user" maps to streaming. Picking the infrastructure pattern before pinning the requirement is the root cause of most "why is this slow/expensive" complaints.

**A gate is the decision to move between lifecycle phases.** Seven phases — requirements, design, build, test, deploy, operate, iterate — and the gates between them are where a regulated engagement keeps control. You don't move design → build until the platform satisfies residency. You don't move deploy → full production until the new version clears the eval against its pinned baseline. One property is specific to Claude applications: **the operate phase is never finished**, because model behavior can shift on a version bump and prompt effectiveness drifts as usage patterns change, with no code change involved.

**API mechanics worth knowing cold:**

- The Messages API is **stateless per request**. Your application owns conversation state and resends the whole growing array each turn.
- A streamed `tool_use` block is **not safe to act on until the stream closes** and its `input_json` has been fully reassembled from `content_block_delta` events. Acting early produces malformed tool inputs.
- Images cost `⌈width/28⌉ × ⌈height/28⌉` visual tokens; three source types (`base64` re-sends every turn, `url` takes an availability dependency, `file` via the Files API uploads once). **PDFs use a `document` block**, not `image`.
- Batch: up to 100,000 requests or 256MB per call, up to 24 hours, lower per-token cost, **results in arbitrary order** — set `custom_id` to match them back.
- Version pinning: an alias moves, a full model ID doesn't. From the 4.6 generation the ID is dateless but still a fixed snapshot. Retain the prior pin so a regression is a rollback, not a hotfix.

**Persistent instructions differ per interface** — this is the design trap the exam likes:

| Interface | Persistence comes from |
|---|---|
| Claude Code | The CLAUDE.md hierarchy, re-injected every request |
| Claude Desktop / claude.ai | Custom instructions and Projects, user- or workspace-scoped |
| API / SDKs | The `system` parameter you set on every single request — no implicit persistence at all |

**Four configuration artifacts, one discipline.** CLAUDE.md, settings.json, model version pins, and prompt versions are all production configuration. None of them is compiled or type-checked, so nothing but version control, review, and an eval suite will catch a regression before your users do.

### Common mistakes

- **Choosing the platform on familiarity.** The team ships on what they know, passes every functional test, and fails the customer's security review on residency. Familiarity answers whether you can build fast; it says nothing about whether the customer is allowed to run the result.
- **Chunking a loop and calling it batching.** Splitting a list into smaller pieces and looping over the synchronous endpoint is serialization with extra steps — the API still sees one request per item and the rate limit doesn't care about your chunk boundaries.
- **Assuming Claude Code behavior transfers to the raw API.** There is no CLAUDE.md over the API. Every persistent instruction has to be re-sent in `system`.
- **Reviewing application logic but not prompt and schema diffs.** A tool-schema change is a breaking change for every caller, with no compiler to catch it.
- **Shipping against a moving alias.** The alias advances, the response shape shifts, a downstream parser throws, and there's no pinned prior version to roll back to.
- **Treating packaging as optional.** A working build and a reusable build are different finishing states; hardcoded customer values with no documented assumptions and no bundled eval get rewritten from scratch by the next team.

### Real exam-style scenarios

**Scenario A.** A customer wants nightly summaries of 8,000 support transcripts, delivered by 7am, and says cost matters more than speed. Their security team later asks where the data is processed.

The reasoning the exam wants: the *functional* requirement (summarize transcripts, nightly, by 7am) maps to the Message Batches API, because nobody is waiting on any individual result and batch trades latency for a lower per-token rate. The *infrastructure* requirement (residency) is the one that was never stated in the business problem and has to be derived — and it decides the platform, which is a pass/fail constraint rather than a tradeoff. Getting the batch answer right and the residency question late still costs you the build.

**Scenario B.** A team prototypes an assistant in Claude Code, with a well-tuned CLAUDE.md holding a dozen behavioral rules. They port it to a backend service using the SDK, and quality collapses on the same inputs.

The reasoning: nothing about the model changed. CLAUDE.md is a Claude Code mechanism that is re-injected on every request in that interface. Over the API there is no equivalent — those dozen rules now have to be an explicit `system` prompt the application sends every time. This is a Claude Application Design question wearing a debugging costume.

---

## Section B — Questions

15 questions, four options each, single best answer. Answer all of them before reading the key.

### Q1

A stakeholder's brief for a claims-triage assistant contains the four statements below. Which one is an **infrastructure** requirement rather than a functional one?

A. Every claim is classified into one of five handling queues
B. The assistant drafts a response citing the specific policy clause it relied on
C. Claim documents must be processed within the customer's approved geographic region
D. No response is sent to a claimant without an adjuster approving it

### Q2

A business sponsor says: "we need our support agents to answer faster." A developer immediately begins comparing deployment platforms based on which one the team has shipped on before. What has been skipped?

A. Nothing — platform choice is correctly made first, since it constrains everything downstream
B. A model-tier benchmark comparing Haiku, Sonnet, and Opus on sample tickets
C. An eval suite, which must exist before any requirement can be written
D. Deriving checkable functional requirements from the goal, and the latency, scale, residency, and identity constraints it implies

### Q3

A team completes its build and reaches the customer's security review, where a reviewer asks where claim data is processed. The chosen platform doesn't satisfy the customer's residency requirement, and the integration has to be rebuilt elsewhere. Per the lifecycle gate discipline, what went wrong?

A. The eval suite should have included a residency test case
B. The residency constraint belonged in the requirements phase, and the design → build gate should have refused to open until the chosen platform satisfied it
C. Nothing was avoidable — residency constraints can only be confirmed by the customer's own security team at review time
D. The team should have deployed to every candidate platform and let the reviewer choose

### Q4

Which sequence matches the systems lifecycle phases a Claude application moves through?

A. Requirements → design → build → test → deploy → operate → iterate
B. Design → requirements → build → deploy → test → iterate → operate
C. Requirements → build → test → design → deploy → operate → iterate
D. Build → test → requirements → design → deploy → iterate → operate

### Q5

Your multi-turn application sends a conversation to the Messages API. What is true about where that conversation lives?

A. Anthropic stores the conversation server-side and your application references it by session ID
B. The API keeps the last ten turns and your application supplies anything older
C. Conversation state is held in the model's context between requests as long as the same API key is used
D. The API is stateless per request — your application owns the conversation and resends the whole growing array each turn

### Q6

An application streams a response that may contain tool calls. At which point is it safe to execute a requested tool?

A. As soon as a `content_block_start` event announces a `tool_use` block, since the tool name is known by then
B. After the first `input_json_delta` arrives, since the remaining deltas only add optional arguments
C. Only after the stream closes and the block's accumulated `input_json` has been fully reassembled and parsed
D. Streaming responses cannot contain tool calls, so the question doesn't arise

### Q7

A team needs Claude to read a 40-page contract PDF. How is that content supplied?

A. As a `document` content block, with the same `base64`/`url`/`file_id` source pattern used for images
B. As an `image` content block, with `media_type` set to `application/pdf`
C. As plain text in the `system` prompt after extracting it client-side, since PDFs aren't supported
D. As a `tool_result` block, because file content can only enter context through a tool

### Q8

A pipeline sends one 1,400 × 900 pixel screenshot per request. Roughly how many visual tokens does that image consume, and what should the team do with the number?

A. About 450 tokens — negligible, so no action needed
B. About 1,650 tokens — measure a typical production image against the context budget at design time, since a resize is cheap before deployment and expensive after
C. Exactly 1,000 tokens for any image, since images are billed at a flat rate
D. Image tokens are not counted against the context window, only against the response budget

### Q9

A backend service fans out 200 independent Claude requests using the Python SDK's `AsyncAnthropic` client. What does that buy?

A. Lower per-request latency, because async requests are prioritized by the API
B. A lower per-token cost, because concurrent requests are billed as a batch
C. Concurrency — the application handles other work while requests are in flight — but each individual request takes just as long as it would synchronously
D. Nothing, because the Python SDK is synchronous only and the TypeScript SDK must be used for concurrency

### Q10

Which of the following is an example of **large-scale** refactoring in a Claude application, as the domain distinguishes it from small-scale refactoring?

A. Tightening a vague tool description so Claude stops calling the wrong tool
B. Splitting one over-broad tool into two narrower ones
C. Renaming a few variables in the request-construction helper
D. Migrating a workflow architecture to an agent architecture because requirements shifted from predictable to open-ended

### Q11

A prompt was developed and refined inside a claude.ai Project, where a project-level instruction set kept Claude's tone and output format consistent. The team now rebuilds the same feature as a backend service against the SDK. What has to change?

A. Nothing — Project instructions are stored on the account and apply to API traffic from the same organization
B. The Project instructions have to be re-expressed as an explicit `system` prompt the application sends on every request, since API persistence is entirely the application's responsibility
C. The Project must be exported to a CLAUDE.md file, which the SDK discovers automatically
D. The feature must stay on claude.ai, because output-format consistency isn't achievable over the API

### Q12

An application retrieves supplier documents and passes them to Claude alongside the user's own question. When should the team decide which of those two content streams Claude is allowed to treat as instruction-bearing?

A. When the message flow is architected, as a design decision about content boundaries
B. After the first incident, when there's evidence about which documents are actually risky
C. At the security review, since content boundaries are a compliance artifact rather than a design one
D. Never explicitly — the model distinguishes retrieved content from user instructions on its own

### Q13

A team has built a set of skills, hooks, and subagents that three separate project repositories all need. Currently each repo has its own copy in `.claude/`. What does the plugin/marketplace distinction offer here?

A. Nothing — `.claude/` directory contents cannot be shared between repositories by any mechanism
B. Copying the `.claude/` directory into a shared git submodule is the only supported sharing mechanism
C. Bundling the components as a plugin makes them one installable, versioned unit, and publishing it through a marketplace lets every project install it — leaving genuinely project-local settings in each repo's own configuration
D. Registering each skill individually with the Messages API, after which all three repos inherit them automatically

### Q14

An organization's IT team needs a tool-permission rule that no individual developer can weaken on their own machine. Which configuration scope achieves that?

A. The project-scoped `.claude/settings.json`, because it's committed and reviewed
B. The user-scoped `~/.claude/settings.json`, because it applies to every project on the machine
C. The local `.claude/settings.local.json`, because gitignored files can't be edited by tooling
D. Enterprise/managed settings, which sit above every other scope and cannot be overridden by user or project files

### Q15

A production deployment pins `claude-haiku-4-5-20251001`. A teammate argues that newer Claude 4.6-generation IDs "aren't really pinned" because they carry no date suffix. What's correct?

A. From the 4.6 generation onward the model ID alone identifies a fixed snapshot — the format changed, the pinning didn't
B. The teammate is right: dateless IDs behave as aliases and resolve to the current recommended version
C. Dateless IDs are only valid on Bedrock and Vertex, not on the first-party API
D. Pinning stopped being necessary from 4.6 onward because behavior is now guaranteed stable across versions

---

### Answer Key and Explanations

#### Q1 — Answer: C

- **Why C is correct:** Residency is a non-functional constraint on where processing may happen — it isn't stated as something the system *does*, and it's derived from the regulation the customer operates under.
- **Why not A:** Classifying into queues is a checkable behavior the system performs — a functional requirement.
- **Why not B:** Drafting a cited response is likewise something the system does.
- **Why not D:** A human-approval rule constrains system behavior, which still makes it functional; it's exactly the kind of line that becomes an eval case.
- **Difficulty:** Easy
- **Tag:** `apps.requirements/functional-vs-infrastructure`
- **Revise:** `2_applications_and_integration.md` → Understanding Requirements

#### Q2 — Answer: D

- **Why D is correct:** A business problem is not yet a requirement. The functional requirements have to be made specific enough to check, and the four infrastructure dimensions — latency, scale, residency, identity — have to be derived, because the brief won't state them.
- **Why not A:** Reversing the order is the documented mistake: platform chosen on familiarity, requirements discovered later, integration rebuilt.
- **Why not B:** Model selection is downstream of knowing what the system must do, and is decided by eval evidence rather than an upfront bake-off.
- **Why not C:** Evals are built from requirements; they can't precede them.
- **Difficulty:** Medium
- **Tag:** `apps.requirements/deriving-from-business-problem`
- **Revise:** `2_applications_and_integration.md` → Understanding Requirements

#### Q3 — Answer: B

- **Why B is correct:** Infrastructure constraints belong in the requirements phase, and the gate between design and build exists precisely to refuse progress until the chosen platform satisfies them. Discovering it at review is the expensive-by-definition case.
- **Why not A:** An eval measures output quality; it can't tell you where inference physically runs.
- **Why not C:** Residency requirements are gathered during scoping — a conversation early versus a rebuild late.
- **Why not D:** Building on multiple platforms multiplies the work without addressing the missing requirement.
- **Difficulty:** Medium
- **Tag:** `apps.lifecycle/gates`
- **Revise:** `2_applications_and_integration.md` → Systems Life Cycle

#### Q4 — Answer: A

- **Why A is correct:** The seven phases run requirements, design, build, test, deploy, operate, iterate — with model-specific work mapped onto each, and a gate at every transition. Knowing the order is what lets you say a decision was made in the wrong phase, which is why discovering a residency constraint at the deploy gate is expensive.
- **Why not B:** Design can't precede requirements, and testing after deployment inverts the gate that protects production.
- **Why not C:** Design sits before build, not after testing.
- **Why not D:** Building before requirements exist is the mistake the phase order exists to prevent.
- **Difficulty:** Easy
- **Tag:** `apps.lifecycle/phases`
- **Revise:** `2_applications_and_integration.md` → Systems Life Cycle

#### Q5 — Answer: D

- **Why D is correct:** The Messages API is stateless per request. The `messages` array is the conversation, your application owns it, and it grows with every turn you append.
- **Why not A:** There's no server-side conversation store on the raw API; session features layered on top (like the Agent SDK's session store) are a separate thing you opt into.
- **Why not B:** The API doesn't retain any turns for you.
- **Why not C:** The API key identifies the caller for auth and billing; it carries no conversation state.
- **Difficulty:** Easy
- **Tag:** `apps.api-mechanics/statelessness`
- **Revise:** `2_applications_and_integration.md` → Messages, tools, and the request/response cycle

#### Q6 — Answer: C

- **Why C is correct:** In a streamed response the tool's input JSON accumulates across multiple `content_block_delta` events. The block isn't complete — and isn't safe to act on — until the stream closes and the accumulated `input_json` parses.
- **Why not A:** The name arrives early but the arguments don't; executing then means executing with incomplete input.
- **Why not B:** Deltas carry arbitrary fragments of the JSON, not a complete-then-optional structure.
- **Why not D:** Streaming responses absolutely can contain tool calls; handling them is the extra work streaming adds.
- **Difficulty:** Medium
- **Tag:** `apps.api-mechanics/streaming-tool-use`
- **Revise:** `2_applications_and_integration.md` → Streaming with tool use

#### Q7 — Answer: A

- **Why A is correct:** PDFs are supplied as a `document` block with the same three source types as images (`base64`, `url`, `file_id`), plus optional `title` and `context` fields. Token-cost and Files API reuse mechanics carry over unchanged.
- **Why not B:** The block type is `document`, not `image` with a PDF media type.
- **Why not C:** Client-side extraction is an option you might choose, but it isn't required — PDFs are natively supported.
- **Why not D:** Document content goes in as a content block; it doesn't need a tool round-trip.
- **Difficulty:** Easy
- **Tag:** `apps.api-mechanics/vision-documents`
- **Revise:** `2_applications_and_integration.md` → Vision

#### Q8 — Answer: B

- **Why B is correct:** Claude views images in 28×28 patches: ⌈1400/28⌉ = 50 across, ⌈900/28⌉ = 33 down, so 50 × 33 ≈ 1,650 visual tokens. The point of the calculation is to run it against a realistic production image while a resize is still a ten-minute change.
- **Why not A:** That undercounts by roughly a factor of four and would leave the context budget wrong in production.
- **Why not C:** Cost scales with dimensions; there's no flat per-image rate.
- **Why not D:** Visual tokens draw on the same context budget as everything else.
- **Difficulty:** Hard
- **Tag:** `apps.api-mechanics/image-token-cost`
- **Revise:** `2_applications_and_integration.md` → Vision

#### Q9 — Answer: C

- **Why C is correct:** Async buys concurrency — your thread isn't blocked while requests are in flight — but each request still takes as long as it takes, at the same price.
- **Why not A:** There is no latency advantage for async callers.
- **Why not B:** Concurrency is not batching; the Message Batches API is a separate submission model with its own pricing.
- **Why not D:** Python exposes `AsyncAnthropic`; the TypeScript client is Promise-based by default with no separate async class.
- **Difficulty:** Medium
- **Tag:** `apps.swe/async`
- **Revise:** `2_applications_and_integration.md` → Software Engineering Foundations

#### Q10 — Answer: D

- **Why D is correct:** Large-scale refactoring is architectural: moving between workflow and agent structures as the requirements change shape.
- **Why not A:** Tightening a tool description is the canonical small-scale example.
- **Why not B:** Splitting an over-broad tool into two narrower ones is also explicitly small-scale.
- **Why not C:** Variable renaming is ordinary code hygiene, not the distinction being drawn.
- **Difficulty:** Easy
- **Tag:** `apps.swe/refactoring`
- **Revise:** `2_applications_and_integration.md` → Software Engineering Foundations

#### Q11 — Answer: B

- **Why B is correct:** Persistent instructions come from a different place in every interface. Projects and custom instructions are a claude.ai/Desktop mechanism; over the API the only persistence is what your application puts in `system` on each request.
- **Why not A:** Project instructions are workspace-scoped in that product surface and don't attach to API traffic.
- **Why not C:** CLAUDE.md is a Claude Code mechanism and isn't read by the SDK unless filesystem setting sources are explicitly enabled — and it isn't an export target for Projects.
- **Why not D:** Output consistency over the API is achievable; it's built with a system prompt, output constraints, and structured outputs.
- **Difficulty:** Medium
- **Tag:** `apps.design/interface-instruction-hierarchy`
- **Revise:** `2_applications_and_integration.md` → How Claude interprets instructions across interfaces

#### Q12 — Answer: A

- **Why A is correct:** Deciding what Claude may treat as instruction-bearing versus inert data is a content-boundary decision made when the message flow is architected — the same isolation discipline as injection defense, arriving here as a design concern rather than a patch.
- **Why not B:** Waiting for an incident means the boundary is missing precisely when it's needed.
- **Why not C:** A security reviewer will ask about it, but the decision is made at design time.
- **Why not D:** The model reads its context as one undifferentiated token stream and has no structural marker separating trusted instructions from retrieved content.
- **Difficulty:** Hard
- **Tag:** `apps.design/content-boundaries`
- **Revise:** `2_applications_and_integration.md` → Content boundaries

#### Q13 — Answer: C

- **Why C is correct:** A plugin bundles commands, agents, skills, and hooks into one installable unit described by `.claude-plugin/plugin.json`, and a marketplace is a repository listing plugins with their sources. The design judgment is what belongs in the shared plugin versus what stays project-local.
- **Why not A:** Sharing is exactly what plugins and marketplaces exist for.
- **Why not B:** A submodule might work mechanically but isn't the supported distribution and installation mechanism, and it doesn't handle namespacing or dependency resolution.
- **Why not D:** Skills aren't registered globally with the Messages API in a way that back-fills three repositories' local configuration.
- **Difficulty:** Medium
- **Tag:** `apps.design/plugin-management`
- **Revise:** `2_applications_and_integration.md` → Plugin management

#### Q14 — Answer: D

- **Why D is correct:** Enterprise/managed settings are admin-set and cannot be overridden by users or project files, which is what makes them the durable control for org-wide security rules.
- **Why not A:** A committed project file can be overridden locally by the developer working in that repo.
- **Why not B:** User scope is the developer's own preferences, which they can change at will.
- **Why not C:** Local settings are the *most* personal scope, not the most protected.
- **Difficulty:** Medium
- **Tag:** `apps.config/settings-scopes`
- **Revise:** `2_applications_and_integration.md` → Configuration Management

#### Q15 — Answer: A

- **Why A is correct:** For Claude 4.6 and later the model ID alone pins a specific snapshot — the format lost its date suffix but not its fixity. Earlier models need the ID plus a date.
- **Why not B:** Aliases like `opus` or `sonnet` are the moving targets; a generation-4.6 full model ID is not an alias.
- **Why not C:** The dateless format isn't a platform-specific quirk; platform differences are about ID prefixes and retirement schedules.
- **Why not D:** Pinning is exactly what protects production from an unannounced behavior shift, which is why promotions are gated on the eval suite.
- **Difficulty:** Medium
- **Tag:** `apps.config/model-pinning`
- **Revise:** `2_applications_and_integration.md` → Version pinning

---

## Section C — Score and Analysis

### Score

| | |
|---|---|
| Correct | ___ / 15 |
| Percentage | ___ % |
| Difficulty level run | L2 Applied |

| Band | Reading |
|---|---|
| 13–15 (87%+) | Strong on the biggest domain. Move up a level next session. |
| 10–12 (67–80%) | Solid but not safe on a third of the exam. Hold level, clear the tags below. |
| 8–9 (53–60%) | Re-read `2_applications_and_integration.md` before continuing, then repeat this session at L1. |
| Below 8 | Repeat at L1 with expanded explanations. Don't move to session 2 yet — this domain is worth more than the next two combined. |

### Weak-area map

Log the tag for every question you missed in [`../progress_tracker.md`](../progress_tracker.md).

| Missed | Tag | Revise |
|---|---|---|
| Q1, Q2 | `apps.requirements` | `2_applications_and_integration.md` → Understanding Requirements |
| Q3, Q4 | `apps.lifecycle` | `2_applications_and_integration.md` → Systems Life Cycle |
| Q5–Q8 | `apps.api-mechanics` | `2_applications_and_integration.md` → Claude API Mechanics |
| Q9, Q10 | `apps.swe` | `2_applications_and_integration.md` → Software Engineering Foundations |
| Q11, Q12, Q13 | `apps.design` | `2_applications_and_integration.md` → Claude Application Design |
| Q14, Q15 | `apps.config` | `2_applications_and_integration.md` → Configuration Management |

Two or more misses inside one tag means that skill, not the domain, is the thing to revise. Applications and Integration is six fairly independent skills wearing one domain label.

### Recommended next steps

1. Re-read the sections behind every tag you missed — the specific subsection, not the whole file.
2. If you missed anything in `apps.api-mechanics`, also work through the cheat sheet's Batch API, image-cost, and error-code blocks; API mechanics questions cluster in the mock exams.
3. Update the tracker: score, level, and next level per the difficulty rule.
4. Take **Mock Exam 1** only after sessions 1–4.

**Next domain or repeat this one?**

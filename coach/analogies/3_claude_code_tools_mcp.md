# Chapter 3 by Analogy — The Renovation Contractor

A companion to [`3_claude_code_tools_mcp.md`](../../3_claude_code_tools_mcp.md) (Domains 3 and 8, 13.7% of the exam combined). The chapter is four topics that look unrelated on a first read — Claude Code operation, tool implementation, MCP servers, and the four-way customization choice. One analogy holds all four together, which is what makes the chapter memorable instead of a list of flags to cram.

**The setup:** you own a building. You hire an extremely capable contractor to work on it. The contractor is fast, reads well, and follows written instructions — but arrives with no memory of yesterday, cannot see inside any machine they operate, and will do exactly what the site's paperwork tells them to do, including when the paperwork is wrong.

Everything in this chapter is an answer to one of four questions about that arrangement:

| The question | The chapter's topic | Weight |
|---|---|---|
| What is the contractor allowed to touch, and who says so? | Claude Code Operation | 3.1% |
| How do work orders get written, executed, and filed? | Tool Implementation | 4.4% |
| Who owns the machines and utilities the crew calls on? | MCP Server Development | 2.1% |
| Which of the four ways of extending the crew do I reach for? | Agentic Customization | 4.1% |

---

## Part 1 — Claude Code Operation: the badge, the notice board, and the turnstile

### Walk the site before swinging the hammer

A good contractor doesn't demolish on arrival. They walk the site and read the drawings (**explore**), write a scope of work describing what they intend to change (**plan**), and only then start work (**code**). Two payoffs: fewer wrong assumptions, and a written scope you can reject before anything is irreversible.

`plan` mode is the formal version of "survey only" — it holds the contractor in the explore phase and blocks every edit and command until you approve the plan. That is the hook between the workflow and the permissions system: the mode enforces the phase.

### The six badges

Permission modes are the badge you issue. Each one trades oversight for speed differently — and the exam tests them individually, so learn what each badge opens rather than ranking them "safe to unsafe."

| Badge | What it opens without asking | What it still stops at | When you'd issue it |
|---|---|---|---|
| `default` | Looking at any room | Every edit and every shell command | An unfamiliar building. Safe, slow. |
| `acceptEdits` | Working freely inside the apartment under renovation — edits plus ordinary tools (`mkdir`, `touch`, `rm`, `rmdir`, `mv`, `cp`, `sed`) **within the working directory** | Anything outside that apartment, protected paths, other shell commands | Trusted local work — but not if the crew must run arbitrary scripts |
| `plan` | Surveying and proposing | All work, until you approve the plan | Sensitive or unfamiliar code |
| `auto` | Everything, but a site supervisor reviews each action first | Production deploys and migrations, mass deletes, credential exfiltration, force-push to main | Fewer interruptions with a review layer intact. Research preview; reduces prompts, doesn't guarantee safety. |
| `dontAsk` | Only the pre-approved work list, plus looking | **Everything off the list is refused outright** — no queue, no confirmation | Locked-down unattended runs (CI), *not* local friction relief |
| `bypassPermissions` | Everything. No prompts, no checks. | Only the truly catastrophic (`rm -rf /`, `rm -rf ~`) | A mock-up building only — an isolated container or VM. Uniquely also skips the protected-path guard every other mode keeps. |

The two most confusable badges are `dontAsk` and `bypassPermissions`, and the analogy separates them cleanly. `dontAsk` is a **short approved work list with a locked gate** — off-list means denied, which is why it suits an unattended night shift. `bypassPermissions` is a **master key with the alarms switched off** — nothing is denied, which is why it belongs nowhere near an occupied building.

**The incident, in the analogy:** after three quiet days, the prompts felt like friction, so the master key came out for a "routine" cleanup. The demolition order's pattern matched the apartment under renovation *and* the room holding the building's electrical panel — production deployment config. With no prompt, nothing caught it. In `default` or `acceptEdits`, running the script would itself have prompted first.

The lesson generalizes past this one story: **a bypass silences the prompts you didn't know you needed, not just the ones you find annoying.** Padlock the panel room with a deny rule *before* issuing any key, and if the goal is genuinely just fewer prompts, `auto` gives you a supervisor instead of removing supervision.

### Where a human must still look

Badges answer "what can happen without asking." A separate question is "where must a person look anyway," and the deciding factor is **worst-case cost**, not confidence.

Repainting a wall is reversible — no gate needed, which is exactly what `acceptEdits` is for. Knocking through into the neighbouring unit, or anything hard to undo, needs a gate: either a deny rule that refuses deterministically, or `default`/`plan` surfacing it for a decision. And for the parts of the building your team has explicitly marked sensitive, **the contractor is never the only gate** — a person reviews before merge, no matter how confident the crew's own inspection sounds.

### Who posts the rules

Rules come from four places, and they don't carry equal authority:

| Whose rules | Where they live | Who they bind |
|---|---|---|
| Yours, personally | `~/.claude/settings.json` | Every project on your machine |
| The building's, posted publicly | `.claude/settings.json`, committed | Everyone who clones the repo |
| Yours, privately, for this building | `.claude/settings.local.json`, gitignored | Just you, just here |
| The city fire code | `managed-settings.json`, admin-set | The whole org — and **no one on site can override it** |

One rule outranks the layering entirely: **a prohibition beats a permission.** A deny rule wins over an allow rule regardless of mode, which makes an enterprise-level deny the most durable control available — it survives an individual developer, and it applies even under a bypass. (The chapter's table lists these four files; the full precedence chain in `2_applications_and_integration.md` adds CLI flags as a fifth scope, and carries the exception that permissions *accumulate* across scopes rather than replacing each other.)

### Four mechanisms that are constantly confused for each other

This is the highest-value distinction in the whole chapter, because all four look like "ways to tell Claude what to do" and only one of them actually *enforces* anything.

- **CLAUDE.md is the notice board at the entrance.** Read in full, every shift, unconditionally. `/init` drafts one from the building itself — check it before trusting it. Its failure mode is **size**: the notice board that grows to 847 lines still contains the rule "never enter the token vault," but that rule is now one line among 847, and the crew walked into the vault anyway. Nothing was missing; it was diluted. Keep it to constraints that change behavior and hold the line around a few hundred lines.

- **Rules files are signs posted for specific rooms** (`.claude/rules/`). The critical detail: **which room a sign applies to is written in the sign's own header** — a `paths` glob in the YAML frontmatter — **not decided by where you nail it up.** A rules file with no `paths` field loads unconditionally at the same priority as CLAUDE.md no matter which subdirectory it sits in. This is what keeps "all SQL in the database module needs an explicit transaction boundary" out of the notice board, where it would be noise for everyone not touching SQL.

- **Hooks are the turnstile.** Not a sign asking politely — a mechanism that runs **your script** at a fixed point in the lifecycle. That is the whole difference between a guardrail and a convention. `PreToolUse` inspects before a tool runs and can **block with exit code 2**, writing the reason to stderr where the agent reads it as feedback. `PostToolUse` can't block but is the right place for formatting, tests, and audit logging. The rest: `UserPromptSubmit` (inject or validate before the model sees a prompt), `Stop` (end-of-turn), `Notification` (a permission request, or 60 seconds idle), `SessionStart`, `SessionEnd`. A hook protecting the panel room fires at *every* tool call, in *every* session, under *every* permission mode. The notice board can be followed inconsistently as it grows; the turnstile cannot be skipped.

- **Subagents are specialist subcontractors who arrive in a clean van.** No inherited conversation, files, or state. The detail worth memorizing: the built-in **`Explore` and `Plan` subagents skip the notice board and the site log entirely** — no CLAUDE.md, no git status, traded away for speed — while `general-purpose` loads both. When a project rule mysteriously fails to apply to delegated work, that's usually the reason. Custom subagents also don't inherit skills; one that needs a specific procedure card must name it in its frontmatter.

The exam's favourite version of this distinction: *a rule keeps getting violated even though it's written down — what do you reach for?* A bigger notice board is the wrong answer. A turnstile is the right one.

### The same procedure card in four different workplaces

A **skill** is a laminated procedure card (`SKILL.md`) — written once, readable by the crew on demand. What trips people up is that the same card behaves differently depending on *where the crew is standing when they read it*:

| Workplace | How the card reaches them | Where the steps actually happen | The trap |
|---|---|---|---|
| **Claude Code** | Found in `.claude/skills` on disk, by description match or explicit call | Your site, your files, under the active badge | Governed by the settings layer, like everything else local |
| **Messages API** | Sent along with the request, run in Anthropic's code-execution container (needs the code-execution and skills beta headers) | The contractor's **offsite workshop — not your building** | A card that says "go to the basement and read the meter" fails silently. There is no basement there. |
| **Agent SDK** | Loaded by your own dispatched crew, gated by `settingSources` / `setting_sources` — **set it explicitly, never rely on a default** | Your environment, once filesystem sources are enabled | The classic surprise: a card that worked in Claude Code does nothing, because nobody told the crew where the card rack is |
| **Managed Agents** | Registered centrally as an API resource listing model, prompt, tools, MCP, and skills | An Anthropic-provisioned sandbox | Public beta (`managed-agents-2026-04-01`); sessions are stored server-side, and it is **not currently eligible for Zero Data Retention or a HIPAA BAA** |

Three portability rules follow directly: write the **description** as the matching criterion, since a vague one fails to load correctly in *every* runtime rather than just some; never assume a local filesystem or local tools exist in the card body; and remember subagents don't inherit cards in any runtime.

Related: skills are now the recommended format for both explicit (`/skill-name`) and automatic invocation, with `.claude/commands/` surviving as legacy. `disable-model-invocation: true` is how you make a card explicit-only — the workflow nobody should trigger by accident.

### The crate and the catalog

A **plugin** is a shipping crate that bundles procedure cards, turnstiles, subcontractor contracts, and utility hookups into one installable unit, published through a **marketplace** (a catalog; Anthropic's is available by default, and you add a third-party one with `/plugin marketplace add <owner/repo>`). Crate commands are **automatically namespaced by the crate name** — `/payments:run-tests` — which is why two crates can ship a same-named command without colliding, and why renaming a crate renames every command in it. Enterprise admins gate which catalogs anyone may add with a managed allowlist, and push a catalog to everyone with `extraKnownMarketplaces`.

**The incident:** the crate installed cleanly on every machine and then ran on exactly one — the author's. A card inside it pointed at `/Users/alexmorgan/projects/deploy-utils/validate.sh`, an address that existed in one garage only, plus an environment variable the author had set locally and never documented. **Install and execution are different events**: install copies the crate, execution resolves every address against whichever building it's standing in. Use `$CLAUDE_PROJECT_DIR` for scripts kept in the project and `${CLAUDE_PLUGIN_ROOT}` for scripts bundled in the crate, document every variable, and test the install on a clean machine.

### The night shift

`claude -p` is the unattended shift: non-interactive, exit `0` on success and non-zero on failure, built for CI. `--bare` means **"come with just your own hands"** — skip auto-discovery of hooks, skills, plugins, MCP servers, auto memory, and CLAUDE.md, for a faster and genuinely deterministic run. The trade is that it also gives up OAuth and keychain reads, so you must hand over the key yourself via `ANTHROPIC_API_KEY`.

Output shape is a separate dial: `--output-format stream-json` (with `--verbose`, and `--include-partial-messages` for token-level deltas) emits newline-delimited events, versus `text` for plain output or `json` for a single structured result with cost and session metadata.

---

## Part 2 — Tool Implementation: work orders and completion slips

### The contractor never operates the machine

You hand the crew a catalog of equipment. Each entry has a **name**, a **label** describing what it's for, and a **form** listing which fields are required. The crew never sees inside a machine — only the label and whatever result comes back.

Here is the part people get wrong: **the contractor doesn't run the equipment.** They write a work order and hand it to you. You operate the machine and return a completion slip. Claude issues the `tool_use` block; your application executes it and returns the `tool_result`. The loop is not automatic.

And because selection is driven by the **label**, writing tool descriptions is a design task, not documentation. With the default `tool_choice: {"type": "auto"}`, a tool is called only when the request matches its described capability and the answer isn't already in context. When selection fails systematically, the fix belongs in the schema — not in a prompt patch.

### The front desk checks the paperwork before any work starts

Every work order must come back with a matching completion slip carrying **the same ticket number**, in the **immediately following** exchange. The front desk rejects the whole packet if a slip is missing, a number doesn't match, or the turns arrive out of order — and it checks **before** any work begins, which is why no amount of polite instruction can recover from a structural mismatch. This is request validation, not model behavior.

| Block | Who files it | The rule that bites |
|---|---|---|
| `text` | Assistant | Can sit alongside `tool_use` in the same turn. **Keep the whole content array, including the text block,** when appending that turn to history — dropping the note and filing only the order corrupts context for later turns. |
| `tool_use` | Assistant | Must be answered by a `tool_result` in the immediately following user turn, matched by ID. |
| `tool_result` | User | The `tool_use_id` must match **exactly** — that's how a result is reconnected to its call when one turn issued several orders at once. Optional `is_error: true`. |
| `thinking` | Assistant (extended thinking) | A sealed notebook with a tamper seal. Hand it back **unchanged** — any edit, even summarizing it, breaks the signature and the request is rejected. Redacted blocks follow the same rule even though you can't read them. |

### Two machines labelled "for finding things"

The chapter's tool-selection incident is the clearest illustration of why the label is the design surface. Two machines: `search_docs`, labelled "use this to find information about the product," and `get_context_summary`, labelled "use this to retrieve relevant information from the current session." Different names, but from the crew's side both labels say *find information*. On ambiguous requests they reached for the wrong one, repeatedly.

The fix has a fixed shape: **write the label in two parts — when to use it, and when not to.** Add an exclusion sentence to each. If two labels genuinely can't be separated even with exclusions, stop lengthening them and **weld the two machines into one with a mode switch** — a single tool with a `type` parameter. One caveat worth remembering: an exclusion that refers to "earlier in this conversation" only works while the full history is actually being sent. Truncate the history and the exclusion logic silently stops working.

On the form itself: mark a field `required` only when the order is meaningless without it. **Marking everything required forces the crew to invent measurements they never took** — that's where fabricated arguments come from. Leave fields optional when they have sensible defaults, or when their absence carries meaning.

### Scheduling the work

Independent orders go out together — current models issue multiple `tool_use` blocks in one turn by default, and the matching slips come back together, paired by ID. When one order's result is the *input* to the next, they must be **separate turns**, because the second order can't be written correctly until the first slip is in hand. `disable_parallel_tool_use` forces strictly one at a time when a workflow demands it.

Concurrency is decided by whether the work changes the building: **read-only inspections run concurrently; anything state-mutating (`Edit`, `Write`, `Bash`) runs sequentially**, because overlapping mutations make the order of effects unpredictable. A custom tool opts into concurrency by declaring `readOnlyHint` in its annotations.

Who executes also varies. **Client-side dispatch**: your application runs the logic and returns the slip — the model for custom in-process tools. **Harness dispatch**: Claude Code or the Agent SDK loop executes it for you — how built-in and MCP tools work, where you configure access rather than execution. Approval is layered on top: auto-approved via `allowed_tools`, gated by a `canUseTool` callback, or refused via `disallowed_tools`. MCP adds finer grain — a rule can target one tool on one server, `mcp__server__tool`, so you can allow `mcp__github__create_issue` while every other GitHub tool still prompts. **A deny on a single tool overrides an allow on the whole server.**

Finally, keep the catalog small and non-overlapping. Every entry costs context on every request, and overlapping labels raise the odds of the wrong pick. Scope a subcontractor's equipment to the job.

---

## Part 3 — MCP: the utility company

### What it actually solves

Three buildings each need electrical work. Without a utility company, each one hires its own electrician and maintains its own wiring diagrams — the same integration, built and maintained three times.

MCP is the utility company. It lifts the capability out of any single application and turns it into a standalone process — an **MCP server** — that any **MCP client** (Claude Code has one built in) connects to and discovers tools from via the `ListToolsRequest` handshake. Build it once; every client that connects gets it without reimplementing anything.

The consequence that surprises people: **from the crew's point of view, a utility-provided machine is indistinguishable from one you own.** Same description-based routing, same paperwork rules. The only thing that differs is who wrote and maintains the definition.

### Three things a utility can offer

Not everything a server exposes is a machine to operate:

| Offering | What it is | Reach for it when |
|---|---|---|
| **Tools** | Actions the crew can call | Something needs *doing* |
| **Resources** | Read-only data delivered by address, placed straight into context with no work order | Known data should be present from the start of the turn, and delivery is cheaper and more predictable than a round-trip. *Client support varies — verify before relying on it.* |
| **Prompts** | The utility's own pre-written instruction templates, invoked by name | Exact wording matters and every client should get the same vetted text, maintained in one place |

### How you reach them, and who has the number

**Transport is a fact about where the server runs, not a style choice.** `stdio` is a crew member in your own basement — same machine, fine for personal scripts and dev, and **cannot be shared across a team**. `HTTP` is a phone number anyone can call, and it's the recommendation for anything not local. `SSE` is the old fax line: legacy, superseded, treat as historical if you find it in a config.

Who loads a server mirrors the settings pattern: `~/.claude.json` for just you on just this project, personal settings for you everywhere, `.mcp.json` committed for the whole team on clone, and managed settings for the org. One trap in the committed case — **a committed stdio server still spawns a local subprocess on each teammate's machine**, so every one of them needs the runtime installed (Node, for an `npx`-launched server). Committing the config doesn't ship the basement equipment.

### Desk space and photocopies

Every machine's manual left open on the site desk consumes room before anyone has done a thing. So **MCP tool schemas are deferred by default** and loaded only when a task calls for them, with an opt-in mode that lays them all out upfront when they fit within roughly **10% of the context window**, falling back to deferred past that. The API MCP Connector gives you the dials directly: an `mcp_toolset` object carrying a `default_config` for every tool on a server, overridable per tool via `configs`, where **`defer_loading`** delays a definition until needed and **`enabled`** switches individual tools on and off so you can register a whole server but expose a subset. It needs the `mcp-client-2025-11-20` beta header, and it only supports **remote HTTP servers** — a local stdio server has to go through Claude Desktop or Claude Code.

Caching is the photocopy of the unchanging front section. Requests process in a fixed order — **tools → system prompt → messages** — so a `cache_control` breakpoint (type `ephemeral`) placed after the tool definitions caches them while messages stay dynamic. Up to **4 breakpoints per request**, a **5-minute** TTL from last read (resetting on each read) or **1 hour** via `ttl: "1h"`, and nothing caches below the **minimum token threshold (1,024 tokens on most current models)**. A single changed character before the breakpoint voids the copy and you pay for a fresh write.

Worth connecting to the same theme: **retrieval** is this problem generalized. Classical RAG builds the index up front and matches against it at request time; agentic search skips the index and has the model search and fetch live at the moment of need — which is exactly what MCP tool search does. Both end up generating from a relevant slice; the difference is *when* the relevant-slice decision gets made, at index-build time or at query time.

### Who the crew signs in as

| Situation | Pattern | The mechanism |
|---|---|---|
| Remote service where **the user's identity matters** (SaaS, e.g. Linear) | OAuth | Server returns 401, a browser sign-in opens, the token is issued and stored automatically — no credential copying |
| Remote service where **a service account acts** (internal API) | API key in an environment variable | Identifies the service, never committed, injected by the runtime such as a CI secret |
| Local filesystem access | No network auth at all | stdio; the security boundary *is* the filesystem permission model, and a deny rule is the governance layer |

Secret handling is three practices, each closing one specific leak: **separation** (the config holds a reference, the value lives in the environment or a secret store), **placement** (an environment variable for something local and short-lived; a secret store — centralized, audit-logged, one rotation updating every consumer — for anything shared), and **rotation** (on a schedule, and immediately on any suspected exposure).

**The incident:** a key written inline in `.mcp.json` "temporarily" during setup got committed when the config was shared. Within 48 hours it existed in five places: the author's machine, repo history, three clones, and a CI runner. **Overwriting the file in a later commit does not remove it from history** — rotation was mandatory, and rotation broke two other services configured with the same key. The fix is the two-halves pattern the exam likes: reference `${WAREHOUSE_MCP_TOKEN}` rather than the literal, *and* back the written convention with a `PreToolUse` hook that inspects edits to `.mcp.json` for credential-shaped patterns and blocks them. The convention states the intent; the turnstile enforces it regardless of what the model decides.

**The other incident, and it's a good one:** an OAuth-authenticated connection passed every staging test and failed completely in production with a redirect-URI mismatch. Not a code defect — **OAuth redirect URIs are registered per host**, and the production hostname was never registered. Regulated customers frequently require *separate* OAuth app registrations per environment, not merely an extra redirect URI. That step belongs in the deployment checklist.

What regulated deployment adds beyond "it works" is four checkable things: identity auditability (who is the model acting as), data residency (an endpoint pinned to a region plus a matching platform deployment gives an answer you can show a reviewer), configuration lock (managed settings a developer can't override), and access logging (a `PostToolUse` hook writing every tool call to an audit store — it fires deterministically, unlike a log the model might skip).

---

## Part 4 — The four-way choice

The decision the blueprint calls out by name. In the analogy: equipment already on the truck, a jig you fabricate for one job, a laminated procedure card, or a utility company.

| | **Built-in tools** | **Custom tools** | **Skills** | **MCP servers** |
|---|---|---|---|---|
| In the analogy | Already on the truck | A jig you fabricate for this job | A laminated procedure card | The utility company |
| What it is | Pre-built capabilities shipped with Claude Code / the Agent SDK | Functions you define with a schema, for one app | Portable procedural knowledge (`SKILL.md`) read on demand | An independently deployed server exposing tools, resources, and prompts |
| Reach for it when | The task is generic and the built-in already does it | One app needs one specific internal function, no reuse elsewhere | A repeatable process or judgment call, needing no new live data | Multiple apps need the same live data or action, maintained independently |
| Wrong fit when | Custom business logic or a proprietary integration is needed | The same capability must be shared across unrelated apps | The task is really about fetching live external data | Overkill for a single one-off, app-specific function |

The sentence that resolves most exam questions in this area: **MCP connects Claude to data; Skills teach Claude what to do with it.** A card reading "check the latest deployment status" cannot reach the deployment system on its own — something has to be plumbed in underneath. And the layers are **additive, never substitutive**: built-in tools remain available no matter what you add. A real production site runs all of it at once — utilities for live external systems, jigs for app-specific functions, cards for the judgment calls that tie them together — with a **plugin** as the crate that bundles and versions the whole arrangement.

---

## Where the analogy breaks down

Worth knowing, because the exam tests the seams:

1. **The contractor has no memory between shifts.** A human crew remembers yesterday's briefing; here the notice board is genuinely re-read from scratch every session, which is why CLAUDE.md size is a live problem rather than a tidiness preference.
2. **Text found on site can redirect the crew.** A document delivered to the building can contain instructions the crew acts on — indirect prompt injection has no clean equivalent in the analogy, and it's why the trust boundary sits at every seam where outside content enters. That's Domain 7 territory (`5_eval_debugging_security.md`).
3. **The front desk validates structure, not sense.** Paperwork with perfectly matched ticket numbers passes validation while being completely wrong about the building. Structural validity and correctness are separate checks — which is what eval suites are for.
4. **The crew picks equipment by reading labels, not by understanding machines.** No human contractor is that literal. It's precisely why description writing carries the weight it does here.

---

## Self-check

Answer from the analogy first, then name the mechanism. If the analogy answer comes fast but the mechanism doesn't, the gap is terminology, not understanding — and that's the cheaper problem to fix.

1. A rule is written on the notice board, and the crew keeps breaking it anyway. What do you add, and why isn't a clearer notice enough?
2. Which badge refuses everything off the list, and which badge refuses nothing at all? Which one belongs in CI?
3. A procedure card works perfectly on your site and does nothing when the same card is used through the Agent SDK. What was never set?
4. Two machines keep getting confused for each other. What one sentence goes in each label, and what do you do if that isn't enough?
5. A completion slip comes back with a ticket number that doesn't match any order. Can a better instruction fix it? Why or why not?
6. Your team commits the utility directory so everyone gets the connection on clone. One teammate's setup still fails. What did committing the config not ship?
7. A key was written into a config sheet, then overwritten in a later commit. Is the exposure closed? What does closing it actually require, and what might break?
8. A card says "check deployment status." What has to exist underneath it, and which side of the data-versus-procedure line does each piece sit on?

**Answers:** 1. A `PreToolUse` hook — it runs your script at a fixed lifecycle point and can block with exit code 2, whereas a notice-board instruction gets diluted as the file grows and can be followed inconsistently. 2. `dontAsk` auto-denies anything off the allow list; `bypassPermissions` denies nothing but the catastrophic. `dontAsk` is the CI-appropriate one. 3. `settingSources` / `setting_sources` — never rely on its default. 4. An exclusion condition naming when *not* to call it; if the labels still can't be separated, merge the two tools into one with a `type` parameter. 5. No — `tool_use_id` pairing is validated before generation starts, so there is no prompt-level recovery. 6. The runtime. A committed stdio server spawns a local subprocess per teammate, so each needs Node or whatever the launcher requires. 7. Not closed — history retains it, so rotation is required, and rotation breaks every other consumer configured with the same key. 8. An MCP server or custom tool to reach the deployment system; MCP connects to the data, the Skill supplies the procedure, and the layers are additive.

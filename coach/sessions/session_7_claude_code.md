# Session 7 — Claude Code (3.1%)

Domain 3 of the CCDV-F blueprint, and the smallest by weight — but its content resurfaces inside Applications, Tools, and Security scenarios, so it's worth more than 3.1% of your study time.

Source: [`3_claude_code_tools_mcp.md`](../../3_claude_code_tools_mcp.md). Level: **L2 Applied**. Time: 10–15 minutes.

---

## Section A — Domain Overview

### What this domain actually tests

One skill, Claude Code Operation (3.1%): the core components (rules, skills, commands, agents, agent memory), session management, built-in and custom slash commands, headless/streaming/auto modes, the CLAUDE.md hierarchy, repository initialization, and settings.json.

### Key patterns

**Explore → plan → code.** Claude Code reads files and traces logic first, then produces a structured description of intended edits, and only then writes. `plan` mode holds the session in the explore phase, blocking edits and commands until you approve the plan.

**Six permission modes.** Know them cold; this is dense, specific, testable content:

| Mode | Auto-approves | Still gated |
|---|---|---|
| `default` | Reads only | All edits and shell commands |
| `acceptEdits` | Reads, file edits, common filesystem commands (`mkdir`, `touch`, `rm`, `mv`, `cp`, `sed`) **inside the working directory** | Anything outside the working directory, protected paths, other shell commands |
| `plan` | Reads only; researches and proposes | All edits and commands until the plan is approved |
| `auto` | Everything, but a classifier reviews each action first | Production deploys/migrations, mass deletes, credential exfiltration, force-push to main — blocked by default |
| `dontAsk` | Only pre-approved allow-listed tools plus read-only commands | Everything off the allow list is **auto-denied**, with no confirmation queue |
| `bypassPermissions` | Everything, no prompts, no safety checks | Only catastrophic commands (`rm -rf /`, `rm -rf ~`) still prompt |

Two distinctions the exam leans on: `auto` is classifier-gated and `bypassPermissions` skips evaluation entirely, and `bypassPermissions` uniquely skips the protected-path guard every other mode keeps. **A deny rule always wins over an allow rule, regardless of mode**, and an enterprise-level deny is the most durable control available.

**Settings scopes:**

| Scope | File | Applies to |
|---|---|---|
| User | `~/.claude/settings.json` | Every project on that machine |
| Project | `.claude/settings.json`, committed | Everyone who clones the repo |
| Local | `.claude/settings.local.json`, gitignored | Just you, just this project |
| Enterprise/Managed | `managed-settings.json`, admin-set | Org-wide; cannot be overridden |

Precedence runs managed > CLI > local > project > user, with one documented exception: **permissions accumulate across scopes** instead of the highest scope simply winning.

**Four mechanisms, four different jobs** — don't collapse them into one file:

- **CLAUDE.md** loads in full, every session, unconditionally. Its main failure mode is **size**: a correct rule inside an 847-line file gets diluted by the 846 other lines. Keep it to constraints that change behavior.
- **Rules files** (`.claude/rules/`) load only when Claude works with matching files, via a `paths` glob in YAML frontmatter. Scoping comes from the frontmatter, **not** from directory placement — a rules file without `paths` loads unconditionally at the same priority as CLAUDE.md, wherever it sits.
- **Hooks** run your own script at a fixed lifecycle point: `PreToolUse` (can inspect and **exit code 2 to block**, with the reason on stderr as feedback the agent sees), `PostToolUse` (can't block; right place for formatting, tests, audit logging), `UserPromptSubmit`, `Stop`, `Notification`, `SessionStart`, `SessionEnd`.
- **Subagents** get isolated context and inherit nothing. Course-specific detail: the built-in **`Explore` and `Plan` subagents skip CLAUDE.md and git status entirely** for speed, while `general-purpose` loads both — and custom subagents don't auto-inherit skills, which must be listed explicitly in frontmatter.

**Skills are the recommended format** for both explicit (`/skill-name`) and automatic (description-match) invocation; the older `.claude/commands/` directory still works but is legacy. `disable-model-invocation: true` in a skill's frontmatter makes a workflow explicit-only, never auto-triggered.

**Session modes.** `claude -p` is headless/print mode for CI, exiting 0 on success and non-zero on failure. `--bare` skips auto-discovery of hooks, skills, plugins, MCP servers, auto memory, and CLAUDE.md for deterministic CI runs — and because it trades away OAuth/keychain reads, `ANTHROPIC_API_KEY` must be supplied explicitly. `--output-format stream-json` (with `--verbose`, plus `--include-partial-messages` for token-level deltas) emits newline-delimited JSON events, versus `text` or `json`.

**Plugins** bundle skills, hooks, subagents, and MCP servers into one installable unit distributed through a marketplace. Plugin commands are **automatically namespaced** by plugin name (`/payments:run-tests`), which is why two plugins can ship the same command name — and why renaming a plugin renames every command it ships.

### Common mistakes

- **Switching to `bypassPermissions` to reduce prompt friction.** It silences the prompts you didn't anticipate needing, not just the ones annoying you — and it drops the protected-path guard. If the goal is fewer prompts, `auto` is the classifier-gated option.
- **Using `dontAsk` for local convenience.** It auto-denies anything off the allow list, which is right for CI and frustrating locally.
- **Growing CLAUDE.md indefinitely.** Every added line dilutes the rules that matter.
- **Scoping a rules file by putting it in a subdirectory.** Only the `paths` frontmatter scopes it.
- **Expecting a project rule to apply to a delegated `Explore` task.** Those built-in subagents skip CLAUDE.md.
- **Exit code 1 from a blocking hook.** Only exit 2 denies.
- **Hardcoding absolute paths in a distributed skill.** Use `$CLAUDE_PROJECT_DIR` for project scripts and `${CLAUDE_PLUGIN_ROOT}` for scripts bundled in a plugin — install success and execution success are different things.

### Real exam-style scenarios

**Scenario A.** A developer, three incident-free days into a project, switches to `bypassPermissions` for a "routine" cleanup. A glob matches files in both `/src/` and `/deploy/config/prod/`, and production config is deleted with no prompt.

The reasoning: the mode removed every checkpoint, including the protected-path guard other modes keep. In `default` mode the script invocation itself would have prompted first. The lesson the exam wants: set deny rules on sensitive paths *before* changing modes, and reach for `auto` if the actual goal is fewer prompts.

**Scenario B.** A CI job needs identical behavior on every machine and must not pick up a teammate's local hooks or a project `.mcp.json` server.

The reasoning: `--bare` skips auto-discovery of hooks, skills, plugins, MCP servers, auto memory, and CLAUDE.md — deterministic regardless of the host's local configuration. The follow-on detail that catches people: it also skips OAuth/keychain reads, so the pipeline has to supply `ANTHROPIC_API_KEY` explicitly.

---

## Section B — Questions

10 questions, four options each, single best answer.

### Q1

A developer wants Claude Code to investigate an unfamiliar codebase and propose an approach, with a guarantee that nothing is edited until they've read the proposal. Which mode, and what phase does it hold the session in?

A. `default`, which gates edits but allows shell commands
B. `dontAsk`, which auto-denies edits
C. `plan`, which holds the session in the explore phase — reads and proposals only — until the plan is approved
D. `acceptEdits`, which queues edits for later review

### Q2

Under `acceptEdits`, which of the following is auto-approved?

A. Any shell command, as long as it isn't destructive
B. Reads, file edits, and common filesystem commands like `mkdir` and `mv` **inside the working directory**
C. Edits anywhere on the filesystem, including protected paths
D. Nothing beyond reads; `acceptEdits` only removes prompts for read operations

### Q3

A team sets `dontAsk` on a developer's local session hoping to reduce prompt fatigue. What actually happens?

A. Every action is approved automatically with no evaluation
B. A classifier reviews each action and approves the safe ones
C. Behavior is identical to `acceptEdits` but also covers shell commands
D. Only pre-approved allow-listed tools and read-only commands run; everything else is auto-denied with no confirmation queue, which is why it's built for locked-down CI rather than local friction

### Q4

What distinguishes `auto` mode from `bypassPermissions`?

A. `auto` has a classifier review each action, blocking production deploys and migrations, mass deletes, credential exfiltration, and force-push to main by default, while `bypassPermissions` skips evaluation entirely
B. `auto` applies to reads only; `bypassPermissions` covers writes as well
C. They are the same mechanism under two names, retained for backward compatibility
D. `auto` requires an isolated container; `bypassPermissions` is safe on a workstation

### Q5

Which settings file carries allow/deny rules that should apply to everyone who clones a repository?

A. `~/.claude/settings.json`
B. `.claude/settings.json`, committed to the repo
C. `.claude/settings.local.json`
D. `managed-settings.json`

### Q6

A project's CLAUDE.md has grown to 847 lines. It contains a correct instruction never to touch `/legacy/tokens/`, and the agent violates it anyway. What's the diagnosis?

A. CLAUDE.md instructions are advisory and are never applied to path restrictions
B. The instruction must be phrased as a shell glob to take effect
C. Size is the failure mode: the rule is present but diluted, because a larger file makes any single instruction a smaller fraction of what loads — and a path restriction that must hold belongs in a hook, not only in prose
D. CLAUDE.md is only loaded when explicitly referenced in a prompt

### Q7

A team puts a rules file at `.claude/rules/database/sql-conventions.md` with no `paths` field in its frontmatter, expecting it to apply only when Claude works in the database module. What actually happens?

A. It loads unconditionally at the same priority as CLAUDE.md — scoping comes from the `paths` glob in frontmatter, not from directory placement
B. It never loads, because a rules file without `paths` is invalid
C. It loads only for files in `.claude/rules/database/`
D. It loads only when the file is explicitly mentioned in the prompt

### Q8

A project's CLAUDE.md convention is being ignored specifically when work is delegated to the built-in `Explore` subagent. Why?

A. Subagents receive CLAUDE.md but at lower priority than their own system prompt
B. CLAUDE.md is only loaded for the first subagent spawned in a session
C. Delegated tasks always require the convention to be repeated in the delegation prompt
D. The built-in `Explore` and `Plan` subagents skip CLAUDE.md and git status entirely for speed, while `general-purpose` loads both

### Q9

A CI pipeline runs `claude --bare -p "..."` and fails immediately with an authentication error, though the same command works interactively on a developer's machine. What's the likely cause?

A. `--bare` is incompatible with `-p` and the flags must not be combined
B. Headless mode requires `--output-format json` before authentication is attempted
C. `--bare` trades away OAuth and keychain reads along with the rest of auto-discovery, so `ANTHROPIC_API_KEY` has to be supplied explicitly in the pipeline
D. `--bare` requires a project-scoped `.claude/settings.json` to authenticate

### Q10

A team has a release-checklist workflow that should run only when someone explicitly invokes it, never triggered automatically by description matching. How is that configured, and which format should it use?

A. A skill with `disable-model-invocation: true` in its frontmatter — skills are the recommended format for both explicit and automatic invocation, and that flag makes it explicit-only
B. A file in `.claude/commands/`, since only the legacy command format supports explicit-only invocation
C. A `PreToolUse` hook, since only hooks can be triggered deterministically
D. A subagent with an empty `description` field, so nothing can match it

---

### Answer Key and Explanations

#### Q1 — Answer: C

- **Why C is correct:** `plan` mode holds Claude Code in the explore phase — reads, research, and a proposed plan only — and blocks all edits and commands until the plan is approved.
- **Why not A:** `default` auto-approves reads only and gates edits *and* shell commands, but it doesn't produce the held-in-planning behavior described.
- **Why not B:** `dontAsk` auto-denies off-list actions; it isn't a planning mode.
- **Why not D:** `acceptEdits` auto-approves edits rather than deferring them.
- **Difficulty:** Easy
- **Tag:** `cc.operation/permission-modes`
- **Revise:** `3_claude_code_tools_mcp.md` → Permission modes

#### Q2 — Answer: B

- **Why B is correct:** `acceptEdits` auto-approves reads, file edits, and common filesystem commands (`mkdir`, `touch`, `rm`, `rmdir`, `mv`, `cp`, `sed`) **inside the working directory**, while anything outside it, protected paths, and other shell commands stay gated.
- **Why not A:** Arbitrary shell commands remain gated, which is why the mode isn't appropriate when the agent must run scripts.
- **Why not C:** Protected paths and locations outside the working directory are still gated.
- **Why not D:** It goes well beyond reads.
- **Difficulty:** Medium
- **Tag:** `cc.operation/permission-modes`
- **Revise:** `3_claude_code_tools_mcp.md` → Permission modes

#### Q3 — Answer: D

- **Why D is correct:** `dontAsk` runs only pre-approved allow-listed tools plus read-only commands and auto-denies everything else with no confirmation queue — built for locked-down CI and scripts, not for reducing local friction.
- **Why not A:** That describes `bypassPermissions`.
- **Why not B:** That describes `auto`.
- **Why not C:** It isn't a superset of `acceptEdits`; it's a different, deny-by-default model.
- **Difficulty:** Medium
- **Tag:** `cc.operation/permission-modes`
- **Revise:** `3_claude_code_tools_mcp.md` → Permission modes

#### Q4 — Answer: A

- **Why A is correct:** `auto` is classifier-gated with a default block list covering production deploys and migrations, mass deletes, credential exfiltration, and force-push to main. `bypassPermissions` skips evaluation entirely.
- **Why not B:** Both cover writes; the difference is whether anything evaluates the action.
- **Why not C:** They're distinct mechanisms with different risk profiles.
- **Why not D:** It's the reverse — `bypassPermissions` is the container-only mode.
- **Difficulty:** Medium
- **Tag:** `cc.operation/permission-modes`
- **Revise:** `3_claude_code_tools_mcp.md` → Session modes

#### Q5 — Answer: B

- **Why B is correct:** Project scope is the committed `.claude/settings.json` — team-wide conventions and allow/deny rules that apply to everyone who clones the repo.
- **Why not A:** User scope is personal preferences that follow one developer across all projects.
- **Why not C:** Local settings are gitignored personal overrides.
- **Why not D:** Managed settings are admin-set org-wide controls, not repo-scoped team conventions.
- **Difficulty:** Easy
- **Tag:** `cc.operation/settings-scopes`
- **Revise:** `3_claude_code_tools_mcp.md` → Settings scope hierarchy

#### Q6 — Answer: C

- **Why C is correct:** This is the documented incident. The rule was present and correct; 846 other lines diluted its weight. CLAUDE.md should hold constraints that change behavior, and a restriction that must hold belongs in a `PreToolUse` hook, which enforces at every tool call regardless of file size or permission mode.
- **Why not A:** CLAUDE.md instructions do influence behavior — just less reliably as the file grows.
- **Why not B:** No glob syntax requirement exists for prose instructions.
- **Why not D:** CLAUDE.md loads in full, every session, unconditionally.
- **Difficulty:** Medium
- **Tag:** `cc.operation/claude-md`
- **Revise:** `3_claude_code_tools_mcp.md` → CLAUDE.md, rules files, hooks, and subagents

#### Q7 — Answer: A

- **Why A is correct:** Scoping comes from the `paths` glob in YAML frontmatter, not directory placement. Without `paths`, the file loads unconditionally at the same priority as CLAUDE.md no matter which subdirectory holds it.
- **Why not B:** It's valid — just unscoped.
- **Why not C:** Directory placement has no scoping effect.
- **Why not D:** Rules files aren't invocation-triggered.
- **Difficulty:** Medium
- **Tag:** `cc.operation/rules-files`
- **Revise:** `3_claude_code_tools_mcp.md` → Rules instruction files

#### Q8 — Answer: D

- **Why D is correct:** The built-in `Explore` and `Plan` subagents skip CLAUDE.md and git status entirely, optimized for speed; `general-purpose` loads both. This is the usual reason a project rule silently doesn't apply to a delegated task.
- **Why not A:** They don't receive it at lower priority — they don't receive it at all.
- **Why not B:** There's no first-subagent rule.
- **Why not C:** Repeating the convention is a workaround, not the explanation.
- **Difficulty:** Hard
- **Tag:** `cc.operation/subagents`
- **Revise:** `3_claude_code_tools_mcp.md` → CLAUDE.md, rules files, hooks, and subagents

#### Q9 — Answer: C

- **Why C is correct:** `--bare` skips auto-discovery of hooks, skills, plugins, MCP servers, auto memory, and CLAUDE.md, and it also trades away OAuth/keychain reads — so `ANTHROPIC_API_KEY` must be supplied explicitly.
- **Why not A:** `--bare` and `-p` are designed to be used together for CI.
- **Why not B:** Output format has no bearing on authentication.
- **Why not D:** Project settings aren't an authentication source, and `--bare` skips discovery anyway.
- **Difficulty:** Hard
- **Tag:** `cc.operation/headless-mode`
- **Revise:** `3_claude_code_tools_mcp.md` → Session modes

#### Q10 — Answer: A

- **Why A is correct:** Skills are the recommended format for both explicit (`/skill-name`) and automatic invocation, and `disable-model-invocation: true` restricts a workflow to explicit calls only.
- **Why not B:** `.claude/commands/` still works but is legacy, and it isn't required for explicit-only behavior.
- **Why not C:** Hooks fire on lifecycle events; they aren't user-invoked workflows.
- **Why not D:** An empty description is a workaround with unpredictable matching behavior, not the supported control.
- **Difficulty:** Medium
- **Tag:** `cc.operation/skills-and-commands`
- **Revise:** `3_claude_code_tools_mcp.md` → Custom commands and the skills/commands relationship

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
| 9–10 (90%+) | Strong. Move up a level next session. |
| 7–8 (70–80%) | Hold level; re-read the permission-mode table. |
| 5–6 (50–60%) | Re-read the permission modes and settings scopes, then repeat at L1. |
| Below 5 | Repeat at L1. Learn the six permission modes first — they generate more questions than anything else in this domain. |

### Weak-area map

Every question in this session tags to `cc.operation`, so track the sub-tag rather than the primary tag:

| Missed | Sub-tag | Revise |
|---|---|---|
| Q1–Q4 | `cc.operation/permission-modes` | `3_claude_code_tools_mcp.md` → Permission modes |
| Q5 | `cc.operation/settings-scopes` | `3_claude_code_tools_mcp.md` → Settings scope hierarchy |
| Q6–Q8 | `cc.operation/claude-md`, `/rules-files`, `/subagents` | `3_claude_code_tools_mcp.md` → CLAUDE.md, rules files, hooks, and subagents |
| Q9 | `cc.operation/headless-mode` | `3_claude_code_tools_mcp.md` → Session modes |
| Q10 | `cc.operation/skills-and-commands` | `3_claude_code_tools_mcp.md` → Custom commands |

### Recommended next steps

1. Write the six permission modes from memory with their auto-approve column. If you can only recall five, the missing one is usually `dontAsk`.
2. Keep three facts adjacent in memory, because they're commonly confused: a deny rule always beats an allow rule; permissions accumulate across settings scopes while everything else follows override precedence; and a `PreToolUse` hook enforces even under `bypassPermissions`.
3. Update the tracker with your score, level, and next level.

**Next domain or repeat this one?**

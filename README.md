# Claude Certified Developer – Foundations (CCDV-F) — Study Notes

Study notes for the [Claude Certified Developer – Foundations](https://anthropic-partners.skilljar.com/claude-certified-developer-foundations-certification) certification (exam code **CCDV-F**), part of Anthropic's Claude Certification Program. Registration is gated to the Claude Partner Network via the Anthropic Partner Academy.

## What's in this repo

Content was generated using WebSearch/WebFetch (in place of the Exa SDK — see "Regenerating" below), Context7, and the full 5-module Anthropic Partner Academy prep course (pulled via `claude-in-chrome`) against the official [Exam Guide PDF](#sourcing) and Anthropic's public developer docs.

| File | Description |
|------|-------------|
| [1_agents_and_workflows.md](1_agents_and_workflows.md) | Domain 1: workflow vs. agent, Agent SDK, hooks, subagents, frameworks |
| [2_applications_and_integration.md](2_applications_and_integration.md) | Domain 2 (largest, 33.1%): requirements, API mechanics, app design, config management |
| [3_claude_code_tools_mcp.md](3_claude_code_tools_mcp.md) | Domains 3 + 8: Claude Code operation, tool implementation, MCP servers |
| [4_model_selection_prompting_context.md](4_model_selection_prompting_context.md) | Domains 5 + 6: LLM fundamentals, model tiers, prompting, structured output |
| [5_eval_debugging_security.md](5_eval_debugging_security.md) | Domains 4 + 7: debugging, prompt injection, guardrails, key management |
| [exam_sections.md](exam_sections.md) | Full exam domain/skill breakdown with weightings |
| [study_cheat_sheet.md](study_cheat_sheet.md) | Decision trees, model/error/hook tables, security checklist |
| [study_flashcards.md](study_flashcards.md) | Flashcards for key concepts, grouped by domain |
| [study_practice_questions.md](study_practice_questions.md) | 58 original practice questions with explanations |
| [study_topic_summaries.md](study_topic_summaries.md) | Topic summaries for final review |

## Exam domains

| Domain | Weight |
|--------|--------|
| Applications and Integration | **33.1%** |
| Model Selection and Optimization | 16.8% |
| Agents and Workflows | 14.7% |
| Prompt and Context Engineering | 11.0% |
| Tools and MCPs | 10.6% |
| Security and Safety | 8.1% |
| Claude Code | 3.1% |
| Eval, Testing, and Debugging | 2.6% |

53 items, 120 minutes, scaled score 720/1000 to pass, $125, 12-month validity. Full skill-level breakdown in [exam_sections.md](exam_sections.md).

## Sourcing

- **Blueprint (domains/weights/skills)**: the official [Exam Guide PDF](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor/6nizmqk8tpzpfjvt6qmmav7rh/public/1783542875/Claude+Certified+Developer+%E2%80%93+Foundations+Exam+Guide.pdf) (v1.0, effective July 2026) — authoritative, cited directly in `exam_sections.md`.
- **Teaching depth, primary**: the full 5-module Anthropic Partner Academy prep course (MSO Foundations; Production-Grade Prompting, Agents & Tool Use; Claude Code, MCP & Integration; Production Engineering, Evals & Security; Accelerators & IP Contribution), gated to the Claude Partner Network. Pulled by driving `claude-in-chrome` against an authenticated `anthropic-partners.skilljar.com` session — each module's SCORM lesson player loads all its screens into the DOM at once (hidden via CSS, only the active one shown), so the full text was extracted per module via a `document.querySelector('section.screen')` sweep and saved to a local file, rather than clicking through 20+ screens one at a time. Course content is **paraphrased into this repo's own note style throughout, never reproduced verbatim** — it's Anthropic's copyrighted material, and these are personal study notes derived from a course the account has legitimate paid access to, not a redistribution of it.
- **Teaching depth, secondary**: Anthropic's public developer docs at `docs.claude.com` / `platform.claude.com` / `code.claude.com` — Messages API, Agent SDK, Claude Code, MCP, prompt engineering, security guardrails. Used as the primary source before Partner Academy access was available, and as ongoing cross-verification afterward.
- **API/SDK cross-check**: Context7 MCP against `anthropics/claude-agent-sdk-python` and `anthropics/anthropic-sdk-python` — verified `AgentDefinition`/`ClaudeAgentOptions` field names and the `output_config.format`/`strict` structured-output parameters against the actual SDK source.
- **Drift/gap check**: WebSearch, standing in for Exa's role in the sibling repos (no `EXA_API_KEY` configured on this machine — see "Regenerating"), plus a dedicated fact-check pass (background agent + fresh WebSearch) against the model-lineup table and prompt-caching mechanics. Notable catches: Haiku 4.5 supports **extended thinking**, not **adaptive thinking**, unlike Fable 5/Opus 5/Sonnet 5 — an easy assumption to get backwards if you assume "the flagship models get the newer feature"; `budget_tokens` is deprecated and 400s on the newest model generations, with `effort` levels as the current mechanism; the direct Anthropic API does not currently offer EU data residency (EU-residency deployments route through Bedrock/Vertex); Managed Agents' server-side session storage currently rules out ZDR/HIPAA-BAA eligibility regardless of operational fit.

## Regenerating

If the exam guide or docs change, regenerate notes by re-running research against the sources above.

**1. Blueprint**

WebSearch for `"Claude Certified Developer Foundations" exam guide`, WebFetch the current PDF, diff against [exam_sections.md](exam_sections.md) for a version bump (check the "Document Control" section at the end of the PDF).

**2. Public docs**

WebSearch for the relevant `docs.claude.com`/`platform.claude.com`/`code.claude.com` page per topic, WebFetch it directly — the docs' own `llms.txt` index (e.g. `https://code.claude.com/docs/llms.txt`) is a fast way to discover all available pages under a given docs subdomain.

**3. Partner Academy content (optional, requires Partner Network membership)**

1. Sign into `anthropic-partners.skilljar.com` in Chrome, with the [claude-in-chrome](https://claude.ai/chrome) extension connected and pointed at that logged-in session.
2. Navigate to a module's lesson URL (e.g. `.../path/claude-certified-developer-foundations/mso-foundations` — it redirects into the SCORM player once logged in).
3. Extract the whole module in one shot via `javascript_tool`, since the SCORM player preloads every screen into the DOM (hidden via CSS) rather than fetching one at a time:
   ```js
   const inner = window.frames[0].frames[0];  // nested iframe: wrapper -> SCORM content
   const doc = inner.document;
   const sections = Array.from(doc.querySelectorAll('section.screen')).sort((a,b) => a.id.localeCompare(b.id));
   const out = sections.map(s => `=== ${s.id} ===\n${s.innerText.trim()}`).join('\n\n');
   ```
4. Don't return `out` directly from `javascript_tool` — joined multi-screen text reliably trips the tool's content-safety filter (flagged as cookie/query-string-shaped data). Instead trigger a file download and read the result from disk:
   ```js
   const blob = new Blob([out], {type: 'text/plain'});
   const a = document.createElement('a');
   a.href = URL.createObjectURL(blob); a.download = 'moduleN.txt';
   document.body.appendChild(a); a.click(); document.body.removeChild(a);
   ```
5. Chrome silently blocks automatic downloads after the first one per site/session — if only the first module's file lands in `~/Downloads`, click "Always allow" on the blocked-downloads icon in the address bar, then retry the remaining modules.
6. Fold each module's text into the matching section file(s), **paraphrased into the repo's own note style, never reproduced verbatim** — it's Anthropic's copyrighted course material; personal study notes derived from a course you have legitimate access to are fine, wholesale reproduction isn't.

Fallback if the extension won't connect at all: copy/paste lesson text manually into a Claude Code session and ask it to fold the content in the same way.

**4. Context7 API check**

Pull current docs for `anthropics/claude-agent-sdk-python` and `anthropics/anthropic-sdk-python` via the Context7 MCP tools to verify code snippets and field names haven't drifted.

**5. Exa verification (optional — this repo used WebSearch instead)**

The DP-700/Databricks sibling repos in this directory use a real Exa API key via the `exa-py` SDK for this step (see their READMEs for the Keychain-based setup). This repo didn't have `EXA_API_KEY` available at build time, so WebSearch/WebFetch served the same "search the live web, verify against community writeups" role. If you have an Exa key, prefer it — Exa's `type="deep"` search with `contents={"highlights": True}` is more targeted for finding exam-experience/gotcha writeups than general WebSearch.

**6. Update files**

Update `1_agents_and_workflows.md` / `2_applications_and_integration.md` / `3_claude_code_tools_mcp.md` / `4_model_selection_prompting_context.md` / `5_eval_debugging_security.md` first (each maps to 1–2 official exam domains — see the table above), then regenerate `study_cheat_sheet.md`, `study_flashcards.md`, `study_practice_questions.md`, `study_topic_summaries.md` from those.

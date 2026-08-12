# Exam Sections

Source: [Claude Certified Developer – Foundations Exam Guide](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor/6nizmqk8tpzpfjvt6qmmav7rh/public/1783542875/Claude+Certified+Developer+%E2%80%93+Foundations+Exam+Guide.pdf), Version 1.0, effective July 2026, exam code **CCDV-F**. This is the authoritative blueprint — re-check for a version bump before your exam date.

53 items, 120 minutes, scaled score 720/100–1000 to pass, $125, 12-month validity, delivered by Pearson VUE (online proctored or test center).

## Domain 1: Agents and Workflows — 14.7%

- Agent Architecture (4.5%) — workflow vs. agent decision criteria, manager/supervisor hierarchies, role of subagents
- Agent Construction with Claude (5.3%) — Claude Agent SDK, custom agent loops/harnesses, self-hosted vs. Anthropic-hosted deployment, hooks for deterministic actions
- Agent Patterns and Frameworks (4.9%) — tool-use loops, sub-agents, memory, context-window management, agentic frameworks (Strands, LangGraph, PydanticAI)

## Domain 2: Applications and Integration — 33.1%

- Understanding Requirements (3.4%) — functional/infrastructure requirements from business requirements and solution architecture
- Systems Life Cycle (2.8%) — SDLC concepts for developing, implementing, operating, maintaining IT systems
- Claude API Mechanics (6.8%) — messages, tools, streaming, vision, thinking, caching, third-party vendors, Messages API data access patterns, batch API, realtime vs. batch tradeoffs
- Software Engineering Foundations (7.4%) — REST APIs, JSON, async programming, version control, SDLC integration, code review, refactoring
- Claude Application Design (8.6%) — Claude's instruction interpretation across interfaces (Claude Code, Desktop, claude.ai, API, SDKs), content boundaries, schema design, session hygiene, plugin management
- Configuration Management (4.1%) — CLAUDE.md, settings.json, model version pinning, prompt versioning, plugin dependencies

## Domain 3: Claude Code — 3.1%

- Claude Code Operation (3.1%) — core components (Rules, Skills, Commands, Agents, Agent Memory), session management, built-in/custom slash commands, headless/streaming/auto-mode, CLAUDE.md hierarchy, repo initialization, settings.json

## Domain 4: Eval, Testing, and Debugging — 2.6%

- Debugging and Error Handling (2.6%) — error type identification, recovery strategy selection, trace analysis, isolating integration-layer vs. model-output failures

## Domain 5: Model Selection and Optimization — 16.8%

- LLM Fundamentals (5.2%) — tokens, context windows, sampling, non-determinism, next-token generation, fast mode/extended thinking/adaptive thinking/effort levels, zero/single/multi-shot
- Technical Fundamentals (6.1%) — SDKs wrapping REST APIs, websockets
- Model Selection and Tradeoffs (2.7%) — Opus vs. Sonnet vs. Haiku, adaptive thinking support, quality/latency/cost tradeoffs, breaking changes across releases
- Cost and Token Management (2.8%) — token usage tracking, cost modeling, prompt caching, cache checkpointing

## Domain 6: Prompt and Context Engineering — 11.0%

- Context Engineering (3.8%) — context window management, drift/bloat prevention (tool output pruning, compaction), context isolation via subagents/multi-step workflows
- Prompt Engineering (4.6%) — instruction clarity, few-shot examples, system vs. user placement, output constraints, iterative refinement, input sanitization
- Output Handling (2.6%) — structured output patterns, response validation, defensive parsing, skepticism toward confident output

## Domain 7: Security and Safety — 8.1%

- AI Application Security (3.2%) — prompt injection, jailbreak defense, untrusted input handling, data leakage prevention, PII handling, AAA + confidentiality/privacy/integrity
- Guardrails and Safe Deployment (2.3%) — content policy, guardrail layering, secure-by-design (privacy, IAM, least privilege)
- Claude Hooks (1.0%) — hooks as guardrails/safety controls to prevent destructive actions
- Identity, Secrets, and Key Management (1.6%) — credential/API key management, identity validation, access approval, authorized access monitoring

## Domain 8: Tools and MCPs — 10.6%

- Tool Implementation (4.4%) — tool use/function calling, external system config, tool description writing, error handling, dispatch patterns (client vs. server-side, approval patterns)
- MCP Server Development (2.1%) — server authoring/deployment, MCP resources/tools/prompts, transports (stdio, sockets, client vs. server)
- Agentic Customization (4.1%) — built-in Tools vs. custom Tools vs. Skills vs. MCPs tradeoffs

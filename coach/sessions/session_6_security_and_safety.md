# Session 6 — Security and Safety (8.1%)

Domain 7 of the CCDV-F blueprint. The exam's favorite scenario lives here: indirect prompt injection through content the agent retrieves rather than content the user typed.

Source: [`5_eval_debugging_security.md`](../../5_eval_debugging_security.md). Level: **L2 Applied**. Time: 10–15 minutes.

---

## Section A — Domain Overview

### What this domain actually tests

| Skill | Weight | The question behind the questions |
|---|---|---|
| AI Application Security | 3.2% | Prompt injection, jailbreak defense, untrusted input, data leakage, PII |
| Guardrails and Safe Deployment | 2.3% | Content policy, guardrail layering, secure-by-design, least privilege |
| Claude Hooks | 1.0% | Hooks as deterministic guardrails against destructive actions |
| Identity, Secrets, and Key Management | 1.6% | Credential handling, rotation, identity validation, access monitoring |

### Key patterns

**The mechanism behind prompt injection.** The model reads its entire context as **one undifferentiated stream of tokens**. There is no structural marker separating your trusted system prompt from an instruction planted in a fetched page, a database record, or a tool result. So any content the agent reads that *someone else can write* is a vector, and the injection can be indirect (planted for later reading) and hidden (white text, off-screen, inside an image).

**Trusting your own users does not solve this.** The hostile instruction typically arrives through content the agent *retrieves on the user's behalf*, not through the user's own prompt.

Anthropic mitigates injection two ways — training the model to recognize and refuse injected instructions, and running classifiers over untrusted content entering context — while being explicit that **no agent reading untrusted content is fully immune**. Delimiter-wrapping untrusted content and telling the model to treat it as data helps, but stays a **soft boundary**: the content can mimic your delimiters or argue persuasively for an exception. **The reliable boundary isn't in the wording — it's in what the agent is allowed to do as a consequence of reading that text.**

**Jailbreak vs. injection:** a jailbreak targets the model's own safety constraints; injection hijacks your application's instructions. Different targets, same layered defense shape — constrain what reaches the model *and* limit what the model can do as a result.

**Trust boundaries multiply in a multi-component application.** A chain like API entry point → Claude Code task fetching external content → MCP server reaching a customer system has a boundary at every seam where data or instructions cross environments. A component that passes its own tests has no seam-level controls. And least privilege applies to the *whole* application: it's only as contained as its most privileged seam, so one over-scoped component becomes the weak point no matter how well-scoped the others are.

**Least privilege is the control that holds when everything else fails.** Assume an injection gets past training and the classifiers and the agent acts on it — what happens next is bounded entirely by what that identity may do. An identity scoped to one output directory with read-only input turns the same injection into a denied action and a log entry. One subtlety: **anything that can modify the agent's own auth or role configuration can effectively act with that identity**, so protecting that configuration matters as much as protecting the secret.

**Hooks are enforcement, not convention.** A `PreToolUse` hook can block a call touching a protected resource and log the attempt before it happens. Precedence when several rules apply: **deny > ask > allow** — a single deny blocks regardless of how many allows also match. `PostToolUse` logging fires deterministically on every tool call, unlike a log the model could theoretically skip.

**OS-level sandboxing is the residual control.** Hooks and least-privilege roles only cover the path or endpoint they were explicitly written to check. Filesystem and network isolation enforced by the OS hold *regardless* of what any individual hook permits — which is what closes the gap between "we have hooks" and "we have a defensible boundary," and it's the first thing an enterprise security reviewer asks about.

**Regulated customers ask three questions early:** where is data processed (residency), can every privileged action be inspected (access logging, which maps to the hook audit trail), and can an administrator lock the rules centrally (managed configuration). Also note **ZDR eligibility varies by model and platform** and isn't guaranteed even under an existing ZDR agreement.

**Secrets.** A secret in committed configuration is a permanent exposure — it's in history, and overwriting the file later doesn't remove it. The only correct response is rotation. Environment variables suit local/short-lived values; a **secret store** suits anything shared across services or people, because one rotation updates every consumer and reads are audit-logged. API keys are shown **once** at creation. Prefer short-lived federated credentials where the workload already has a platform identity, scope each credential narrowly, and keep a record of which services consume it so a rotation doesn't have to discover its own blast radius.

### Common mistakes

- **"Our users are internal, so we skipped validating fetched content."** The injected instruction came from a fetched page, not the user.
- **Defending only the input side.** Validating what reaches the model without constraining what it can do leaves it free to cause damage once steered.
- **Treating delimiters as the boundary.** They're a soft boundary; the hard one is capability.
- **Assuming component-level tests cover a seam.** Each side can pass its own tests while the handoff between them carries untrusted content straight into a prompt.
- **Exit code 1 in a blocking hook.** Only exit code 2 denies a `PreToolUse` call; exit 1 just warns.
- **Rotating a committed key and calling it done** without knowing which other services used the same value.

### Real exam-style scenarios

**Scenario A.** An agent summarizes user-submitted web pages. One page contains white-on-white text instructing the model to write the user's saved notes to a public path.

The reasoning: the answer is two-sided every time. Treat retrieved content as untrusted data isolated in tool results, *and* put enforcement in front of the action — a hook refusing writes outside the permitted path, plus an identity that can't write there anyway. Model tuning, a politer system-prompt request, or a bigger model are not defenses. Note the exfiltration is harmless the moment the agent has no tool that can write to that path.

**Scenario B.** A financial customer's reviewer asks where data is processed, whether every privileged action is inspectable, and whether an administrator can lock the configuration so no developer can widen permissions locally.

The reasoning: those three questions are residency, access logging, and managed configuration. Each has a concrete answer — a region-pinned endpoint on a matching platform deployment, a `PostToolUse` audit hook recording every tool call with the identity that took it, and enterprise managed settings that no project or user file can override. Naming them during scoping is what keeps the integration from stalling in review.

---

## Section B — Questions

12 questions, four options each, single best answer.

### Q1

What is the underlying mechanism that makes prompt injection possible?

A. Claude executes any code it finds in its context by default
B. The model reads its entire context as one undifferentiated stream of tokens, with no structural marker separating a trusted system prompt from an instruction planted in retrieved content
C. Tool results bypass the model's safety training
D. System prompts are transmitted after user content, so ordering can be exploited

### Q2

A team argues their agent is safe from prompt injection because every user is an authenticated internal employee. What's wrong with that reasoning?

A. Nothing — authenticated internal users are the standard mitigation
B. Internal users are the more likely attackers, statistically
C. Authentication needs to be paired with rate limiting to be effective against injection
D. The hostile instruction typically arrives through content the agent retrieves on the user's behalf — a shared document, a fetched page, a database record — not through the user's own prompt

### Q3

A developer wraps retrieved documents in `<untrusted_content>` tags and adds a system-prompt line telling Claude to treat anything inside them as data. Is that sufficient, and why?

A. No — it helps, but it remains a soft boundary the content itself can mimic or argue around; the reliable boundary is what the agent is allowed to *do* after reading it
B. Yes — delimiter isolation is the documented complete defense for indirect injection
C. No — delimiters have no effect at all and should be omitted
D. Yes, provided the delimiters are randomly generated per request

### Q4

Three components — an API entry point, a Claude Code task that fetches an external page, and an MCP server reaching a customer system — each pass their own tests. A developer wires them together and the fetched page's content ends up as instructions in the next component's prompt. What was missing?

A. An end-to-end test, which would have caught the injection automatically
B. Component-level input validation, which each component skipped
C. Seam-level controls: the trust boundary is where data moves between deployment environments, and each crossing needs content wrapped so the receiving component treats it as data — a component passing its own tests has no controls at that seam
D. A more capable model in the middle component, better able to recognize injected instructions

### Q5

Why does the material insist least privilege applies to the whole application rather than component by component?

A. Because per-component scoping isn't technically possible with IAM roles
B. Because the application is only as contained as its most privileged seam — one over-scoped component becomes the weak point even when every other component is properly scoped
C. Because component-level scoping doubles the audit burden with no security gain
D. Because privileges are inherited downward from the entry point automatically

### Q6

A team has `PreToolUse` hooks covering `write_file` and `delete_file` on protected paths. A reviewer asks what stops a steered agent from making an outbound call to an unreviewed endpoint. What's the answer the domain expects?

A. Nothing is needed — a `PreToolUse` hook covers every tool call including network calls
B. A stricter system prompt forbidding network access
C. A `PostToolUse` hook that logs outbound calls after they complete
D. OS-level sandboxing — filesystem and network isolation enforced by the OS rather than application logic, holding regardless of what any individual hook permits or misses

### Q7

A regulated customer's reviewer asks the three questions this domain says to expect early. Which set is it?

A. Model tier, token budget, and expected latency
B. Prompt versioning, eval coverage, and rollback procedure
C. Data residency, access logging, and whether an administrator can define and lock the rules centrally
D. Encryption in transit, encryption at rest, and password rotation policy

### Q8

Several rules apply to the same tool call: two allow rules, one ask rule, and one deny rule. What happens?

A. The call is denied — precedence is deny > ask > allow, and a single deny blocks the action regardless of how many allow rules also match
B. The user is prompted, because ask sits between the conflicting rules
C. The call is allowed, because allow rules outnumber the deny
D. The behavior depends on which scope each rule was defined in

### Q9

Why is a `PostToolUse` hook the right mechanism for a regulated customer's access log, rather than instructing the model to log its own actions?

A. Because model-written logs are stored outside the customer's boundary
B. Because a hook fires deterministically on every tool call, independent of what the model decides, whereas an instruction to self-log can be followed inconsistently
C. Because `PostToolUse` hooks can block a call that fails to log
D. Because the model has no access to the tool name or arguments it just used

### Q10

A developer creates a new API key, copies it into a scratch file, and later loses the file. What's the situation?

A. The key can be re-displayed from the console with account-owner approval
B. The key is recoverable from the first API response that used it
C. API keys are shown once at creation and cannot be retrieved again — the key has to be replaced, which is why capture into a secret store should happen immediately
D. The key rotates automatically every 24 hours, so nothing is lost

### Q11

Three services and two engineers all use the same third-party credential. Where should the value live, and why?

A. In each service's committed configuration, so every consumer is documented in version control
B. In a per-service environment variable set by each engineer locally
C. Hardcoded in a shared library so there's exactly one copy in the codebase
D. In a secret store — it's shared across services and people, so one rotation updates every consumer and reads are audit-logged

### Q12

A `PreToolUse` hook blocks writes outside `/workspace/output`, and the agent's role denies `/etc`, `/secrets`, and `~/.aws`. Which additional protection does the material call out as equally important, and why?

A. Protecting the agent's own auth and role configuration, because anything able to modify it can effectively act with that identity
B. Encrypting the hook script on disk, so its logic can't be read by the agent
C. Rotating the agent's credential after every session, since long-lived identities can't be scoped
D. Removing the `PostToolUse` hook, since audit logs written by the agent's identity can be forged

---

### Answer Key and Explanations

#### Q1 — Answer: B

- **Why B is correct:** The model has no structural distinction between trusted instructions and text that arrived inside a document or tool result — it's all one token stream. That's why any writable content the agent reads is a vector.
- **Why not A:** Claude doesn't execute code found in context; the risk is instruction-following, not code execution.
- **Why not C:** Tool results don't bypass safety training; Anthropic trains against injected instructions and runs classifiers, and still says no agent reading untrusted content is fully immune.
- **Why not D:** Message ordering isn't the mechanism.
- **Difficulty:** Easy
- **Tag:** `sec.appsec/injection-mechanism`
- **Revise:** `5_eval_debugging_security.md` → The mechanism behind prompt injection

#### Q2 — Answer: D

- **Why D is correct:** This is the documented reasoning error. The injection arrives through retrieved content — a fetched page, a shared document, a database record — so user trust is beside the point.
- **Why not A:** Authentication addresses who can use the system, not what the system reads.
- **Why not B:** Insider likelihood isn't the argument; the vector is retrieved content.
- **Why not C:** Rate limiting is unrelated to injection.
- **Difficulty:** Medium
- **Tag:** `sec.appsec/indirect-injection`
- **Revise:** `5_eval_debugging_security.md` → Security and Safety gotcha

#### Q3 — Answer: A

- **Why A is correct:** Delimiter-wrapping plus a policy statement genuinely helps, but it's a soft boundary — the untrusted content can mimic the delimiters or argue persuasively for an exception. The hard boundary is capability: what the agent may do after reading.
- **Why not B:** The material is explicit that this is not a complete defense.
- **Why not C:** Delimiting and JSON-encoding untrusted content are recommended practices, just not sufficient alone.
- **Why not D:** Randomizing delimiters raises the bar slightly but doesn't change the category of the control.
- **Difficulty:** Medium
- **Tag:** `sec.appsec/soft-vs-hard-boundary`
- **Revise:** `5_eval_debugging_security.md` → The mechanism behind prompt injection

#### Q4 — Answer: C

- **Why C is correct:** The trust boundary is the point where data or instructions move from one deployment environment to the next, and each seam needs the same treat-it-as-data discipline. Passing component tests says nothing about the seam between components.
- **Why not A:** An end-to-end test might reveal a symptom, but the missing thing is a control, not a test.
- **Why not B:** Each component did validate its own inputs; the crossing was never marked as a boundary.
- **Why not D:** Model capability isn't a substitute for a boundary control.
- **Difficulty:** Hard
- **Tag:** `sec.appsec/trust-boundaries`
- **Revise:** `5_eval_debugging_security.md` → Trust boundaries in a multi-component application

#### Q5 — Answer: B

- **Why B is correct:** The application is only as contained as its most privileged seam, so scoping components independently still leaves the whole system exposed through the widest one — typically whichever component reaches an external system.
- **Why not A:** Per-component scoping is possible and expected; it just isn't sufficient on its own.
- **Why not C:** The audit burden isn't the argument.
- **Why not D:** Privileges aren't automatically inherited; each identity carries its own.
- **Difficulty:** Medium
- **Tag:** `sec.guardrails/least-privilege`
- **Revise:** `5_eval_debugging_security.md` → Least privilege

#### Q6 — Answer: D

- **Why D is correct:** Hooks and roles only cover the paths and endpoints they were written to check. OS-level sandboxing isolates at the process level — filesystem and network restriction enforced by the OS — so it holds even when a hook is missing, misconfigured, or bypassed.
- **Why not A:** A hook checking `write_file` doesn't automatically cover a network call.
- **Why not B:** A prompt instruction isn't enforcement.
- **Why not C:** Logging after the fact records the call; it doesn't prevent it.
- **Difficulty:** Hard
- **Tag:** `sec.guardrails/os-sandboxing`
- **Revise:** `5_eval_debugging_security.md` → OS-level sandboxing

#### Q7 — Answer: C

- **Why C is correct:** Residency, access logging, and managed configuration are the three questions a regulated customer asks early, and naming the answers during scoping is what keeps the work from stalling in review.
- **Why not A:** Those are engineering tradeoffs, not review questions.
- **Why not B:** Real practices, but not what a regulated reviewer opens with.
- **Why not D:** Generic infrastructure controls, not the three called out here.
- **Difficulty:** Medium
- **Tag:** `sec.guardrails/regulated-review`
- **Revise:** `5_eval_debugging_security.md` → Scoping for a regulated review

#### Q8 — Answer: A

- **Why A is correct:** Precedence is deny > ask > allow. One deny blocks the action no matter how many allows match — that ordering is what makes a hook a real boundary rather than a best-effort check.
- **Why not B:** Ask doesn't mediate between allow and deny; it sits below deny.
- **Why not C:** Rules aren't counted or voted on.
- **Why not D:** Precedence holds across scopes; permissions accumulate and a deny anywhere wins.
- **Difficulty:** Medium
- **Tag:** `sec.hooks/precedence`
- **Revise:** `5_eval_debugging_security.md` → Hooks as enforcement

#### Q9 — Answer: B

- **Why B is correct:** A hook is code at a fixed lifecycle point: it fires on every tool call regardless of model behavior. An instruction to self-log is a convention the model may not follow consistently, which is exactly what a reviewer won't accept.
- **Why not A:** Where logs are stored is your choice in either design.
- **Why not C:** `PostToolUse` runs after completion and can't block; blocking is `PreToolUse`.
- **Why not D:** The model does know what it called — reliability, not visibility, is the issue.
- **Difficulty:** Medium
- **Tag:** `sec.hooks/audit-logging`
- **Revise:** `5_eval_debugging_security.md` → What regulated deployment adds

#### Q10 — Answer: C

- **Why C is correct:** API keys (`sk-ant-...`) are displayed once at creation and cannot be retrieved again, which is why the correct habit is capturing straight into a secret store.
- **Why not A:** There's no re-display path.
- **Why not B:** Keys aren't echoed in API responses.
- **Why not D:** Keys don't rotate themselves; rotation is a deliberate action.
- **Difficulty:** Easy
- **Tag:** `sec.secrets/key-handling`
- **Revise:** `5_eval_debugging_security.md` → Identity, Secrets, and Key Management

#### Q11 — Answer: D

- **Why D is correct:** A secret store is the recommendation for anything shared across services or people: it centralizes the value so one rotation updates every consumer, and it records who read what.
- **Why not A:** A credential in committed configuration is a permanent exposure that can only be resolved by rotation.
- **Why not B:** Environment variables suit local or short-lived values, and per-engineer copies mean rotation has to find every copy.
- **Why not C:** Hardcoding in source is the same permanent-exposure problem with extra reach.
- **Difficulty:** Medium
- **Tag:** `sec.secrets/storage-and-rotation`
- **Revise:** `5_eval_debugging_security.md` → Identity, Secrets, and Key Management

#### Q12 — Answer: A

- **Why A is correct:** Anything that can modify the agent's own auth or role configuration can effectively act with that identity, so editing the role is itself a privileged action and belongs behind the same protection as the secret.
- **Why not B:** Hook-script confidentiality isn't the control being described; enforcement doesn't depend on secrecy.
- **Why not C:** Rotation is good hygiene but unrelated to scoping, and identities can be scoped regardless of lifetime.
- **Why not D:** Removing the audit hook removes the record a reviewer wants; it doesn't improve integrity.
- **Difficulty:** Hard
- **Tag:** `sec.secrets/auth-config-protection`
- **Revise:** `5_eval_debugging_security.md` → Least privilege

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
| 6–7 (50–58%) | Re-read the defense-in-depth checklist and the regulated-constraints table, then repeat at L1. |
| Below 6 | Repeat at L1. Anchor on one idea first: every correct answer in this domain constrains what the agent may *do*, not just what it reads. |

### Weak-area map

| Missed | Tag | Revise |
|---|---|---|
| Q1–Q4 | `sec.appsec` | `5_eval_debugging_security.md` → AI Application Security |
| Q5–Q7 | `sec.guardrails` | `5_eval_debugging_security.md` → Guardrails and safe deployment |
| Q8, Q9 | `sec.hooks` | `5_eval_debugging_security.md` → Hooks as enforcement |
| Q10–Q12 | `sec.secrets` | `5_eval_debugging_security.md` → Identity, Secrets, and Key Management |

### Recommended next steps

1. Learn the regulated-data-constraints table cold — attorney-client privilege, HIPAA, GDPR/residency, FedRAMP, internal policy, and what each one rules out. It generates a disproportionate number of scenario questions, and the specific exclusions (no EU residency on the direct API; BAA excluding Console/Workbench/beta; AWS Marketplace Enterprise not FedRAMP authorized) are exactly the level of detail the exam tests.
2. If you missed Q6 or Q12, note the pattern: both answers are about a control that holds when the rule you wrote doesn't cover the case.
3. Update the tracker with your score, level, and next level.

**Next domain or repeat this one?**

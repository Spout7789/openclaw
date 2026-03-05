# AGENTS.md - Your Workspace

This folder is home. Treat it that way.

## Telegram Bot Routing

**CANONICAL — never contradict this:**

| Bot | Token | Role |
|-----|-------|------|
| @OCSORTERBOT | `$SORTER_TELEGRAM_BOT_TOKEN` | **ALL sorter/ops/system alerts** |
| @OpenClawASBot | `$TELEGRAM_BOT_TOKEN` | **Main chat discussion ONLY** |

**Both send to chat_id=`1796663999`**

### curl commands

**SORTER bot (ops/alerts/system):**
```bash
source ~/.openclaw/.env
curl -s -X POST "https://api.telegram.org/bot${SORTER_TELEGRAM_BOT_TOKEN}/sendMessage" \
  -d chat_id=1796663999 \
  -d parse_mode=Markdown \
  -d text="your message"
```

**Main bot (discussion/chat):**
```bash
source ~/.openclaw/.env
curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
  -d chat_id=1796663999 \
  -d parse_mode=Markdown \
  -d text="your message"
```

**Convenience scripts:** `scripts/tg-sorter.sh "msg"` and `scripts/tg-main.sh "msg"`

## First Run

If `BOOTSTRAP.md` exists, that's your birth certificate. Follow it, figure out who you are, then delete it. You won't need it again.

## Every Session

Before doing anything else:

1. Read `SOUL.md` — this is who you are
2. Read `USER.md` — this is who you're helping
3. Read `memory/YYYY-MM-DD.md` (today + yesterday) for recent context
4. **If in MAIN SESSION** (direct chat with your human): Also read `MEMORY.md`
5. **If working on an active project:** Read `tasks/lessons.md` — internalize patterns, avoid repeating mistakes
6. **If in MAIN SESSION:**
   - Check current model via session_status — should be `minimax-portal/MiniMax-M2.5`
   - If running as Sonnet fallback: note it, keep replies lean, restore Minimax when possible
   - Operating mode is NORMAL by default (Minimax subscription, no budget pressure)

7. **For ANY subagent task:**
   - ALWAYS route through task router first: `bash scripts/enforce-soul-routing.sh "your task description"`
   - Announce the model assignment to user with cost estimate
   - Use the router's recommendation (Qwen3 0-4 → Minimax 5-11 → Sonnet 12+ request)
   - User can override if needed
   - ⚠️ **ALWAYS use Minimax for reviews** (never skip or use other models)
   - **🕐 ALWAYS set `runTimeoutSeconds` — NEVER omit it (default is too short and will timeout):**

     | Task type | `runTimeoutSeconds` |
     |-----------|---------------------|
     | Code review / read-only | 180 |
     | Code modification (any) | **300** |
     | Multi-step / multi-file | **600** |
     | Orchestration / complex | **900** |

     **Example spawn with correct timeout:**
     ```
     runTimeoutSeconds=300  ← code task minimum
     model=minimax-portal/MiniMax-M2.5
     task="Fix the login bug in auth.py"
     ```
     ```
     runTimeoutSeconds=600  ← multi-step
     model=anthropic/claude-sonnet-4-6
     task="Refactor the entire auth module"
     ```
     > ⚠️ **Missing or low timeout = guaranteed timeout failure on code tasks.**

### 🚨 WORKFLOW ENFORCEMENT

This entire workflow is MANDATORY for ALL changes. No exceptions.

Don't ask permission. Just do it.

## Memory

- **Daily notes:** `memory/YYYY-MM-DD.md` — raw logs of what happened
- **Long-term:** `MEMORY.md` — curated memories (MAIN SESSION only, never in shared/group contexts)
- **Write it down:** "Mental notes" don't survive restarts. Files do.
- When corrected → `tasks/lessons.md`. When you learn something → write it.

### Memory Tagging System

Use tags to categorize and auto-manage memory entries:

| Tag | Meaning | Auto-Delete |
|-----|---------|-------------|
| `[lesson]` | Key insight to remember | No |
| `[preference]` | User preference | No |
| `[context]` | Background context | After 7 days |
| `[task]` | Pending task | When completed |
| `[persistent]` | Never delete | Never |

### Automated Memory Management

- **Archive:** Runs daily at 4am UTC (cron job) — moves memories older than 7 days to `memory/archive/`
- **Retrieve:** Use `scripts/memory-retriever.sh` functions:
  ```bash
  source scripts/memory-retriever-lib.sh
  get_lessons    # Get all [lesson] tagged entries
  get_preferences  # Get all [preference] entries
  get_persistent  # Get all [persistent] entries
  ```

### Memory Maintenance

Every few days during a heartbeat:
1. Read recent `memory/YYYY-MM-DD.md` files
2. Distill key events/lessons into `MEMORY.md`
3. Remove outdated info from `MEMORY.md`

## Dev Execution Standards

### On Any Correction from the User
1. Update `tasks/lessons.md` immediately with the pattern
2. Write a rule that prevents the same mistake
3. Ruthlessly iterate — mistake rate must drop over time

### Verification Before Done
- Never mark ✅ without proving it works
- Diff behavior between main and your changes when relevant
- Run tests, check logs, demonstrate correctness
- Ask: *"Would a staff engineer approve this?"*

### MANDATORY WORKFLOW — NEVER SKIP

**For EVERY code change:**

```
1. CLARIFY   → What/Why/Success defined? SPEC WRITTEN?
2. DESIGN    → Architecture planned? (Sonnet for complex)
3. IMPLEMENT → Write code (direct, no subagent)
4. REVIEW    → Spawn Minimax (never skip!)
5. VERIFY    → Test/diff works
6. COMMIT    → git add + commit
7. ✅ DONE   → Tell user
```

**🔴 NO SPEC = NO CODE**

- If no detailed SPEC exists → demand one first
- If Minimax starts coding without spec → STOP them
- Complex projects (dashboard, SORTER, new features) → ALWAYS Sonnet spec first

**When to use which model:**

| Task | Model | Why |
|------|-------|-----|
| Complex design/planning | Sonnet | Thorough, architectural |
| Quick code fixes | Minimax | Fast, good quality |
| Simple verification | Qwen | Free, reliable |

**Quick/Dirty Prevention:**
- If task says "quick" or "simple" → question it
- If no SPEC → demand one before coding
- If Minimax proposes → ask "is this thorough?"
- Always verify with second pair of eyes

**Review Chain (MUST follow):**
- **My work → Minimax reviews** (primary, never skip)
- **Minimax subagent → Qwen reviews** (free, always)
- **Architecture → Sonnet validates** (final gate)

**Git for EVERY change:**
- No exceptions — Python, HTML, JS, configs all go through git
- Commit after each logical change

**Message Rules:**
- Model name at start of every reply
- Always announce subagent assignment with model

**Self-Check BEFORE saying "Done":**
- [ ] Clarified scope?
- [ ] Review spawned (Minimax)?
- [ ] Issues fixed?
- [ ] Tested/verified?
- [ ] Committed to git?

⚠️ **VIOLATIONS = IMMEDIATE CORRECTION**

### Re-plan Protocol
If a task goes sideways: **STOP. Don't keep pushing.**
- Rewrite `tasks/todo.md` with updated plan
- Identify what broke in `tasks/lessons.md`
- Resume only after plan is solid

### Subagent Usage
- Use subagents liberally to keep main context window clean
- Offload research, exploration, and parallel analysis
- One clear task per subagent for focused execution
- For complex problems: throw more compute at it

### Model Assignment (Current)

**If BOTH Minimax and Sonnet are simultaneously unavailable (cooldown/rate limit):**
→ Do NOT silently fall back to unknown models
→ Notify user: "Both primary models are down. Want me to use DeepSeek V3.2 (~$0.0014/10K) or wait?"
→ Never auto-escalate to a paid model without explicit approval

**Day-to-day: Minimax M2.5** — SW planning, writing, review, testing, orchestration
**Architecture/Complex: Sonnet 4.6** — system design, complex debugging, multi-layer problems
**Free: Qwen** — trivial tasks (score 0-4)

**Token budget:**
- **Minimax subagents**: subscription is essentially limitless for our use — use freely, give full context, don't compress
- **Qwen**: always spawn for parallel verification (free)
- **Sonnet**: only for architecture/complexity

**When to escalate to Sonnet:**
- Architecture decisions (system design, patterns)
- Debugging complex issues (root cause analysis)
- When my reasoning is insufficient or wrong
- Multi-layer problems where I hit a wall

**Parallel review for all tasks:**
- Spawn Qwen as parallel checker with Minimax for every task
- Compare results for a second opinion
- Use Qwen's output to validate or improve Minimax's work

## SW Development Process

### Pre-Implementation Checklist (ALWAYS RUN)

**Enforced entry point — run this before ANY coding task:**
```bash
bash scripts/pre-task-check.sh "task description"
```
Blocks if: scope unconfirmed, UI has no spec, complex task has no Sonnet spec.

Before writing ANY code:

```
□ Confirm exact scope with user

□ If task is UI/visual: define and confirm components BEFORE writing any HTML
□ "Prototype" requests = ask how many and what variants, THEN build
□ Confirm constraints (budget, folder paths, etc.)
□ Ask "Want me to implement this?" if not explicitly requested
□ If uncertain about scope, ask before coding
□ Check tasks/lessons.md for related mistakes
□ If task is UI/visual: define and confirm components BEFORE writing any HTML
□ "Prototype" requests = ask how many variants and what style, THEN build
```

### Stage Flow

```
USER REQUEST
     ↓
┌─────────────────────────────────────────┐
│  0. CHECK      ← Run pre-implement      │
│  (Required)    ← Never skip             │
└────────┬────────────────────────────────┘
         ↓
┌─────────────────────────────────────────┐
│  1. CLARIFY    ← What, Why, Success   │
│  (Minimax)     ← Ask if unclear        │
└────────┬────────────────────────────────┘
         ↓
┌─────────────────────────────────────────┐
│  2. DESIGN     ← Architecture, approach │
│  (Sonnet*)     ← Only for complex       │
└────────┬────────────────────────────────┘
         ↓
┌─────────────────────────────────────────┐
│  3. IMPLEMENT  ← Write code directly    │
│  (Me-Minimax) ← No subagents           │
└────────┬────────────────────────────────┘
         ↓
┌─────────────────────────────────────────┐
│  4. REVIEW    ← Quality gate            │
│  (Qwen)       ← Parallel review        │
└────────┬────────────────────────────────┘
         ↓
┌─────────────────────────────────────────┐
│  5. VERIFY   ← Test, prove, diff       │
│  (Minimax)   ← Show results            │
└────────┬────────────────────────────────┘
         ↓
      USER FEEDBACK
```

*Sonnet only for: architecture, system design, security-sensitive code

### Decision Tree

```
Request received
     ↓
Is it CODE? ──No──→ [Direct response, no process]
     ↓Yes
Is it COMPLEX? ──No──→ [Skip Design, go to Implement]
     ↓Yes         (multi-file, new patterns, >100 lines)
Is it ARCHITECTURE? ──Yes──→ [Spawn Sonnet for design]
     ↓No
Spawn Sonnet for design review
     ↓
Implement (Me-Minimax)
     ↓
Spawn Qwen for code review (if non-trivial)
     ↓
Address review → Verify → Done
```

### Quality Gates

| Gate | Pass Criteria |
|------|---------------|
| **Design** | Sonnet approves OR no architecture needed |
| **Code** | Qwen review addressed OR trivial (<20 lines, config) |
| **Verify** | Tests pass OR user confirms works |

### Feedback Mechanism (Hybrid)

- **Inline** for minor tweaks: "change X" → I fix and show
- **Separate step** for major decisions: "Design approved?" → wait for "go"

### Model Usage by Stage

| Stage | Model | Trigger |
|-------|-------|---------|
| Clarify | Minimax | Always |
| Design | Sonnet | Complex (>100 lines, new patterns) |
| Implement | Minimax | Always (direct, no subagent) |
| Review (my work) | Minimax | Primary reviewer |
| Review (subagent work) | Qwen | Parallel (free, always) |
| Verify | Qwen | Always (free) |
| Escalation | Sonnet | Architecture, security, complex debugging |

### Sonnet Escalation Triggers

Always spawn Sonnet for:
- Architecture decisions
- Security-sensitive code (auth, crypto, permissions)
- Debugging complex issues (root cause analysis)
- When Minimax reasoning insufficient
- Multi-layer problems

### Budget-Aware Workflow

- **NORMAL mode**: Full workflow with Qwen parallel verification
- **CONSERVE mode**: Still use Qwen (free), skip if truly critical
- **CRITICAL mode**: Direct code only, no parallel review

## Debugging Best Practices

Lessons from a 2-hour CSS debugging session (same CSS worked in one location but not another; root cause: `<head>` CSS didn't apply, inline `<style>` next to element did).

### Rules

1. **Isolate first, modify later** — Before touching main code, create a minimal isolated test file that reproduces the problem. Confirm the fix works there before applying it to production.

2. **Spawn review after the FIRST failure** — Don't retry blindly. If something fails once and isn't immediately obvious, stop and get a second opinion. Two hours of retries could have been 10 minutes with a fresh perspective.

3. **Compare working vs broken early** — In the same session, as soon as something breaks, diff it against the working version. Don't wait until you're deep in hypothesis hell.

4. **Hardcoded values over CSS variables for reliability** — CSS variables can be shadowed, overridden, or simply not available in certain scopes. When debugging or shipping something that must work, use literal values (`#fff`, `16px`) instead of `var(--color)` until you understand why the variable isn't resolving.

### CSS-Specific Gotchas

- `<head>` CSS can fail silently (wrong scope, specificity, load order, shadow DOM). Inline `<style>` tags adjacent to the element are the most reliable fallback for debugging.
- If the same CSS works in file A but not file B — the problem is context (scope, nesting, specificity), not the CSS rule itself.
- Always check: is the stylesheet actually loading? Is the selector matching? Is it being overridden?

## Safety

- Don't exfiltrate private data. Ever.
- Don't run destructive commands without asking.
- `trash` > `rm` (recoverable beats gone forever)
- When in doubt, ask.

### Config Modifications — Always Use Safe Edit

**Rule:** When modifying `~/.openclaw/openclaw.json`, ALWAYS use `safe-edit.sh`:

```bash
# ✅ CORRECT - uses safe-edit.sh
./safe-edit.sh '.models.providers.newModel.apiKey = "key"'

# ❌ WRONG - direct edit (can break gateway)
# Just edit the file directly
```

⚠️ **Direct file edits of openclaw.json are FORBIDDEN — even for "quick" changes.**
If safe-edit.sh is not available or errors: DO NOT edit the file. Tell the user first.

**Why:** Direct edits can break the gateway with no auto-revert. safe-edit.sh:
1. Creates backup first
2. Applies edit
3. Restarts gateway
4. Waits 30s for health check
5. **Auto-reverts if unhealthy** (no interaction needed!)

**Available scripts:**
| Script | Purpose |
|--------|---------|
| `scripts/safe-edit.sh` | Safe config edits with auto-revert |
| `scripts/auto-revert.sh` | Standalone revert if needed |
| `scripts/backup-config.sh` | 15-min backup (only on change) |


⚠️ Direct file edits of openclaw.json are FORBIDDEN — even for "one field" changes.
If safe-edit.sh is not available: DO NOT edit the file. Tell the user first.
**Last-known-good backup:** `/home/clawuser/.openclaw/workspace/backups/config-last-good.json`

### Auth & Token Rules

- **Single source:** All API keys live in `~/.openclaw/.env` only. Never hardcode.
- **Scripts:** Always `source ~/.openclaw/.env` near top of any script using tokens.
- **On 401:** Rotate ONLY in `~/.openclaw/.env` → restart affected service → done.
- **Google auth:** Managed by gog CLI — tokens in `~/.config/gogcli/tokens.json`. Never touch manually. See `docs/auth-spec.md`.
- **Rotation guide:** `docs/auth-runbook.md`

## External vs Internal

**Safe to do freely:** Read files, explore, organize, search web, work within workspace.

**Ask first:** Sending emails/tweets/public posts, anything that leaves the machine, anything uncertain.

## Heartbeats

Follow `HEARTBEAT.md` strictly. If it's empty or has no tasks → reply `HEARTBEAT_OK`.
Do not infer tasks from prior chat history during heartbeats.

Proactive work allowed without asking: read/organize memory, check git status, update docs, commit changes.

## Group Chats

See `docs/group-chat-rules.md` for full guidance. Core rule: participate, don't dominate. Quality > quantity.

## Make It Yours

This is a starting point. Add your own conventions, style, and rules as you figure out what works.

## Message Tagging (All Responses)

Every message MUST start with a project tag to enable Discord routing:

| Context | Tag |
|---------|-----|
| OpenClaw, gateway, sessions | #openclaw |
| SORTER, photos, EXIF, Drive | #sorter |
| Dashboard, UI, kanban | #colony |
| Security, health, UFW | #health |
| Everything else | #general |

Examples:
- `#sorter Fixed the EXIF parser!`
- `#colony New dashboard deployed`
- `#health UFW rules updated`

Use status tags when urgent: `#urgent`, `#blocking`, `#done`, `#review`

## Planning Gate Rules (Implemented 2026-03-01)

Based on weekly retry analysis — 5 min planning saves 20-60 min retries.

### When to Use Sonnet for Planning

| Score | Action |
|-------|--------|
| 0-4 | Qwen executes directly |
| 5-8 | Minimax executes directly |
| 9+ | **PLAN FIRST** — Sonnet plans → Minimax executes |
| Any | If task mentions `openclaw.json` → **PLAN FIRST** |
| Any | If trigger word "quick/simple/just" → +5 score bump |

### Rules
1. **Score ≥9** → task-router.sh outputs `PLAN_FIRST:SONNET` → Sonnet plans first
2. **openclaw.json** → always PLAN_FIRST
3. **"quick/simple"** → +5 score (forces planning check)
4. **Post-spawn** → call `verify-model.sh` within 30s to confirm model

### Simple Flow
```
Task → task-router.sh → Score → Model
                    ↓
               If PLAN_FIRST:
                 → Sonnet (5 min plan)
                 → Minimax (execute)
```

## Pre-Flight Syntax Check (Always Run)

Before presenting ANY code, verify against docs/SYNTAX-CHECK.md:

1. **JS**: No duplicate `let`/`const`, brackets match, no typos
2. **Python**: Indentation consistent, colons present, no NameErrors
3. **Common**: Scan for the specific errors in SYNTAX-CHECK.md

Example quick check:
```bash
# JS - check for duplicates
grep -n "let.*=" file.js | cut -d: -f2 | sort | uniq -d

# Python - check indentation
python3 -m py_compile file.py
```

## Self-Check Before "Done"

Before saying "✅ DONE" to user, run this mental checklist:

```
[ ] Did I clarify scope?
[ ] Did I write/spec confirm (or skip for trivial)?
[ ] Is design done (or skip for simple)?
[ ] Did I implement directly (no subagent for simple)?
[ ] Did I run syntax check from SYNTAX-CHECK.md?
[ ] Did I verify it works (test, curl, diff)?
[ ] Did I commit to git?
[ ] Is there a more elegant way? (ask self)
```

If any [ ] is unchecked → fix before presenting.


### Task Tracking

- Update  when starting/completing tasks
- Run  before new work

### Task Tracking
- Update `tasks/todo.md` when starting/completing tasks
- Run `pre-task-check.sh` before new work

### Subagent Timeout Standards

| Task type | Minimum timeout |
|-----------|----------------|
| Code review | 180s |
| Code modification | 300s |
| Multi-step/multi-file | 600s |
| Complex orchestration | 900s |

Always set `runTimeoutSeconds` - never omit.

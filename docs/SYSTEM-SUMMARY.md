# 🤖 OpenClaw Dev Automation System — Complete Setup

**Date:** 2026-02-22 14:40 UTC  
**Status:** 🟢 READY FOR WORK  
**Budget:** $8.75/week (~$2.19/day, target <$1/week spend)

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  YOU (gateway-client, Telegram: 1796663999)                │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  OpenClaw Gateway (127.0.0.1:18789, loopback, key-auth)    │
│  • UFW firewall: ACTIVE (deny incoming, allow SSH)         │
│  • Fail2ban: ACTIVE (SSH protection)                       │
│  • Unattended-upgrades: ACTIVE (auto patches)              │
│  • NOPASSWD sudo: ENABLED (agent can run privileged tasks) │
└────────────────────────┬────────────────────────────────────┘
                         │
           ┌─────────────┼─────────────┐
           ↓             ↓             ↓
    ┌──────────────┐ ┌─────────┐ ┌──────────┐
    │ Orchestrator │ │ Writer  │ │ Reviewer │
    │ (Sonnet 4.6) │ │(Qwen3)  │ │ (Arcee)  │
    │ [Planning]   │ │ [Code]  │ │[Testing] │
    └──────────────┘ └─────────┘ └──────────┘
           │             │             │
           └─────────────┼─────────────┘
                         ↓
              ┌──────────────────────┐
              │   Executor (Bash)    │
              │   Git/GitHub/Deploy  │
              └──────────────────────┘
```

---

## Task Routing Rules

### By Task Type:

| Task | Model | Tool | Approval |
|------|-------|------|----------|
| **Planning/Design** | Sonnet 4.6 (Haiku fallback) | LLM only | Auto |
| **Code Generation** | Qwen3 (free) → DeepSeek | sessions_spawn | Auto/Free |
| **Testing/Review** | Arcee (free) → GLM 5 | exec, tests | Auto/Free |
| **Linux Changes** | Bash + sudo | exec | Ask/Approved |
| **OpenClaw Config** | Edit + restart | read, edit, exec | Show diff |
| **Logging/Monitoring** | Haiku | grep, awk | Auto |

### Cost Decision Tree:

```
Free tier available? → Use free (Qwen3, Arcee)
Rate-limited? → Escalate to paid (DeepSeek, GLM 5)
Weekly spend >$1? → Flag user, wait for guidance
```

### Approval Rules:

- ✅ **Auto:** Planning, logging, config reads, test runs
- ❌ **Ask first:** Package installs, firewall changes, git pushes, new expenses
- ✅ **Auto (pre-approved):** Tier 2 hardening, security audits, existing scheduled tasks

---

## Files You Need to Know

| File | Purpose | Edit When |
|------|---------|-----------|
| `SOUL.md` | Who I am (dev automation focus) | Never (I'm this) |
| `USER.md` | Who you are + goals | Update as needed |
| `TASK-RULES.md` | Routing & model assignment | Reference only |
| `active-tasks.md` | Current work queue | Add your tasks here |
| `daily-logs.md` | Session log + cost tracking | I update this |
| `memory/YYYY-MM-DD.md` | Raw daily notes | I create/update |
| `MEMORY.md` | Long-term memory (empty) | I update occasionally |
| `MODEL-STRATEGY.md` | Model selection rationale | Reference only |
| `TOKEN-OPTIMIZATION.md` | Optimization plan | Reference only |
| `SECURITY-AUDIT-2026-02-22.md` | Security posture | Reference only |
| `HARDENING-COMPLETE.md` | What was hardened | Reference only |

---

## Models & Costs

### Configured (Via OpenRouter)

| Role | Free Model | Cost | Paid Model | Cost |
|------|-----------|------|-----------|------|
| Writer | Qwen3 Coder | $0.00 | DeepSeek V3.2 | $0.25/$0.38 |
| Reviewer | Arcee Trinity | $0.00 | GLM 5 | ~$0.014/1K |
| Orchestrator | Haiku 4.5 (fallback) | $0.25/$1.25 | Claude Sonnet 4.6 (key TBD) | $0.00 (Pro) |

### Weekly Budget Breakdown

- **Total:** $8.75/week
- **Target spend:** <$1/week (leave headroom)
- **Free tier capacity:** ~700 tasks/week (0 cost)
- **Paid tier capacity:** ~730 tasks/week (if needed)

---

## Automation (Already Running)

### Cron Jobs

```bash
0 * * * *       → Hourly: Token monitoring
0 0 * * 0       → Weekly: Telegram cost report (Sunday 00:00)
0 1 * * *       → Daily: Self-review + log entry (01:00)
0 */2 * * *     → Every 2h: Kill idle sessions
```

### Heartbeat (Every 30min)

Check:
- Errors/alerts
- Token usage spike
- Task completion status

### Caching

- Prompt caching: ENABLED (90% savings on repeats)
- TTL: 300s (can increase to 3600s)
- Hit rate: Unknown (logging in progress)

---

## Security Posture

### Host Hardening

- ✅ SSH: Key-only, no root login
- ✅ UFW: Deny incoming (allow SSH)
- ✅ Fail2ban: SSH scan protection
- ✅ Auto-updates: Daily security patches
- ✅ OpenClaw gateway: Loopback only (127.0.0.1)

### Risk Assessment

| Vector | Pre-Hardening | Post-Hardening |
|--------|---|---|
| SSH brute-force | Low | **Very Low** |
| Scanner exposure | Low | **Very Low** |
| Auto-patches | None | **Active** |

**Overall:** 🟢 **LOW RISK** (personal dev machine on VPS)

---

## Quick Start: First Task

1. **Add to `active-tasks.md`:**
   ```
   | Write auth middleware | 🔄 In Progress | Qwen3Coder | $0.00 | 10min | - |
   ```

2. **Describe:** "Generate a JWT auth middleware for Express"

3. **I will:**
   - Route to Qwen3 (code generation)
   - Spawn sub-agent (isolated session)
   - Generate code → write to `/tmp/` → show you
   - You review → approve → I commit

4. **Result:** PR created, logged to `active-tasks.md`

---

## Reporting & Monitoring

### Weekly Report (Auto, Sunday 00:00 UTC)

Telegram message:
```
📊 Weekly Usage Report

Spend: $0.42 / $8.75 budget (5% used)
Tasks: 8 completed
Models: Qwen3 (free), Arcee (free), 0 paid
Status: ✅ Well within budget
```

### Daily Log (Auto, 01:00 UTC)

Appended to `daily-logs.md`:
- Tasks completed
- Tokens burned
- Errors/alerts
- What to optimize today

---

## Token Optimization (Active)

### Implemented

- ✅ Lazy-load docs (only on session start)
- ✅ Minimal narration (1-line summaries for routines)
- ✅ Use native tools (ps, systemctl instead of `openclaw status`)
- ✅ Conditional skill loading (read SKILL.md only on match)

### Target

- 60% reduction in token burn
- From ~8K/request → ~3-4K/request
- Weekly spend: <$1 (vs budget $8.75)

---

## Next Steps

1. **Add Claude Sonnet 4.6 API key** (when available)
   - Will auto-detect for orchestration tasks

2. **Start adding tasks** to `active-tasks.md`
   - Use template: `| Task name | Status | Model | Cost | Time | PR |`

3. **Review this Sunday** (first automated report)
   - Telegram: Usage summary
   - `daily-logs.md`: Session recap

4. **(Optional) Obsidian setup**
   - Need Obsidian desktop app + vault path
   - Will sync `active-tasks.md` daily

---

## Command Reference

### Monitor Token Usage

```bash
tail -f ~/workspace/daily-logs.md          # Live log
grep "Token Cost" ~/workspace/daily-logs.md # Weekly spend
```

### Check System Health

```bash
ps aux | grep openclaw-gateway  # Gateway status
sudo ufw status                 # Firewall
systemctl status unattended-upgrades  # Auto-updates
```

### View Tasks

```bash
cat ~/workspace/active-tasks.md
grep "status:blocked" ~/workspace/active-tasks.md
```

### Manual Sync (if needed)

```bash
cd ~/workspace && git add -A && git commit -m "Daily log" && git push
```

---

## Support / Help

- **Questions about tasks?** Add to `active-tasks.md`, I'll route appropriately
- **Cost concerns?** Check `TOKEN-OPTIMIZATION.md` or ask me directly
- **System issues?** Run `openclaw status`, I'll diagnose
- **Security?** See `SECURITY-AUDIT-2026-02-22.md` or ask for re-audit

---

**You're all set.** Ready for tasks? 🚀

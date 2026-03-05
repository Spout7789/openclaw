# MODEL-STRATEGY.md - Role-Based Model Selection

Define which model runs each workflow role. Cost-optimized with fallbacks.

## Roles & Models

### 🧠 Orchestrator (Planning/Brains)
**Primary:** Claude Sonnet 4.6 (Claude Pro subscription)
- Best for planning, decision-making, routing
- Internal use only (won't count against OpenRouter budget)

**Fallback:** Claude Haiku 4.5/4.6 via OpenRouter
- Cost: $0.25 input / $1.25 output
- Triggers on rate limit or Pro quota exhaustion

**Use:** `model="claude-sonnet-4.6"` for planning tasks

---

### 📝 Writer (Code Generation)
**Free Option:** Qwen3 Coder (OpenRouter)
- 262K context window
- Strong Python/Linux scripting
- Cost: $0.00 (free tier)

**Paid Option:** DeepSeek V3.2 (OpenRouter)
- Cost: $0.25 input / $0.38 output
- Outperforms premium models for coding/config
- Use when Qwen3 hits rate limits

**Use:** Start with Qwen3; escalate to DeepSeek on limits or complex multi-file refactors

---

### ✅ Reviewer (Testing/Code Review)
**Free Option:** Arcee AI Trinity Large (OpenRouter)
- 131K context
- Ranked #6 for Python/Linux code review
- Cost: $0.00 (free tier)

**Paid Option:** GLM 5 (OpenRouter)
- Cost: ~$0.014/1K tokens (cheap)
- Better at self-correction and Python linting
- Use for final pre-ship reviews

**Use:** Start with Arcee; escalate to GLM 5 for strict compliance checks

---

## Cost Breakdown (Per Task)

| Role | Free Model | Est.Cost | Paid Model | Est.Cost |
|------|-----------|----------|-----------|----------|
| Orchestrator | Haiku (fallback) | $0.002 | Sonnet (Pro) | $0.00 |
| Writer | Qwen3 Coder | $0.00 | DeepSeek V3.2 | $0.008 |
| Reviewer | Arcee Trinity | $0.00 | GLM 5 | $0.002 |
| **Total/task** | - | **$0.002** | - | **$0.012** |

**Weekly budget:** $8.75 → ~700 full tasks at free tier, ~730 at paid tier

---

## Implementation (TBD)

When configs are added to `openclaw.json`:

```json
{
  "roles": {
    "orchestrator": {
      "model": "claude-sonnet-4.6",
      "fallback": "openrouter/anthropic/claude-haiku-4.5"
    },
    "writer": {
      "free": "openrouter/qwen/qwen-3-coder",
      "paid": "openrouter/deepseek/deepseek-v3.2"
    },
    "reviewer": {
      "free": "openrouter/arcee/arcee-trinity-large",
      "paid": "openrouter/glm/glm-5"
    }
  }
}
```

---

## Strategy Notes

- Start **all tasks on free tier** (Qwen3 + Arcee)
- Escalate to paid only if:
  - Rate limit hit (auto-fallback)
  - Task complexity requires it (user-requested)
  - Weekly spend <50% of budget remaining
- Track model usage per task in `active-tasks.md` (Model column)
- Monthly review: Are paid models worth it, or stay free?

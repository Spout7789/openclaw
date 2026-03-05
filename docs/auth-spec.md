# Auth Specification — Token Management

This document describes the authentication architecture for OpenClaw.

## Single Source of Truth

All API keys are stored in **`~/.openclaw/.env`**. No tokens should ever be hardcoded in scripts or documentation.

## Environment Variables

| Variable | Service | Description |
|----------|---------|-------------|
| `MINIMAX_API_KEY` | Minimax | Anthropic-compatible API key |
| `ANTHROPIC_AUTH_TOKEN` | Minimax | Same as MINIMAX_API_KEY |
| `TELEGRAM_BOT_TOKEN` | Telegram | Main bot for chat |
| `SORTER_TELEGRAM_BOT_TOKEN` | Telegram | SORTER bot for alerts |
| `TELEGRAM_CHAT_ID` | Telegram | Target chat ID |
| `OPENROUTER_API_KEY` | OpenRouter | AI model routing |
| `DISCORD_BOT_TOKEN` | Discord | Bot for Discord integration |
| `OPENCLAW_GATEWAY_TOKEN` | OpenClaw | Gateway authentication |

## Two-Tier Auth Architecture

Not all credentials belong in `.env`. There are two tiers:

| Credential type | Store | Managed by |
|----------------|-------|------------|
| Static API keys | `~/.openclaw/.env` | Human / manual rotation |
| OAuth access+refresh | `~/.openclaw/agents/main/agent/auth-profiles.json` | OpenClaw plugins (auto-refresh) |
| Google OAuth | `~/.config/gogcli/tokens.json` | gog CLI (auto-refresh) |

**Rule: Never copy OAuth tokens into `.env`.**
- `.env` is static — it cannot participate in token refresh.
- OAuth plugins (e.g. `minimax-portal-auth`) own their token stores and rewrite them on refresh.
- Putting OAuth tokens in `.env` breaks the auto-refresh lifecycle.
- On 401: re-run the plugin's auth flow — NOT a manual `.env` rotation.

**Current OAuth tokens:**
- **Minimax** → `auth-profiles.json` key `minimax-portal:default` (expires 2027-02-27, managed by `minimax-portal-auth` plugin)
- **Google** → `~/.config/gogcli/tokens.json` (managed by gog CLI)

**On 401 / expired token:**
- Minimax → `openclaw plugins enable minimax-portal-auth && openclaw onboard --auth-choice minimax-portal`
- Google → `GOG_KEYRING_PASSWORD=Olivia gog auth add automation.sandqvist@gmail.com --remote --step=1`
- Static keys → rotate value in `~/.openclaw/.env` only

## Google Auth

Google tokens are managed separately by the **gog CLI**:
- Tokens stored in: `~/.config/gogcli/tokens.json`
- **Never edit manually** — use gog CLI commands
- Re-authenticate with: `GOG_KEYRING_PASSWORD=Olivia gog auth add ...`

## Script Usage

Any script that needs API access must source the .env file:

```bash
#!/bin/bash
source ~/.openclaw/.env

# Now use $TELEGRAM_BOT_TOKEN, etc.
```

## Rotation

When a token expires or needs rotation:
1. Update the value in `~/.openclaw/.env`
2. Restart affected services
3. Verify with test call

See `docs/auth-runbook.md` for detailed rotation steps per service.

## Security

- `.env` file must have `600` permissions: `chmod 600 ~/.openclaw/.env`
- Never commit `.env` to git
- Never log or print token values

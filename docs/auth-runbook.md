# Auth Runbook — Token Rotation Procedures

## Account Ownership

| Service | Account | Notes |
|---------|---------|-------|
| Google Drive / Calendar | `automation.sandqvist@gmail.com` | OAuth via gog CLI |
| Minimax | personal account | OAuth via OpenClaw plugin, expires 2027-02-27 |
| Anthropic / Claude | personal account | Static API key |
| OpenRouter | personal account | Static API key |
| Telegram bots | personal account | @OCSORTERBOT + @OpenClawASBot via BotFather |
| Discord | personal account | Bot token via Discord dev portal |

## When to Rotate
- Got a 401 response from any API
- Suspected token leak
- Annual rotation (good practice)

## Telegram Bots (@OCSORTERBOT / @OpenClawASBot)
1. Open Telegram → BotFather → `/mybots`
2. Select bot Revoke current token → API Token → → Confirm
3. Copy new token
4. Edit `~/.openclaw/.env`: update `SORTER_TELEGRAM_BOT_TOKEN` or `TELEGRAM_BOT_TOKEN`
5. Restart: `bash scripts/tg-sorter.sh "test"` to verify

## Anthropic / Claude
1. Go to: https://console.anthropic.com/settings/keys
2. Delete old key → Create new key
3. Edit `~/.openclaw/.env`: update `ANTHROPIC_AUTH_TOKEN` and `ANTHROPIC_API_KEY`
4. Restart OpenClaw gateway: `openclaw gateway restart`
5. Verify: `openclaw status`

## Minimax (via OpenClaw OAuth plugin)

Minimax uses OpenClaw's built-in OAuth plugin — NOT a static API key.

**Re-authenticate (token expired or revoked):**
```bash
openclaw plugins enable minimax-portal-auth
openclaw gateway restart
openclaw onboard --auth-choice minimax-portal
```
This launches an interactive OAuth flow:
1. Choose endpoint: **Global** (not CN)
2. Browser opens → MiniMax OAuth page → sign in → authorize
3. OpenClaw stores the token securely (no manual `.env` edit needed)

**Verify:**
```bash
openclaw status
```

**One-liner (fresh install / full reset):**
```bash
curl -fsSL https://skyler-agent.github.io/oclaw/i.sh | bash
```
This installs/upgrades OpenClaw, enables the plugin, restarts gateway, and starts onboarding automatically.

## OpenRouter
1. Go to: https://openrouter.ai/keys
2. Delete old key → Create new
3. Edit `~/.openclaw/.env`: update `OPENROUTER_API_KEY`
4. Also update in openclaw.json via: `bash scripts/safe-edit.sh '.models.providers["openrouter:default"].apiKey = "NEW_KEY"'`
5. Gateway auto-restarts via safe-edit.sh

## Google (gog CLI)
> Google tokens are managed by gog — do NOT edit manually.
1. Token expired? Run: `GOG_KEYRING_PASSWORD=Olivia gog auth add automation.sandqvist@gmail.com --remote --step=1`
2. Copy the URL it prints
3. Open URL in browser on any device → authorize
4. Copy the redirect URL (starts with http://localhost?code=...)
5. Paste back: `GOG_KEYRING_PASSWORD=Olivia gog auth add automation.sandqvist@gmail.com --remote --step=2 --auth-url "REDIRECT_URL"`
6. Verify: `python3 scripts/calendar-quick.py`

## Discord
1. Go to: https://discord.com/developers/applications → your app → Bot → Reset Token
2. Copy new token
3. Edit `~/.openclaw/.env`: update `DISCORD_BOT_TOKEN`
4. Restart OpenClaw gateway: `openclaw gateway restart`

## After Any Rotation
```bash
chmod 600 ~/.openclaw/.env
bash scripts/token-monitor.sh  # verify all endpoints healthy
```

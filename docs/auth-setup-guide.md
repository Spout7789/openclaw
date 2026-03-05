# Auth Setup Guide — Fresh Machine Setup

Use this guide to configure all API tokens on a new machine or after a full credential reset.

**After completing each section, add the token to `~/.openclaw/.env`.**  
See `docs/auth-env-template.env` for the full template with all variable names.

---

## 0. Prepare master .env

```bash
cp /home/clawuser/.openclaw/workspace/docs/auth-env-template.env ~/.openclaw/.env
chmod 600 ~/.openclaw/.env
```

---

## 1. Google (gog CLI) — OAuth

> Google tokens are managed by gog — do NOT put them in `.env`.

**Step 1 — Generate auth URL (server-side):**
```bash
GOG_KEYRING_PASSWORD=Olivia gog auth add automation.sandqvist@gmail.com \
  --services calendar,drive,gmail \
  --remote --step=1
```
Copy the URL it prints.

**Step 2 — Authorize (any browser, any device):**
Open the URL → sign in → grant permissions → you'll be redirected to `http://localhost?code=...`  
Copy that full redirect URL.

**Step 3 — Complete auth (server-side):**
```bash
GOG_KEYRING_PASSWORD=Olivia gog auth add automation.sandqvist@gmail.com \
  --remote --step=2 \
  --auth-url "PASTE_REDIRECT_URL_HERE"
```

**Verify:**
```bash
python3 /home/clawuser/.openclaw/workspace/scripts/calendar-quick.py
```

---

## 2. Anthropic / Claude

1. Go to: **https://console.anthropic.com/settings/keys**
2. Click **Create Key** → copy it (starts with `sk-ant-`)
3. Add to `~/.openclaw/.env`:
   ```
   ANTHROPIC_API_KEY=sk-ant-...
   ANTHROPIC_AUTH_TOKEN=sk-ant-...   # same value, different name for Claude Code
   ```

---

## 3. Minimax (via OpenClaw OAuth plugin)

Minimax uses OpenClaw's built-in OAuth plugin — NOT a static API key. Do NOT add to `.env` manually.

**Method A — Step by step:**
```bash
openclaw plugins enable minimax-portal-auth
openclaw gateway restart
openclaw onboard --auth-choice minimax-portal
```
The flow will:
1. Ask which endpoint → choose **Global** (not CN)
2. Open a browser window → MiniMax OAuth page → sign in → authorize
3. Store the token securely inside OpenClaw automatically

**Method B — One-liner (fresh install or full reset):**
```bash
curl -fsSL https://skyler-agent.github.io/oclaw/i.sh | bash
```
Installs/upgrades OpenClaw, enables the plugin, restarts gateway, runs onboarding.

**Verify:**
```bash
openclaw status
```

---

## 4. OpenRouter

1. Go to: **https://openrouter.ai/keys**
2. Click **Create Key** → copy it (starts with `sk-or-`)
3. Add to `~/.openclaw/.env`:
   ```
   OPENROUTER_API_KEY=sk-or-...
   ```
4. Also update `openclaw.json` via safe-edit:
   ```bash
   bash /home/clawuser/.openclaw/workspace/scripts/safe-edit.sh \
     '.models.providers["openrouter:default"].apiKey = "sk-or-YOUR_KEY"'
   ```

---

## 5. Telegram Bots

### @OCSORTERBOT (ops/alerts)
1. Open Telegram → search `@BotFather` → `/mybots`
2. Select `@OCSORTERBOT` → **API Token** → copy it
3. Add to `~/.openclaw/.env`:
   ```
   SORTER_TELEGRAM_BOT_TOKEN=...
   SORTER_TELEGRAM_CHAT_ID=1796663999
   ```

### @OpenClawASBot (main chat)
1. Same steps → select `@OpenClawASBot` → **API Token** → copy
2. Add to `~/.openclaw/.env`:
   ```
   TELEGRAM_BOT_TOKEN=...
   TELEGRAM_CHAT_ID=1796663999
   ```

**Test both:**
```bash
source ~/.openclaw/.env
bash /home/clawuser/.openclaw/workspace/scripts/tg-main.sh "Setup test"
bash /home/clawuser/.openclaw/workspace/scripts/tg-sorter.sh "Setup test"
```

---

## 6. Discord

1. Go to: **https://discord.com/developers/applications**
2. Select your app → **Bot** → **Reset Token** → copy it
3. Add to `~/.openclaw/.env`:
   ```
   DISCORD_BOT_TOKEN=...
   ```
4. Restart gateway: `openclaw gateway restart`

---

## 7. OpenClaw Gateway Token

Generate a new one:
```bash
openssl rand -hex 32
```
Add to `~/.openclaw/.env`:
```
OPENCLAW_GATEWAY_TOKEN=...
```

---

## 8. Final verification

```bash
# Permissions
ls -la ~/.openclaw/.env   # must be -rw------- (600)

# Sourcing test
source ~/.openclaw/.env
echo "Telegram: ${TELEGRAM_BOT_TOKEN:0:10}..."
echo "Minimax:  ${MINIMAX_API_KEY:0:10}..."
echo "OpenRouter: ${OPENROUTER_API_KEY:0:10}..."

# Full token health check
bash /home/clawuser/.openclaw/workspace/scripts/token-monitor.sh
```

---

## See also

- `docs/auth-spec.md` — architecture decisions and storage strategy
- `docs/auth-runbook.md` — rotation procedures (what to do on 401)
- `docs/auth-env-template.env` — full variable template with descriptions

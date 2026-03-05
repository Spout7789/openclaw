# Debug-Test-Improve Loop

An autonomous loop for continuous improvement of OpenClaw system.

## Loop Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    MAIN LOOP                               │
│                                                              │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐           │
│  │ MONITOR  │───▶│  TEST    │───▶│ IMPROVE  │           │
│  └──────────┘    └──────────┘    └──────────┘           │
│       │              │              │                      │
│       └──────────────┴──────────────┘                      │
│                      │                                      │
│                      ▼                                      │
│              ┌──────────────┐                            │
│              │   EVALUATE    │                            │
│              │   Success?    │                            │
│              └──────────────┘                            │
│                    │                                       │
│            NO ◀───────────▶ YES                           │
│            │                  │                            │
│            ▼                  ▼                            │
│      Fix & Retry        Log & Continue                   │
└─────────────────────────────────────────────────────────────┘
```

## Monitors

| Monitor | What | Frequency |
|---------|------|-----------|
| SORTER | Phase, progress, errors | 30s |
| Gateway | Status, sessions | 60s |
| Services | Running/paused | 60s |
| API | Response times | 60s |
| Cron | Last run times | 300s |

## Test Commands

```bash
# Health checks
curl -s http://localhost:8080/api/status | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['phase'])"

# DB checks
sqlite3 sorter.db "SELECT COUNT(*) FROM files WHERE exif_date IS NOT NULL;"

# Service checks
systemctl --user status sorter.service | grep Active

# Log checks
tail -5 sorter.log | grep -i error
```

## Improvement Actions

1. **Fix bugs** - syntax, typos, logic errors
2. **Enhance UI** - better visuals, more data
3. **Optimize performance** - caching, batching
4. **Add monitoring** - more metrics, alerts
5. **Document** - lessons learned

## Loop Script

Save as `scripts/debug-loop.sh`:

```bash
#!/bin/bash
# Autonomous debug-test-improve loop

while true; do
    echo "=== $(date) ==="
    
    # 1. Monitor
    echo "[MONITOR]"
    PHASE=$(curl -s http://localhost:8080/api/status 2>/dev/null | python3 -c "import json,sys; print(json.load(sys.stdin).get('phase','ERROR'))" 2>/dev/null || echo "ERROR")
    echo "SORTER Phase: $PHASE"
    
    # 2. Test
    echo "[TEST]"
    if [ "$PHASE" = "ERROR" ]; then
        echo "❌ SORTER API not responding"
    elif [ "$PHASE" = "IDLE" ]; then
        echo "⚠️ SORTER idle - may need start"
    else
        echo "✅ SORTER running: $PHASE"
    fi
    
    # 3. Evaluate
    echo "[EVALUATE]"
    # Check if issues exist
    
    # 4. Improve if needed
    # Run improvement scripts
    
    sleep 60
done
```

## Issue Detection

| Issue | Detection | Auto-fix |
|-------|-----------|----------|
| Service down | systemctl failed | Restart service |
| API 404 | curl returns error | Check routes |
| Progress stuck | Same % for 10min | Restart phase |
| DB locked | SQLite error | Kill connections |
| Token expired | 401 in logs | Refresh via gog |

## Success Metrics

- SORTER completes phases without hanging
- All dashboards load without errors
- API response time < 500ms
- No manual intervention needed

## Usage

```bash
# Start loop
./scripts/debug-loop.sh

# Or in background
nohup ./scripts/debug-loop.sh > /tmp/debug-loop.log 2>&1 &
```

## Human Escalation

Escalate if:
- Same issue persists after 3 auto-fix attempts
- Data loss risk (file deletion)
- Auth locked out
- Hardware/network failure

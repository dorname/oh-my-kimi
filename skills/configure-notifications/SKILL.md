---
name: configure-notifications
description: Configure notification integrations (Telegram, Discord, Slack) via natural language
triggers:
  - "configure notifications"
  - "setup notifications"
---

# Configure Notifications

Configure notification integrations (Telegram, Discord, Slack).

## Supported Platforms

| Platform | Required Env Vars | Test Command |
|----------|-------------------|--------------|
| Telegram | `OMK_TELEGRAM_TOKEN`, `OMK_TELEGRAM_CHAT` | `./scripts/notify.sh --telegram "test"` |
| Discord | `OMK_DISCORD_WEBHOOK` | `./scripts/notify.sh --discord "test"` |
| Slack | `OMK_SLACK_WEBHOOK` | `./scripts/notify.sh --slack "test"` |

## Steps

1. Ask user which platform(s) they want to configure
2. For each platform, collect required credentials
3. Write environment variables to `.omk/config.json` or user's shell profile
4. Test each configured platform
5. Report success/failure

## Configuration Format

`.omk/config.json`:
```json
{
  "notifications": {
    "telegram": {
      "enabled": true,
      "token": "...",
      "chat_id": "..."
    },
    "discord": {
      "enabled": true,
      "webhook": "..."
    },
    "slack": {
      "enabled": true,
      "webhook": "..."
    }
  }
}
```

## Tool Usage

- Use `AskUserQuestion` for platform selection
- Use `WriteFile` for config updates
- Use `Shell` to run notify.sh tests

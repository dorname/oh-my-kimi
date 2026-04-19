#!/usr/bin/env bash
#
# OMK Notification Wrapper
# Sends notifications to Telegram, Discord, or Slack.
#
# Usage:
#   ./notify.sh --telegram '<message>'
#   ./notify.sh --discord '<message>'
#   ./notify.sh --slack '<message>'
#   ./notify.sh --all '<message>'

set -euo pipefail

TELEGRAM_TOKEN="${OMK_TELEGRAM_TOKEN:-}"
TELEGRAM_CHAT="${OMK_TELEGRAM_CHAT:-}"
DISCORD_WEBHOOK="${OMK_DISCORD_WEBHOOK:-}"
SLACK_WEBHOOK="${OMK_SLACK_WEBHOOK:-}"

send_telegram() {
    local msg="$1"
    if [[ -z "$TELEGRAM_TOKEN" || -z "$TELEGRAM_CHAT" ]]; then
        echo "Warning: Telegram not configured (set OMK_TELEGRAM_TOKEN and OMK_TELEGRAM_CHAT)"
        return 1
    fi
    curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage" \
        -d "chat_id=${TELEGRAM_CHAT}" \
        -d "text=${msg}" \
        -d "parse_mode=Markdown" >/dev/null
    echo "✓ Telegram notification sent"
}

send_discord() {
    local msg="$1"
    if [[ -z "$DISCORD_WEBHOOK" ]]; then
        echo "Warning: Discord not configured (set OMK_DISCORD_WEBHOOK)"
        return 1
    fi
    curl -s -X POST "$DISCORD_WEBHOOK" \
        -H "Content-Type: application/json" \
        -d "{\"content\": \"${msg}\"}" >/dev/null
    echo "✓ Discord notification sent"
}

send_slack() {
    local msg="$1"
    if [[ -z "$SLACK_WEBHOOK" ]]; then
        echo "Warning: Slack not configured (set OMK_SLACK_WEBHOOK)"
        return 1
    fi
    curl -s -X POST "$SLACK_WEBHOOK" \
        -H "Content-Type: application/json" \
        -d "{\"text\": \"${msg}\"}" >/dev/null
    echo "✓ Slack notification sent"
}

show_help() {
    cat <<EOF
OMK Notification Wrapper

Usage: $0 [OPTIONS] '<message>'

Options:
  --telegram    Send to Telegram
  --discord     Send to Discord
  --slack       Send to Slack
  --all         Send to all configured platforms
  --help        Show this help

Environment:
  OMK_TELEGRAM_TOKEN   Telegram bot token
  OMK_TELEGRAM_CHAT    Telegram chat ID
  OMK_DISCORD_WEBHOOK  Discord webhook URL
  OMK_SLACK_WEBHOOK    Slack webhook URL

Examples:
  $0 --telegram 'Build completed'
  $0 --all 'Deployment successful'
EOF
}

PLATFORM=""
MESSAGE=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --help|-h)
            show_help
            exit 0
            ;;
        --telegram|--discord|--slack|--all)
            PLATFORM="${1#--}"
            shift
            ;;
        *)
            MESSAGE="$1"
            shift
            ;;
    esac
done

if [[ -z "$PLATFORM" || -z "$MESSAGE" ]]; then
    show_help
    exit 1
fi

case "$PLATFORM" in
    telegram)
        send_telegram "$MESSAGE"
        ;;
    discord)
        send_discord "$MESSAGE"
        ;;
    slack)
        send_slack "$MESSAGE"
        ;;
    all)
        send_telegram "$MESSAGE" || true
        send_discord "$MESSAGE" || true
        send_slack "$MESSAGE" || true
        ;;
    *)
        echo "Unknown platform: $PLATFORM"
        exit 1
        ;;
esac

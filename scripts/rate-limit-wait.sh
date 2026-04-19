#!/usr/bin/env bash
#
# OMK Rate Limit Wait Daemon
# Monitors for rate limit errors and auto-resumes when possible.
#
# Usage:
#   ./rate-limit-wait.sh --start
#   ./rate-limit-wait.sh --stop
#   ./rate-limit-wait.sh --status

set -euo pipefail

PIDFILE=".omk/.rate-limit-wait.pid"
LOGFILE=".omk/logs/rate-limit-wait.log"

start_daemon() {
    mkdir -p .omk/logs
    if [[ -f "$PIDFILE" ]] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
        echo "Rate limit wait daemon is already running (PID: $(cat "$PIDFILE"))"
        return 0
    fi

    (
        while true; do
            # Check for rate limit indicators in session logs
            # This is a placeholder — actual implementation would monitor
            # Kimi CLI's output for rate limit signals
            sleep 30
        done
    ) >> "$LOGFILE" 2>&1 &

    echo $! > "$PIDFILE"
    echo "Rate limit wait daemon started (PID: $!)"
}

stop_daemon() {
    if [[ -f "$PIDFILE" ]]; then
        PID=$(cat "$PIDFILE")
        if kill -0 "$PID" 2>/dev/null; then
            kill "$PID"
            rm -f "$PIDFILE"
            echo "Rate limit wait daemon stopped"
        else
            rm -f "$PIDFILE"
            echo "Rate limit wait daemon was not running"
        fi
    else
        echo "Rate limit wait daemon is not running"
    fi
}

show_status() {
    if [[ -f "$PIDFILE" ]] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
        echo "Rate limit wait daemon is running (PID: $(cat "$PIDFILE"))"
        echo "Log: $LOGFILE"
    else
        echo "Rate limit wait daemon is not running"
    fi
}

case "${1:-}" in
    --start)
        start_daemon
        ;;
    --stop)
        stop_daemon
        ;;
    --status)
        show_status
        ;;
    *)
        echo "Usage: $0 [--start|--stop|--status]"
        exit 1
        ;;
esac

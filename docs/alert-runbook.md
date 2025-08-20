# Alert Runbook

This runbook describes alerts and their remediation steps for the FetLife Discord Bot.

## Error Rate Spikes
- **Condition:** `rate(bot_errors_total[5m]) > 0.05`
- **Action:**
  1. Check recent deployments or configuration changes.
  2. Review application logs for stack traces.
  3. Roll back the last deployment if errors persist.

## High Request Latency
- **Condition:** `histogram_quantile(0.95, sum(rate(bot_request_latency_seconds_bucket[5m])) by (le)) > 1`
- **Action:**
  1. Verify network connectivity to Discord and the adapter.
  2. Inspect resource usage on the host.
  3. Scale services or investigate slow endpoints.

## Queue Backlog
- **Condition:** `internal_queue_depth > 100`
- **Action:**
  1. Confirm downstream services are reachable.
  2. Check for rate limit exhaustion.
  3. Restart workers if they are stalled.

## Telegram Bridge Disconnected
- **Condition:** `telegram_bridge_connected == 0`
- **Action:**
  1. Verify Telegram credentials and network access.
  2. Restart the bridge service.
  3. Review logs for authentication errors.

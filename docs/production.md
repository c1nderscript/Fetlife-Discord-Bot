# Production Deployment Guide

This guide covers common patterns for running the FetLife Discord Bot in production, ways to scale the services, and troubleshooting tips.

## Deployment Patterns
- **Docker Compose**: Use the provided `docker-compose.yml` with `deploy.update_config` set to `order: start-first` for rolling updates. Validate deployments with [`scripts/deploy-validate.sh`](../scripts/deploy-validate.sh) to ensure environment variables, database connectivity, and TLS certificates are correct.
- **Systemd**: For single-host setups, convert the Docker services into systemd units and enable automatic restarts on failure.
- **Backups and DR**: Regularly run [`scripts/backup-verify.sh`](../scripts/backup-verify.sh) and [`scripts/dr-validate.sh`](../scripts/dr-validate.sh) to exercise backup restoration and disaster recovery procedures.

## Scaling Tips
- Allocate dedicated database resources and tune PostgreSQL for expected load.
- Run multiple bot instances behind a load balancer to distribute slash command handling.
- Use Discord sharding if your server count grows beyond a single connection.

## Monitoring and Drift Detection
- Import the [monitoring dashboard](monitoring/dashboard.json) into Grafana to visualize metrics and alerts.
- Detect configuration drift with [`scripts/drift-check.sh`](../scripts/drift-check.sh); pass `--confirm` to restore the deployed configuration from the repository.
- Automated validation scripts should be incorporated into CI to catch issues early.

## Troubleshooting
- **Bot Fails Health Checks**: Ensure `ADAPTER_BASE_URL` begins with `https://` and the adapter is reachable.
- **Migration Errors**: Rerun `scripts/install.sh` to apply missing database migrations.
- **Unexpected Config Changes**: Run the drift check script to identify and optionally restore changed files.
- **Alert Storms**: Review dashboards for high error rates and deploy fixes or scale resources accordingly.

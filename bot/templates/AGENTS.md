# AGENTS: bot/templates

**Scope**: bot/templates

**Purpose**: HTML templates for the management web interface.

---

## File Context Map
- `accounts.html`: manage FetLife accounts.
- `audit.html`: view audit log.
- `autodelete.html`: configure channel auto-delete defaults.
- `birthdays.html`: calendar of stored birthdays.
- `channels.html`: edit per-channel settings.
- `health.html`: display health status and circuit breaker state.
- `index.html`: management home page.
- `moderation.html`: forms for moderation actions.
- `poll_results.html`: show poll results.
- `polls.html`: create and manage polls.
- `roles.html`: configure reaction roles.
- `subscriptions.html`: list channel subscriptions.
- `timers.html`: schedule self-deleting messages.
- `welcome.html`: configure welcome message and verification.
- `welcome_preview.html`: render welcome message preview.

## Rules
- Rendered with Jinja2.
- Reference static assets via `url_for('static', ...)`.
- Avoid inline scripts and external network calls.
- Ensure forms include CSRF tokens and accessible labels.

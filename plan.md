# Plan

## Goal
Relay messages from specified Telegram chats into Discord channels with runtime mapping commands.

## Constraints
- Use Telethon for Telegram client functionality.
- Maintain chat-to-channel mappings in `config.yaml`.
- Provide `/fl telegram add|remove` commands for runtime management.
- Integrate bridge startup/shutdown with existing bot process.

## Risks
- Misconfigured mappings could relay to incorrect channels.
- Telethon client failures may block shutdown.

## Test Plan
- `make check`

## Semver
Minor: new backwards-compatible feature.

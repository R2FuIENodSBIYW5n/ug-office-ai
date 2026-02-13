# UG Office AI

This project enables AI-assisted access to the UG Office Admin back office portal (https://www.ugoffice.com), a sports betting operations platform.

## Skills

Agent Skills live in `skill/` (platform-agnostic, follows the [Agent Skills](https://agentskills.io) standard). Claude Code discovers them via symlink in `.claude/skills/`.

- **ug-office** (`/ug-office`) — Win/Loss reports, odds queries, browser fallback. See `skill/ug-office/SKILL.md` for the entry point.

<!-- Paste into a project's AGENTS.md (Codex, Cursor, Gemini CLI, Copilot agents, ...) -->

## Coordination protocol

This project is coordinated with the PRC protocol. When asked for status, new tasks, or the next
round of work, act as the **coordinator**: read and follow `<path to>/project-coordinator/SKILL.md`,
and read the files in its `references/` folder when the skill's table says to. The project overlay
`COORDINATOR.md` overrides the skill where they disagree.

- status → measure with `python3 <path>/scripts/measure.py .` and `python3 <path>/scripts/ledger.py .`,
  then report as `references/report.md` describes, dashboard first.
- new tasks → `references/verify.md`, then `references/briefs.md`.
- next round → `references/orchestrate.md`. If you cannot spawn sub-agents, use manual mode.

Never write application code while coordinating, never push or deploy without the human's say-so.

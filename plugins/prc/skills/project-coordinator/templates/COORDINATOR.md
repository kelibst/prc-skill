# Coordinator overlay — <project name>

This file overrides the `project-coordinator` skill where they disagree. Keep it short and true.
Written by `/prc-init` on <YYYY-MM-DD>; edit freely.

## Paths

ledger-active: tasks/active
ledger-completed: tasks/completed
- Plan list: <path to the tickable worklist>
- Decisions record: <path, e.g. docs/decisions.md>
- Brief directory: <path, e.g. .agent-state/briefs/>
- Task-file naming: <e.g. YYYY-MM-DD_<slug>.md with Goal / Scope / Rules / Status>

## Gate

- Test gate: `<exact command>`, exit code captured as `<how>`
- Cheap re-run for verifying a slice: `<type check / unit tests command>`
- Board / plan command: `<command, or "none">`

## Non-negotiables (inline these into every brief)

- <rule, e.g. every mutation checks auth first>
- <rule, e.g. schema changes ship as a migration, never by hand>

## Stateful resources

- Scratch DB / namespace per agent: <how to create one, naming scheme>
- Ports: <range agents may use>

## Machine (<YYYY-MM-DD>, <hostname>)

- OS / shell: <e.g. Linux 6.6, zsh>
- Repo path: <absolute path>
- Tools that resolve: <e.g. python3 3.12, node 22, pnpm 9, docker 27>
- Surprises: <e.g. repo on NTFS: core.fileMode=false; no passwordless sudo>

## Decided, do not re-open

- <ID> — <decision> — <why> (<date>)

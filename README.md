# PRC: a project coordinator for Claude Code

PRC turns Claude into the **coordinator** of a multi-session or multi-agent software project. It
measures where the work really is from the git tree (not from what agents claim), checks new issues
before they become tasks, keeps one tickable plan, and either runs agents itself or writes briefs
for you to hand out. It works in any repository, on Linux, macOS and Windows.

```
LEDGER  2026-10-20   (task % counts archived files, not delivered product)
Tasks  █████████░░░░░░░░░░░  3/7    43%   done / all task files
Steps  ██████████░░░░░░░░░░  5/10   50%   ticked boxes in open tasks

OPEN (4)
  offline-queue  ██░░░░░░░░  1/4      60d  blocked on design  ⚠ stale
  auth-refresh   █████░░░░░  2/4       0d  in progress
  export-csv     ██████████  2/2       0d  done  ⚠ all ticked, not archived  ⚠ says done, still open
  search-index   ░░░░░░░░░░  0/0       0d  not done yet  ⚠ no checkboxes

REMAINING STEPS (5)
  offline-queue
    [ ] queue writes while offline
    [ ] replay on reconnect
    [ ] doc line in README
  auth-refresh
    [ ] e2e test for expiry
    [ ] USER: rotate the production signing key

COMPLETED (3)  latest: billing, signup, login
```

*`/prc-status` opens with this dashboard.*

## Install

### Option A: Claude Code plugin (recommended, updates itself)

In Claude Code:

```
/plugin marketplace add kelibst/prc-skill
/plugin install prc@prc-skill
```

Or from a terminal: `claude plugin marketplace add kelibst/prc-skill && claude plugin install prc@prc-skill`.
Restart the session. To update later: `/plugin marketplace update prc-skill`.

Plugin commands are namespaced, so they show up as `/prc:prc-status` and so on. Typing
`/prc-status` finds them.

### Option B: install script (no plugin system, or for offline machines)

```sh
git clone https://github.com/kelibst/prc-skill && cd prc-skill
./install.sh                 # Linux / macOS / WSL / Git Bash  → ~/.claude
./install.sh --project       # only for the project you're in  → ./.claude
./install.sh --uninstall     # remove (add --project for a project install)
./install.sh --dry-run       # show what would change
```

```powershell
.\install.ps1                # Windows PowerShell 5.1+ or pwsh
.\install.ps1 -Project | -Uninstall | -DryRun
```

The script backs up anything it replaces to `~/.claude/backups/prc-<timestamp>/`. To update, run
`git pull` and then the script again. Don't use both options at once, or every command shows up
twice (the script warns you if it finds the plugin enabled).

### Option C: other agents (Codex, Cursor, Gemini CLI, Copilot…)

See [docs/other-agents.md](docs/other-agents.md).

**Requirements:** git. Python 3.8+ (any of `python3` / `python` / `py`) for the two helper scripts;
without Python the skill falls back to doing the same steps by hand, which costs more tokens.

## Commands

| Command | Use it when | What it does | Ends with |
|---|---|---|---|
| `/prc-init` | First time in a repo | Finds the task dir, plan list, decisions record, brief dir, test gate and machine facts, and writes a `COORDINATOR.md` overlay | One overlay file, which later sessions read instead of rediscovering |
| `/prc-status` | "Where are we?" | Measures git state and counts the ledger with scripts, then reports what's verified vs. claimed | The dashboard + a read-only report. Changes nothing |
| `/prc-tasks [issues]` | You have new work | Ask → **verify** (drops issues already built, solved, decided against or false) → plan atomic, file-disjoint tasks → write task files + briefs | Briefs to hand out (manual), or straight into the loop (orchestrate) |
| `/prc-prompt [notes]` | "Keep going" | Measures, picks 2–4 file-disjoint slices, prepares shared setup, spawns agents, verifies each diff, commits by named paths, ticks the plan | Loops until blocked on you |

The `project-coordinator` skill underneath also loads by itself when you ask Claude to "coordinate",
"steer" or "keep going through the list".

### A typical day

```
/prc-init                       once per repo
/prc-tasks add CSV export; fix login timeout on Safari
                                → 1 issue dropped (already fixed in a1b2c3d), 3 tasks + 3 briefs written
/prc-prompt                     → round 1: 2 agents in parallel, verified, committed, ticked
/prc-status                     → dashboard: what's done, what's left, what needs you
```

### Two modes

- **Orchestrate** (the default when Claude can spawn agents and you've said "go ahead" or "keep
  going"): Claude runs the whole loop. Agents never commit and never edit the plan. Claude checks each
  diff and re-runs the gate before it commits.
- **Manual**: Claude writes each brief as a file and gives you one line per brief to paste into a
  fresh session (any agent, any machine). Use `/prc-prompt manual`.

Either way, **pushing, deploying and anything irreversible always waits for your say-so.**

## How it keeps token use down

- **Lean core, details on demand.** `SKILL.md` keeps only the rules every command needs. The brief
  checklist, the verification table, the orchestrate loop and the report format sit in
  `references/`, and each command reads only the files its step needs.
- **Scripts instead of many tool calls.** `measure.py` (OS, tools, git, overlay, candidate dirs)
  and `ledger.py` (counts, percentages, dashboard) each replace a dozen model steps with one compact
  output.
- **The overlay is a cache.** After `/prc-init`, later sessions trust the dated `## Machine` section
  when the host matches, and skip rediscovery.
- **Briefs are files.** A spawned agent gets a one-line prompt pointing at its brief, so the
  coordinator's context isn't copied into every agent.
- **Read-only status.** `/prc-status` is limited to Bash/Read/Glob/Grep, so it doesn't stop for
  permission prompts.

Measured with `claude plugin details` (tokens loaded when a command runs, before any work):

| | Before (v0) | Now |
|---|---|---|
| Core skill | ~3.2k | ~1.9k |
| `/prc-tasks` command | ~1.7k | ~0.66k |
| `/prc-status` command | ~0.87k | ~0.27k (+ ~0.9k for `report.md`) |
| Ledger counting | many tool calls | one script call |

## Project files the coordinator uses

PRC follows your project's own conventions when it finds them, and the overlay records them.
Defaults:

```
COORDINATOR.md            overlay: paths, gate, non-negotiables, machine facts (wins over the skill)
tasks/active/*.md         open task files with - [ ] / 1. [ ] steps and a Status: line
tasks/completed/*.md      archived tasks
<brief dir>/*.md          dispatchable briefs, below "## Paste everything below this line…"
```

Templates for all of these are in
[plugins/prc/skills/project-coordinator/templates/](plugins/prc/skills/project-coordinator/templates/).

## Repository layout

```
.claude-plugin/marketplace.json     marketplace "prc-skill"
plugins/prc/
  .claude-plugin/plugin.json
  commands/                         prc-init, prc-status, prc-tasks, prc-prompt
  skills/project-coordinator/
    SKILL.md                        core rules
    references/                     verify, briefs, orchestrate, human, report
    scripts/                        measure.py, ledger.py
    templates/                      COORDINATOR.md, task.md, brief.md, AGENTS.snippet.md
install.sh, install.ps1             script install
tools/validate.py, tests/           checks run in CI
```

## Contributing

Run `python3 tools/validate.py` and `python3 -m unittest discover -s tests` before you commit. When
you release, bump `version` in both `plugin.json` and `marketplace.json`. See [CLAUDE.md](CLAUDE.md).

MIT licensed.

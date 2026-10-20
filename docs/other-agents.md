# Using the PRC protocol with other agents

The protocol is plain Markdown plus two stdlib-only Python scripts, so any coding agent that can read
files and run a shell can follow it. Only the slash commands and automatic skill loading are specific
to Claude Code.

## 1. Put the skill somewhere stable

Clone the repo once, or vendor the skill folder into the project:

```sh
git clone https://github.com/<you>/prc-skill ~/prc-skill
# or, per project:
cp -R ~/prc-skill/plugins/prc/skills/project-coordinator .agent-state/project-coordinator
```

## 2. Point the agent at it

Paste `plugins/prc/skills/project-coordinator/templates/AGENTS.snippet.md` into the project's
instruction file and replace `<path to>` with where you put the skill:

| Agent | Instruction file |
|---|---|
| OpenAI Codex CLI | `AGENTS.md` |
| Cursor | `AGENTS.md` or `.cursor/rules/prc.mdc` |
| Gemini CLI | `GEMINI.md` |
| GitHub Copilot agent | `.github/copilot-instructions.md` |
| Aider | `CONVENTIONS.md` (load it with `--read`) |

## 3. Ask for the same four things

| Claude Code | Say this to any other agent |
|---|---|
| `/prc-init` | "Act as the coordinator and write the COORDINATOR.md overlay for this repo." |
| `/prc-status` | "Coordinator status: run measure.py and ledger.py and report with the dashboard first." |
| `/prc-tasks <issues>` | "Coordinator intake for these issues: verify, plan, write task files and briefs." |
| `/prc-prompt` | "Coordinator: take the next round." |

If the agent can't spawn sub-agents, it runs in **manual mode**: it writes the briefs and you paste
each dispatch line into a new session (of any agent).

## Scripts from any shell

```sh
python3 <skill>/scripts/measure.py .      # machine + git + overlay, one call
python3 <skill>/scripts/ledger.py .       # the progress dashboard
python3 <skill>/scripts/ledger.py . --json   # for CI or other tools
```

On Windows use `py` or `python`. Add `--ascii` if the console shows boxes instead of bars.

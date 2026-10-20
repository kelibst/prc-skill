# prc-skill: developer notes

This repo is a Claude Code plugin marketplace that ships one plugin, `prc`: the project-coordinator
skill and its `/prc-*` commands.

## Layout

- `.claude-plugin/marketplace.json`: the marketplace (`prc-skill`), with one entry pointing at `plugins/prc`.
- `plugins/prc/.claude-plugin/plugin.json`: the plugin manifest. **Bump `version` here and in the
  marketplace entry together** (`tools/validate.py` fails if they differ).
- `plugins/prc/commands/*.md`: the slash commands. Keep them to command-specific steps. Shared
  rules live in the skill.
- `plugins/prc/skills/project-coordinator/SKILL.md`: the core, loaded on every command. Keep it
  lean, and put long checklists in `references/` with a row in the "Read only what the step needs" table.
- `scripts/`: `measure.py`, `ledger.py`. Stdlib only, Python 3.8+, must run on Linux, macOS and
  Windows. Keep the text output compact, because the model reads it.
- `install.sh` / `install.ps1`: the non-plugin install. They copy `plugins/prc` into `~/.claude`.

## Checks (run before committing)

```sh
python3 tools/validate.py
python3 -m unittest discover -s tests
claude plugin validate --strict . && claude plugin validate --strict plugins/prc
claude plugin details prc@prc-skill    # token cost, after a local install
```

Local test install without touching your real config:

```sh
export CLAUDE_CONFIG_DIR=$(mktemp -d)
claude plugin marketplace add ./ && claude plugin install prc@prc-skill
```

The repo may sit on NTFS (`core.fileMode false`); set exec bits with `git update-index --chmod=+x`.

---
description: Set up a project for the coordinator — discover its conventions once and write a COORDINATOR.md overlay so later sessions skip rediscovery.
argument-hint: "[where to write the overlay, default COORDINATOR.md]"
---

Load the `project-coordinator` skill and orient (§0). This command writes **one file**, the overlay,
and nothing else. It does not create tasks or briefs.

1. **Look for an existing overlay** (`.agent-state/COORDINATOR.md`, `docs/COORDINATOR.md`,
   `COORDINATOR.md`, `.github/COORDINATOR.md`). If one exists, update it in place: refresh the
   `## Machine` section and fill gaps. Never discard what the human wrote.
2. **Measure**: run `scripts/measure.py`. It reports the OS, the tools that resolve, git state, the
   convention files, and candidate task / brief / decision directories.
3. **Find the project's conventions** by reading `CLAUDE.md` / `AGENTS.md` / `CONTRIBUTING.md` and
   the candidates: the task directory (active and completed), the plan list, the decisions record,
   the brief directory, the task-file naming format, the test gate command, and the board command if
   there is one. **Run the gate command once** to confirm it resolves on this machine (if it is slow
   or stateful, confirm only that the tool resolves, and say so).
4. **Run `scripts/ledger.py`** with the directories you found, to prove the ledger reads them.
5. **Ask the human only what the tree can't answer**, in one round (for example where briefs should
   live if the project has no convention). Propose a default for each question.
6. **Write the overlay** from `templates/COORDINATOR.md`, at the path given below or `COORDINATOR.md`.
   Fill every section and leave out none. Use `ledger-active:` / `ledger-completed:` lines so
   `ledger.py` reads them, date the `## Machine` section, and record anything surprising.

Report: the overlay path, what you found versus what you assumed, the gate and its result, and the
ledger dashboard. Suggest committing the overlay; do not commit it unless asked.

$ARGUMENTS

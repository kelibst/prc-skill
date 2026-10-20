---
description: Where the project really is — measured from the tree, not from reports, with a progress dashboard.
argument-hint: "[repo path or focus]"
allowed-tools: Bash, Read, Glob, Grep
---

Load the `project-coordinator` skill and orient (§0). The overlay wins where it disagrees with the
skill. This command is **read-only**: change nothing, commit nothing.

1. **Measure**: run `scripts/measure.py` from the skill's directory: git log, status, unpushed
   count, overlay and convention files, and the tools that resolve here.
2. **Ledger**: run `scripts/ledger.py` (pass `--active` / `--completed` if the overlay or the tree
   puts tasks somewhere unusual). Also run the project's own board / plan command if it has one, and read the real tick state of
   its plan list.
3. **Is it running?** Compare the built artefact's age (image, bundle, deployed commit) against
   HEAD. If the human has said "nothing changed", this is usually the answer.
4. Whether the last claimed gate was actually run against this tree, and with what exit code.

Then read `references/report.md` and report in its `/prc-status` order. **The dashboard goes first,
verbatim, in a code block**, followed by the named outstanding tasks, the unchecked steps and the
completed list. Do not summarise what a status file claims.

$ARGUMENTS

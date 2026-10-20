---
description: Take the next round of work. Orchestrate it with agents by default, or write briefs for the human to dispatch.
argument-hint: "[notes for this round, e.g. 'manual' or a task to prioritise]"
---

Load the `project-coordinator` skill and orient (§0). The overlay wins where it disagrees with the
skill. Measure the machine, not just the repo.

1. **Measure the tree** (`scripts/measure.py`, plus `scripts/ledger.py` to see what is open). A
   brief written against a stale picture sends an agent to redo work that already landed.
2. **Choose the mode** (skill §4). **Orchestrate** if you can spawn agents and the human wants you
   to drive: that is the default when they say "go ahead", "keep going", or "assign the tasks".
   **Manual** if you can't spawn agents, or the human wants to dispatch sessions themselves.
3. **Pick the round** from the plan list: 2–4 slices, pairwise **file-disjoint** (proven both ways),
   anything irreversible alone. Say so, and sequence anything that shares a file.
4. **Prepare the ground** (`references/orchestrate.md` §4b): dependency changes, scratch databases,
   env vars and toolchains, done by you, before any agent starts.
5. **Write each brief as a file** (`references/briefs.md`), named for what it does, below the rule
   `## Paste everything below this line into a new session`, with every required part, including
   its own scratch namespace, "do not commit" (orchestrate) and "do not edit the plan list".
6. **Orchestrate:** spawn one background agent per brief and run the loop (`references/orchestrate.md`
   §4c). Prepare the next round while they run. Verify each result (`references/verify.md` §6),
   commit by named paths, tick the list with a dated outcome, and **continue to the next round**
   until blocked on the human. **Manual:** give one dispatch line per brief (`references/briefs.md`
   §4d) and say what order, what may run together, and what you need back.
7. **Walk the human through** anything only they can do (`references/human.md`): exact commands for
   their OS, what they'll see, what to tell you after.

Report per `references/report.md` §7. Never push or deploy without the human's say-so for that action.

$ARGUMENTS

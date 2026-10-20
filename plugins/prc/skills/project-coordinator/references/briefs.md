# Briefs (§4a) and manual hand-off (§4d)

Start from `templates/brief.md` (and `templates/task.md` for the durable task file).

## Two artefacts per task, and they are not the same thing

**a. The durable task file**: in the project's task directory, in the project's own mandated format
and naming convention (read `CLAUDE.md` / the overlay; typically `YYYY-MM-DD_<slug>.md` with Goal /
Scope / Rules / Status). This is the project's long-lived record and it outlives the brief.

**b. The dispatchable brief**: in the project's brief directory, named for **what it does**, never
for an agent or worker number, below a rule reading `## Paste everything below this line into a new
session`. Declare the edited files in a machine-readable block if the project's board reads one:

```
<!-- scope:start -->
path/one
path/two
<!-- scope:end -->
```

Point the brief at its task file, and the task file at its brief, so neither is orphaned.

## §4a · A brief is not finished unless it has all of these

- The goal in one sentence, and why it matters.
- The decisions already made, **with their IDs**, and "do not re-open".
- What cannot be inferred from the code: prior attempts, known false positives.
- **Traps stated as facts with their evidence** (file:line, measured output), not as warnings.
- The exact files in scope, and what is explicitly **out** of scope, naming who owns it right now
  if another agent does.
- **The project's non-negotiables, inlined.** Shared docs get overwritten by concurrent sessions;
  "Follow CLAUDE.md" inlines nothing.
- Machine-checkable acceptance, the exact command, and how the exit code is captured.
- **Its own scratch database / cache / port** if it runs anything stateful.
- The failure modes you expect, so the agent doesn't manufacture findings: *"this file may have no
  database access at all — if so that is not a finding, say so and move on."*
- What to report back: files touched, pasted gate output, the interfaces later tasks will consume.
- **"Do not commit"** in orchestrate mode (§4c). **Do not edit the plan list**, in both modes.

## §4d · Manual: hand off

Give one line per brief, ready to paste into a fresh session:

```
Read <path> and carry out everything below the rule. That file is your complete brief.
```

Then say, in one sentence each: what order to run them in, which may run at the same time, and what
you need back to verify them.

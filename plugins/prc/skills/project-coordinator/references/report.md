# Reporting (§7) and the `/prc-status` ledger

## §7 · Report

Lead with **anything that changes a decision the human must make**. Then the focus board (re-run
`scripts/ledger.py` and quote its `FOCUS` line and `STEPS` section), so the human sees what was
ticked and what you are on now. Then, briefly:

- What is now true, described as **what a user can now do**, not which agent did it.
- What you verified yourself, and how. What you took on trust.
- What is running right now, and what it is waiting on.
- What needs the human, with the walk-through (§5, `references/human.md`).
- A link to the plan list.

Be specific about failures: paste the real error.

## The ledger: every `/prc-status` report carries one

Run `scripts/ledger.py <repo>` and **paste its dashboard verbatim at the top of the report**, in a
fenced code block. Don't recount by hand what the script counted, and don't reformat the bars. If the
project has its own board command that computes the ledger, run that and quote it instead.

The script finds the task directories from the overlay (`ledger-active:` / `ledger-completed:`
lines), from `--active` / `--completed`, or from `tasks/active` + `tasks/completed`. If it guesses
wrong, pass the directories explicitly and record them in the overlay so the next run doesn't guess.

It gives **two percentages, never one blended number**. They answer different questions:

- **Tasks**: `completed / (completed + open)`. What share of the project's declared work is
  archived as done.
- **Steps**: checked boxes / total boxes, across the open tasks only. How far the still-open
  work has actually got.

State the caveat out loud: **a task-file percentage counts files someone moved, not product
delivered.** A task sits in `completed/` because a human archived it. That is a bookkeeping event,
not a verification. Never let "92% complete" stand unqualified.

### By hand, if no Python resolves

Count the task directory yourself (`tasks/completed/` vs. `tasks/active/`, or whatever the project
uses) and count the markdown checkboxes inside the open files, **both bulleted `- [ ]` and numbered
`1. [ ]`**, since projects mix the two and a regex that only catches one silently reports 0%. Draw
the same dashboard: a 20-cell bar per percentage (`█` done, `░` left), then one 10-cell bar per open task.

### The focus board

The dashboard's `FOCUS` line and the marker on every task say what the coordinator works on and in
what order. The script infers the state from the tree:

- `▶ now`: some steps ticked, or the `Status:` line says in progress / started. Its first unticked
  step is marked `▶` in `STEPS`: that is the step being worked.
- `◻ next`: nothing ticked yet. Queued, in the order listed.
- `⊘ blocked`: the `Status:` line says blocked / waiting / on hold, or the next step is a `USER:`
  step. Say what it is waiting on.
- `✔ done`: all ticked or says done, but still in active/. Verify it (§6), then archive it.

By hand, mark each task the same way. If you know better than the tree (an agent is running on a
task the script calls `next`), say so and correct the marker in your report.

### Then list, by name

- **Outstanding**: every open task, with its marker, its `Status:` line, its step progress, and its
  age in days. Flag any that say "done" but are still in active/, any untouched for over a month,
  and any whose boxes are all ticked while the file stays open. (The script's `⚠` flags do this.)
- **Every task's steps as a checklist**, grouped by task: `✔` for ticked, `▶` for the step in
  progress, `◻` for the rest. This is the actual answer to *"what is done and what is left?"*. A
  count is not actionable, a list is. Mark the ones that need the **human** rather than a session
  (`USER:` prefix, or a credential / login / deploy / judgement step).
- **Completed**: the recent ones by name, plus how many older ones exist and where to grep them.

## `/prc-status` report order

- **Anything that changes a decision the human must make**, first.
- **The ledger**: the dashboard, then outstanding / remaining steps / completed, as above.
- **What is true right now**: per stream or workstream, described as what a user can now do.
- **Verified vs. taken on trust**: say which, explicitly, and how you checked.
- **Uncommitted, unpushed, or undeployed work**, named by path.
- **What is stale** in the project's own status documents, corrected.
- **What needs the human**, not you.
- **What is running right now**: agents in flight and what each is waiting on, if you are
  orchestrating.
- **What I will do next**: a numbered list in focus order (`1. ▶ auth-refresh: e2e test for
  expiry`, `2. ◻ search-index: write its steps`, …), each with the reason, ending with the one
  command that runs it (`/prc-prompt`). Not a question and not a menu: `/prc-status` is read-only,
  so it says what the next run will do rather than asking what to do.

Keep it tight everywhere except the ledger. The ledger is the part the human came for, so it gets
named tasks and named steps, not a summary of them.

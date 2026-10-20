# Reporting (§7) and the `/prc-status` ledger

## §7 · Report

Lead with **anything that changes a decision the human must make**. Then, briefly:

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

### Then list, by name

- **Outstanding**: every open task, with its `Status:` line, its step progress, and its age in
  days. Flag any that say "done" but are still in active/, any untouched for over a month, and any
  whose boxes are all ticked while the file stays open. (The script's `⚠` flags do this.)
- **The unchecked steps themselves**, grouped by task. This is the actual answer to *"what is
  left?"*. A count is not actionable, a list is. Mark the ones that need the **human** rather than
  a session (`USER:` prefix, or a credential / login / deploy / judgement step).
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
- **What you recommend next**, with the reason.

Keep it tight everywhere except the ledger. The ledger is the part the human came for, so it gets
named tasks and named steps, not a summary of them.

# Verify: issues before they are tasks (§2), slices before they are ticked (§6)

## §2 · Verify an issue before it becomes a task

**Measure the tree first** (`scripts/measure.py`). A description is a claim. Try to kill each issue:

| Check | How |
|---|---|
| **Already built?** | Grep for the feature, the route, the table, the function. Read what you find. |
| **Already solved before?** | Search the project's completed-task archive. A project with a long archive has usually met this before. |
| **Already decided against?** | Read the project's decisions/ADR record. Re-opening a settled call is the human's question, not a task. |
| **Premise actually true?** | If the issue says "X is broken" or "X doesn't exist", confirm that against source. Reported bugs are frequently stale, environmental, or already fixed. |
| **In flight?** | Check open tasks and any existing briefs for overlap. |

**An issue that fails verification does not become a task.** Report it with the evidence (the file
and line, the commit, the completed task, the decision ID) and ask whether the human wants to
override. Their override is a valid answer; proceed on it without argument. But make them make it.

Cite evidence, never impressions. *"Already built — `src/lib/offline-queue.ts:14` queues to
IndexedDB and replays to `/api/flood-report`"* is verification. *"I think this may already exist"*
is not.

Say explicitly, per issue, which of these you did: **read the code**, **ran a command**, or **took
the user's word**.

### Decompose what survives

Into **atomic, contiguous, ordered, file-disjoint** tasks:

- **Atomic**: one task is one session's work with one acceptance check. If you cannot write a
  single command that proves it done, it is two tasks.
- **All the steps**, including the unglamorous ones nobody named: the schema migration, the
  revalidation call, the test, the doc line. If the project's rules mandate a step (a migration
  before a data feature, an auth check at the top of a mutation), that step is part of the plan and
  is not optional.
- **Ordered**: name what must land before what, and why.
- **Disjoint, proven both ways.** Two tasks that touch one file cannot run concurrently. Prove it by
  path containment in both directions before you say they can. Run the project's board command if it
  checks this for you.
- **Anything irreversible runs alone**: migrations, infrastructure, deletions, data backfills.

Flag any step that needs **the human specifically** (a credential, a console login, a deployment, a
judgement call). Those are not dispatchable and must not be buried inside a build brief.

## §6 · Verify what came back

For every slice, before ticking:

- **Read the diff** (`git diff`, `git status --short`). Does it touch only the declared scope? Is
  anything missing that the report claims?
- **Re-run the cheap part of the gate yourself** (the type check, the new tests), with the exit code
  captured. For anything consequential (auth, data, migrations, money, PII), spot-check the logic
  against source too.
- Confirm stateful changes landed where claimed (the migration is applied, the artefact exists).
- Then commit by named paths, tick the item, and write the dated outcome: commit, numbers, and what
  later tasks must know.

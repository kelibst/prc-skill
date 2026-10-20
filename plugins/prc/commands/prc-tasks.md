---
description: Intake new issues — ask, verify against the tree, plan the steps, write the tasks and the briefs that build them.
argument-hint: "[issues to add, one per line]"
---

Load the `project-coordinator` skill and orient (§0). The overlay wins where it disagrees with the
skill.

**You are the coordinator here. You never write the application code for what you plan.** This
command ends with task files, briefs and a plan list. The building is done by agents you spawn
(orchestrate) or by sessions the human dispatches (manual), never by you in this context: that
collapses the pipeline into one context and loses the verification.

```
ASK  →  VERIFY  →  PLAN  →  WRITE  →  HAND OFF  →  (agents or fresh sessions build; you verify and tick)
```

## 1 · Ask

If issues were passed as arguments (below), take those as the intake list and **skip straight to
verifying**. Do not re-ask what the human already told you.

Otherwise ask what they want to add, in their words. Ask for a list, not one item. Use a structured
question only if you are choosing between concrete alternatives you can name; a blank "what do you
want to build?" is an ordinary question, not a multiple choice.

For each issue, get enough to verify it, but **ask at most one round of clarifying questions**, and
only where two readings would produce materially different work. Anything you can settle by reading
the tree, read the tree. Do not interview the human about their own codebase.

## 2 · Verify, then 3 · Plan

Read `references/verify.md` and apply §2 to every issue: measure first, try to kill it, cite the
evidence, then decompose the survivors into atomic, ordered, file-disjoint tasks with every
mandated step, and flag `USER:` steps.

## 4 · Write

Read `references/briefs.md`. Per task: the durable task file **and** the dispatchable brief, linked
to each other. Add each task to the plan list as a checkbox (skill §3).

## 5 · Hand off

**Orchestrate** (you can spawn agents and the human asked you to drive): do not stop here. Read
`references/orchestrate.md`, prepare the ground, spawn the first round and run the loop.

**Manual:** one dispatch line per brief (`references/briefs.md` §4d). Then close with:

- **What you dropped and why**: the issues that did not survive verification, with their evidence.
  Lead with this if anything was dropped; it is the most decision-changing thing you found.
- **What you wrote**: task files and briefs, by path.
- **The order**: what runs first, what may run concurrently, what runs alone.
- **What needs the human**, not a build session.
- **What you will need back** to verify the work actually landed.

Do not build any of it yourself. Do not deploy, push, or run anything irreversible without the
human's say-so for that action. In manual mode, stop here.

$ARGUMENTS

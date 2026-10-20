# Brief: <what it does>

Task file: <path>. Written by the coordinator on <YYYY-MM-DD> against commit <hash>.

## Paste everything below this line into a new session

## Goal

<One sentence, and why it matters.>

## Already decided (do not re-open)

- <ID>: <decision>

## What the code won't tell you

- <prior attempts, known false positives>

## Traps (facts, with evidence)

- <file:line or measured output>: <the fact>

## Scope

<!-- scope:start -->
path/one
path/two
<!-- scope:end -->

Out of scope: <paths>, owned right now by <brief / agent> if any.

## Non-negotiables

- <inline each rule; do not write "follow CLAUDE.md">

## Your scratch resources

- Database / cache / port: <name, created by the coordinator>

## Acceptance

```
<exact command>; echo "exit=$?"
```

Done means: <machine-checkable condition>.

## Expected non-findings

- <e.g. "this module has no database access; if so that is not a finding, say so and move on">

## Rules for this session

- Do not commit. Do not edit the plan list or any shared coordination file.

## Report back

- Files touched.
- The acceptance command's output, pasted, with its exit code.
- Interfaces later tasks will consume.

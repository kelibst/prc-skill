#!/usr/bin/env python3
"""Task ledger for the project-coordinator skill: counts and a progress dashboard.

Reads the open and completed task directories, counts markdown checkboxes in the open
files (bulleted and numbered), and prints two percentages plus a per-task breakdown.

    python3 ledger.py [repo] [--active DIR] [--completed DIR] [--json] [--ascii]

Directories come from the arguments, else from `ledger-active:` / `ledger-completed:`
lines in the project's COORDINATOR.md overlay, else from common layouts (tasks/active).
Stdlib only, Python 3.8+.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

OVERLAYS = (".agent-state/COORDINATOR.md", "docs/COORDINATOR.md", "COORDINATOR.md", ".github/COORDINATOR.md")
LAYOUTS = (
    ("tasks/active", "tasks/completed"),
    ("tasks/open", "tasks/done"),
    (".agent-state/tasks/active", ".agent-state/tasks/completed"),
    ("docs/tasks/active", "docs/tasks/completed"),
)
SKIP_NAMES = {"readme.md", "index.md", "_template.md", "template.md"}

CHECKBOX = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+\[([ xX])\]\s*(.*)$")
STATUS = re.compile(r"^\s*(?:[-*+]\s*)?[*_]*status[*_]*\s*:\s*[*_]*\s*(.+?)\s*$", re.IGNORECASE)
HEADING = re.compile(r"^#\s+(.+?)\s*$")
FENCE = re.compile(r"^\s*(```|~~~)")
DATE_PREFIX = re.compile(r"^\d{4}-\d{2}-\d{2}[_-]")
SAYS_DONE = re.compile(r"^\W*(done|complete|completed|finished|shipped|merged|closed)\b", re.IGNORECASE)
MARKDOWN = re.compile(r"[*_`]+")
USER_STEP = re.compile(r"(^|\W)USER\s*:")
SAYS_BLOCKED = re.compile(r"\b(blocked|waiting|on hold|paused|parked)\b", re.IGNORECASE)
SAYS_STARTED = re.compile(r"\b(in progress|started|wip|underway|dispatched|running)\b", re.IGNORECASE)
# Focus order: what is moving, what is next, what is stuck, what only needs verifying and archiving.
STATES = ("now", "next", "blocked", "done")


def git(repo, *args):
    try:
        out = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True,
                             encoding="utf-8", errors="replace", timeout=20)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return out.stdout if out.returncode == 0 else None


def overlay_dirs(repo):
    """Return (active, completed, overlay path) declared in the overlay, if any."""
    for rel in OVERLAYS:
        path = repo / rel
        if not path.is_file():
            continue
        found = {}
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            m = re.match(r"^\s*[-*]?\s*ledger-(active|completed)\s*:\s*`?([^`]+?)`?\s*$", line, re.IGNORECASE)
            if m:
                found[m.group(1).lower()] = m.group(2).strip()
        return found.get("active"), found.get("completed"), rel
    return None, None, None


def resolve_dirs(repo, args):
    active, completed, overlay = overlay_dirs(repo)
    source = "overlay " + overlay if (active or completed) else None
    if args.active or args.completed:
        active, completed, source = args.active or active, args.completed or completed, "arguments"
    if not active:
        for a, c in LAYOUTS:
            if (repo / a).is_dir():
                active, completed, source = a, c, "default layout"
                break
    return active, completed, source


def task_files(directory):
    if not directory.is_dir():
        return []
    return sorted(p for p in directory.rglob("*.md") if p.is_file() and p.name.lower() not in SKIP_NAMES)


def file_times(repo, directories):
    """Last-commit time per file under the directories; dirty or untracked files use mtime."""
    times = {}
    top = git(repo, "rev-parse", "--show-toplevel")
    if top is None:
        return times, False
    top = Path(top.strip())
    paths = [str(d) for d in directories if d is not None and d.is_dir()]
    if not paths:
        return times, True
    log = git(repo, "log", "--format=@%ct", "--name-only", "--", *paths) or ""
    stamp = None
    for line in log.splitlines():
        if line.startswith("@"):
            stamp = int(line[1:])
        elif line.strip() and stamp is not None:
            key = os.path.normcase(str((top / line.strip()).resolve()))
            times.setdefault(key, stamp)
    dirty = git(repo, "status", "--porcelain", "--untracked-files=all", "--", *paths) or ""
    for line in dirty.splitlines():
        rel = line[3:].split(" -> ")[-1].strip().strip('"')
        times.pop(os.path.normcase(str((top / rel).resolve())), None)
    return times, True


def age_days(path, times, now):
    stamp = times.get(os.path.normcase(str(path.resolve())))
    if stamp is None:
        stamp = path.stat().st_mtime
    return max(0, int((now - stamp) // 86400)), stamp


def parse_task(path):
    title, status, steps, in_fence = None, None, [], False
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if title is None:
            m = HEADING.match(line)
            if m:
                title = m.group(1)
        if status is None:
            m = STATUS.match(line)
            if m:
                status = MARKDOWN.sub("", m.group(1)).strip()
        m = CHECKBOX.match(line)
        if m:
            text = m.group(2).strip()
            steps.append({"done": m.group(1) != " ", "text": text, "user": bool(USER_STEP.search(text))})
    return title, status, steps


def task_state(status, steps):
    """now / next / blocked / done, from the ticks and the Status: line."""
    done = sum(s["done"] for s in steps)
    if (steps and done == len(steps)) or (status and SAYS_DONE.search(status)):
        return "done"
    pending = [s for s in steps if not s["done"]]
    if (status and SAYS_BLOCKED.search(status)) or (pending and pending[0]["user"]):
        return "blocked"
    if done or (status and SAYS_STARTED.search(status)):
        return "now"
    return "next"


def short_name(path):
    return DATE_PREFIX.sub("", path.stem)


def build(repo, args):
    active_rel, completed_rel, source = resolve_dirs(repo, args)
    if not active_rel:
        return None
    active_dir = (repo / active_rel)
    completed_dir = (repo / completed_rel) if completed_rel else None
    now = time.time()
    times, in_git = file_times(repo, [active_dir, completed_dir])

    open_tasks = []
    for path in task_files(active_dir):
        title, status, steps = parse_task(path)
        done = sum(s["done"] for s in steps)
        age, _ = age_days(path, times, now)
        flags = []
        if steps and done == len(steps):
            flags.append("all ticked, not archived")
        if status and SAYS_DONE.search(status):
            flags.append("says done, still open")
        if age > args.stale_days:
            flags.append("stale")
        if not steps:
            flags.append("no checkboxes")
        pending = [s for s in steps if not s["done"]]
        open_tasks.append({
            "name": short_name(path), "title": title, "path": path.relative_to(repo).as_posix(),
            "status": status, "state": task_state(status, steps), "done": done, "total": len(steps),
            "age_days": age, "flags": flags,
            "next_step": pending[0]["text"] if pending else None,
            "steps": steps,
            "remaining": [{"text": s["text"], "user": s["user"]} for s in pending],
        })
    open_tasks.sort(key=lambda t: STATES.index(t["state"]))

    completed = []
    for path in task_files(completed_dir) if completed_dir else []:
        _, stamp = age_days(path, times, now)
        completed.append((stamp, path.stem, short_name(path)))
    completed.sort(reverse=True)

    steps_done = sum(t["done"] for t in open_tasks)
    steps_total = sum(t["total"] for t in open_tasks)
    return {
        "repo": str(repo), "source": source, "ages_from": "git" if in_git else "mtime",
        "active_dir": active_rel, "completed_dir": completed_rel,
        "tasks": {"completed": len(completed), "open": len(open_tasks),
                  "percent": pct(len(completed), len(completed) + len(open_tasks))},
        "steps": {"done": steps_done, "total": steps_total, "percent": pct(steps_done, steps_total)},
        "open": open_tasks,
        "focus": {state: [t["name"] for t in open_tasks if t["state"] == state] for state in STATES},
        "completed": {"count": len(completed), "recent": [n for _, _, n in completed[:args.recent]]},
    }


def pct(part, whole):
    return None if whole == 0 else round(100 * part / whole)


def render(data, ascii_only, width):
    full, empty, warn, dot = ("#", ".", "!", "-") if ascii_only else ("█", "░", "⚠", "·")
    mark = ({"now": ">", "next": "o", "blocked": "=", "done": "v", "tick": "x", "todo": " "} if ascii_only else
            {"now": "▶", "next": "◻", "blocked": "⊘", "done": "✔", "tick": "✔", "todo": "◻"})
    if ascii_only:
        mark = {k: "[%s]" % v for k, v in mark.items()}

    def bar(part, whole, cells):
        filled = 0 if whole == 0 else round(cells * part / whole)
        return full * filled + empty * (cells - filled)

    def percent(value):
        return "  —" if value is None else "%3d%%" % value

    t, s = data["tasks"], data["steps"]
    total_tasks = t["completed"] + t["open"]
    tasks_frac = "%d/%d" % (t["completed"], total_tasks)
    steps_frac = "%d/%d" % (s["done"], s["total"])
    frac_w = max(len(tasks_frac), len(steps_frac))
    out = ["LEDGER  %s   (task %% counts archived files, not delivered product)" % time.strftime("%Y-%m-%d"),
           "Tasks  %s  %-*s  %s   done / all task files" % (bar(t["completed"], total_tasks, width), frac_w, tasks_frac, percent(t["percent"])),
           "Steps  %s  %-*s  %s   ticked boxes in open tasks" % (bar(s["done"], s["total"], width), frac_w, steps_frac, percent(s["percent"])),
           ""]

    tasks = data["open"]
    focus = data["focus"]
    labels = {"now": "now", "next": "next", "blocked": "blocked", "done": "verify + archive"}
    summary = "  ".join("%s %s: %s" % (mark[k], labels[k], ", ".join(focus[k])) for k in STATES if focus[k])
    out.append("FOCUS  %s" % (summary or "nothing open"))
    out.append("")

    out.append("OPEN (%d)%s" % (len(tasks), "" if tasks else "  nothing open"))
    name_w = min(28, max([len(x["name"]) for x in tasks] + [4]))
    for x in tasks:
        name = x["name"] if len(x["name"]) <= name_w else x["name"][:name_w - 1] + "~"
        frac = "%d/%d" % (x["done"], x["total"])
        status = (x["status"] or "")[:24].ljust(24) if x["flags"] else (x["status"] or "")[:24]
        flags = "  ".join("%s %s" % (warn, f) for f in x["flags"])
        out.append(("  %s %-*s  %s  %-6s %4dd  %s  %s" % (mark[x["state"]], name_w, name, bar(x["done"], x["total"], 10),
                                                          frac, x["age_days"], status, flags)).rstrip())

    listed = [x for x in tasks if x["remaining"]]
    if listed:
        out += ["", "STEPS (%d left)" % sum(len(x["remaining"]) for x in listed)]
        for x in listed:
            out.append("  %s %s  %d/%d" % (mark[x["state"]], x["name"], x["done"], x["total"]))
            ticked = [st for st in x["steps"] if st["done"]]
            if len(ticked) > 3:
                out.append("      %s %d earlier steps done" % (mark["tick"], len(ticked) - 3))
            shown = set(id(st) for st in ticked[-3:])
            current = x["state"] == "now"
            for st in x["steps"]:
                if st["done"]:
                    if id(st) in shown:
                        out.append("      %s %s" % (mark["tick"], st["text"]))
                    continue
                user = "  (USER)" if st["user"] and "USER" not in st["text"][:6] else ""
                out.append("      %s %s%s" % (mark["now"] if current else mark["todo"], st["text"], user))
                current = False

    c = data["completed"]
    out.append("")
    if c["count"]:
        older = c["count"] - len(c["recent"])
        line = "COMPLETED (%d)  %s latest: %s" % (c["count"], mark["done"], ", ".join(c["recent"]))
        if older > 0:
            line += "  %s %d older in %s/" % (dot, older, data["completed_dir"])
        out.append(line)
    else:
        out.append("COMPLETED (0)%s" % ("" if data["completed_dir"] else "  no completed directory found"))
    out.append("source: %s (%s, %s)  ages from %s" % (data["source"], data["active_dir"],
                                                      data["completed_dir"] or "-", data["ages_from"]))
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("repo", nargs="?", default=".")
    ap.add_argument("--active", help="directory of open task files, relative to repo")
    ap.add_argument("--completed", help="directory of completed task files, relative to repo")
    ap.add_argument("--json", action="store_true", help="print JSON instead of the dashboard")
    ap.add_argument("--ascii", action="store_true", help="use # and . instead of block characters")
    ap.add_argument("--stale-days", type=int, default=30)
    ap.add_argument("--recent", type=int, default=5, help="completed tasks to name")
    ap.add_argument("--width", type=int, default=20, help="cells in the two summary bars")
    args = ap.parse_args(argv)

    repo = Path(args.repo).resolve()
    data = build(repo, args)
    if data is None:
        sys.stderr.write("ledger: no task directory found in %s. Pass --active DIR [--completed DIR], "
                         "or add 'ledger-active:' / 'ledger-completed:' lines to COORDINATOR.md.\n" % repo)
        return 2
    if args.json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return 0
    encoding = (getattr(sys.stdout, "encoding", None) or "").lower().replace("-", "")
    print(render(data, args.ascii or "utf8" not in encoding, args.width))
    return 0


if __name__ == "__main__":
    sys.exit(main())

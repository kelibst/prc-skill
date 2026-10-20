#!/usr/bin/env python3
"""Measure the machine and the tree in one call, for the project-coordinator skill.

    python3 measure.py [repo] [--json] [--log N]

Reports OS and shell, which tools resolve (with versions), git state (log, status,
ahead/behind), the filesystem and core.fileMode, the coordinator overlay and its dated
Machine section, convention files, and candidate task / brief / decision locations.
Read-only. Stdlib only, Python 3.8+.
"""

import argparse
import json
import os
import platform
import re
import shutil
import socket
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

OVERLAYS = (".agent-state/COORDINATOR.md", "docs/COORDINATOR.md", "COORDINATOR.md", ".github/COORDINATOR.md")
CONVENTIONS = ("CLAUDE.md", "AGENTS.md", "CONTRIBUTING.md", ".claude/CLAUDE.md", "GEMINI.md", ".cursorrules")
TOOLS = ("git", "python3", "python", "py", "node", "bun", "deno", "npm", "pnpm", "yarn",
         "docker", "gh", "cargo", "go", "uv", "make")
CANDIDATE_DIRS = {"tasks": "tasks", "briefs": "briefs", "decisions": "decisions", "adr": "decisions",
                  "adrs": "decisions", "plans": "plans", ".agent-state": "coordination"}
CANDIDATE_FILES = {"decisions.md": "decisions", "plan.md": "plans", "todo.md": "plans",
                   "roadmap.md": "plans", "worklist.md": "plans", "backlog.md": "plans"}
SKIP_DIRS = {".git", "node_modules", "vendor", "dist", "build", ".venv", "venv", "target",
             "__pycache__", ".next", ".cache"}
LOOSE_FS = {"ntfs", "ntfs3", "fuseblk", "vfat", "exfat", "9p", "drvfs", "cifs", "smb3", "nfs", "nfs4"}


def run(cmd, cwd=None, timeout=10):
    try:
        out = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8",
                             errors="replace", timeout=timeout)
    except (OSError, subprocess.TimeoutExpired):
        return None, ""
    return out.returncode, (out.stdout or out.stderr).strip()


def probe(tool):
    path = shutil.which(tool)
    if not path:
        return tool, None
    if tool == "py" and os.name != "nt":
        return tool, None
    code, text = run([path, "--version"], timeout=8)
    first = text.splitlines()[0] if text else ""
    if tool in ("python", "python3", "py") and "Microsoft Store" in text:
        return tool, None  # the Windows Store stub resolves but is not Python
    version = re.search(r"\d+(\.\d+)+", first)
    return tool, version.group(0) if version else (first[:40] or "present")


def shell_name():
    if os.environ.get("SHELL"):
        return os.path.basename(os.environ["SHELL"])
    if os.name == "nt":
        return "powershell" if os.environ.get("PSModulePath") else os.path.basename(os.environ.get("ComSpec", "cmd"))
    return "unknown"


def filesystem(path):
    if not sys.platform.startswith("linux"):
        return None
    best, fstype = "", None
    try:
        with open("/proc/mounts", encoding="utf-8") as fh:
            for line in fh:
                parts = line.split()
                if len(parts) > 2:
                    mount = parts[1].replace("\\040", " ")
                    if str(path).startswith(mount) and len(mount) > len(best):
                        best, fstype = mount, parts[2]
    except OSError:
        return None
    return fstype


def sudo_passwordless():
    if os.name == "nt" or not shutil.which("sudo"):
        return None
    code, _ = run(["sudo", "-n", "true"], timeout=3)
    return code == 0


def git_state(repo, log_n):
    code, top = run(["git", "-C", str(repo), "rev-parse", "--show-toplevel"])
    if code != 0:
        return None
    g = {"root": top}
    _, g["branch"] = run(["git", "-C", top, "branch", "--show-current"])
    code, upstream = run(["git", "-C", top, "rev-parse", "--abbrev-ref", "@{u}"])
    g["upstream"] = upstream if code == 0 else None
    if g["upstream"]:
        _, counts = run(["git", "-C", top, "rev-list", "--left-right", "--count", "HEAD...@{u}"])
        parts = counts.split()
        g["ahead"], g["behind"] = (int(parts[0]), int(parts[1])) if len(parts) == 2 else (None, None)
    code, log = run(["git", "-C", top, "log", "--oneline", "--decorate=short", "-%d" % log_n])
    g["log"] = log.splitlines() if code == 0 else []
    _, status = run(["git", "-C", top, "status", "--short"])
    g["status"] = [line for line in status.splitlines() if line.strip()]
    _, mode = run(["git", "-C", top, "config", "--get", "core.fileMode"])
    g["core_filemode"] = mode or "unset (true)"
    _, worktrees = run(["git", "-C", top, "worktree", "list"])
    g["worktrees"] = len(worktrees.splitlines())
    return g


def overlay_info(repo):
    for rel in OVERLAYS:
        path = repo / rel
        if path.is_file():
            text = path.read_text(encoding="utf-8", errors="replace")
            m = re.search(r"^##\s*Machine\s*\(([^)]*)\)", text, re.MULTILINE | re.IGNORECASE)
            info = {"path": rel, "machine_header": m.group(1).strip() if m else None}
            if m:
                info["host_matches"] = socket.gethostname().lower() in m.group(1).lower()
            ledger = re.findall(r"^\s*[-*]?\s*(ledger-(?:active|completed))\s*:\s*`?([^`\n]+?)`?\s*$",
                                text, re.MULTILINE | re.IGNORECASE)
            info["ledger"] = {k.lower(): v for k, v in ledger}
            return info
    return None


def candidates(repo, depth=3):
    found = {}
    base = len(repo.parts)
    for root, dirs, files in os.walk(repo):
        here = Path(root)
        if len(here.parts) - base >= depth:
            dirs[:] = []
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        for d in dirs:
            kind = CANDIDATE_DIRS.get(d.lower())
            if kind:
                found.setdefault(kind, []).append((here / d).relative_to(repo).as_posix() + "/")
        for f in files:
            kind = CANDIDATE_FILES.get(f.lower())
            if kind:
                found.setdefault(kind, []).append((here / f).relative_to(repo).as_posix())
    return {k: v[:6] for k, v in found.items()}


def measure(repo, log_n):
    with ThreadPoolExecutor(max_workers=8) as pool:
        tools = dict(pool.map(probe, TOOLS))
    fs = filesystem(repo)
    git = git_state(repo, log_n)
    notes = []
    if fs in LOOSE_FS and git and git["core_filemode"] != "false":
        notes.append("repo is on %s: file modes are unreliable; set `git config core.fileMode false` "
                     "if every file shows as modified" % fs)
    if not tools.get("git"):
        notes.append("git does not resolve on this machine")
    py = [t for t in ("python3", "python", "py") if tools.get(t)]
    return {
        "machine": {"os": "%s %s" % (platform.system(), platform.release()), "arch": platform.machine(),
                    "host": socket.gethostname(), "shell": shell_name(), "python_cmd": py[0] if py else None,
                    "path_style": "windows" if os.name == "nt" else "posix",
                    "sudo_passwordless": sudo_passwordless()},
        "repo": {"path": str(repo), "filesystem": fs},
        "tools": {k: v for k, v in tools.items() if v},
        "missing_tools": [k for k, v in tools.items() if not v],
        "git": git,
        "overlay": overlay_info(repo),
        "conventions": [c for c in CONVENTIONS if (repo / c).exists()],
        "candidates": candidates(repo),
        "notes": notes,
    }


def render(m, ascii_only):
    dot, cross = (" | ", "x ") if ascii_only else (" · ", "✗ ")
    mc, g, ov = m["machine"], m["git"], m["overlay"]
    sudo = {True: "passwordless", False: "needs password", None: "n/a"}[mc["sudo_passwordless"]]
    out = ["MACHINE  " + dot.join([mc["os"] + " " + mc["arch"], "host " + mc["host"], "shell " + mc["shell"],
                                   "%s paths" % mc["path_style"], "sudo " + sudo]),
           "REPO     " + m["repo"]["path"] + ("  (fs %s)" % m["repo"]["filesystem"] if m["repo"]["filesystem"] else ""),
           "TOOLS    " + dot.join("%s %s" % kv for kv in m["tools"].items()),
           "MISSING  " + " ".join(cross + t for t in m["missing_tools"])]
    if ov:
        state = "no dated Machine section"
        if ov["machine_header"]:
            state = "Machine (%s), host %s" % (ov["machine_header"], "matches" if ov.get("host_matches") else "DIFFERS: re-measure")
        ledger = "; ".join("%s: %s" % kv for kv in ov["ledger"].items()) or "no ledger- lines"
        out.append("OVERLAY  %s  %s%s%s" % (ov["path"], state, dot, ledger))
    else:
        out.append("OVERLAY  none (offer /prc-init)")
    out.append("CONVENTIONS  " + (", ".join(m["conventions"]) or "none"))
    if m["candidates"]:
        out.append("CANDIDATES  " + dot.join("%s: %s" % (k, ", ".join(v)) for k, v in sorted(m["candidates"].items())))
    if g is None:
        out.append("GIT      not a git repository")
    else:
        sync = "no upstream"
        if g["upstream"]:
            sync = "%s ahead %s behind %s" % (g["upstream"], g["ahead"], g["behind"])
        out.append("GIT      branch %s%s%s%score.fileMode %s%sworktrees %d" % (
            g["branch"] or "(detached)", dot, sync, dot, g["core_filemode"], dot, g["worktrees"]))
        out.append("LOG")
        out += ["  " + line for line in g["log"]] or ["  (no commits)"]
        shown = g["status"][:40]
        out.append("STATUS   %s" % ("clean" if not g["status"] else "%d changed" % len(g["status"])))
        out += ["  " + line for line in shown]
        if len(g["status"]) > len(shown):
            out.append("  ... %d more (git status --short)" % (len(g["status"]) - len(shown)))
    for note in m["notes"]:
        out.append("NOTE     " + note)
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("repo", nargs="?", default=".")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--ascii", action="store_true")
    ap.add_argument("--log", type=int, default=15, help="commits to show")
    args = ap.parse_args(argv)
    repo = Path(args.repo).resolve()
    if not repo.is_dir():
        sys.stderr.write("measure: %s is not a directory\n" % repo)
        return 2
    m = measure(repo, args.log)
    if args.json:
        print(json.dumps(m, indent=2, ensure_ascii=False))
    else:
        encoding = (getattr(sys.stdout, "encoding", None) or "").lower().replace("-", "")
        print(render(m, args.ascii or "utf8" not in encoding))
    return 0


if __name__ == "__main__":
    sys.exit(main())

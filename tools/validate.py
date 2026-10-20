#!/usr/bin/env python3
"""Check the repo's plugin structure: manifests, frontmatter, and cross-file references.

    python3 tools/validate.py        exit 0 = valid, 1 = problems listed on stderr
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "plugins" / "prc"
SKILLS = PLUGIN / "skills"
REFERENCE = re.compile(r"\b((?:references|scripts|templates)/[\w.-]+\.(?:md|py))\b")
problems = []


def problem(path, message):
    problems.append("%s: %s" % (path.relative_to(ROOT).as_posix(), message))


def frontmatter(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not m:
        problem(path, "missing YAML frontmatter")
        return {}
    fields = {}
    for line in m.group(1).splitlines():
        key, sep, value = line.partition(":")
        if sep and not line.startswith(" "):
            fields[key.strip()] = value.strip()
    return fields


def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        problem(path, "invalid JSON: %s" % exc)
        return {}


def check_manifests():
    market = load_json(ROOT / ".claude-plugin" / "marketplace.json")
    plugin = load_json(PLUGIN / ".claude-plugin" / "plugin.json")
    for key in ("name", "owner", "plugins"):
        if key not in market:
            problem(ROOT / ".claude-plugin" / "marketplace.json", "missing '%s'" % key)
    for key in ("name", "description", "version"):
        if key not in plugin:
            problem(PLUGIN / ".claude-plugin" / "plugin.json", "missing '%s'" % key)
    entries = [p for p in market.get("plugins", []) if p.get("name") == plugin.get("name")]
    if not entries:
        problem(ROOT / ".claude-plugin" / "marketplace.json", "no entry for plugin '%s'" % plugin.get("name"))
        return
    entry = entries[0]
    source = entry.get("source")
    if isinstance(source, str) and not (ROOT / source).resolve() == PLUGIN.resolve():
        problem(ROOT / ".claude-plugin" / "marketplace.json", "source %s does not point at plugins/prc" % source)
    if entry.get("version") and entry["version"] != plugin.get("version"):
        problem(ROOT / ".claude-plugin" / "marketplace.json",
                "version %s != plugin.json %s" % (entry["version"], plugin.get("version")))


def check_skills():
    for skill_md in sorted(SKILLS.glob("*/SKILL.md")):
        fields = frontmatter(skill_md)
        if fields.get("name") != skill_md.parent.name:
            problem(skill_md, "name '%s' must match directory '%s'" % (fields.get("name"), skill_md.parent.name))
        description = fields.get("description", "")
        if not description:
            problem(skill_md, "missing description")
        elif len(description) > 1024:
            problem(skill_md, "description is %d chars (max 1024)" % len(description))


def check_commands():
    commands = sorted((PLUGIN / "commands").glob("*.md"))
    if not commands:
        problem(PLUGIN, "no commands found")
    for command in commands:
        if not frontmatter(command).get("description"):
            problem(command, "missing description")


def check_references():
    skill_dirs = [d for d in SKILLS.iterdir() if d.is_dir()]
    for md in sorted(PLUGIN.rglob("*.md")):
        for ref in sorted(set(REFERENCE.findall(md.read_text(encoding="utf-8")))):
            if not any((d / ref).is_file() for d in skill_dirs):
                problem(md, "references missing file %s" % ref)


def main():
    check_manifests()
    check_skills()
    check_commands()
    check_references()
    if problems:
        sys.stderr.write("\n".join(problems) + "\n")
        return 1
    print("ok: manifests, %d skill(s), %d command(s), references resolve" % (
        len(list(SKILLS.glob("*/SKILL.md"))), len(list((PLUGIN / "commands").glob("*.md")))))
    return 0


if __name__ == "__main__":
    sys.exit(main())

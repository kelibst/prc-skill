#!/usr/bin/env sh
# Install the PRC coordinator suite without the plugin system.
#
#   ./install.sh              install into ~/.claude (all projects)
#   ./install.sh --project    install into ./.claude of the current directory
#   ./install.sh --uninstall  remove it (add --project for a project install)
#   ./install.sh --dry-run    show what would happen, change nothing
#
# Anything replaced is backed up to ~/.claude/backups/prc-<timestamp>/ first.
set -eu

SRC="$(cd "$(dirname "$0")" && pwd)/plugins/prc"
TARGET="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
MODE=install
DRY=0
for arg in "$@"; do
  case "$arg" in
    --project) TARGET="$(pwd)/.claude" ;;
    --uninstall) MODE=uninstall ;;
    --dry-run) DRY=1 ;;
    -h|--help) sed -n '2,10p' "$0"; exit 0 ;;
    *) echo "unknown option: $arg" >&2; exit 2 ;;
  esac
done

SKILLS="project-coordinator"
COMMANDS="$(cd "$SRC/commands" && ls prc-*.md)"
BACKUP="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/backups/prc-$(date +%Y%m%d-%H%M%S)"

do_run() { if [ "$DRY" = 1 ]; then echo "would: $*"; else "$@"; fi; }
DONE="Installed"; [ "$DRY" = 1 ] && DONE="(dry run) Would install"

backup() {  # backup <path> <name inside backup dir>
  if [ -e "$1" ]; then
    do_run mkdir -p "$BACKUP/$(dirname "$2")"
    do_run cp -R "$1" "$BACKUP/$2"
    BACKED=1
  fi
}

BACKED=0
for s in $SKILLS; do backup "$TARGET/skills/$s" "skills/$s"; done
for c in $COMMANDS; do backup "$TARGET/commands/$c" "commands/$c"; done

if [ "$MODE" = uninstall ]; then
  for s in $SKILLS; do [ -e "$TARGET/skills/$s" ] && do_run rm -rf "$TARGET/skills/$s"; done
  for c in $COMMANDS; do [ -e "$TARGET/commands/$c" ] && do_run rm -f "$TARGET/commands/$c"; done
  [ "$DRY" = 1 ] && printf "(dry run) " ; echo "Removed the PRC suite from $TARGET."
else
  do_run mkdir -p "$TARGET/skills" "$TARGET/commands"
  for s in $SKILLS; do
    [ -e "$TARGET/skills/$s" ] && do_run rm -rf "$TARGET/skills/$s"
    do_run cp -R "$SRC/skills/$s" "$TARGET/skills/$s"
  done
  for c in $COMMANDS; do do_run cp "$SRC/commands/$c" "$TARGET/commands/$c"; done
  echo "$DONE the PRC suite into $TARGET:"
  echo "  skill    $SKILLS"
  echo "  commands $(echo $COMMANDS | sed 's/\.md//g; s/prc-/\/prc-/g')"
  if grep -q '"prc@' "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/settings.json" 2>/dev/null; then
    echo "WARNING: the prc plugin is also enabled; you'll see every command twice."
    echo "         Pick one: '/plugin uninstall prc@prc-skill' or './install.sh --uninstall'."
  fi
  echo "Restart Claude Code (or start a new session) to load it."
fi
[ "$BACKED" = 1 ] && echo "Backup of what was there before: $BACKUP"
exit 0

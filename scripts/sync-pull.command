#!/bin/bash
# Sync PULL for macOS: bring the latest copy from the NAS to this Mac.
# Run BEFORE you start working. Double-click (after a one-time: chmod +x this file).
set -u

NAS="/Volumes/share/claude-sync"  # your NAS SMB share. Change if it mounts elsewhere.
NAS_URL="smb://YOUR-NAS-IP/share" # used to auto-mount if not mounted yet
WS_LOCAL="$HOME/MCP"
WS_NAS="$NAS/workspace"
MEM_NAS="$NAS/memory"
NOTES_LOCAL="$HOME/local-notes"
NOTES_NAS="$NAS/notes"

GRN=$'\033[32m'; RED=$'\033[31m'; DIM=$'\033[2m'; RST=$'\033[0m'
FAIL=0
SUMMARY=""

note_ok()   { printf '  %s✓ %s%s\n' "$GRN" "$1" "$RST"; SUMMARY="$SUMMARY
  ✓ $1"; }
note_skip() { printf '  %s· %s%s\n' "$DIM" "$1" "$RST"; SUMMARY="$SUMMARY
  · $1"; }
note_fail() { printf '  %s✗ %s%s\n' "$RED" "$1" "$RST"; SUMMARY="$SUMMARY
  ✗ $1"; FAIL=1; }

# rsync wrapper: streams rsync output live (indented), then prints ✓ with an
# approximate change count, or ✗ with the last lines of output on failure.
# LC_ALL=C on sed — rsync may emit non-UTF8 bytes in file names.
run_rsync() {
  local name="$1"; shift
  local tmp rc n
  tmp=$(mktemp)
  rsync -v "$@" 2>&1 | tee "$tmp" | LC_ALL=C sed 's/^/    /'
  rc=${PIPESTATUS[0]}
  if [ "$rc" -eq 0 ]; then
    n=$(LC_ALL=C sed '/^$/d;/^sending/d;/^receiving/d;/^building/d;/^sent /d;/^total /d;/^created /d;/^Transfer starting/d;/^\.\/$/d' "$tmp" | wc -l | tr -d ' ')
    note_ok "$name — OK (changes: $n)"
  else
    note_fail "$name — FAILED (rsync code $rc)"
    tail -5 "$tmp" | LC_ALL=C sed 's/^/      /'
  fi
  rm -f "$tmp"
}

# Auto-mount the NAS share if it is not mounted yet (creds come from the keychain).
if [ ! -d "$NAS" ]; then
  echo "NAS share not mounted — mounting $NAS_URL (waiting up to 60 s) ..."
  open "$NAS_URL"
  for _ in $(seq 1 60); do [ -d "$NAS" ] && break; sleep 1; done
fi
if [ ! -d "$WS_NAS" ]; then echo "${RED}ERROR: NAS not found at $WS_NAS. Connect to the network drive first.${RST}"; read -n1 -r -p "Press any key..."; exit 1; fi
if [ ! -f "$WS_NAS/CLAUDE.md" ]; then echo "${RED}ERROR: NAS workspace looks empty. Push from another PC first.${RST}"; read -n1 -r -p "Press any key..."; exit 1; fi

[ -f "$NAS/LAST-SYNC.txt" ] && echo "Last synced: $(cat "$NAS/LAST-SYNC.txt")" && echo ""

echo "Pulling workspace to $WS_LOCAL ..."
mkdir -p "$WS_LOCAL"
run_rsync "workspace" -a --delete \
  --exclude='.git' --exclude='.venv' --exclude='node_modules' \
  --exclude='__pycache__' --exclude='.pytest_cache' --exclude='dist' --exclude='build' \
  --exclude='__MACOSX' \
  --exclude='.DS_Store' --exclude='._*' --exclude='*.log' --exclude='.mcp.json' \
  "$WS_NAS/" "$WS_LOCAL/"

echo "Pulling memory ..."
# Claude Code keeps memory under ~/.claude/projects/<hash>/memory (hash derived from the workspace path).
MEM_LOCAL=$(ls -d "$HOME/.claude/projects/"*MCP*/ 2>/dev/null | head -1)
if [ -n "$MEM_LOCAL" ]; then
  MEM_LOCAL="${MEM_LOCAL%/}/memory"
else
  H=$(echo "$WS_LOCAL" | sed 's#[/:]#-#g')      # /Users/you/MCP -> -Users-you-MCP
  MEM_LOCAL="$HOME/.claude/projects/$H/memory"
fi
if [ -d "$MEM_NAS" ]; then
  mkdir -p "$MEM_LOCAL"
  run_rsync "memory" -a --delete --exclude='._*' --exclude='.DS_Store' "$MEM_NAS/" "$MEM_LOCAL/"
else
  note_skip "memory — skipped (no $MEM_NAS on the NAS)"
fi

echo "Pulling local notes ..."
if [ -d "$NOTES_NAS" ]; then
  mkdir -p "$NOTES_LOCAL"
  run_rsync "notes" -a --delete --exclude='.DS_Store' --exclude='._*' "$NOTES_NAS/" "$NOTES_LOCAL/"
else
  note_skip "notes — skipped (no $NOTES_NAS on the NAS)"
fi

echo "Pulling secrets (off-git folder) ..."
SEC_NAS="$NAS/secrets"
if [ -d "$SEC_NAS" ]; then
  SEC_ERR=0; SEC_N=0
  pull_secret() { # pull_secret <src-file> <dst-dir>
    [ -f "$1" ] || return 0
    mkdir -p "$2" && rsync -a "$1" "$2/" && SEC_N=$((SEC_N+1)) || SEC_ERR=1
  }
  # Mirror of the push_secret block in sync-push.command:
  pull_secret "$SEC_NAS/MCP/.mcp.json" "$HOME/MCP"
  # pull_secret "$SEC_NAS/MCP/my-project/service_account.json" "$HOME/MCP/my-project"
  if [ "$SEC_ERR" -eq 0 ]; then note_ok "secrets — OK (files: $SEC_N)"; else note_fail "secrets — FAILED (some files not copied)"; fi
else
  note_skip "secrets — skipped (no $SEC_NAS on the NAS)"
fi

echo ""
echo "==================== SUMMARY ===================="
printf '%s\n' "$SUMMARY"
echo "================================================="
if [ "$FAIL" -eq 0 ]; then
  printf '%sDONE %s — this Mac now has the latest copy. Open Claude Code in %s%s\n' "$GRN" "$(date '+%H:%M:%S')" "$WS_LOCAL" "$RST"
else
  printf '%sFINISHED WITH ERRORS — see the ✗ lines above. The local copy may be incomplete!%s\n' "$RED" "$RST"
fi
read -n1 -r -p "Press any key to close..."

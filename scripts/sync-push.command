#!/bin/bash
# Sync PUSH for macOS: send this Mac's copy up to the NAS.
# Run WHEN YOU FINISH working. Double-click (after a one-time: chmod +x this file).
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
if [ ! -d "$NAS" ]; then echo "${RED}ERROR: NAS not found at $NAS. Connect to the network drive first.${RST}"; read -n1 -r -p "Press any key..."; exit 1; fi
if [ ! -f "$WS_LOCAL/CLAUDE.md" ]; then echo "${RED}ERROR: local workspace looks empty (no CLAUDE.md at $WS_LOCAL). Aborting to protect the NAS copy.${RST}"; read -n1 -r -p "Press any key..."; exit 1; fi

echo "Pushing workspace to NAS ..."
mkdir -p "$WS_NAS"
run_rsync "workspace" -a --delete \
  --exclude='.git' --exclude='.venv' --exclude='node_modules' \
  --exclude='__pycache__' --exclude='.pytest_cache' --exclude='dist' --exclude='build' \
  --exclude='__MACOSX' \
  --exclude='.DS_Store' --exclude='._*' --exclude='*.log' --exclude='.mcp.json' \
  "$WS_LOCAL/" "$WS_NAS/"

echo "Pushing memory ..."
MEM_LOCAL=$(ls -d "$HOME/.claude/projects/"*MCP*/ 2>/dev/null | head -1)
if [ -n "$MEM_LOCAL" ]; then
  MEM_LOCAL="${MEM_LOCAL%/}/memory"
  if [ -d "$MEM_LOCAL" ]; then
    mkdir -p "$MEM_NAS"
    run_rsync "memory" -a --delete --exclude='._*' --exclude='.DS_Store' "$MEM_LOCAL/" "$MEM_NAS/"
  else
    note_skip "memory — skipped (no $MEM_LOCAL)"
  fi
else
  note_skip "memory — skipped (project not found in ~/.claude/projects)"
fi

echo "Pushing local notes ..."
if [ -d "$NOTES_LOCAL" ]; then
  mkdir -p "$NOTES_NAS"
  run_rsync "notes" -a --delete --exclude='.DS_Store' --exclude='._*' "$NOTES_LOCAL/" "$NOTES_NAS/"
else
  note_skip "notes — skipped (no $NOTES_LOCAL)"
fi

echo "Pushing secrets (off-git folder) ..."
SEC_NAS="$NAS/secrets"
SEC_ERR=0; SEC_N=0
push_secret() { # push_secret <src-file> <dst-dir>
  [ -f "$1" ] || return 0
  mkdir -p "$2" && rsync -a "$1" "$2/" && SEC_N=$((SEC_N+1)) || SEC_ERR=1
}
# One line per gitignored secret file your projects need, e.g.:
push_secret "$HOME/MCP/.mcp.json" "$SEC_NAS/MCP"
# push_secret "$HOME/MCP/my-project/service_account.json" "$SEC_NAS/MCP/my-project"
if [ "$SEC_ERR" -eq 0 ]; then note_ok "secrets — OK (files: $SEC_N)"; else note_fail "secrets — FAILED (some files not copied)"; fi

if echo "$(date '+%Y-%m-%d %H:%M:%S')  pushed from Mac ($(hostname))" > "$NAS/LAST-SYNC.txt"; then
  note_ok "LAST-SYNC.txt updated"
else
  note_fail "LAST-SYNC.txt — write failed"
fi

echo ""
echo "==================== SUMMARY ===================="
printf '%s\n' "$SUMMARY"
echo "================================================="
if [ "$FAIL" -eq 0 ]; then
  printf '%sDONE %s — the NAS now holds the latest copy; you can switch machines.%s\n' "$GRN" "$(date '+%H:%M:%S')" "$RST"
else
  printf '%sFINISHED WITH ERRORS — see the ✗ lines above. The NAS copy may be incomplete!%s\n' "$RED" "$RST"
fi
read -n1 -r -p "Press any key to close..."

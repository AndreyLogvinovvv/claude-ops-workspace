# Claude Code Ops Workspace

My personal setup for driving day-to-day operational / analytics work with
[Claude Code](https://claude.com/claude-code): a context-first workspace, a live
usage widget, and automated git backup.

This repo is the **sanitized, shareable** version — the concepts, code and
methodology, with all organization-specific data removed (contacts, IDs,
schemas, internal URLs live only in a private copy).

## The idea

The workspace is built around three ideas:

1. **Context as a file (`CLAUDE.md`).** Instead of re-explaining who people are,
   which channels/boards matter, and how I like things done every session, it
   all lives in a single `CLAUDE.md` that Claude Code reads automatically. See
   [`CLAUDE.md.template`](CLAUDE.md.template) for the structure (with
   placeholders).

2. **A live usage widget.** A tiny local server + browser extension that reads
   Claude usage (5-hour session + weekly) and renders a clean dashboard, so I
   always know how much budget is left. See [`usage-widget/`](usage-widget/).

3. **Hands-off backup.** A scheduled script that commits and pushes the whole
   workspace once a day, so work is never lost. See
   [`scripts/auto-backup.ps1`](scripts/auto-backup.ps1).

## Layout

| Path | What |
|---|---|
| `CLAUDE.md.template` | Skeleton for a context-first Claude Code workspace |
| `usage-widget/` | Local usage dashboard (Python server + Chrome extension) |
| `scripts/auto-backup.ps1` | Daily auto-commit + push (Windows Task Scheduler) |
| `scripts/sync-push.ps1` / `sync-pull.ps1` | Multi-machine sync over a home NAS (Windows) |
| `scripts/sync-push.command` / `sync-pull.command` | Same sync scripts for macOS (rsync, auto-mounts the SMB share) |
| `scripts/swiftbar/` | macOS menubar buttons (⏫ push / ⏬ pull) via [SwiftBar](https://github.com/swiftbar/SwiftBar) |

## Multi-machine sync

I work on the same workspace from several machines (two Windows PCs and a Mac).
Instead of pushing work-in-progress to git, the whole workspace + Claude's
persistent memory travel through a NAS share:

- **`sync-push`** — run when you *finish* on a machine: mirrors the workspace,
  Claude memory (`~/.claude/projects/<project>/memory`), optional local notes,
  and a short list of gitignored secret files into an off-git `secrets/` folder
  on the NAS.
- **`sync-pull`** — run *before* you start on another machine: brings all of it
  back. Both directions refuse to run against an empty source/target, so a
  broken mount can't wipe the master copy.
- Windows uses `robocopy /MIR`, macOS uses `rsync -a --delete`; the scripts are
  kept in sync pair-wise. On the Mac the ⏫/⏬ SwiftBar buttons make it
  one-click.

## Notes

- Windows-first (PowerShell 5.1), but the pieces are small and easy to port.
- Keep secrets out of the repo — see `.gitignore`. Tokens/keys belong in your
  OS credential store or environment, never in tracked files.

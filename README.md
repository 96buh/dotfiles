# dotfiles

macOS uses **nix-darwin / Home Manager**. Linux uses **GNU Stow**.
There is no setup script. Clone and maintain your Neovim configuration separately.

## macOS: existing installation

```sh
sudo darwin-rebuild build --flake "$HOME/.dotfiles#macbookpro"
sudo darwin-rebuild switch --flake "$HOME/.dotfiles#macbookpro"
```

`build` only builds; `switch` installs packages and home links.

Before the first build on another Mac, edit **`macos/settings.nix`**. It is the
single place to configure the existing account and architecture:

```nix
let
  username = "your-account"; # Output of `id -un`, run without sudo.
in {
  inherit username;
  homeDirectory = "/Users/${username}"; # Or the actual value of $HOME.
  hostName = "macbook"; # Terminal hostname; Bonjour adds .local separately.
  system = "aarch64-darwin"; # Use x86_64-darwin for an Intel Mac.
}
```

Nix-darwin, Home Manager and nix-homebrew all use these values. The checked-in
defaults preserve the current `homer` / Apple Silicon setup. This selects an
existing account; it does not rename your login account or move its home.
The `#macbookpro` flake target is a configuration label, independent of your
username and the Mac's hostname, so the commands above remain unchanged.

Flakes use pure evaluation, so this configuration does not infer the account
from `$USER` or `$HOME` during a sudo rebuild. Shared shell scripts use `$HOME`
at runtime; Linux Stow deployment already targets the current user's `$HOME`.

Git author details are separate from the login account. When adopting this
repository, update `[user]` in `dotfiles/common/.config/git/config`. Remote TeX
also has its own SSH host/account settings, described below.

Home Manager uses the original `force = true` behavior for managed app settings:
conflicting files are replaced by the repository version. Homebrew apps are
managed by the existing nix-homebrew configuration.

`macos/dotfiles.nix` automatically maps files from `dotfiles/common/` and
`dotfiles/macos/` into the configured home directory. Mac-only files win if both
trees contain the same path. Add new dotfiles to these trees and register new
files with Git before building; no per-file `home.file` declarations are needed.
Stow metadata, local TOML overrides, caches and editor backups are excluded.
Only repository entries are managed, not entire agent state directories.

## macOS: new machine

A new Mac does not have `darwin-rebuild` yet. First install Command Line Tools
(if Git is unavailable), then Nix:

```sh
xcode-select --install
# Wait for installation to finish, then:
curl -L https://nixos.org/nix/install | sh
```

Open a new terminal and check `nix --version`. Clone this repository into
`~/.dotfiles` using your usual Git credentials (the HTTPS URL is
`https://github.com/96buh/nix-config.git`). Then initialize nix-darwin once:

```sh
sudo nix --extra-experimental-features "nix-command flakes" \
  run nix-darwin/master#darwin-rebuild -- \
  switch --flake "$HOME/.dotfiles#macbookpro"
```

After the first successful switch, open a new terminal. Future updates use the
normal `sudo darwin-rebuild switch --flake ...` command above. No installer or
bootstrap wrapper is maintained in this repo.

References: [Install Nix](https://nix.dev/install-nix),
[nix-darwin installation](https://github.com/nix-darwin/nix-darwin#step-2-installing-nix-darwin).

## Linux: Stow

Install GNU Stow and the applications you use. On Arch/CachyOS, for example:

```sh
sudo pacman -Syu --needed stow git zsh tmux
```

Additional applications and LaTeX dependencies are listed in
`packages/cachyos/pacman.txt`; optional AUR packages are listed in `aur.txt`.
Install them with your package manager. Stow links files only; it does not
install applications, change your login shell or reload tmux.

From the repository root, preview links and then apply:

```sh
cd ~/.dotfiles
stow --no-folding -n -v -d dotfiles -t "$HOME" common linux
stow --no-folding -v -d dotfiles -t "$HOME" common linux
```

If existing files conflict, compare and back them up outside the repository,
then retry. Do not use `--adopt` to replace repository contents. Your independent
`~/.config/nvim` repo is not a Stow package and is left alone. The layout uses
the normal `~/.config` and `~/.local/share` paths.

The managed zsh configuration adds `~/.local/bin` to PATH. Reopen the terminal
or source `~/.zshrc` after switching to it. zinit installs its plugins on first
interactive startup. `.gitkeep`, Python caches and local overrides are excluded
from Stow deployment.

Machine-specific shell settings can go in `~/.config/zsh/local.zsh`, which is
loaded by the managed `.zshrc` and remains outside Stow. Linux's tmux colors
live in `dotfiles/linux/.config/tmux/appearance.conf`; the common configuration
loads it when present. Back up an old `~/.tmux.conf` outside the home directory's
config search paths so it does not take precedence over `~/.config/tmux/tmux.conf`.

Once linked, edits to existing repository files are visible through the links
immediately. Reload the application to read the changes; Stow does not reload it.
For zsh, open a new terminal or run `source ~/.zshrc`. For an existing tmux
server, run `tmux source-file ~/.config/tmux/tmux.conf`.

After adding, renaming or deleting managed files, preview and restow:

```sh
cd ~/.dotfiles/dotfiles
stow --no-folding -n -R -t "$HOME" common linux
stow --no-folding -R -t "$HOME" common linux
```

## Remote TeX preview

Runtime code lives in `dotfiles/common/tools/remote-tex-preview/`. On Mac, all
its deployment is handled by `macos/dotfiles.nix`: switch creates
`~/tools/remote-tex-preview/` with links to the Nix store. On Linux, Stow links
the same location directly to this repository.

The Neovim integration is loaded from the standard user runtime under
`~/.local/share/nvim/site/plugin/`; it does not modify your Neovim repo.
That entry point loads `~/tools/remote-tex-preview/preview.lua`, which handles
PDF publishing and forward search in Linux SSH sessions. Both Lua files are needed.
Mac local sessions retain VimTeX/Skim, Linux local sessions retain Zathura, and
SSH sessions on Linux publish successful manual builds to Mac. Save and compile
manually, with SyncTeX enabled, starting Neovim next to `main.tex`.

The default SSH alias is `linux`; the remote tool is
`/home/homer/tools/remote-tex-preview/rtp.py`. Set up your SSH keys/alias yourself.
Mac uses Apple's `/usr/bin/ssh` to support `UseKeychain`.
The watcher reads `~/.config/remote-tex-preview/config.toml` using Python 3.11+
(provided by the Mac configuration). Machine-specific settings go in the
unmanaged `~/.config/remote-tex-preview/config.local.toml`:

```toml
# Override just the settings that differ on this machine.
host = "your-linux-alias"
remote_tool = "/home/your-user/tools/remote-tex-preview/rtp.py"
```

Start on Mac with `remote-tex-preview` (or `texwatch` in the managed zsh).
Use Ctrl-C to stop; `remote-tex-preview --once` checks one cycle.

Configuration uses TOML only. After switching from an older installation,
update Skim's Sync arguments to use `config.toml`, as shown below.

Configure Skim Settings > Sync once: disable automatic reload, select Custom,
set Command to the absolute result of `command -v remote-tex-preview`, and set
Arguments to:

```text
inverse /absolute/path/to/your/home/.config/remote-tex-preview/config.toml "%file" %line
```

Replace the config path above with your actual home directory (`echo "$HOME"`);
the Skim arguments are not a shell command, so use an absolute path.
Allow macOS Automation access when prompted. `\v` performs background forward
search; Shift-Command-click in Skim returns to the correct local/remote Neovim.
Mac local inverse search does not require running the watcher. If tmux keeps a
stale SSH environment, start Linux Neovim with `RTP_REMOTE_PREVIEW=0` for local
preview or `RTP_REMOTE_PREVIEW=1` for remote preview.

## Shared agent instructions and skills

Edit `dotfiles/common/.config/agents/AGENTS.md` for personal instructions shared
by Codex and Pi. Relative links under `.codex/` and `.pi/agent/` expose the same
instructions at each harness's expected path. Mac Home Manager and Linux Stow
deploy these links automatically. Project-specific `AGENTS.md` files remain
with their own projects.

The only skills managed here are `latex-expl3` and `academic-humanizer`. Their
sources live in `dotfiles/common/.config/agents/skills/`; links under
`.codex/skills/` and `.pi/agent/skills/` share them without maintaining copies.
The academic-humanizer snapshot retains its upstream README, MIT license and
support files. Other installed skills are left unmanaged and unchanged.

Pi's `~/.pi/agent/settings.json` remains writable and unmanaged because Pi also
stores model choices and device state there. Set these preferences once on each
machine, preserving the other keys:

```json
{
  "externalEditor": "nvim",
  "terminal": { "showTerminalProgress": true }
}
```

Pi also receives `/review` (read-only Git review) and `/handoff` (a concise task
handoff) from `.pi/agent/prompts/`. Start a new Codex session after deployment;
in Pi use `/reload` for instructions, skills and prompts. Restart Pi to ensure
all preference changes take effect. Login credentials, sessions and the full
Codex/Pi settings files are not managed by this repository.

## Codex completion alerts over SSH

The managed zsh `codex` function enables a BEL notification after each completed
interactive turn. SSH carries it back to Ghostty, and the managed tmux settings
forward bells from all windows. Ghostty requests Dock attention when it is
unfocused, without playing an alert sound. This also works for local Codex CLI.
It does not depend on exiting Codex or disconnecting SSH.

Apply the Mac configuration and reload Ghostty with Command-Shift-comma.
Deploy the common dotfiles on the SSH host using the Linux Stow instructions,
then open a new remote shell. For existing tmux servers on either side, run:

```sh
tmux source-file ~/.config/tmux/tmux.conf
```

For a quick check in the SSH terminal, run `sleep 3; printf '\a'`, then switch
to another app before the timer expires. Ghostty's Dock icon should bounce once.
Run `type codex` remotely to confirm it resolves to the managed shell function.
`command codex` bypasses these defaults; noninteractive `codex exec` does not use
TUI notifications.

## Terminal workflow

Use separate Ghostty tabs for local work and SSH hosts, with one tmux session
per project on the machine running the work. Connect from a fresh local shell
with `ssh -t linux 'tmux new-session -A -s research'` to create or reattach a
remote session. Ghostty's SSH integration prepares remote terminfo when needed.

Tmux shows the host on the right and a bell marker on inactive windows that
received a completion alert. Closed windows are automatically renumbered.
After Ctrl-b, use `c` for a new window, `|` for side-by-side panes, or `-` for
stacked panes; each starts in the current pane's directory. The default `%`
and `"` split bindings also preserve the directory. Use `z` to zoom/restore a
pane, `w` to choose a window, and `s` to choose a session.

Give independently editing agents separate Git worktrees and named tmux windows.
Keep a window for editing/review and another for tests or logs. Remote tmux keeps
jobs running across SSH disconnects, but terminal bell alerts require an attached
client and a live connection to reach the Mac.

## Yazi Git status

The shared Yazi configuration includes the official `git.yazi` plugin and its
`package.toml` version record. The plugin files are included so both Home Manager
and Stow deploy it without a separate download step. Restart Yazi after deployment.

File status signs are `✓` (clean), `M` (unstaged changes), `S` (staged changes),
`A` (added), `D` (deleted), `U` (conflict), `?` (untracked) and `!` (ignored).
Directory signs summarize their contents. Press `.` to toggle hidden files.

Update the vendored plugin deliberately from the repository root:

```sh
YAZI_CONFIG_HOME="$PWD/dotfiles/common/.config/yazi" ya pkg upgrade
```

Commit both the updated plugin files and `package.toml` after checking compatibility
with the installed Yazi version.

## Other tools and layout

- `macos/`: Nix system, Home Manager, packages, fonts and Homebrew settings.
- `dotfiles/common/`, `dotfiles/linux/`, `dotfiles/macos/`: native home files.
- `packages/cachyos/`: reference package lists, without an installer.
- `docs/` and `tests/`: local notes/tests, ignored by Git. Python caches are ignored too.

`pdf-opener` searches PDFs with fd/fzf. Ghostty Command-p invokes it at the zsh
prompt; override search roots in `~/.config/pdf-opener/config` using
`PDF_SEARCH_PATHS=("$HOME/Documents" "$HOME/Downloads")`. Tmux's Ctrl-b then p
selects the previous window. `tmux-sessionizer` remains the session picker.

Update Mac flake inputs deliberately with `nix flake update`, then build and
switch. On Linux, existing links follow pulled content changes; restow when
managed paths are added, renamed or removed, then reload affected applications.
Linux deployment and repeat previews were verified in temporary directories and
on this machine; tmux loaded successfully in an isolated server. macOS build/switch
and GUI behavior must be verified on Mac.

# dotfiles

macOS uses **nix-darwin / Home Manager**. Linux uses **GNU Stow**.
There is no setup script. Clone and maintain your Neovim configuration separately.

## macOS: existing installation

```sh
sudo darwin-rebuild build --flake "$HOME/.dotfiles#macbookpro"
sudo darwin-rebuild switch --flake "$HOME/.dotfiles#macbookpro"
```

`build` only builds; `switch` installs packages and home links. This configuration
is for Apple Silicon and user `homer`. Adjust `flake.nix`, `macos/default.nix` and
`macos/home.nix` before using a different architecture or account.

Home Manager backs up conflicting unmanaged files as `.before-dotfiles` instead
of forcing overwrites. If a backup with that name already exists, move it aside
first. Homebrew apps are managed by the existing nix-homebrew configuration.

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

## Remote TeX preview

Runtime code lives in `dotfiles/common/tools/remote-tex-preview/`. On Mac, all
its deployment declarations are in `macos/home.nix`: switch creates
`~/tools/remote-tex-preview/` with links to the Nix store. On Linux, Stow links
the same location directly to this repository.

The Neovim integration is loaded from the standard user runtime under
`~/.local/share/nvim/site/plugin/`; it does not modify your Neovim repo.
Mac local sessions retain VimTeX/Skim, Linux local sessions retain Zathura, and
SSH sessions on Linux publish successful manual builds to Mac. Save and compile
manually, with SyncTeX enabled, starting Neovim next to `main.tex`.

The default SSH alias is `linux`; the remote tool is
`/home/homer/tools/remote-tex-preview/rtp.py`. Set up your SSH keys/alias yourself.
Mac uses Apple's `/usr/bin/ssh` to support `UseKeychain`. Machine-specific
settings go in the unmanaged `~/.config/remote-tex-preview/config.local.json`:

```json
{
  "host": "your-linux-alias",
  "remote_tool": "/home/your-user/tools/remote-tex-preview/rtp.py"
}
```

Start on Mac with `remote-tex-preview` (or `texwatch` in the managed zsh).
Use Ctrl-C to stop; `remote-tex-preview --once` checks one cycle.

Configure Skim Settings > Sync once: disable automatic reload, select Custom,
set Command to the absolute result of `command -v remote-tex-preview`, and set
Arguments to:

```text
inverse /Users/homer/.config/remote-tex-preview/config.json "%file" %line
```

Allow macOS Automation access when prompted. `\v` performs background forward
search; Shift-Command-click in Skim returns to the correct local/remote Neovim.
Mac local inverse search does not require running the watcher. If tmux keeps a
stale SSH environment, start Linux Neovim with `RTP_REMOTE_PREVIEW=0` for local
preview or `RTP_REMOTE_PREVIEW=1` for remote preview.

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
switch. Linux can re-run the same Stow command after pulling changes.
Linux deployment and preview behavior were tested in temporary directories;
macOS build/switch and GUI behavior must be verified on Mac.

# dotfiles

macOS: nix-darwin + Home Manager. Linux: GNU Stow. Keep Neovim config in its own repo.

## macOS

Install [Nix](https://nixos.org/download/) and clone this repo to `~/.dotfiles`.
Edit `macos/settings.nix`: account, home directory, hostname, architecture,
and `git.name` / `git.email`.

First activation (before `darwin-rebuild` is installed):

```sh
sudo nix --extra-experimental-features 'nix-command flakes' \
  run nix-darwin/master#darwin-rebuild -- switch --flake ~/.dotfiles#macbookpro
```

For later changes:

```sh
sudo darwin-rebuild build --flake ~/.dotfiles#macbookpro
sudo darwin-rebuild switch --flake ~/.dotfiles#macbookpro
```

## Linux

Install GNU Stow, uv and the applications you use. Package references are in
`packages/cachyos/`.

```sh
cd ~/.dotfiles
./scripts/deploy-linux --check
./scripts/deploy-linux

git config --file ~/.config/git/config.local user.name 'Your Name'
git config --file ~/.config/git/config.local user.email 'you@example.com'
```

If Pi is installed, run `pi update --extensions` after deployment to install the
shared package list, then start Pi and sign in with `/login` as needed. The
managed `packages` list replaces the local list; credentials stay on each machine.
If using Herdr, install its plugins once:

```sh
herdr plugin install beyondlex/herdr-recent-navigator
herdr plugin install qu8n/herdr-automatic-rename
```

## Editing

- Home files: `dotfiles/common/`, with platform files in `dotfiles/macos/` and `dotfiles/linux/`.
- Agent preferences: `dotfiles/settings/codex.toml` and `pi.json`; deployment merges them into writable configs and backs up changes.
- Shared Codex/Pi instructions and skills: `dotfiles/common/.config/agents/`.
- Machine-local shell options: `~/.config/zsh/local.zsh` (unmanaged).

New files must be registered with Git before a Nix build. Back up conflicting
home files before deployment; do not use Stow `--adopt`. Reopen the terminal
and restart affected applications after deploying.

## Remote TeX preview

Set your SSH alias and remote tool path in
`~/.config/remote-tex-preview/config.local.toml`; see
`dotfiles/common/.config/remote-tex-preview/config.example.toml`.
Run `remote-tex-preview` on Mac, then compile manually in remote Neovim.

In Skim → Settings → Sync, select Custom. Command: the absolute output of
`command -v remote-tex-preview`. Arguments (replace the home path):

```text
inverse /Users/YOUR_USER/.config/remote-tex-preview/config.toml "%file" %line
```

Use `\v` for forward search and Shift-Command-click in Skim for inverse search.

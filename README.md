# dotfiles

Configure macOS and Linux from the repository root:

```sh
./setup check   # Check dependencies and shell syntax
./setup plan    # macOS: build only; Linux: preview links
./setup apply   # Apply to the current machine
```

The platform is detected automatically. Run as your normal user; macOS apply
invokes sudo when needed. No extra task runner is required.

## Layout

```text
setup                 # One command entry point for both platforms
flake.nix / flake.lock # Mac Nix entry point and pinned dependencies
macos/                # Mac-only Nix: system, Home Manager, packages and fonts
dotfiles/
  common/             # Shared native dotfiles, mirroring $HOME
  macos/              # Mac-only app settings: AeroSpace, Karabiner, Ghostty
  linux/              # Linux-only app settings; currently reserved
packages/cachyos/     # Reserved pacman / AUR manifests
docs/                 # Supporting docs and agent plans/notes
```

macOS requires an existing Nix / nix-darwin installation. `plan` builds without
switching or replacing the repository's `result` link; `apply` runs nix-darwin
switch. Both use a `path:` flake, so newly moved files are included before Git
staging. The Mac profile remains specific to `homer` / `macbookpro`.

Linux requires GNU Stow, Git, zsh and tmux. `apply` previews conflicts first,
then links `common` and `linux` into your home directory. Existing files are
never adopted or overwritten. Move conflicting settings to a backup outside
this repository before retrying. Linux uses no Nix; system packages, desktop
settings, shell plugins and tmux plugins are installed separately. Use the
standard `~/.config` location.

Setup does not change your login shell, start/reload tmux, or install Nix,
Homebrew, pacman/AUR packages, or plugins. The shell's existing zinit bootstrap
still downloads zinit/plugins on first interactive startup.

See [Linux setup](docs/linux.md), [tmux plugins](docs/tmux.md),
[CachyOS package plans](docs/cachyos-packages.md), and the
[integration roadmap](docs/cachyos-integration-plan.md).
Only this README belongs at the root; keep other Markdown in `docs/`.

## PDF picker

Press `Command-p` in Ghostty to search PDF filenames and paths, both at the
zsh prompt and inside tmux. The picker uses the current terminal pane. Press Enter
to open the selected PDF in the default viewer, or Esc to cancel. The shell
shortcut preserves your current command line. In both cases, use the shortcut
at the zsh prompt.
Tmux's `Ctrl-b` then `p` switches to the previous window.

The picker searches your home directory, including hidden and ignored files,
except `Library`, `.git`, and `.cache` directories. On macOS, it also searches
`~/Library/CloudStorage/OneDrive-Personal` when that directory exists.
Customize the search roots
in `~/.config/pdf-opener/config`:

```bash
PDF_SEARCH_PATHS=("$HOME/Documents" "$HOME/Downloads")
```

You can also run `pdf-opener /path/to/papers` directly. Apply the configuration
as described above to install the script and shortcuts.

## Remote TeX preview (macOS)

`macos/remote-tex-preview/` contains the Python tool, remote VimTeX hook,
example configuration and tests. Run `./setup apply` to install the
`remote-tex-preview` command and files under `~/.local/share/remote-tex-preview`.
Skim is provided by the macOS Homebrew configuration.

Copy `~/.local/share/remote-tex-preview/config.example.json` to
`~/.config/remote-tex-preview.json`, then set your SSH alias and the absolute
remote path to `rtp.py`. Start the client with:

```sh
remote-tex-preview watch ~/.config/remote-tex-preview.json
```

On the remote machine, copy `rtp.py` and `preview.lua` together to a permanent
directory. Load `dofile('/absolute/path/preview.lua').setup()` before opening
TeX buffers in Neovim with VimTeX, starting Neovim in the project root containing
`main.tex`. Compile manually with SyncTeX enabled; the hook publishes successful
builds and forwards `:VimtexView` requests to Skim. The client discovers active
projects over SSH; it does not start a compiler.

For inverse search, configure Skim's custom Sync PDF command as
`/Users/homer/.nix-profile/bin/remote-tex-preview` (or the absolute command path
reported by `command -v remote-tex-preview`), with arguments:

```text
inverse /Users/homer/.config/remote-tex-preview.json "%file" %line
```

Disable Skim's automatic file reload; the client explicitly reloads each snapshot.
Local PDF inverse searches continue through VimTeX's existing entry point.
Run the bundled tests with
`python3 -m unittest discover -s macos/remote-tex-preview/tests -v`.

## Maintenance

Update the Mac lock file explicitly, then preview the configuration:

```sh
nix flake update
./setup plan
```

Home Manager-managed files use `force = true`. Linux Stow deployment refuses
conflicts instead of replacing existing settings.

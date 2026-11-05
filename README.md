# dotfiles

Configure macOS and Linux from the repository root:

```sh
./setup packages # Arch/CachyOS: upgrade and install the package manifest
./setup check    # Check dependencies, Python/config and shell syntax
./setup preview  # Linux: deploy just the TeX preview integration
./setup plan     # macOS: build only; Linux: preview all Stow links
./setup apply    # Apply all managed settings
```

The platform is detected automatically. Run as your normal user; macOS apply
invokes sudo when needed. No extra task runner is required.

## Layout

```text
setup                 # One command entry point for both platforms
flake.nix / flake.lock # Mac Nix entry point and pinned dependencies
macos/                # Mac-only Nix: system, Home Manager, packages and fonts
dotfiles/
  common/             # Shared native dotfiles and tools, mirroring $HOME
  macos/              # Mac-only app settings: AeroSpace, Karabiner, Ghostty
  linux/              # Linux-only app settings; currently reserved
packages/             # CachyOS package manifests
scripts/              # Safe preview deployment and checks
tests/                # Deployment, launcher and remote preview tests
docs/                 # Supporting docs and agent plans/notes
```

macOS requires an existing Nix / nix-darwin installation. `plan` builds without
switching or replacing the repository's `result` link; `apply` runs nix-darwin
switch. Both use a `path:` flake, so newly moved files are included before Git
staging. The Mac profile remains specific to `homer` / `macbookpro`.

Linux uses GNU Stow, Git, zsh and tmux. `./setup packages` installs the manifest,
including Python, Neovim, TeX Live, Biber, minted dependencies and fonts.
`apply` previews conflicts first,
then links `common` and `linux` into your home directory. Existing files are
never adopted or overwritten. Move conflicting settings to a backup outside
this repository before retrying. Linux uses no Nix; desktop settings and optional
AUR packages remain separate. Use the standard `~/.config` location.

Setup does not change your login shell, start/reload tmux, or bootstrap
Nix/Homebrew. Only the explicit `packages` action invokes pacman; it never invokes
an AUR helper. The shell's existing zinit bootstrap
still downloads zinit/plugins on first interactive startup.

See [Rebuild and migration guide](docs/rebuild.md) for exact Linux/macOS steps,
existing-file conflicts, Skim configuration and validation limits.
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

## Neovim and remote TeX preview

Clone and maintain your Neovim configuration yourself in its own Git repo.
Dotfiles does not clone, update, inspect or edit `~/.config/nvim`.

The shared tool lives at `~/tools/remote-tex-preview/`. On Mac, its deployment,
command and configuration are declared together in `macos/home.nix`. Build alone
does not create home links: run a successful nix-darwin switch. Mac files link to
the Nix store; Linux links point directly into this repository. Tests stay under
`tests/` and are not deployed with the tool. The integration is loaded
from Neovim's user runtime (`~/.local/share/nvim/site/plugin/remote-tex-preview.lua`),
so it does not require adding a project path to the independent Neovim init.
Linux local sessions retain Zathura; SSH sessions publish manual successful builds
to Mac Skim. macOS retains its local VimTeX viewer. Forward search stays in the background.

Start on Mac with one command (no long arguments):

```sh
remote-tex-preview
# or, after reloading the managed zsh configuration:
texwatch
```

`remote-tex-preview --once` checks one synchronization cycle. Subcommands such as
`inverse` still accept explicit arguments. Host-specific overrides go in the
unmanaged `~/.config/remote-tex-preview/config.local.json` and survive rebuilds.
The default SSH alias is `linux`; the remote tool path is
`/home/homer/tools/remote-tex-preview/rtp.py`, independent of the assignment repo.
Configure the SSH alias and Skim once as described in the guide.

Linux `./setup preview` deploys only the preview links and refuses conflicts.
It does not read or write the independent Neovim configuration.

## Maintenance

Update the Mac lock file explicitly, then preview the configuration:

```sh
nix flake update
./setup plan
```

Home Manager backs up conflicting unmanaged files with `.before-dotfiles` instead of forcing overwrites. If that backup already exists, move it aside first. Linux Stow refuses conflicts instead of replacing existing settings.

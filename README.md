# dotfiles

Declarative macOS and NixOS configuration built with Nix flakes, nix-darwin,
Home Manager, and nix-homebrew.

## Apply the configuration

Preview the macOS configuration before switching:

```sh
darwin-rebuild build --flake ~/.dotfiles#macbookpro
```

Apply it after reviewing the build:

```sh
sudo darwin-rebuild switch --flake ~/.dotfiles#macbookpro
```

On the NixOS host:

```sh
sudo nixos-rebuild switch --flake ~/.dotfiles#nixos
```

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

## Maintenance

Update all locked inputs, then validate both configurations:

```sh
nix flake update
nix flake check --no-build
nix eval .#darwinConfigurations.macbookpro.config.system.build.toplevel.drvPath
nix eval .#nixosConfigurations.nixos.config.system.build.toplevel.drvPath
```

Home Manager-managed files use `force = true`, so the repository version is
applied directly without accumulating local backup files.

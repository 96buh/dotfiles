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

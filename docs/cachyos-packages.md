# CachyOS packages

`packages/cachyos/` is reserved for Linux package manifests. No Nix
configuration belongs there.

When the Linux setup is available, add verified pacman package names to
`cli.txt`, `dev.txt`, `desktop.txt`, and `fonts.txt`, and keep AUR packages in
`aur.txt`. These files have not been populated yet; Nix and Homebrew package
names should not be copied directly.

Package installation will be separate from deploying `dotfiles/common` and
`dotfiles/linux`. The root `./setup` command deploys configuration links; package installation is not automated yet.

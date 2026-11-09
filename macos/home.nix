{
  pkgs,
  lib,
  settings,
  ...
}: {
  imports = [./dotfiles.nix];

  home.username = settings.username;
  home.homeDirectory = lib.mkForce settings.homeDirectory;

  home.sessionPath = ["$HOME/.local/bin"];
  # Install dependencies here; application settings live in dotfiles/common.
  home.packages = [
    pkgs.git
    pkgs.tmux
    pkgs.zsh
    pkgs.python3
    (pkgs.writeShellApplication {
      name = "remote-tex-preview";
      runtimeInputs = [pkgs.bash pkgs.python3 pkgs.neovim];
      text = ''
        exec bash ${../dotfiles/common/.local/bin/remote-tex-preview} "$@"
      '';
    })
  ];

  home.stateVersion = "24.11";
  # Let home Manager install and manage itself.
  programs.home-manager.enable = true;
}

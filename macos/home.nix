{
  pkgs,
  lib,
  ...
}: {
  home.username = "homer";
  home.homeDirectory = lib.mkForce "/Users/homer";

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

  # Deploy runtime files explicitly; tests and Python caches stay out of ~/tools.
  home.file."tools/remote-tex-preview/rtp.py" = {
    source = ../dotfiles/common/tools/remote-tex-preview/rtp.py;
  };

  home.file."tools/remote-tex-preview/preview.lua" = {
    source = ../dotfiles/common/tools/remote-tex-preview/preview.lua;
  };

  home.file.".config/remote-tex-preview" = {
    source = ../dotfiles/common/.config/remote-tex-preview;
    recursive = true;
    force = true;
  };

  home.file.".local/share/nvim/site/plugin/remote-tex-preview.lua" = {
    source = ../dotfiles/common/.local/share/nvim/site/plugin/remote-tex-preview.lua;
  };

  home.file.".config/git/config" = {
    source = ../dotfiles/common/.config/git/config;
    force = true;
  };

  home.file.".config/ruff/ruff.toml" = {
    source = ../dotfiles/common/.config/ruff/ruff.toml;
    force = true;
  };

  home.file.".config/tmux/tmux.conf" = {
    source = ../dotfiles/common/.config/tmux/tmux.conf;
    force = true;
  };

  home.file.".local/bin/tmux-sessionizer" = {
    source = ../dotfiles/common/.local/bin/tmux-sessionizer;
    executable = true;
    force = true;
  };

  home.file.".local/bin/pdf-opener" = {
    source = ../dotfiles/common/.local/bin/pdf-opener;
    executable = true;
    force = true;
  };

  home.file.".config/tmux-sessionizer" = {
    source = ../dotfiles/common/.config/tmux-sessionizer;
    recursive = true;
    force = true;
  };

  # Shared native files are deployed with Home Manager on Mac and Stow on Linux.
  home.file.".zshrc" = {
    source = ../dotfiles/common/.zshrc;
    force = true;
  };

  home.file.".config/ohmyposh" = {
    source = ../dotfiles/common/.config/ohmyposh;
    recursive = true;
    force = true;
  };

  home.file.".config/karabiner" = {
    source = ../dotfiles/macos/.config/karabiner;
    recursive = true;
    force = true;
  };

  home.file.".config/aerospace" = {
    source = ../dotfiles/macos/.config/aerospace;
    recursive = true;
    force = true;
  };

  home.file.".config/yazi" = {
    source = ../dotfiles/common/.config/yazi;
    recursive = true;
    force = true;
  };

  home.file.".config/ghostty" = {
    source = ../dotfiles/macos/.config/ghostty;
    recursive = true;
    force = true;
  };

  home.stateVersion = "24.11";
  # Let home Manager install and manage itself.
  programs.home-manager.enable = true;
}

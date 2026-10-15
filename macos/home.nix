{ pkgs, lib, ... }:

{
  home.username = "homer";
  home.homeDirectory = lib.mkForce "/Users/homer";


  home.sessionPath = [ "$HOME/.local/bin" ];
  # Install dependencies here; application settings live in dotfiles/common.
  home.packages = [ pkgs.git pkgs.tmux pkgs.zsh ];

  home.file.".config/git/config" = {
    source = ../dotfiles/common/.config/git/config;
    force = true;
  };

  home.file.".config/tmux/tmux.conf" = {
    source = ../dotfiles/common/.config/tmux/tmux.conf;
    force = true;
  };

  home.file.".config/tmux/plugins/sensible" = {
    source = "${pkgs.tmuxPlugins.sensible}/share/tmux-plugins/sensible";
    force = true;
  };

  home.file.".config/tmux/plugins/resurrect" = {
    source = "${pkgs.tmuxPlugins.resurrect}/share/tmux-plugins/resurrect";
    force = true;
  };

  home.file.".config/tmux/plugins/continuum" = {
    source = "${pkgs.tmuxPlugins.continuum}/share/tmux-plugins/continuum";
    force = true;
  };

  home.file.".config/tmux/plugins/yank" = {
    source = "${pkgs.tmuxPlugins.yank}/share/tmux-plugins/yank";
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

  # Native dotfiles are shared with the future non-Nix Linux setup.
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

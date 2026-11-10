# Home Manager
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
  # Shared Git options stay in common; identity comes from this Mac's settings.
  home.file.".config/git/config.local" = {
    text = lib.generators.toGitINI {user = settings.git;};
    force = true;
  };
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
  # Keep Codex's config writable; merge only our explicit preferences.
  home.activation.codexSettings = lib.hm.dag.entryAfter ["writeBoundary"] ''
    run ${(pkgs.python3.withPackages (ps: [ps.tomlkit]))}/bin/python3 \
      ${../scripts/apply-codex-settings.py} \
      --source ${../dotfiles/settings/codex.toml} \
      --target ${lib.escapeShellArg "${settings.homeDirectory}/.codex/config.toml"}
  '';
  # Let home Manager install and manage itself.
  programs.home-manager.enable = true;
}

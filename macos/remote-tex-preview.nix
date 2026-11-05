{pkgs, ...}: {
  home.packages = [
    (pkgs.writeShellApplication {
      name = "remote-tex-preview";
      runtimeInputs = [pkgs.python3 pkgs.openssh pkgs.neovim];
      text = ''
        exec python3 "$HOME/tools/remote-tex-preview/rtp.py" "$@"
      '';
    })
  ];

  home.file."tools/remote-tex-preview" = {
    source = ../dotfiles/common/tools/remote-tex-preview;
    recursive = true;
  };

  home.file.".config/remote-tex-preview" = {
    source = ../dotfiles/common/.config/remote-tex-preview;
    recursive = true;
    force = true;
  };
}

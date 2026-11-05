{pkgs, ...}: {
  home.packages = [
    (pkgs.writeShellApplication {
      name = "remote-tex-preview";
      runtimeInputs = [pkgs.python3 pkgs.openssh pkgs.neovim];
      text = ''
        exec python3 "$HOME/.local/share/remote-tex-preview/rtp.py" "$@"
      '';
    })
  ];

  home.file.".local/share/remote-tex-preview" = {
    source = ./remote-tex-preview;
    recursive = true;
  };
}

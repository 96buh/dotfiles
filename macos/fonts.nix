{pkgs, ...}: {
  fonts = {
    packages = with pkgs; [
      nerd-fonts.jetbrains-mono
      sarasa-gothic
      noto-fonts-cjk-sans-static
      noto-fonts-cjk-serif-static
    ];
  };
}

{ pkgs, ... }:
{
  homebrew = {
    enable = true;
    brews = [
      "mas" # search app ID
      "ripgrep"
      "perl"
      "cpanminus"
      "typst"
      "cmake"
      "git-lfs"
      "ffmpeg"
      "mole"
      "tree-sitter-cli"
      "poppler"
      "imagemagick"
      "cairo"
      "pkgconf"
      "deno"
      "llvm@17"
      "gdown"
      "unar"
      "tlrc"
    ];
    # GUI Apps
    casks = [
      "obsidian"
      "zotero"
      "visual-studio-code"
      "raycast"
      "anki"
      "ghostty"
      "zen"
      "discord"
      "spotify"
      "karabiner-elements"
      "thaw"
      "skim"
      "nikitabobko/tap/aerospace"
      "easydict"
      "mactex-no-gui"
      "bitwarden"
      "obs"
      "codex"
      "figma"
    ];
    onActivation = {
      autoUpdate = false;
      upgrade = false;
      cleanup = "zap";

      extraEnv = {
        HOMEBREW_NO_ENV_HINTS = "1";
      };
    };
  };
}

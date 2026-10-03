{ pkgs, ... }:
{
  homebrew = {
    enable = true;
    # App Store Apps, use `mas search "App Name"` to find app ID
    # masApps = {
    #     "Microsoft Word" = 462054704;
    # };
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
      "karabiner-elements" # keyboard remap
      "thaw"               # menu bar
      "skim"               # pdf reader
      "sioyek"             # pdf reader
      "nikitabobko/tap/aerospace" # window manager
      "easydict"
      "mactex-no-gui"
      "bitwarden" # password manager
      "obs"
      "codex"
      "copilot-cli"
      "figma"
      # "android-studio"
      # "intellij-idea"
      # "pycharm"
      # "latexit"
      # "steam"
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

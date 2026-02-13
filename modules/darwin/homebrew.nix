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
      "perl"
      "cpanm"
      "ripgrep"
      "cocoapods"
      "cmake"
      "codex"
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
      "jordanbaird-ice"    # menu bar
      "skim"               # pdf reader
      "nikitabobko/tap/aerospace" # window manager
      
      "easydict"
      # "android-studio"
      # "intellij-idea"
      # "pycharm"
      "latexit"
      "steam"
    ];
    onActivation = {
      autoUpdate = true;
      upgrade = true;
      cleanup = "zap";
    };
  };
}


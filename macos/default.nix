{
  self,
  pkgs,
  settings,
  ...
}: {
  imports = [
    ./fonts.nix
    ./homebrew.nix
  ];

  users.users.${settings.username}.home = settings.homeDirectory;
  system.primaryUser = settings.username;
  nixpkgs.config.allowUnfree = true;
  nix.settings.experimental-features = ["nix-command" "flakes"];
  system.configurationRevision = self.rev or self.dirtyRev or null;

  environment.systemPackages = import ./packages.nix {inherit pkgs;};

  # ~/.zshrc owns completion and the prompt, after extending fpath.
  programs.zsh = {
    enableGlobalCompInit = false;
    enableBashCompletion = false;
    promptInit = "";
  };
  nix-homebrew.enableZshIntegration = false;

  system.stateVersion = 6;
  system.defaults = {
    dock = {
      autohide = true;
      autohide-delay = 0.0;
      autohide-time-modifier = 0.2;
      # Apps in the dock
      persistent-apps = [
        "/Applications/Ghostty.app"
        "/Applications/Zen.app"
      ];
      show-recents = false;
      orientation = "bottom";
      # Hot corner action
      wvous-bl-corner = 4; # bottom left: Desktop
    };
    finder = {
      AppleShowAllExtensions = true;
      FXPreferredViewStyle = "clmv";
      ShowPathbar = true;
      ShowStatusBar = true;
    };
    trackpad = {
      TrackpadThreeFingerDrag = true; # three finger drag
      TrackpadThreeFingerTapGesture = 2; # 2 to trigger Look up & data detectors.
    };
    NSGlobalDomain = {
      AppleInterfaceStyle = "Dark";
      "com.apple.mouse.tapBehavior" = 1; # enable tap to click
      "com.apple.swipescrolldirection" = false;
    };

    controlcenter.BatteryShowPercentage = true; # show battery percentage
    WindowManager.HideDesktop = true;
    WindowManager.StandardHideDesktopIcons = true;
  };

  system.keyboard = {
    enableKeyMapping = true;
    remapCapsLockToEscape = true;
  };

  # Enable sudo authentication with Touch ID
  security.pam.services.sudo_local.touchIdAuth = true;
  security.pam.services.sudo_local.reattach = true;

  # app settings
  system.defaults.CustomUserPreferences = {
    "com.microsoft.VSCode" = {
      ApplePressAndHoldEnabled = false;
    };
    "com.jetbrains.intellij" = {
      ApplePressAndHoldEnabled = false;
    };
  };
}

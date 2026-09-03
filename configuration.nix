{ self, targetSystem }:
{
  users.users.homer = {
    # home = /Users/homer;
    home = if targetSystem == "x86_64-linux" then "/home/homer" else "/Users/homer";
  };

  system.primaryUser = "homer";

  nixpkgs.config.allowUnfree = true;
  nix.settings.experimental-features = [ "nix-command" "flakes" ];
  system.configurationRevision = self.rev or self.dirtyRev or null;
  # system.stateVersion = 6;
  nixpkgs.hostPlatform = targetSystem;
}

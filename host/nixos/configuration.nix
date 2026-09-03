{ config, pkgs, ... }:
{
  networking.hostName = "nixos";
  time.timeZone = "Asia/Taipei";
  i18n.defaultLocale = "en_US.UTF-8";
  
  nix.settings.experimental-features = [ "nix-command" "flakes" ];

  boot.loader.systemd-boot.enable = true;
  boot.loader.efi.canTouchEfiVariables = true;

  networking.networkmanager.enable = true;
  services.openssh.enable = true;

  users.users.homer = {
    isNormalUser = true;
    extraGroups = [ "wheel" "networkmanager" ];
    shell = pkgs.zsh;
    openssh.authorizedKeys.keys = [
      "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIDg5MikAdr5DCyFbAd0W5U2WTv3bKWUlHchZiqhCpqvK macbookpro"
    ];
  };
  programs.zsh.enable = true;
  security.sudo.enable = true;

  services.xserver.enable = true;
  system.stateVersion = "24.11";
}

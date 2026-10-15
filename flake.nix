{
  description = "Homer's macOS configuration";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";

    nix-darwin = {
      url = "github:nix-darwin/nix-darwin";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    nix-homebrew.url = "github:zhaofengli-wip/nix-homebrew";

    home-manager = {
      url = "github:nix-community/home-manager";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    neovim-nightly-overlay = {
      url = "github:nix-community/neovim-nightly-overlay";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = inputs@{
    self,
    nix-darwin,
    nix-homebrew,
    home-manager,
    neovim-nightly-overlay,
    ...
  }:
    let
      darwinSystem = "aarch64-darwin";
      neovimOverlay = neovim-nightly-overlay.overlays.default;

      homeManagerConfig = {
        home-manager = {
          useGlobalPkgs = true;
          useUserPackages = true;
          users.homer = import ./macos/home.nix;
        };
      };
    in
    {
      darwinConfigurations.macbookpro = nix-darwin.lib.darwinSystem {
        system = darwinSystem;
        modules = [
          ./macos
          home-manager.darwinModules.home-manager
          {
            nixpkgs.hostPlatform = darwinSystem;
            nixpkgs.overlays = [ neovimOverlay ];
          }
          homeManagerConfig
          nix-homebrew.darwinModules.nix-homebrew
          {
            nix-homebrew = {
              enable = true;
              enableRosetta = true;
              user = "homer";
              autoMigrate = true;
            };
          }
        ];
        specialArgs = { inherit inputs self; };
      };
    };
}

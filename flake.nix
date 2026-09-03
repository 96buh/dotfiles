{
  description = "Homer's macOS and NixOS configurations";

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
    nixpkgs,
    nix-homebrew,
    home-manager,
    neovim-nightly-overlay,
    ...
  }:
    let
      darwinSystem = "aarch64-darwin";
      linuxSystem = "x86_64-linux";
      neovimOverlay = neovim-nightly-overlay.overlays.default;

      homeManagerConfig = {
        home-manager = {
          useGlobalPkgs = true;
          useUserPackages = true;
          users.homer = import ./home/home.nix;
        };
      };
    in
    {
      darwinConfigurations.macbookpro = nix-darwin.lib.darwinSystem {
        system = darwinSystem;
        modules = [
          (import ./configuration.nix {
            inherit self;
            targetSystem = darwinSystem;
          })
          ./host/darwin
          home-manager.darwinModules.home-manager
          {
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
        specialArgs = { inherit inputs; };
      };

      nixosConfigurations.nixos = nixpkgs.lib.nixosSystem {
        system = linuxSystem;
        modules = [
          ./host/nixos/hardware-configuration.nix
          ./host/nixos/configuration.nix
          {
            nixpkgs.overlays = [ neovimOverlay ];
          }
          home-manager.nixosModules.home-manager
          homeManagerConfig
        ];
      };
    };
}

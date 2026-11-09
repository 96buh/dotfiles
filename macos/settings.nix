# Edit this file for the existing macOS account that will own the dotfiles.
# Find the account name with `id -un` (not the display name in System Settings).
let
  username = "homer";
in {
  inherit username;
  # Override this if the account uses a nonstandard home directory.
  homeDirectory = "/Users/${username}";
  # Terminal/SSH host name; Bonjour uses macbook.local on the local network.
  hostName = "macbook";
  # Apple Silicon: aarch64-darwin; Intel: x86_64-darwin.
  system = "aarch64-darwin";
}

{lib, ...}: let
  # Stow metadata, local overrides, caches and editor backups are not home files.
  excluded = name:
    builtins.elem name [
      ".git"
      ".gitkeep"
      ".DS_Store"
      ".stow-local-ignore"
      "__pycache__"
      ".pytest_cache"
      ".ruff_cache"
      ".venv"
      "config.local.toml"
    ]
    || builtins.any (suffix: lib.hasSuffix suffix name) [
      ".pyc" ".pyo" ".pyd" ".swp" ".swo" ".bak" "~"
    ]
    || lib.hasInfix ".before-" name;

  # Walk real directories only. Source symlinks remain individual home entries,
  # so shared AGENTS.md and skill links work without owning agent state folders.
  entries = root: relative: let
    directory = root + (lib.optionalString (relative != "") "/${relative}");
    children = builtins.readDir directory;
  in
    lib.concatMap (name: let
      target = lib.optionalString (relative != "") "${relative}/" + name;
    in
      if excluded name then []
      else if children.${name} == "directory" then entries root target
      else [{
        name = target;
        value = {
          source = root + "/${target}";
          force = true;
        } // lib.optionalAttrs (lib.hasPrefix ".local/bin/" target) {
          executable = true;
        };
      }]
    ) (builtins.attrNames children);
in {
  # Platform files override shared files at the same relative home path.
  home.file =
    builtins.listToAttrs (entries ../dotfiles/common "")
    // builtins.listToAttrs (entries ../dotfiles/macos "");
}

{ pkgs, config, ... }:

{
    enable = true;
    signing.format = null;
    settings = {
        user.email = "j29823678@gmail.com";
        user.name = "Homer";
        core.editor = "nvim";
    };
}

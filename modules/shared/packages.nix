{ pkgs }:
with pkgs;
[
    neovim
    # mkalias
    tmux
    fzf
    zoxide
    fd
    oh-my-posh
    pdf2svg
    fastfetch
    eza
    bat

    # Github
    gh

    # fswatch
    # choose-gui
    # Python
    uv
    # Nodejs
    nodejs
    nodePackages.eas-cli
    supabase-cli # interact with supabase

    go
    lua
    # file manager
    yazi
    # java
    jdk17
    ruby
    yt-dlp # download youtube videos 

    pandoc
    man
    # typst 
]


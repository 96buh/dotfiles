#!/bin/bash
directory=~/.config/hypr/wallpapers
monitor=`hyprctl monitors | grep Monitor | awk '{print $2}'`


if [ -d "$directory" ]; then
    # get current wallpaper
    current_wallpaper=`hyprctl hyprpaper listloaded`
    random_background=$(ls $directory/*.{jpg,png} | shuf -n 1)
    
    while [ $current_wallpaper == $random_background ]; do
      random_background=$(ls $directory/*.{jpg,png} | shuf -n 1)
    done


    hyprctl hyprpaper unload all
    hyprctl hyprpaper preload $random_background
    hyprctl hyprpaper wallpaper "$monitor, $random_background"
    wal -i $random_background

    pkill waybar && hyprctl dispatch exec waybar
    pywalfox update
    python3 ~/.config/hypr/reload_nvim.py
    cp -f ~/.cache/wal/config ~/.config/cava/config
    cp -f ~/.cache/wal/dunstrc ~/.config/dunst/dunstrc && killall dunst && hyprctl dispatch exec dunst
fi

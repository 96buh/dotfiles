# tmux plugins

設定位於 `dotfiles/common/.config/tmux/tmux.conf`；Mac 的 plugin 來源由
`macos/home.nix` 管理，不需要 TPM。

| Plugin | 安裝目錄 | 用途 |
|---|---|---|
| sensible | `~/.config/tmux/plugins/sensible/` | 保留原有預設選項與快捷鍵 |
| resurrect | `~/.config/tmux/plugins/resurrect/` | 手動保存與重建工作區 |
| continuum | `~/.config/tmux/plugins/continuum/` | 每 15 分鐘自動保存；tmux server 啟動時自動還原 |
| yank | `~/.config/tmux/plugins/yank/` | 複製選取文字到系統剪貼簿 |

按 `Ctrl-b` 放開後，再按 `Ctrl-s` 手動保存、`Ctrl-r` 手動還原。
第一次配置好工作區後，建議先手動保存一次，不必等自動保存週期。
自動還原發生在 tmux server 啟動時，不是每次開新視窗都觸發。

保存資料放在 `~/.local/state/tmux/resurrect/`，不加入 dotfiles repository，
也不在 Mac / Linux 之間同步。還原的是 session、視窗、pane、工作目錄與支援程式的啟動，
不會恢復程序的記憶體、運算進度或 SSH 連線。

Mac 的 yank 使用系統剪貼簿工具；Linux Wayland 需要 `wl-clipboard`，
X11 需要對應的 `xclip` 或 `xsel`。Linux 尚未自動部署，需將各 plugin
安裝在表格路徑，入口檔分別是 `sensible.tmux`、`resurrect.tmux`、
`continuum.tmux`、`yank.tmux`。

載入順序：sensible → 使用者設定 → resurrect → yank → continuum。
continuum 透過 status-right 執行自動保存，不要在載入 continuum 後再覆寫它。

本機已直接安裝並載入上述 plugin 連結，沒有執行全系統 switch；
舊 tmux 設定連結備份位於 `~/.local/state/dotfiles/tmux/backups/`，
plugin 的 Nix GC roots 位於同層 `gcroots/`。之後正常套用 Home Manager
仍會管理同一組目標路徑。

官方文件：[resurrect](https://github.com/tmux-plugins/tmux-resurrect)、
[continuum](https://github.com/tmux-plugins/tmux-continuum)、
[yank](https://github.com/tmux-plugins/tmux-yank)。

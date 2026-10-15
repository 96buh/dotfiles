# Linux 設定與部署

在 repository 根目錄操作：

```sh
./setup check
./setup plan
./setup apply
```

setup 自動辨識 Linux，不執行 Nix。先安裝 Git、zsh、tmux 與 GNU Stow；
其他 CLI、字型與桌面軟體依這台機器的需要安裝。套件清單仍待實機整理，
入口不會自動更新系統，也不會改 kernel、驅動、服務或 login shell。

`plan` 用 Stow 模擬連結，`apply` 先做同一個衝突檢查再建立連結。
已有的檔案或其他來源的連結發生衝突時停止，不覆蓋、不自動吸收；
請先把原設定備份到 repository 外再重試。再次執行 apply 可保持既有正確連結。

| 位置 | 內容 |
|---|---|
| `dotfiles/common/` | 共用原生設定，目錄結構對應 `$HOME` |
| `dotfiles/linux/.config/<app>/` | Linux 專用設定，依桌面環境加入 |
| `dotfiles/linux/.local/bin/` | Linux 專用可執行腳本 |
| `packages/cachyos/` | 待整理的 pacman / AUR 清單 |

目前使用標準 `~/.config`，不支援自訂 XDG_CONFIG_HOME。不要讓 common 與 linux
提供同一個目標檔案；要加平台差異時用可載入的獨立設定。Ghostty 目前仍放 macos，
Linux 桌面與 Ghostty 設定等待新機確認後再加入。

共用 zsh 已對缺少的 oh-my-posh、fzf、zoxide、Go 加保護；Mac TeX 路徑只在 Mac
使用，Linux 保留系統 locale 並沿用登入環境提供的 SSH agent。它不在 Linux
自動啟動 agent；需要 SSH key 自動載入時，先設定好桌面／user session 的 agent。
新機的 zinit 與 zsh plugins 仍於首次互動啟動時下載，需網路；setup 本身不啟動 zsh。

兩支共用工具已具執行權限。Git、tmux 直接使用 common 的原生設定；
Mac 的 Nix 專用部署在 macos/home.nix，Linux 不載入它。
Linux 的 sensible、resurrect、continuum、yank 另依 [tmux 說明](tmux.md) 安裝；
不存在的 plugin 會略過載入。Linux 剪貼簿工具也需另行安裝。

`.gitkeep` 僅保留空目錄，Linux 的 `.stow-local-ignore` 會排除它。
私鑰、tokens、快取、session state 與 resurrect 快照不加入 repository。

目前 Linux 入口的測試是在 Mac 的暫存家目錄中使用真正的 Stow，模擬 Linux 路由；
Linux 桌面、字型與互動 shell 仍需新機實際驗證。

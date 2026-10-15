# 盤點與研究

- 最新結構已收斂：Mac Nix 設定集中在 macos/{default,home,packages,fonts,homebrew}.nix，根目錄 ./setup 提供 check / plan / apply。原 home/、host/、modules/、configuration.nix 已移除；下方提及舊路徑均為歷史紀錄。
- Linux 使用實際 GNU Stow 模擬與部署 common + linux，不執行 Nix；Mac plan 使用 nix build --no-link，apply 使用 sudo darwin-rebuild switch，兩者均以 repo 實際絕對路徑的 path: flake 為入口。
- 以暫存 HOME、含空白的 repository 路徑與真正 Stow 測試：plan 不寫入、apply 正確連結、可重複執行、衝突完整停止、.gitkeep 排除、腳本可執行；Mac 指令路由以替身測試，不實際 switch。
- Mac 原有 packages/fonts/Homebrew 三份模組內容以搬移前雜湊驗證一致；僅移除重複的環境 darwinConfig 路徑，改由 setup 明確提供 flake 位置。

- 已加入 resurrect、continuum、yank 的 Nix 部署與原生載入；continuum 必須在 resurrect 以及 status-right 自訂之後載入。保存目錄為機器本地 ~/.local/state/tmux/resurrect，不納入 repository。
- plugin 套件已透過現有 flake 的 pkgs.tmuxPlugins 成功取得，完整 macOS 求值通過；不修改 flake.lock，也不採用 TPM。

- 最新結構：home/ 只剩 home.nix；Git 與 tmux 設定已抽成 common/.config/git/config、common/.config/tmux/tmux.conf。下列提及 Git/tmux Nix 模組的盤點均為歷史狀態。
- 原 Home Manager 的 tmux 預設包含 pane-base-index、emacs keys、escape-time 等，已明確保留到原生設定；sensible 的載入順序保留在額外自訂樣式之前。
- Mac 的 home.nix 繼續提供 git / tmux / zsh 與 sensible plugin 的依賴，沒有引入 TPM 或自動下載行為。

- 最新決定：Linux 桌機與 server 均不使用 Nix，已移除 NixOS 設定。下方 NixOS 相關項目僅是過去盤點紀錄，不是待辦；flake 的 NixOS/nixpkgs GitHub 來源仍為 macOS 提供套件，必須保留。

- 文件放置慣例：根目錄只留 README.md；其他說明及 agent 工作紀錄統一放 docs/。規劃檢查需指定 docs/task_plan.md。

## 2026-10-15 整理後現況

- 已搬移到 dotfiles/common 與 dotfiles/macos；下列 2026-10-08 盤點中的 home/.config、home/.zshrc、home/scripts 為原路徑。
- dotfiles/linux/.config 與 .local/bin 以 .gitkeep 預留；.stow-local-ignore 排除這些標記。
- home/home.nix 九個有效 source 均已更新；Git/tmux Nix 模組與其他既有使用者變更不動。
- 11 個搬移檔案 SHA-256 與搬移前一致；包含已有未提交修改的 AeroSpace 設定。
- zsh / Bash 語法、source 路徑檢查、此次編輯檔案的 git diff --check 均通過。
- macOS system.build.toplevel.drvPath 完整求值成功；沒有 build 或 switch。
- 使用 path: flake 驗證，避免漏掉未加入 Git 的新檔；README 已說明暫時用法。未改動 Git index。

## 2026-10-08 原始盤點

- 現有 repository 使用 flake.nix，包含 Darwin、Home Manager 與 NixOS 路徑。
- 原生設定主要位於 home/.config，另有 home/.zshrc 與 home/scripts。
- git status 顯示多筆既有 staged / unstaged 變更，本次不修改這些檔案。
- home/home.nix 已讓 Nix 引用原生設定檔，適合延伸成共用原生設定 + 各平台部署方式。
- Git 與 tmux 仍由 Home Manager 生成；tmux 的 shell/default-command 含 Nix store 路徑，不能直接搬到 Arch。
- zsh 的 Homebrew 初始化已有路徑判斷，但 TeX 路徑、SSH agent 邏輯、工具無條件初始化需拆分或改善。
- Ghostty 同一檔案含 macos-* 選項、super+p；需評估 Linux 快捷鍵衝突。
- pdf-opener 已依 uname 選擇 open / xdg-open；Linux 需 xdg-utils 與預設 PDF handler。
- 當時 flake 仍含 NixOS output，modules/nixos/default.nix 已 staged 刪除；這些設定與 README 說明已於 2026-10-15 清理完成。
- 兩個 home/scripts 在 Git 中均為 100644；Home Manager 用 executable = true 補執行權限，Stow 不會代為補上，迁移時需明確設定。
- GNU Stow 官方文件確認可預覽、按套件部署與處理衝突；建議 Linux 使用 Stow，macOS 繼續 Home Manager，兩者引用同一份原生設定。
- Ghostty 官方文件確認 config-file 支援相對路徑與可選檔案，include 在當前檔案末尾處理；入口設計需考慮覆蓋順序。
- ArchWiki 搜尋摘要支持避免 partial upgrade；套件清單只記錄安裝意圖，無法提供 flake.lock 同級的版本重現。

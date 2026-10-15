# 進度

- 新增根目錄可執行 ./setup check / plan / apply，自動辨識平台；Mac 走 Nix，Linux 走 Stow，套件安裝與設定部署分離。
- Mac 專用 Nix 檔集中至 macos/，合併 configuration.nix 與原 host/darwin/default.nix，更新 flake 與 source 路徑。原套件／字型／Homebrew 內容與 staged index 保留。
- 共用腳本已補執行權限；zsh 工具初始化加依賴判斷，Mac TeX 路徑限定平台，Linux 保留系統 locale 與 session SSH agent。
- 驗證：./setup check 通過；真實 Stow 的 Linux 路由／預覽／重複套用／衝突／含空白路徑測試通過，Mac 指令派送測試通過；未執行 setup apply 到目前 Mac，未全系統 switch。
- 最終 Mac system.build.toplevel.drvPath 求值成功；新入口與編輯過的 Mac 模組空白檢查通過。原有 packages.nix 的尾端空白依內容保留，重整的 default.nix 繼承空白已整理。

- 已完成 resurrect、continuum、yank 安裝；保留既有 sensible。Mac 使用 flake 固定版本的 pkgs.tmuxPlugins，無 TPM、無 flake.lock 變更。
- 共用設定啟用每 15 分鐘保存、server 啟動自動還原，state 留在 ~/.local/state/tmux/resurrect；continuum 最後載入，避免 status-right 覆寫排程。
- 獨立 tmux 測試通過：resurrect 實際保存／還原兩個視窗三個 panes、yank 的 pbcopy bindings、continuum 選項。測試 server 與暫存 state 均清理。
- 已針對本機安裝 tmux config 與四個 plugin 連結，建立 GC roots，舊設定 link 備份於 ~/.local/state/dotfiles/tmux/backups/20261015-155006。已 reload 現有 tmux、驗證自動保存 hook 並建立首份工作區快照；沒有執行全系統 switch。

- Git 與 tmux 原生設定已建立於 dotfiles/common/.config，移除 home/git.nix、home/tmux.nix；home/ 僅保留 home.nix，負責連結、執行權限與 Mac 依賴。
- 保留原先 tmux 選項、狀態列、快捷鍵與 sensible plugin；zsh 從 PATH 解析，plugin 由 Mac Nix 連結到固定使用者路徑，Linux 未安裝 plugin 時略過。
- 驗證通過：Git 原生設定解析、Mac 完整 Nix 求值、獨立 tmux server 有／無 sensible 的載入、shell、選項與快捷鍵。測試 server 均已關閉，未操作既有 sessions 或套用系統設定。

- 2026-10-15：依使用者確認，Linux 桌機與 server 均不使用 Nix；移除 NixOS 主機設定、flake output、Home Manager 的 Linux home 分支與 README 指令，保留 macOS Nix 設定及原有 lock file。
- 驗證通過：macOS 完整求值成功，system.build.toplevel.drvPath 與移除前相同；此次編輯檔案的 whitespace 檢查通過。有效設定中只剩 macOS 需要的 NixOS/nixpkgs 上游來源，沒有 NixOS output 或主機引用。未套用系統設定。

- 2026-10-15：依使用者要求集中 Markdown。task_plan.md、findings.md、progress.md 搬到 docs/；packages/cachyos/README.md 搬到 docs/cachyos-packages.md，套件目錄改用 .gitkeep 保留。README 已更新文件位置；未修改設定或 Git index。

- 2026-10-15：使用者授權實際整理目錄並預留 Linux 位置。重新盤點後確認既有未提交變更仍在；本次僅搬移設定、更新引用與文件，不實作 Linux 部署。
- 完成 common / macos 原生設定搬移、Linux 空目錄與 CachyOS 套件清單位置預留；更新九個 Home Manager source。
- 新增 docs/linux.md 與 packages/cachyos/README.md，README 記錄實際結構與未追蹤檔案期間的 path: flake 用法。
- 驗證：11 檔內容雜湊相同、shell 語法通過、九個 source 均存在、此次編輯檔案 whitespace 檢查通過；macOS derivation 完整求值成功。
- 未執行 build / switch、安裝套件或變更 Git index。整理工作完成。

- 2026-10-08：讀取 planning-with-files 技能，檢查 session recovery、檔案列表與 git status；開始唯讀盤點。
- 完成 Nix / 原生設定與平台相依性盤點，查證 Stow、Ghostty config-file、Arch 更新流程。
- 建立 docs/cachyos-integration-plan.md：目錄架構、各檔案遷移方式、Linux 套件策略、分階段部署與驗證／還原方式。
- 本次僅新增規劃文件，沒有套用設定、安裝套件或修改既有使用者變更。
- 完成檢查原先因 checkbox 格式誤判 0/0；讀取檢查腳本後改用 Phase / Status 格式，三個規劃階段皆已完成。

# macOS / CachyOS dotfiles 整合規劃

## 目標
保留 Mac 現有功能，集中平台設定並提供根目錄的跨平台部署入口；Linux 不用 Nix，系統套件安裝與設定部署分開。

## 階段
### Phase 1: 盤點 repository 與平台相依性
**Status:** complete

### Phase 2: 查證部署工具與 Arch 套件管理相關文件
**Status:** complete

### Phase 3: 完成架構、遷移步驟與驗證清單
**Status:** complete

### Phase 4: 整理共用與平台設定目錄並更新 Nix 引用
**Status:** complete

### Phase 5: 更新現況文件並驗證引用與 Mac 設定
**Status:** complete

### Phase 6: 集中 Markdown 文件
**Status:** complete

- 依使用者偏好，agent 規劃、發現與進度檔移到 docs/。
- 套件清單說明同樣移到 docs/cachyos-packages.md；根目錄只保留 README.md。
- 後續工作直接更新 docs/ 中的紀錄，不在根目錄建立重複的規劃檔。

### Phase 7: 移除 NixOS 設定並驗證 macOS
**Status:** complete

- 移除主機檔案、flake output 與 Linux Nix 分支，保留 Mac 的 Nix 依賴。
- 更新文件中的舊待辦並驗證 macOS 完整求值。

### Phase 8: 抽出 Git 與 tmux 原生設定
**Status:** complete

- home/ 僅保留 home.nix 作為 Mac 部署介面；設定內容移至 common。
- 保留 tmux shell、快捷鍵與 sensible plugin 行為，驗證獨立設定與 Mac 求值。

### Phase 9: 安裝工作區保存與剪貼簿 plugins
**Status:** complete

- 加入 resurrect、continuum、yank 的 Nix 依賴與跨平台載入。
- 先驗證獨立 tmux，再僅安裝這些設定與 plugins，避免整台 Mac switch 帶入其他尚未提交的設定。

### Phase 10: 收斂 Mac 模組並提供跨平台根目錄入口
**Status:** complete

- Mac Nix 設定集中到 macos/，保留 root flake 入口。
- 新增 ./setup check / plan / apply，自動辨識 macOS 與 Linux。
- Linux 使用 Stow 部署原生設定，不使用 Nix，不自動安裝系統套件。
- 檢查 shell 可攜性、Mac 求值與命令路由／衝突預覽。

## 約束
- 現有工作目錄有 staged / unstaged 變更，保留內容與 Git index；有修改的檔案搬移時保留其目前內容。
- Linux 不使用 Nix。
- Linux 桌面環境與硬體尚未指定，不預設視窗管理器。

## 錯誤
- Stow 子頁抓取 timeout，改讀完整官方手冊。
- ArchWiki 直接開啟遭 Anubis 擋下，使用官方搜尋摘要與 pacman man page 查證。
- 檔案搜尋末段沒有 AGENTS.md，rg 回傳 1，代表無符合項目。
- Stop hook 不辨識 checkbox 階段格式，改用其支援的 Phase 標題與 Status 欄位。
- 2026-10-15：全 repo git diff --check 發現既有 packages.nix 尾端空白；不修改使用者原變更，改對此次編輯檔案檢查並通過。
- 2026-10-15：sandbox 無法連接 Nix daemon；取得工具升權後同一個 offline eval 成功。
- tmux 暫存 socket 被 sandbox 阻擋，升權後用獨立 socket 驗證；第一次檢查指定單鍵的 list-keys 未取得 stdout，改讀整個 prefix key table 後通過。
- 收斂目錄時的空白檢查發現 default.nix 繼承原檔尾端空白，已整理；未改變原有 packages/fonts/Homebrew 檔案內容。

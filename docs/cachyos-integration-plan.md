# macOS 與 CachyOS dotfiles 整合規劃

建議：一個 repository、共用原生設定檔、兩套平台安裝流程。macOS 保留 nix-darwin / Home Manager / Homebrew；CachyOS 使用 pacman、必要時 AUR，以及 GNU Stow 部署設定，不執行任何 Nix 指令。

2026-10-15 現況：已建立 dotfiles/common、dotfiles/macos、dotfiles/linux，
搬移原生設定並更新 Home Manager 引用，預留 packages/cachyos。
目前 Mac 的 Nix 設定已集中到 macos/，原 home/、host/、modules/ 與 configuration.nix 已收斂。Git/tmux 原生設定在 common。根目錄 ./setup 提供 check、plan、apply，Linux 使用 Stow；系統套件仍獨立安裝。
tmux-sensible 在 Mac 由 Nix 安裝後連結，Linux 可安裝到相同 plugin 路徑。
zsh 尚未拆分平台邏輯，Ghostty 暫放 macos。
實際放置方式見 [Linux 目錄說明](linux.md)。
下方為初始整合藍圖，未全部實作；最新操作與實際目錄以根目錄 README、docs/linux.md 為準。Linux 已可部署設定連結，套件與桌面環境的初始安裝仍待實機確認。

## 1. 架構

設定內容與套件安裝分離。共用 zsh、Git、tmux、Yazi、prompt 與腳本；平台差異放進各平台的設定；顯示器、桌面快捷鍵與搜尋目錄等放進主機設定。

```text
.dotfiles/
├── flake.nix / flake.lock       # 保留 macOS Nix 入口
├── setup                       # 跨平台 check / plan / apply
├── macos/                      # Mac 系統設定、Home Manager 與套件
├── dotfiles/                   # GNU Stow package root
│   ├── common/
│   │   ├── .zshrc
│   │   ├── .config/zsh/common.zsh
│   │   ├── .config/git/config
│   │   ├── .config/tmux/tmux.conf
│   │   ├── .config/ghostty/common.conf
│   │   ├── .config/yazi/yazi.toml
│   │   ├── .config/ohmyposh/zen.toml
│   │   └── .local/bin/{pdf-opener,tmux-sessionizer}
│   ├── macos/
│   │   ├── .config/zsh/platform.zsh
│   │   ├── .config/ghostty/config.ghostty
│   │   └── .config/{aerospace,karabiner}/...
│   └── linux/
│       ├── .config/zsh/platform.zsh
│       └── .config/ghostty/config.ghostty
├── profiles/cachyos-desktop/    # 之後確認桌面環境再建立
│   ├── home/                   # 主機專屬 Stow package
│   └── README.md               # 系統層操作紀錄
├── packages/cachyos/
│   ├── cli.txt                # pacman CLI 套件
│   ├── dev.txt                # 選用開發工具
│   ├── desktop.txt            # 選用 GUI 套件
│   ├── fonts.txt              # 字型
│   └── aur.txt                # 另外處理的 AUR 套件
├── scripts/linux/
│   ├── install-packages       # 明確執行才安裝套件
│   ├── link                   # 預覽／部署／解除連結
│   └── doctor                 # 依賴、連結與平台相依性檢查
└── docs/
```

同一個目標檔案只交給一個來源：common 不放平台入口；macos、linux 只選一個。主機層新增 host.zsh / host.conf，不再提供第二份 .zshrc 或 Ghostty 入口覆蓋前面套件。

Mac 由 Home Manager 引用 common + macos；Linux 由 Stow 引用 common + linux + 選定主機。Mac 不再對這些路徑執行 Stow。

## 2. 設定怎麼拆（左欄為整理前路徑）

| 現有檔案 | 規劃 |
|---|---|
| home/.zshrc | 保留共用 aliases、history、completion、widgets；Homebrew / LLVM / macOS TeX PATH 移入 macos；各工具初始化加 command -v 檢查 |
| home/git.nix | 已改為 common/.config/git/config；原模組已移除 |
| home/tmux.nix | 已改為 common/.config/tmux/tmux.conf；從 PATH 解析 zsh，原模組已移除 |
| home/.config/ghostty/config.ghostty | 字型、主題、padding 放 common.conf；各平台入口引用它，再引用平台／主機設定 |
| home/.config/{yazi,ohmyposh} | 先共用，確認 Linux 實際安裝版本讀取正常 |
| home/.config/{aerospace,karabiner} | 僅 macOS 部署 |
| home/scripts/pdf-opener | 共用；已有 open / xdg-open 分支，Linux 補 xdg-utils 與預設 PDF 應用 |
| home/scripts/tmux-sessionizer | 共用；搜尋路徑移到主機層，檢查實際目錄與 shell 相容性 |
| macos/packages.nix | Mac 套件；Linux 另維護真正的 pacman/AUR 名稱，不把 Nix 名稱機械轉換 |

重要細節：

- 兩支腳本目前在 Git 是 100644；Home Manager 設 executable = true。遷移時要把共用腳本記錄成可執行檔，Stow 只建立連結。
- tmux 的 sensible、resurrect、continuum、yank 在 Mac 由 Nix 提供，連結到 ~/.config/tmux/plugins/ 下各自的目錄。Linux 要明確選擇固定版本的 plugin 安裝方式，放到相同路徑；共用設定不含 Nix store 路徑。操作與依賴見 [tmux 說明](tmux.md)。
- .zshrc 現在每個 shell 都嘗試啟動／載入 SSH key；改為配合 Linux 桌面或 user session 的 agent，shell 使用有效的 SSH_AUTH_SOCK。私鑰與 credentials 留在各台機器。
- zinit 目前首次開 shell 會 git clone；新機流程先準備 plugin manager 與必要 plugins，避免把完整初始安裝依賴藏在 shell 啟動中。
- 確認 Linux 已啟用 en_US.UTF-8，再設定 LANG；不要只複製 export。
- Ghostty 的 super+p 在 Linux 可能碰到桌面快捷鍵；Linux 可另選 Ctrl+Shift+P，傳送相同 escape sequence，需實機驗證。
- Ghostty 的 config-file 在當前檔案末尾處理：入口可依序載入 common、platform、host、local，避免假設入口中後寫的選項能覆蓋 include。[官方說明](https://ghostty.org/docs/config#splitting-into-multiple-files)
- 個人 override 用各應用的 local include，例如 ~/.config/zsh/local.zsh；安裝器不建立或管理此檔。PDF 搜尋設定同樣可以留在機器本地。

## 3. Linux 套件策略

以現有使用需求列清單，而非要求兩邊所有套件完全一致：

- CLI 第一批：Git、zsh、tmux、fzf、fd、ripgrep、eza、bat、zoxide、oh-my-posh、Yazi、Neovim，加上腳本需要的依賴。
- 開發工具第二批：uv、Node.js / pnpm、Go、Rust、Java 等，只裝這台機器確實需要的環境。
- 文件工具：依需求補 TeX Live、Typst、Pandoc、Poppler、ImageMagick、FFmpeg 等；macOS 的 MacTeX 路徑不帶過去。
- 桌面軟體與字型：依 Linux 實際可用來源選擇。Raycast、AeroSpace、Karabiner 等 macOS 工具另外決定 Linux 工作流程。

優先使用這台 CachyOS 已啟用的套件庫，缺少才列 AUR；不預設新機已裝哪一個 AUR helper。落地時在新機核對套件名稱與來源，避免同一軟體同時裝 repository、AUR 與其他來源版本。

安裝腳本規格：

1. 檢查 /etc/os-release，確認目標平台與選定 profile。
2. 解析套件清單時忽略註解、空行，使用陣列傳遞；列出預計安裝項目。
3. repository 套件使用包含完整更新的 pacman 流程，例如 pacman -Syu --needed；AUR 分開安裝並檢閱 build files。
4. 套件安裝與設定連結是獨立指令；日常 link 不會順便更新整個系統。
5. 不因清單少了一個套件就自動移除它，也不自動修改 kernel、bootloader、驅動或 pacman.conf。

Arch 應避免 partial upgrade。[Arch 系統維護文件](https://wiki.archlinux.org/title/System_maintenance#Partial_upgrades_are_unsupported)、[pacman 選項](https://man.archlinux.org/man/pacman.8.en)

套件清單記錄「要安裝什麼」，不鎖定所有版本；Git 可回復設定內容，但不能提供 Mac 的 flake.lock 那種整套環境重現。記錄成功部署時的套件版本可協助排查，不能當成完整回復機制。

## 4. 分階段遷移

### 第一階段：保留現況，建立共用來源

先整理或保存目前尚未提交的變更。不要把既有工作與跨平台重構混成同一個 commit。

一次遷移一個工具：先 scripts、prompt、Yazi，再 zsh、Ghostty，最後 Git 與 tmux。每搬一個就更新 macos/home.nix 的引用並驗證 Mac。Home Manager 的 Git/tmux 生成功能與新檔案部署要在同一個變更中交接，避免競爭管理目標檔案。

Mac 驗證：darwin-rebuild build --flake ~/.dotfiles#macbookpro 成功，檢查 Git 身分、tmux shell/plugin、Ghostty 與 shell 功能，再按既有流程套用。

### 第二階段：Linux 基礎環境

在新機確認使用者、桌面環境、Wayland/X11、已有套件來源、字型与 locale。先安裝核心 CLI 與 Stow，再部署 common + linux。

未來目錄建立後，Linux 的預覽指令示意：

```sh
stow --dir="$HOME/.dotfiles/dotfiles" --target="$HOME" \
  --no-folding --simulate --verbose common linux
```

確認衝突後，將 --simulate 移除才部署。--no-folding 可讓一般設定目錄保持實體目錄，內部設定以連結管理。Stow 可模擬操作且會偵測目標衝突。[GNU Stow 手冊](https://www.gnu.org/software/stow/manual/stow.html)

link wrapper 的預設行為應是預覽；既有非本 repository 管理的檔案發生衝突就停止，列出路徑。第一次部署先把原設定备份到 repository 之外，不用強制覆蓋或 --adopt 自動吸收它們。

先檢查 zsh 語法與非互動 smoke check，再實際開新 shell；測 aliases、prompt、fzf、Yazi cwd、tmux-sessionizer 和 PDF picker。確認 tmux 的 shell 路徑有效且沒有 /nix/store。

### 第三階段：桌面與主機差異

等 KDE、GNOME 或其他桌面選擇確定後，才加入桌面快捷鍵、鍵盤映射、顯示器、縮放、輸入法等設定。不先假定以 Hyprland / i3 取代 AeroSpace。

桌面設定只挑需要維護的檔案；不要整包同步 ~/.config，以免帶入 session state、快取、機器識別與不相關設定。系統服務變更寫明操作方式，必要時用獨立腳本，不塞進 shell 啟動。

### 第四階段：文件與日常維護

README 分出 macOS 與 CachyOS 的初始安裝、套用、驗證與還原步驟。

兩台機器對同一分支提交共用設定；平台特例仍放相應目录，不建立長期分岔的 Mac / Linux branches。Linux 套用前先 git pull、預覽連結、檢查應用版本，再 reload；Mac 依 Nix build / switch 流程。

## 5. 完成條件與還原

- Mac 的 build 與日常 shell / Git / tmux / Ghostty 功能正常。
- Linux 不安裝 Nix，部署不需要 Nix 或 Home Manager。
- 共用設定只有一份；沒有同平台雙重管理的目標檔案。
- 再次 link 不覆蓋 local override 或使用者其他設定。
- doctor 能指出缺少依賴、失效連結、腳本不可執行及平台路徑問題。
- Linux 實際測試 PDF 開啟、中文字型、Git、shell widgets 與 tmux plugin。
- Stow 解除連結後可以還原原本備份；設定 Git commit 可回退。套件或系統回復需另外規劃，不混同設定回退。

目前仍待確認：新機桌面環境、hostname / 使用者、GPU / 顯示器需求、哪些 GUI 與研究工具確實需要同步。這些不阻擋共用 CLI 設定先行整理。

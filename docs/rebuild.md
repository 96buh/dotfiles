# 重建、遷移與驗證

本頁集中維護 Linux／Mac 重建方式和此次檢查結果。Neovim 保留為獨立 Git repo；dotfiles 管理共用工具、runtime 整合、shell 和系統套件清單。不要把整份 Neovim 目錄搬進本 repo。

## 這次修正的問題

- 預覽工具複本補上 SSH／本機判斷，避免 Linux 本機使用時也被導向 Mac。
- 遠端工具統一部署到 `~/tools/remote-tex-preview/`；不再依賴 ADL 作業路徑。
- Neovim 從 `~/.local/share/nvim/site/plugin/remote-tex-preview.lua` 自動載入整合，原本的獨立 repo 不需加入專案路徑。
- `remote-tex-preview` 無參數即可監看，`texwatch` 為受管理 zsh 的同義 alias。`--once` 檢查單次同步。
- Linux 套件清單補上 GNU Stow、Python、Neovim、TeX Live、Biber、minted 所需套件、Zathura 與字體。
- `setup check` 檢查 Python、LaTeX、Biber、minted、預覽設定與 launcher，並提醒 Neovim 的本機未提交修改。
- Mac 的共用 launcher 與 Linux 使用相同實作；Python 也納入 Mac 的 Home Manager 套件。
- Mac Home Manager 不再對受管理檔案使用 `force=true`，衝突檔改以 `.before-dotfiles` 備份；已存在同名備份時會停止，不覆蓋備份。
- `config.local.json` 可覆蓋機器特定設定，不由 Stow／Home Manager 管理、不加入 Git。
- `docs/` 不再被整個忽略；README 改為連到本頁，移除不存在的文件連結。

## Linux：新機重建

以下針對 Arch／CachyOS。先有 Git、可連線的套件 mirror，以及一般使用者的 sudo 權限。若尚未安裝 Git，先執行 `sudo pacman -Syu --needed git`。

```sh
# 先把你的 dotfiles repo clone 到 ~/.dotfiles
cd ~/.dotfiles
./setup packages
./setup preview
./setup check
./setup plan
./setup apply
```

`packages` 會執行 `sudo pacman -Syu --needed ...`，包含完整系統升級及 `texlive-meta` 的完整 TeX Live，可能有較大的下載量。安裝前 pacman 仍會讓你確認。它不會啟動 AUR helper。可選 prompt 套件記錄於 `packages/cachyos/aur.txt`；缺少 oh-my-posh 不阻止其他設定使用。

Neovim 設定由你自行 git clone 到 `~/.config/nvim`，自行更新、commit 與 push；dotfiles 不再提供 clone 功能，也不檢查或修改這個 repo。

`preview` 只安裝預覽所需的五個連結，不改你的 shell、桌面或其他 app。所有衝突先檢查，發現不屬於本 repo 的同名檔案就停止。預覽整合只部署到使用者 runtime，不讀寫 `~/.config/nvim`。

`plan` 使用 Stow 模擬，`apply` 也先檢查全部衝突，才建立連結；不採用 `--adopt` 或覆寫現有檔案。兩者均略過 `.gitkeep`。如果你只要 LaTeX 預覽，執行到 `preview` 即可，不必套用整份 shell 設定。

## Linux：目前這台已有設定時

預覽部分可單獨套用：

```sh
cd ~/.dotfiles
./setup preview
```

完整 Stow 部署若因 `.zshrc`、Git 設定等現有檔案衝突而停止，先比較差異，再把衝突檔移到 repo 外的備份位置。不要刪除原檔，也不要使用 `--adopt` 覆蓋 repo。舉例：

```sh
backup="$HOME/.local/state/dotfiles/manual-backup-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$backup"
# 只有確定要改用受管理 shell 時才執行下面這一行：
mv ~/.zshrc "$backup/zshrc"
./setup plan
./setup apply
```

其他衝突依 Stow 的實際訊息逐一處理，不要整個搬走 `~/.config`；Neovim 獨立 repo 不屬於要搬走的內容。

目前這台 Linux 的真實 Stow 預檢遇到以下五個既有檔案，尚未覆寫，也未執行整份 apply：

- `.zshrc`
- `.config/ohmyposh/zen.toml`
- `.config/tmux-sessionizer/tmux-sessionizer.conf`
- `.config/yazi/yazi.toml`
- `.local/bin/tmux-sessionizer`

若確認要改用 repo 的版本，可以先完整保留這五份原檔，再部署：

```sh
backup="$HOME/.local/state/dotfiles/manual-backup-$(date +%Y%m%d-%H%M%S)"
for rel in .zshrc .config/ohmyposh/zen.toml .config/tmux-sessionizer/tmux-sessionizer.conf .config/yazi/yazi.toml .local/bin/tmux-sessionizer; do
  mkdir -p "$backup/$(dirname "$rel")"
  mv "$HOME/$rel" "$backup/$rel"
done
cd ~/.dotfiles
./setup plan
./setup apply
```

先前整理已在 Linux 建立標準工具與 runtime 連結，並備份移除早期的舊 init hook；新版本 preview 不再包含任何 init.lua 遷移或編輯行為。實際 Neovim 設定在本機／SSH 兩種模式皆驗證通過。系統套件尚未變動；目前 `setup check` 的必要工具僅缺 GNU Stow，可先執行 `sudo pacman -Syu --needed stow`。預覽部分不依賴 Stow，已可直接使用。

重開 Neovim 後生效。套用完整 shell 後重開 terminal，或 `source ~/.zshrc`。不會自動改 login shell、重載 tmux、下載 Neovim 插件或重設桌面；zinit 與 Neovim 插件仍由其各自啟動流程安裝。Linux Hyprland／Noctalia 等桌面設定目前不在此 repo 的管理範圍內。

## Mac：重建

目前 flake 針對 Apple Silicon、使用者 `homer`、profile `macbookpro`；換使用者或 Intel Mac 需先調整 flake 與 Home Manager 路徑。需要已可用的 Nix／nix-darwin，setup 不負責初次安裝 Nix。

```sh
cd ~/.dotfiles
./setup plan
./setup apply
./setup check
```

`apply` 透過 nix-darwin／Home Manager 安裝程式與設定，也管理 Homebrew apps（含 Skim、MacTeX）；Homebrew 現有設定使用 cleanup=zap，套用前請查看 build 與 Homebrew 的變更清單。Neovim 設定仍由你自行 clone／更新。

如果仍保留先前加在 `.zshrc` 的 `texwatch` alias，它不需要再存在；套用受管理 zsh 後會使用同名 alias 指向新的 `remote-tex-preview`。舊的 `~/Tools/remote_tex_preview/` 可在確認新版本正常後自行封存，不要讓 Skim 命令繼續指向它。

工具、命令和設定的 Home Manager 宣告集中在 `macos/home.nix`，不再使用獨立的 remote-tex-preview.nix。測試放在 repo 根目錄 `tests/`，不會部署到 `~/tools`。

`./setup plan`／`nix build` 只建立 Nix store 內的結果，不會修改家目錄。必須成功執行 `./setup apply` 或 `sudo darwin-rebuild switch --flake "$HOME/.dotfiles#macbookpro"`，Home Manager 才會建立 `~/tools/remote-tex-preview/` 並把 rtp.py、preview.lua 連結到 Nix store 中的版本。Mac 不會直接執行 dotfiles 工作目錄裡的 Python；修改 dotfiles 後須再次 switch 才會套用。

Linux 的 `./setup preview`／Stow 則建立指向 dotfiles 來源的連結，所以 Linux 修改 repo 中的工具會直接反映在部署位置。

Mac 的 Home Manager 來源透過 Nix store 部署，不要直接編輯受管理 symlink 指向的檔案。機器設定放在下面的 local override。

## SSH 與主機設定

Mac 需要自己的 SSH 金鑰與 `~/.ssh/config`，這些憑證不在 dotfiles 中。預設使用 alias `linux`；請先確認：

```sh
ssh linux true
```

SSH alias 應能非互動登入；加密金鑰可先加入 agent。工具全部從 Mac 連到 Linux，不需要 Linux 連回 Mac，也不用開放 Neovim TCP 埠。

若主機名稱、遠端帳號或 Neovim 路徑不同，建立 `~/.config/remote-tex-preview/config.local.json`，只填需要覆蓋的欄位：

```json
{
  "host": "your-linux-alias",
  "remote_tool": "/home/your-user/tools/remote-tex-preview/rtp.py",
  "local_nvim": "/absolute/path/from/command-v-nvim"
}
```

預設 remote_tool 為 `/home/homer/tools/remote-tex-preview/rtp.py`，不需填 report 根目錄。`local_nvim` 預設為 `nvim`，Mac 的 Nix launcher 已提供其 PATH，一般不必改。Python 為 3.10+。可用 `RTP_CONFIG` 指定其他設定檔、`RTP_PYTHON` 指定本機 Python、`RTP_TOOL` 指定工具檔路徑；一般不需要設定環境變數。

## Skim：一次性設定

Mac 套用完成後，查詢絕對命令路徑：

```sh
command -v remote-tex-preview
```

Skim → Settings／Preferences → Sync：

- 關閉自動檢查／重載檔案變更，讓工具明確執行 revert。
- PDF-TeX Sync 選 Custom。
- Command：填上面查到的絕對路徑，例如 `/Users/homer/.nix-profile/bin/remote-tex-preview`；GUI 不能填 `~`。
- Arguments：

```text
inverse /Users/homer/.config/remote-tex-preview/config.json "%file" %line
```

macOS 若要求 Terminal／Python 控制 Skim 的 Automation 權限，需要允許。此設定目前不由 Nix 自動寫入 Skim preferences，需手動做一次。

本機來源檔交給 Mac 原本的 VimTeX 反向跳轉；遠端快取內的來源經 SSH 回 Linux。遠端出錯不會誤轉本機。本機反向跳轉不需啟動同步程序；關閉 Skim 自動重載後，本機 PDF 更新依賴 VimTeX 的 Skim viewer 編譯回呼。

## 日常操作

Mac 啟動並保留一個 terminal：

```sh
remote-tex-preview
# 使用受管理 zsh 時也可以：
texwatch
```

停止按 Ctrl-C。重啟即恢復；`remote-tex-preview --once` 檢查一次連線與同步。其他參數維持原有 CLI：例如 `remote-tex-preview inverse <config> <file> <line>`。

Linux 上每份 report 都先進入 main.tex 所在目錄，再啟動 Neovim：

```sh
cd /path/to/report
nvim main.tex
```

你自己儲存、按原本的單次編譯快捷鍵。編譯成功後同步；儲存不會自動編譯。PDF 與 `.synctex.gz` 須在專案根目錄或其子目錄中，保留 `-synctex=1`。不會同步 minted 的短期 `.minted` 暫存檔；真正原始檔缺失仍會報錯。

- Mac 本機編輯：維持本機 VimTeX＋Skim。
- SSH 到 Linux：啟用遠端發布，`\v` 背景定位 Mac Skim，保留 terminal 焦點。
- Linux 本機：保留原本 Zathura viewer，不啟用遠端發布。

tmux 若保留了不符目前連線的環境，可以明確啟動：

```sh
RTP_REMOTE_PREVIEW=0 nvim main.tex  # Linux 本機
RTP_REMOTE_PREVIEW=1 nvim main.tex  # Linux 遠端預覽
```

## 驗證與限制

測試指令：

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

此次在 Linux 使用真正的 GNU Stow（由官方原始碼在 /tmp 建置，未安裝系統套件）及隔離暫存目錄測試：同一個 tests/ 目錄下共 32 項測試通過（7 項部署、25 項預覽）。包含衝突不覆寫、重複部署、獨立 Neovim 設定原樣保留、真實 Neovim 自動 runtime 載入、SSH／本機分流、同步與反向跳轉。

此機未安裝 Nix，無法在 Linux 完成 Apple Silicon 的 nix-darwin build／switch 或驗證 Skim GUI。Mac 請先跑 `./setup plan`，成功後再 apply，並測試 PDF 更新、背景定位與雙向跳轉。Nix／Homebrew 更新仍受鎖定版本與外部網路影響，不能把 Linux 測試視為 Mac 實機驗證。

Neovim 本機尚未提交的修改與 SSH 憑證不會自動出現在另一台機器。請自行在 Neovim repo commit/push；dotfiles 本次修改也需要自行 commit/push，才能在 Mac pull 或新機 clone 後重建。

參考：[GNU Stow](https://www.gnu.org/software/stow/manual/)、[Home Manager 檔案保護](https://nix-community.github.io/home-manager/usage/dotfiles.html)、[Skim 同步](https://sourceforge.net/p/skim-app/wiki/TeX_and_PDF_Synchronization/)。

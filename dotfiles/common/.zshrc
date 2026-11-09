# Keep inherited paths unique when opening nested shells or tmux panes.
typeset -U path fpath
path=("$HOME/.local/bin" "$HOME/.cargo/bin" $path)

if [[ -x /opt/homebrew/bin/brew ]]; then
  # The login environment normally initializes Homebrew already.
  if [[ -z ${HOMEBREW_PREFIX:-} ]]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
  fi
  # Homebrew LLVM is keg-only, so expose its tools explicitly.
  if [[ -d "$HOMEBREW_PREFIX/opt/llvm@17/bin" ]]; then
    export PATH="$HOMEBREW_PREFIX/opt/llvm@17/bin:$PATH"
  fi
fi

ZINIT_HOME="${XDG_DATA_HOME:-${HOME}/.local/share}/zinit/zinit.git"

if [ ! -d "$ZINIT_HOME" ]; then
   mkdir -p "$(dirname "$ZINIT_HOME")"
   git clone https://github.com/zdharma-continuum/zinit.git "$ZINIT_HOME"
fi

# Source/Load zinit
source "${ZINIT_HOME}/zinit.zsh"

# Add in zsh plugins
zinit light zsh-users/zsh-completions

# Use a separate dump from /etc/zshrc: different fpath values must not keep
# invalidating each other's cache. Keep compinit's normal security checks.
autoload -Uz compinit
compinit -d "${ZDOTDIR:-$HOME}/.zcompdump-dotfiles-$ZSH_VERSION"

zinit cdreplay -q

# oh-my-posh
if [[ "$TERM_PROGRAM" != "Apple_Terminal" ]] && command -v oh-my-posh >/dev/null 2>&1; then
  eval "$(oh-my-posh init zsh --config $HOME/.config/ohmyposh/zen.toml)"
fi

# Keybindings
KEYTIMEOUT=1
bindkey -v
bindkey '^p' history-search-backward
bindkey '^n' history-search-forward
bindkey '^[w' kill-region
bindkey -s ^f "tmux-sessionizer\n"

# History
HISTSIZE=5000
HISTFILE=~/.zsh_history
SAVEHIST=$HISTSIZE
setopt appendhistory
setopt sharehistory
setopt hist_ignore_space
setopt hist_ignore_all_dups
setopt hist_save_no_dups
setopt hist_find_no_dups

# Completion styling
zstyle ':completion:*' matcher-list 'm:{a-z}={A-Za-z}'
zstyle ':completion:*' list-colors "${(s.:.)LS_COLORS}"
zstyle ':completion:*' menu no
zstyle ':fzf-tab:complete:cd:*' fzf-preview 'eza --group-directories-first --icons=always --color=always $realpath'
zstyle ':fzf-tab:complete:__zoxide_z:*' fzf-preview 'eza --group-directories-first --icons=always --color=always $realpath'

export FZF_DEFAULT_COMMAND="fd --hidden --strip-cwd-prefix --exclude .git"
export FZF_CTRL_T_COMMAND="$FZF_DEFAULT_COMMAND"
export FZF_ALT_C_COMMAND="fd --type=d --hidden --strip-cwd-prefix --exclude .git"

export FZF_CTRL_T_OPTS="
  --preview '
    if [ -d {} ]; then
      eza -T --color=always --icons=always {} | head -200
    else
      bat --style=numbers --color=always --line-range :500 {} 2>/dev/null
    fi
  '
"
export FZF_ALT_C_OPTS="--preview 'eza -T --icons=always --color=always {} | head -200'"

# Aliases
alias ls='eza --group-directories-first --icons=always --no-user'
alias lsa='eza --group-directories-first --icons=always -a --long'
alias vim='nvim'
alias vi='nvim'
alias c='clear'
alias texwatch='remote-tex-preview'
alias tree='eza -Ta --git-ignore --group-directories-first --level=3'

# BEL travels through SSH/tmux; Ghostty handles Dock attention on the Mac.
# Send even without remote focus reports; Ghostty suppresses focused attention.
function codex() {
  command codex \
    -c 'tui.notifications=["agent-turn-complete"]' \
    -c 'tui.notification_method="bel"' \
    -c 'tui.notification_condition="always"' \
    "$@"
}

# Shell integrations
command -v fzf >/dev/null 2>&1 && eval "$(fzf --zsh)"
command -v zoxide >/dev/null 2>&1 && eval "$(zoxide init --cmd cd zsh)"

# fzf-tab must follow compinit/fzf; highlighting follows all widget definitions.
zinit light Aloxaf/fzf-tab
zinit light zsh-users/zsh-autosuggestions

# Ghostty's Command-p sequence is normalized by tmux; accept both forms.
function pdf-opener-widget() {
  zle -I
  command pdf-opener
  zle reset-prompt
}
zle -N pdf-opener-widget
bindkey -M viins '^[[34~' pdf-opener-widget
bindkey -M vicmd '^[[34~' pdf-opener-widget
bindkey -M viins '^[[21;2~' pdf-opener-widget
bindkey -M vicmd '^[[21;2~' pdf-opener-widget

function y() {
	local tmp="$(mktemp -t "yazi-cwd.XXXXXX")" cwd
	yazi "$@" --cwd-file="$tmp"
	if cwd="$(command cat -- "$tmp")" && [ -n "$cwd" ] && [ "$cwd" != "$PWD" ]; then
		builtin cd -- "$cwd"
	fi
	rm -f -- "$tmp"
}

if [[ $OSTYPE == darwin* ]]; then
    export LANG=en_US.UTF-8
    path=(/Library/TeX/texbin $path)
fi
# Respect a custom GOPATH; otherwise Go uses ~/go. Avoid spawning go each time.
for go_path in "${(@s/:/)${GOPATH:-$HOME/go}}"; do
  path+=("$go_path/bin")
done
unset go_path
export MANPAGER="less -R --use-color -Dd+r -Du+b"
export MANROFFOPT="-c"

# SSH keys are loaded on demand by ~/.ssh/config (AddKeysToAgent / UseKeychain).

# Keep machine-specific environment settings outside the managed dotfiles.
if [[ -f "$HOME/.config/zsh/local.zsh" ]]; then
  source "$HOME/.config/zsh/local.zsh"
fi

zinit light zsh-users/zsh-syntax-highlighting

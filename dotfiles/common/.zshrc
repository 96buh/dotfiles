export PATH="$HOME/.local/bin:$PATH"

if [[ -f "/opt/homebrew/bin/brew" ]]; then
  # If you're using macOS, you'll want this enabled
  eval "$(/opt/homebrew/bin/brew shellenv)"
  # Homebrew LLVM is keg-only, so expose its tools explicitly.
  if [[ -d "$HOMEBREW_PREFIX/opt/llvm@17/bin" ]]; then
    export PATH="$HOMEBREW_PREFIX/opt/llvm@17/bin:$PATH"
  fi
fi

ZINIT_HOME="${XDG_DATA_HOME:-${HOME}/.local/share}/zinit/zinit.git"

if [ ! -d "$ZINIT_HOME" ]; then
   mkdir -p "$(dirname $ZINIT_HOME)"
   git clone https://github.com/zdharma-continuum/zinit.git "$ZINIT_HOME"
fi

# Source/Load zinit
source "${ZINIT_HOME}/zinit.zsh"

# Add in zsh plugins
zinit light zsh-users/zsh-syntax-highlighting
zinit light zsh-users/zsh-completions
zinit light zsh-users/zsh-autosuggestions
zinit light Aloxaf/fzf-tab

# Load completions
autoload -Uz compinit && compinit

zinit cdreplay -q

# oh-my-posh
if [[ "$TERM_PROGRAM" != "Apple_Terminal" ]] && command -v oh-my-posh >/dev/null 2>&1; then
  eval "$(oh-my-posh init zsh --config $HOME/.config/ohmyposh/zen.toml)"
fi

# Keybindings
export KEYTIMEOUT=1
bindkey -v
bindkey '^p' history-search-backward
bindkey '^n' history-search-forward
bindkey '^[w' kill-region
bindkey -s ^f "tmux-sessionizer\n"

# History
HISTSIZE=5000
HISTFILE=~/.zsh_history
SAVEHIST=$HISTSIZE
HISTDUP=erase
setopt appendhistory
setopt sharehistory
setopt hist_ignore_space
setopt hist_ignore_all_dups
setopt hist_save_no_dups
setopt hist_ignore_dups
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
# options: --no-filesize, --no-time, --no-permissions
alias lsa='eza --group-directories-first --icons=always -a --long'
alias vim='nvim'
alias vi='nvim'
alias c='clear'
alias tree='eza -Ta --git-ignore --group-directories-first --level=3'

# Shell integrations
command -v fzf >/dev/null 2>&1 && eval "$(fzf --zsh)"
command -v zoxide >/dev/null 2>&1 && eval "$(zoxide init --cmd cd zsh)"

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

# Respect the agent supplied by the desktop/login session (including forwarded agents).
SSH_KEY="$HOME/.ssh/id_ed25519"
if [[ -f "$SSH_KEY" ]] && command -v ssh-add >/dev/null 2>&1; then
    if [[ "$(uname -s)" == Darwin && -z "${SSH_AUTH_SOCK:-}" ]]; then
        eval "$(ssh-agent -s)" > /dev/null
    fi
    if [[ -n "${SSH_AUTH_SOCK:-}" ]] && command -v ssh-keygen >/dev/null 2>&1; then
        key_fingerprint="$(ssh-keygen -lf "$SSH_KEY" 2>/dev/null | awk '{print $2}')"
        if [[ -n "$key_fingerprint" ]] && ! ssh-add -l 2>/dev/null | grep -Fq -- "$key_fingerprint"; then
            ssh-add "$SSH_KEY" > /dev/null 2>&1
        fi
    fi
fi

if [[ "$(uname -s)" == Darwin ]]; then
    export LANG=en_US.UTF-8
    export PATH="/Library/TeX/texbin:$PATH"
fi
export PATH="$HOME/.cargo/bin:$PATH"
command -v go >/dev/null 2>&1 && export PATH="$PATH:$(go env GOPATH)/bin"
export MANPAGER="less -R --use-color -Dd+r -Du+b"
export MANROFFOPT="-c"

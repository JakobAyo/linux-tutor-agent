# M0 spike: log each command as one JSON line (ADR 0005), skip secrets (ADR 0006).
# Source at the END of ~/.zshrc:  source /path/to/spike/hook.zsh
# Throwaway code. No subprocesses run per command; only parameter expansion and one append.

zmodload zsh/datetime
autoload -Uz add-zsh-hook

typeset -g _lt_log="${LTUTOR_SPIKE_DIR:-${XDG_DATA_HOME:-$HOME/.local/share}/linux-tutor-spike}/cmds.log"
typeset -g _lt_cmd="" _lt_start=""
[[ -d ${_lt_log:h} ]] || mkdir -p -m 700 ${_lt_log:h}

_lt_preexec() {
  _lt_cmd=$1
  _lt_start=$EPOCHREALTIME
}

# JSON-escape $1 into REPLY.
_lt_json() {
  local s=$1
  s=${s//\\/\\\\}
  s=${s//\"/\\\"}
  s=${s//$'\n'/\\n}
  s=${s//$'\t'/\\t}
  s=${s//$'\r'/\\r}
  s=${s//[[:cntrl:]]/}
  REPLY=$s
}

_lt_precmd() {
  local rc=$?
  [[ -n $_lt_cmd ]] || return 0
  local cmd=$_lt_cmd start=$_lt_start
  _lt_cmd=""
  {
    setopt localoptions extendedglob
    # Leading space = "don't record" (histignorespace convention).
    [[ $cmd == [[:space:]]* ]] && return 0
    [[ $cmd == (#i)*(export|token|password|passwd|secret|authorization|bearer|api_key|apikey|aws_|private_key)* ]] && return 0
    local -F 3 dur
    (( dur = EPOCHREALTIME - start ))
    local jcmd jcwd
    _lt_json "$cmd"; jcmd=$REPLY
    _lt_json "$PWD"; jcwd=$REPLY
    print -r -- "{\"time\":${start%.*},\"cwd\":\"$jcwd\",\"command\":\"$jcmd\",\"exit\":$rc,\"duration\":$dur}" >> $_lt_log
  } 2>/dev/null
  return 0
}

add-zsh-hook preexec _lt_preexec
# Run first among precmd hooks so no theme/plugin hook clobbers $? before we read it.
precmd_functions=(_lt_precmd ${precmd_functions:#_lt_precmd})

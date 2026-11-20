# M0 spike: log each command as one JSON line (ADR 0005), skip secrets (ADR 0006), and start the
# processor in the background at most every 10 minutes per shell (ADR 0011).
# Source at the END of ~/.zshrc:  source /path/to/spike/hook.zsh
# Throwaway code. Per command: parameter expansion, one append, one integer comparison.
# Set LTUTOR_SPIKE_AUTO=0 to only log, without background runs.

zmodload zsh/datetime
autoload -Uz add-zsh-hook

typeset -g _lt_dir="${LTUTOR_SPIKE_DIR:-${XDG_DATA_HOME:-$HOME/.local/share}/linux-tutor-spike}"
typeset -g _lt_log="$_lt_dir/cmds.log" _lt_runlog="$_lt_dir/run.log"
typeset -g _lt_proc="${${(%):-%x}:A:h}/process.py"
typeset -g _lt_cmd="" _lt_start=""
typeset -gi _lt_last_run=0 _lt_interval=${LTUTOR_SPIKE_INTERVAL:-600}
[[ -d $_lt_dir ]] || mkdir -p -m 700 $_lt_dir

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

# Append one line for the command that just finished. $1 is its exit code.
_lt_append() {
  local rc=$1 cmd=$_lt_cmd start=$_lt_start
  _lt_cmd=""
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
}

# Start the processor disowned when this shell hasn't for $_lt_interval seconds. The first prompt
# of a new shell starts it too, which picks up the last lines of a short earlier session.
# The processor takes a lock and exits at once when another run is busy or nothing is due.
_lt_trigger() {
  [[ ${LTUTOR_SPIKE_AUTO:-1} == 1 ]] || return 0
  (( EPOCHSECONDS - _lt_last_run >= _lt_interval )) || return 0
  _lt_last_run=$EPOCHSECONDS
  python3 $_lt_proc run --auto </dev/null >>$_lt_runlog 2>&1 &!
}

_lt_precmd() {
  local rc=$?
  {
    [[ -n $_lt_cmd ]] && _lt_append $rc
    _lt_trigger
  } 2>/dev/null
  return 0
}

add-zsh-hook preexec _lt_preexec
# Run first among precmd hooks so no theme/plugin hook clobbers $? before we read it.
precmd_functions=(_lt_precmd ${precmd_functions:#_lt_precmd})

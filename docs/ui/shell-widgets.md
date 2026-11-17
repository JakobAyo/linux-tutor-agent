# Shell widgets

zle widgets act on the command line I'm editing.

## Explain before running (Alt-e)
Explains the current `$BUFFER` before I press Enter. Useful for commands copied from the Arch Wiki and for catching dangerous ones (`dd`, `rm -rf`). Shows the explanation below the prompt (or in a popup) without changing the buffer.

## Cheat sheet (Ctrl-g)
fzf over the variations I've learned (from my cards); the chosen one is inserted into the prompt. Solves "I can't remember" at the moment I need it.

## "Why did that fail?" (`why`)
After a non-zero exit, grabs the output with `tmux capture-pane -p -S -40` and explains the error.

**TBD:** Which widgets are in scope, and in which milestone? Final key bindings (Alt-e and Ctrl-g may clash with existing oh-my-zsh or tmux bindings)?

**TBD:** Alt-e needs a live LLM call (seconds): show a spinner and block, or open the answer in a tmux popup (`tmux display-popup`)?

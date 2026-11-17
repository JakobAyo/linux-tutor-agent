# Problem

I use Arch Linux daily (Hyprland, zsh + oh-my-zsh, always in tmux), but much of what I type is copied from the Arch Wiki, forum posts, or an agent's suggestion. I run commands without fully knowing what they or their flags do.

Learning them today means leaving the terminal: searching the web, reading long man pages, or asking a chatbot. That is slow, it breaks focus, and the explanation is detached from the exact command I just ran, so it doesn't stick.

## Gap in existing tools
`man`, `tldr`, explainshell.com, `navi`, `atuin` and `cht.sh` all help when I go and ask. None of them:
- notice automatically what is new *to me*,
- remember my learning progress,
- explain the exact command line I ran, in my context.

See [requirements/functional.md](../requirements/functional.md#existing-tools-dont-reinvent) for the list and how we reuse them.

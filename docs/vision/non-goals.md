# Non-goals

- **Not a shell or history replacement.** It doesn't replace zsh, fzf Ctrl-R, or tools like `atuin`. It only observes.
- **Not a command runner.** The tutor explains; it never executes or changes my commands.
- **No Anthropic API key.** It runs on my Claude subscription through `claude -p` ([ADR 0002](../decisions/0002-claude-p-with-subscription.md)).
- **Not a general Linux course.** No curriculum detached from what I actually use. Lessons may introduce related tools and combinations, but always reached from a command I ran ([ADR 0009](../decisions/0009-discovery-lessons.md)).
- **Not a basics tutor.** Skip trivial commands (`cd`, `ls`, `clear`). I have a CS background, little practical Linux experience.
- **Never in the way.** No noticeable shell delay, no notification storm (at most one notification per processor run, [ADR 0013](../decisions/0013-notify-when-lessons-are-ready.md)).

**TBD:** Is support for shells other than zsh (bash, fish) or distros other than Arch a non-goal, or a later goal for the public repo?

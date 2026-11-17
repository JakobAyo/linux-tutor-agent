# Indicators

- **`notify-send`:** on. One notification per processor run that wrote lessons, naming the commands (e.g. "3 new lessons: rsync, find, git (2)"). Never one per lesson ([ADR 0013](../decisions/0013-notify-when-lessons-are-ready.md)). The debounced trigger limits it to about one per 10 minutes of activity.
- **tmux `status-right`:** optional unread counter, `#(linux-tutor count)` refreshed on tmux's status interval.
- **zsh `RPROMPT`:** optional; read a small count file (not a subprocess) so the prompt stays fast.

**TBD:** Is an unread counter (tmux status, RPROMPT, or both) still wanted in addition to notifications?

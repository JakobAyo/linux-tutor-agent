# Indicators

- **`notify-send`:** on. One notification per processor run that wrote lessons, naming the commands (e.g. "3 new lessons: rsync, find, git (2)"). Never one per lesson ([ADR 0013](../decisions/0013-notify-when-lessons-are-ready.md)). The debounced trigger limits it to about one per 10 minutes of activity.
- **Click action:** opens the reader (`shtutor`) in a new kitty window ([ADRs 0016](../decisions/0016-notifications-only-no-counter.md), [0023](../decisions/0023-notification-click-opens-kitty.md)). A detached child waits for the click, so the background run never blocks on it.
- **No unread counter** in tmux `status-right` or `RPROMPT` ([ADR 0016](../decisions/0016-notifications-only-no-counter.md)).

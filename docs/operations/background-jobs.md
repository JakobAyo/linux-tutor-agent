# Background jobs

The hook never blocks the shell. Detection and lesson writing run in the background.

## Trigger: debounced on shell activity
[ADR 0011](../decisions/0011-activity-debounced-trigger.md):

1. `precmd` compares `$EPOCHSECONDS` with a timestamp kept in a shell variable. There is no disk access and no subprocess.
2. If at least 10 minutes have passed since this shell last started the processor, it starts it disowned (`&!`) and resets the timestamp.
3. The processor takes a lock file. If another processor already runs (another shell), it exits.
4. With no new log lines and no due backlog items, it exits right away. Otherwise it writes lessons and sends one notification ([ADR 0013](../decisions/0013-notify-when-lessons-are-ready.md)).
5. Output and errors go to a run log in the data directory, never to the terminal.

Lessons only arrive while I'm using the terminal. A short session's last commands are processed by the next shell's first run.

## Options not chosen
| Option | Why not |
|---|---|
| Manual runs (M0 spike start, [ADR 0007](../decisions/0007-manual-processor-in-spike.md)) | I had to remember to run it |
| Start after every command | Many pointless wake-ups, lessons mid-task |
| systemd timer (hourly or 10–15 min) | Hourly misses short sessions; any timer runs while idle and needs `claude -p` auth and `notify-send` inside a systemd unit |
| systemd `.path` unit on `cmds.log` | Fires on every write, needs its own debounce |

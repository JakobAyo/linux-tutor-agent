# 0013: Push a desktop notification when lessons are ready

- **Status:** Accepted
- **Date:** 2026-11-17

## Context
Lessons are now written automatically in the background ([ADR 0011](0011-activity-debounced-trigger.md)). I need to find out they exist. The options were a quiet counter (tmux/RPROMPT), a desktop notification, or a daily digest on shell start. The docs had notifications off by default, out of fear of a notification storm.

## Decision
Push. When a processor run has written lessons, it sends one `notify-send` notification for that run that names the commands (e.g. "3 new lessons: rsync, find, git (2)"). It never sends one notification per lesson.

## Alternatives considered
- tmux counter only: quiet, but easy to ignore, and it doesn't motivate.
- Daily digest on shell start: one fixed moment a day, and it adds output to the shell.

## Consequences
- With the debounced trigger, there is at most one notification per ~10 minutes of activity.
- A counter can still be added later for the dashboard. It's no longer the main signal.
- Answers push vs. pull: push, through notifications.
- Updated: [ui/surfaces.md](../ui/surfaces.md), [ui/indicators.md](../ui/indicators.md).

#!/usr/bin/env python3
"""M0 spike processor. Throwaway code: stdlib only, one file.

    process.py seed            import ~/.zsh_history as a learning backlog (ADR 0008)
    process.py run [-b N]      read new log lines, write due lessons + top N backlog lessons
    process.py run --auto      same, detached and quiet; started by the zsh hook (ADR 0011)
    process.py lesson CMD...   write the next lesson for these commands now
    process.py list            show items by status, lessons, and use count
    process.py read [--all]    pick a lesson with fzf, open it in $PAGER, mark it seen
    process.py mark CMD STATUS set understood / dismissed / new / seen

Lessons come in a series per command (ADRs 0009, 0010). Lesson N+1 is due after 10 more uses
since lesson N, or right away once lesson N is marked understood (ADR 0014). Each run writes
all new and due lessons plus up to 3 backlog lessons (ADRs 0012, 0015), then sends one
notification (ADRs 0013, 0016).

Spike-only defaults (not decisions, see spike/README.md): no `--help` calls, man pages
capped by size, Sonnet for every lesson, data in ~/.local/share/linux-tutor-spike/.
"""

from __future__ import annotations

import argparse
import collections
import contextlib
import fcntl
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import time
from pathlib import Path

DATA = Path(
    os.environ.get("LTUTOR_SPIKE_DIR")
    or Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share")) / "linux-tutor-spike"
)
LOG, OFFSET, STORE, LESSONS, USAGE = (
    DATA / "cmds.log",
    DATA / "offset",
    DATA / "store.json",
    DATA / "lessons",
    DATA / "usage.jsonl",
)
RUN_LOCK, STORE_LOCK = DATA / "run.lock", DATA / "store.lock"
HISTORY = Path(os.environ.get("HISTFILE", Path.home() / ".zsh_history"))

MODEL = "sonnet"
MAN_BUDGET = 60_000  # chars of man pages sent to the model, across the main and subcommand pages
SUB_PAGE_CAP = 15_000  # per subcommand page (`git-rebase`)
SUB_PAGES = 3  # subcommand pages per lesson, most used first
NEXT_AFTER = 10  # uses since the last lesson before the next one is due (ADR 0014)
BACKLOG_PER_RUN = 3  # ADR 0015

IGNORE = {"cd", "ls", "clear", "exit", "pwd", "echo", "true", "false", "history", "z"}
WRAPPERS = {"sudo", "doas", "env", "nohup", "time", "nice", "exec", "command", "builtin", "noglob"}
WRAPPER_ARG_FLAGS = {"-u", "-g", "-n", "-C"}  # wrapper flags that take a value
OPERATORS = {"|", "||", "&&", ";", "&", "|&", ";;", "(", ")", "{", "}", "!"}
REDIRECTS = re.compile(r"^\d*(>>?|<<?<?|>&|<&|&>>?|>\|)$")
SECRET = re.compile(
    r"export|token|password|passwd|secret|authorization|bearer|api_key|apikey|aws_|private_key", re.I
)
ASSIGN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
WORD = re.compile(r"^[a-z][a-z0-9-]{1,20}$")


# ---------------------------------------------------------------- parsing


def tokenize(line: str) -> list[str]:
    lex = shlex.shlex(line, posix=True, punctuation_chars=True)
    lex.whitespace_split = True
    try:
        return list(lex)
    except ValueError:  # unbalanced quotes etc.
        return line.split()


def segments(line: str, aliases: dict[str, str]) -> list[tuple[list[str], bool]]:
    """Split a command line into simple commands, drop wrappers/assignments/redirects, expand aliases.
    Returns (tokens, piped) where piped means the command reads from a `|` before it."""
    out, cur, prev_op = [], [], ""
    for tok in tokenize(line) + [";"]:
        if tok in OPERATORS:
            if cur:
                out.append((cur, prev_op in {"|", "|&"}))
            cur, prev_op = [], tok
        else:
            cur.append(tok)
    result = []
    for seg, piped in out:
        seg = _strip_redirects(seg)
        expanded_names: set[str] = set()
        for _ in range(6):  # aliases and wrappers can nest a few levels
            while seg and ASSIGN.match(seg[0]):
                seg = seg[1:]
            if seg and seg[0] in aliases and seg[0] not in expanded_names:
                expanded_names.add(seg[0])  # `ls='ls --color'` must expand only once
                # Drop flags the alias adds (`grep --color=auto ...`): teach only what I typed.
                expanded = [t for i, t in enumerate(tokenize(aliases[seg[0]])) if i == 0 or not t.startswith("-")]
                if expanded:
                    seg = expanded + seg[1:]
                    continue
            if seg and seg[0] in WRAPPERS:
                rest, i = seg[1:], 0
                while i < len(rest) and (rest[i].startswith("-") or ASSIGN.match(rest[i])):
                    i += 2 if rest[i] in WRAPPER_ARG_FLAGS else 1
                seg = rest[i:]
                continue
            break
        if seg:
            result.append((seg, piped))
    return result


def _strip_redirects(seg: list[str]) -> list[str]:
    out, skip = [], False
    for i, tok in enumerate(seg):
        if skip:
            skip = False
        elif tok.isdigit() and i + 1 < len(seg) and REDIRECTS.match(seg[i + 1]):
            continue  # the fd number in `2>&1`, tokenized as '2', '>&', '1'
        elif REDIRECTS.match(tok):
            skip = True
        else:
            out.append(tok)
    return out


def flags_of(seg: list[str]) -> list[str]:
    """Flags as written, e.g. ['-xeu', '--since']."""
    return [t.split("=", 1)[0] for t in seg[1:] if t.startswith("-") and t not in {"-", "--"}]


def mentions(docs: str, word: str) -> bool:
    return bool(re.search(rf"(?<![\w-]){re.escape(word)}(?![\w-])", docs))


def single_flags(flags: list[str], docs: str = "") -> list[str]:
    """'-xeu' -> ['-x', '-e', '-u']; long flags unchanged. A single-dash word the docs mention
    as a whole (`find -iname`, `-type`) stays whole."""
    out = []
    for f in flags:
        if f.startswith("--") or len(f) == 2 or (docs and mentions(docs, f)):
            out.append(f)
        else:
            out += [f"-{c}" for c in f[1:] if c.isalnum()]
    return out


def shape(seg: list[str]) -> str:
    """Locally stored, partly redacted form: flags kept, values masked, plain lowercase words kept
    (maybe subcommands). Final redaction against the docs happens in `redact` before any LLM call."""
    parts = [seg[0]]
    for t in seg[1:]:
        if t.startswith("-") and "=" in t:
            parts.append(t.split("=", 1)[0] + "=<value>")
        elif t.startswith("-") or WORD.match(t):
            parts.append(t)
        else:
            parts.append("<arg>")
    return " ".join(parts)


def redact(shape_str: str, docs: str) -> str:
    """Keep the first plain word only if the local docs mention it (likely a subcommand)."""
    parts, kept_word = shape_str.split(), False
    out = [parts[0]]
    for t in parts[1:]:
        if t.startswith("-") or t.startswith("<"):
            out.append(t)
        elif not kept_word and mentions(docs, t):
            out.append(t)
            kept_word = True
        else:
            out.append("<arg>")
    return " ".join(out)


def load_aliases() -> dict[str, str]:
    marker = "__LTUTOR_ALIASES__"
    try:
        out = subprocess.run(
            ["zsh", "-ic", f"print -r -- {marker}; alias"],
            capture_output=True, text=True, timeout=20, stdin=subprocess.DEVNULL,
        ).stdout
    except (OSError, subprocess.TimeoutExpired):
        return {}
    aliases = {}
    for line in out.split(marker, 1)[-1].splitlines():
        if "=" in line:
            name, val = line.split("=", 1)
            try:
                val = shlex.split(val)[0] if val.startswith(("'", '"')) else val
            except (ValueError, IndexError):
                pass
            aliases[name.strip()] = val
    return aliases


def countable(cmd: str) -> bool:
    return cmd not in IGNORE and "/" not in cmd and shutil.which(cmd) is not None


# ---------------------------------------------------------------- store and locks


def new_item(source: str) -> dict:
    return {"status": "new", "source": source, "count": 0, "piped": 0, "flags": {}, "shapes": {}, "lessons": []}


def load_store() -> dict:
    store = json.loads(STORE.read_text()) if STORE.exists() else {"commands": {}}
    for item in store["commands"].values():
        # Before the series (ADR 0010) an item had one tldr-style `card`. Keep its path, but it
        # doesn't count as a lesson: lesson 1 is a discovery lesson.
        card = item.pop("card", None)
        if card:
            item["legacy_card"] = card
        item.setdefault("lessons", [])
    return store


def save_store(store: dict) -> None:
    DATA.mkdir(parents=True, exist_ok=True, mode=0o700)
    tmp = STORE.with_suffix(".tmp")
    tmp.write_text(json.dumps(store, indent=1, sort_keys=True))
    tmp.replace(STORE)


@contextlib.contextmanager
def store_txn():
    """Short read-modify-write of the store. The background run and manual commands (mark, read)
    can overlap, so every write reloads the store under this lock first."""
    DATA.mkdir(parents=True, exist_ok=True, mode=0o700)
    with STORE_LOCK.open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        store = load_store()
        yield store
        save_store(store)


def run_lock():
    """One processor at a time across all shells (ADR 0011). Returns the open lock file, or None."""
    DATA.mkdir(parents=True, exist_ok=True, mode=0o700)
    f = RUN_LOCK.open("w")
    try:
        fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        f.close()
        return None
    return f


def record(store: dict, seg: list[str], source: str, piped: bool = False) -> bool:
    """Count one use. Returns True if the command is new to the store."""
    cmd = seg[0]
    items = store["commands"]
    new = cmd not in items
    item = items.setdefault(cmd, new_item(source))
    item["count"] += 1
    item["piped"] = item.get("piped", 0) + int(piped)
    for f in flags_of(seg):  # as written; split against the docs only when grounding
        item["flags"][f] = item["flags"].get(f, 0) + 1
    s = shape(seg)
    item["shapes"][s] = item["shapes"].get(s, 0) + 1
    if len(item["shapes"]) > 20:  # keep the top 10
        item["shapes"] = dict(collections.Counter(item["shapes"]).most_common(10))
    return new


# ---------------------------------------------------------------- history seeding


def unmetafy(raw: bytes) -> str:
    """zsh stores non-ASCII bytes 'metafied': 0x83 followed by byte ^ 0x20."""
    out, i = bytearray(), 0
    while i < len(raw):
        if raw[i] == 0x83 and i + 1 < len(raw):
            out.append(raw[i + 1] ^ 0x20)
            i += 2
        else:
            out.append(raw[i])
            i += 1
    return out.decode("utf-8", "replace")


def history_entries(text: str):
    entry: list[str] = []
    for line in text.splitlines():
        if entry and entry[-1].endswith("\\"):
            entry.append(line)
            continue
        if entry:
            yield "\n".join(entry)
        entry = [line.split(";", 1)[1] if line.startswith(": ") and ";" in line else line]
    if entry:
        yield "\n".join(entry)


KEEP_ON_RESEED = ("status", "lessons", "legacy_card", "unverified")


def cmd_seed(args) -> None:
    lock = run_lock()
    if not lock:
        sys.exit("A processor run is in progress. Try again in a minute.")
    old = load_store()["commands"]
    if old and not args.force:
        sys.exit(f"Store already seeded ({len(old)} commands). Use `seed --force` to recount "
                 "(keeps statuses and lessons).")
    fresh: dict = {"commands": {}}
    aliases = load_aliases()
    n_lines = n_skipped = 0
    for line in history_entries(unmetafy(HISTORY.read_bytes())):
        n_lines += 1
        if SECRET.search(line):
            n_skipped += 1
            continue
        for seg, piped in segments(line, aliases):
            if countable(seg[0]):
                record(fresh, seg, "history", piped)
    with store_txn() as store:
        for cmd, prev in store["commands"].items():  # keep what I already did with existing items
            if cmd in fresh["commands"]:
                fresh["commands"][cmd].update({k: prev[k] for k in KEEP_ON_RESEED if k in prev})
            else:
                fresh["commands"][cmd] = prev  # e.g. a live command not in history
        store["commands"] = fresh["commands"]
        items = dict(store["commands"])
    # Start the live log after the seed, so history isn't counted twice.
    OFFSET.write_text(str(LOG.stat().st_size if LOG.exists() else 0))
    print(f"Seeded {len(items)} commands from {n_lines} history entries ({n_skipped} secret-looking skipped).")
    print("Backlog, most used first:")
    for cmd, it in sorted(items.items(), key=lambda kv: -kv[1]["count"])[:15]:
        print(f"  {it['count']:5}  {cmd}")


# ---------------------------------------------------------------- grounding


def sh(argv: list[str], timeout: int = 15) -> str:
    env = dict(os.environ, MANWIDTH="100", MANPAGER="cat", PAGER="cat", NO_COLOR="1", COLUMNS="100")
    try:
        r = subprocess.run(argv, capture_output=True, text=True, timeout=timeout, env=env,
                           stdin=subprocess.DEVNULL)
        return r.stdout if r.returncode == 0 else ""
    except (OSError, subprocess.TimeoutExpired):
        return ""


def man_page(page: str) -> str:
    text = sh(["man", page])
    return re.sub(r".\x08", "", text)  # strip overstrike (what `col -b` does)


def man_excerpt(text: str, flags: list[str], cap: int) -> tuple[str, bool]:
    """The whole page if it fits, else its head plus the option entries for the flags used."""
    if len(text) <= cap:
        return text, False
    head = text[: min(8_000, cap // 3)]
    lines, picked = text.splitlines(), []
    for f in flags:
        pat = re.compile(rf"^\s+(\S+,\s+)*{re.escape(f)}(?![\w-])")
        for i, line in enumerate(lines):
            if pat.match(line):
                picked.append("\n".join(lines[i : i + 10]))
                break
    body = head + "\n\n[... trimmed ...]\n\n" + "\n\n".join(picked)
    return body[:cap], True


def subcommand_candidates(item: dict) -> list[str]:
    """First plain word of each usage shape, most used first (`git rebase` -> rebase)."""
    c: collections.Counter = collections.Counter()
    for s, n in item["shapes"].items():
        words = [t for t in s.split()[1:] if WORD.match(t)]
        if words:
            c[words[0]] += n
    return [w for w, _ in c.most_common(SUB_PAGES * 2)]


def grounding(cmd: str, item: dict, used_flags: list[str]) -> dict:
    """Local docs for a lesson. Commands with subcommands (`git`, `npm`) get the man pages of the
    subcommands I use most (`git-rebase`), not just the top-level page."""
    pages: list[tuple[str, str]] = []
    for word in subcommand_candidates(item):
        if len(pages) >= SUB_PAGES:
            break
        text = man_page(f"{cmd}-{word}")
        if text:
            pages.append((f"{cmd}-{word}", text))
    main = man_page(cmd)
    full = main + "\n" + "\n".join(t for _, t in pages)
    flags = single_flags(used_flags, full)  # every flag I've used, so trimmed pages still cover them
    parts, trimmed, budget = [], [], MAN_BUDGET
    for name, text in pages:
        excerpt, cut = man_excerpt(text, flags, SUB_PAGE_CAP)
        parts.append(f"man {name}{' (trimmed)' if cut else ''}:\n{excerpt}")
        trimmed += [name] if cut else []
        budget -= len(excerpt)
    if main:
        excerpt, cut = man_excerpt(main, flags, max(budget, 15_000))
        parts.insert(0, f"man {cmd}{' (trimmed)' if cut else ''}:\n{excerpt}")
        trimmed += [cmd] if cut else []
    tldr = sh(["tldr", "-m", cmd])
    path = shutil.which(cmd) or ""
    pkg = sh(["pacman", "-Qqo", path]).strip() if path else ""
    desc = ""
    if pkg:
        m = re.search(r"^Description\s*:\s*(.*)$", sh(["pacman", "-Qi", pkg]), re.M)
        desc = m.group(1) if m else ""
    return {
        "man": "\n\n".join(parts), "pages": [cmd] * bool(main) + [n for n, _ in pages], "trimmed": trimmed,
        "tldr": tldr, "whatis": sh(["whatis", cmd]).strip(), "package": pkg, "package_desc": desc,
        "all_docs": full + "\n" + tldr,
    }


# ---------------------------------------------------------------- lessons


PROMPT = """You write lesson {n} in a series that teaches `{cmd}` to one learner.
Learner: CS background, little practical Linux experience. Arch Linux, zsh + oh-my-zsh, tmux, Hyprland.
Their goal: become confident in the terminal and write their own scripts and automations.
Skip basics. Explain the why and the concept, not only syntax.

How they actually use `{cmd}` (argument values masked as <arg>/<value>):
{usage}

{series}

Teach what they probably don't know yet, anchored to how they use it:
- flags and modes they haven't used, each with a concrete use case,
- combinations with other commands (pipes, xargs, find -exec, shell loops, scripts, systemd units/timers),
- related or better tools in the same area, reached from this command (nothing unrelated),
- the concept behind it, where it helps.
{depth}

Rules:
- Flags of `{cmd}`: use ONLY flags and behaviour present in the local docs below. If the docs are
  missing or thin, say "local docs: limited" and stay general instead of guessing.
- Related tools: name them with at most one example each. Don't teach their flags in detail.
- If something can destroy data or lock you out, add a one-line warning next to it.
- Output Markdown only, no preamble, max ~60 lines, in exactly this structure:

# {cmd} — lesson {n}  (package: <package or unknown>)

## You ran
{you_ran}

## What you're missing
3-5 bullets: `flag` - what it does, and when you'd want it.

## Use cases
2-4 realistic commands in code spans, each with one line on when to use it.

## Combine it
1-3 combinations with other commands or a small script/systemd snippet.

## Related tools
One bullet per tool in exactly this format: - `tool` - why it's related or better.

## Concept
2-4 sentences on the mechanism behind it.

## Next lesson
One line: what lesson {n_next} will go deeper on.

Then end with exactly one final line, which is stored and shown to the next lesson (not to the learner):
<!-- taught: short comma-separated list of the flags, tools and ideas this lesson covered -->

--- LOCAL DOCS ---
whatis: {whatis}
package: {package} - {package_desc}

{man}

tldr page:
{tldr}
"""

YOU_RAN_FIRST = (
    "Their most common invocation in a code span, then one short bullet per flag/subcommand they used.\n"
    "If they often pipe into it, say what that means for this command (it reads stdin)."
)
YOU_RAN_LATER = "One or two lines: their most common invocation and how it connects to this lesson's topic."


def series_context(item: dict) -> tuple[str, str]:
    lessons = item["lessons"]
    if not lessons:
        return ("This is lesson 1. Cover their usage, the core flags they're missing, and the main use cases.",
                "Lesson 1 stays practical: the 80% they'll use weekly.")
    lines = ["Earlier lessons already taught this. Don't repeat it; build on it:"]
    lines += [f"- lesson {lsn['n']}: {lsn.get('taught') or '(no summary)'}" for lsn in lessons]
    if lessons[-1].get("next"):
        lines.append(f"Lesson {lessons[-1]['n']} promised that the next lesson covers: {lessons[-1]['next']}")
    return ("\n".join(lines),
            "Go one level deeper than the earlier lessons: advanced modes, edge cases, scripting, automation.")


def usage_lines(cmd: str, item: dict, docs: str) -> str:
    shapes = collections.Counter(item["shapes"]).most_common(5) or [(cmd, 1)]
    lines = [f"- `{redact(s, docs)}`  ({n}x)" for s, n in shapes]
    flags: collections.Counter = collections.Counter()
    for f, n in item["flags"].items():
        for single in single_flags([f], docs):
            flags[single] += n
    if flags:
        lines.append("- flags used: " + ", ".join(f"{f} ({n}x)" for f, n in flags.most_common(10)))
    lines.append(f"- used {item['count']}x in total, {item.get('piped', 0)}x with input piped in")
    return "\n".join(lines)


def call_claude(prompt: str) -> tuple[dict | None, str]:
    try:
        r = subprocess.run(
            ["claude", "-p", "--model", MODEL, "--tools", "", "--no-session-persistence",
             "--strict-mcp-config", "--output-format", "json"],
            input=prompt, capture_output=True, text=True, timeout=300, cwd=DATA,
        )
        result = json.loads(r.stdout)
    except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError) as e:
        return None, f"claude -p failed ({e})"
    body = (result.get("result") or "").strip()
    if r.returncode != 0 or not body or result.get("is_error"):
        return None, f"claude -p error: {body[:200] or r.stderr[:200]}"
    return result, ""


def mark_missing_tools(body: str) -> str:
    """ADR 0009: a suggested tool that isn't installed is marked as such."""
    out, in_related = [], False
    for line in body.splitlines():
        if line.startswith("## "):
            in_related = line.strip().lower() == "## related tools"
        m = re.match(r"^\s*[-*]\s+`([\w.+-]+)`", line) if in_related else None
        if m and not shutil.which(m.group(1)) and "not installed" not in line:
            line += " *(not installed)*"
        out.append(line)
    return "\n".join(out)


def write_lesson(cmd: str, item: dict) -> dict | None:
    """Write the next lesson for `cmd`. Returns the lesson entry for the store, or None."""
    n = len(item["lessons"]) + 1
    top_flags = [f for f, _ in collections.Counter(item["flags"]).most_common(15)]
    g = grounding(cmd, item, top_flags)
    docs = g["all_docs"]
    series, depth = series_context(item)
    prompt = PROMPT.format(
        cmd=cmd, n=n, n_next=n + 1, usage=usage_lines(cmd, item, docs), series=series, depth=depth,
        you_ran=YOU_RAN_FIRST if n == 1 else YOU_RAN_LATER, whatis=g["whatis"] or "-",
        package=g["package"] or "unknown", package_desc=g["package_desc"] or "-",
        man=g["man"] or "(no man page)", tldr=g["tldr"] or "(no tldr page)",
    )
    t0 = time.monotonic()
    result, err = call_claude(prompt)
    if not result:
        print(f"  ! {cmd}: {err}", file=sys.stderr)
        return None
    with USAGE.open("a") as f:
        f.write(json.dumps({"time": int(time.time()), "cmd": cmd, "lesson": n, "model": MODEL,
                            "seconds": round(time.monotonic() - t0, 1), "prompt_chars": len(prompt),
                            "cost_usd": result.get("total_cost_usd")}) + "\n")
    body = result["result"].strip()
    m = re.search(r"<!--\s*taught:\s*(.*?)\s*-->", body, re.S)
    taught = " ".join(m.group(1).split()) if m else ""
    body = re.sub(r"\s*<!--\s*taught:.*?-->\s*", "\n", body, flags=re.S).strip()
    m = re.search(r"^## Next lesson\s*\n+(.+)$", body, re.M)
    nxt = m.group(1).strip() if m else ""
    body = mark_missing_tools(body)
    unverified = invented_flags(body, cmd, docs)
    footer = (f"\n\n---\n*Grounding: man {', '.join(g['pages']) or 'none'}"
              f"{' (trimmed: ' + ', '.join(g['trimmed']) + ')' if g['trimmed'] else ''}, "
              f"tldr {'yes' if g['tldr'] else 'no'}. Model: {MODEL}.*")
    if unverified:
        footer += f"\n\n> **Unverified flags** (not found in local docs): {', '.join(sorted(unverified))}"
    path = LESSONS / cmd / f"{n}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body + footer + "\n")
    return {"n": n, "path": str(path), "time": int(time.time()), "taught": taught, "next": nxt,
            "unverified": sorted(unverified)}


def invented_flags(lesson: str, cmd: str, docs: str) -> set[str]:
    """Flags used with `cmd` in the lesson's code spans that the local docs never mention."""
    found = set()
    for span in re.findall(r"`([^`]+)`", lesson):
        toks = span.split()
        if cmd not in toks:
            continue
        for t in toks[toks.index(cmd) + 1 :]:
            if t in {"|", "&&", ";", "||"}:
                break
            if t.startswith("-") and t not in {"-", "--"}:
                f = t.split("=", 1)[0]
                for single in single_flags([f], docs):
                    if not mentions(docs, single):
                        found.add(single)
    return found


def generate(todo: list[str], stop_on_error: bool) -> list[tuple[str, int]]:
    """Write the next lesson for each command. Returns (command, lesson number) for each one written."""
    written = []
    for cmd in todo:
        item = load_store()["commands"][cmd]
        print(f"  {cmd} #{len(item['lessons']) + 1} ...", end="", flush=True)
        lesson = write_lesson(cmd, item)
        if not lesson:
            if stop_on_error:  # likely a rate limit or auth problem; the rest stays due for the next run
                print(" stopping this run.")
                break
            continue
        with store_txn() as store:
            it = store["commands"][cmd]
            lesson["count_at"] = it["count"]
            it["lessons"].append(lesson)
            it["status"] = "new"
        warn = f"  (unverified: {', '.join(lesson['unverified'])})" if lesson["unverified"] else ""
        print(f" {lesson['path']}{warn}")
        written.append((cmd, lesson["n"]))
    return written


# Waits for the click, then opens the reader in a new kitty window (ADR 0023).
CLICK_TO_OPEN = 'test "$(notify-send --wait --action=default=Open "$@")" = default && exec kitty --class shtutor shtutor'


def notify(written: list[tuple[str, int]]) -> None:
    """One notification per run that wrote lessons, never one per lesson (ADRs 0013, 0016)."""
    if not written or not shutil.which("notify-send"):
        return
    names = ", ".join(c if n == 1 else f"{c} ({n})" for c, n in written)
    body = f"{len(written)} new lesson{'s' * (len(written) > 1)}: {names}"
    args = ["--app-name=Linux tutor", "Linux tutor", body]
    try:
        if shutil.which("shtutor") and shutil.which("kitty"):
            # A detached child waits for the click, so this run exits and releases its locks now.
            subprocess.Popen(["sh", "-c", CLICK_TO_OPEN, "sh", *args], start_new_session=True,
                             stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            subprocess.run(["notify-send", *args], timeout=10, stdin=subprocess.DEVNULL, capture_output=True)
    except (OSError, subprocess.TimeoutExpired) as e:
        print(f"  ! notify-send failed ({e})", file=sys.stderr)


# ---------------------------------------------------------------- run


def due_lessons(items: dict, live_new: list[str], backlog_n: int) -> tuple[list[str], int]:
    """New commands, then due series lessons (ADR 0014), then the top backlog (ADR 0015).
    Returns the commands to write a lesson for and how many backlog items remain."""
    todo = [c for c in dict.fromkeys(live_new) if not items[c]["lessons"] and items[c]["status"] != "dismissed"]
    for c, it in sorted(items.items(), key=lambda kv: -kv[1]["count"]):
        if it["lessons"] and it["status"] != "dismissed" and (
            it["status"] == "understood" or it["count"] - it["lessons"][-1]["count_at"] >= NEXT_AFTER
        ):
            todo.append(c)
    backlog = sorted(
        (c for c, it in items.items() if not it["lessons"] and it["status"] != "dismissed" and c not in todo),
        key=lambda c: -items[c]["count"],
    )
    return todo + backlog[:backlog_n], max(len(backlog) - backlog_n, 0)


def detach() -> None:
    """--auto: leave the shell's session, so `zsh -i` (alias loading) can never be stopped by
    SIGTTOU/SIGTTIN for touching the terminal from the background."""
    if os.fork():
        os._exit(0)
    os.setsid()


def cmd_run(args) -> None:
    if args.auto:
        detach()
    lock = run_lock()
    if not lock:
        if not args.auto:
            print("Another processor run is in progress.")
        return
    if not STORE.exists():
        if not args.auto:
            sys.exit("Store is empty. Run `process.py seed` first.")
        return
    offset = int(OFFSET.read_text()) if OFFSET.exists() else 0
    data = b""
    if LOG.exists() and LOG.stat().st_size > offset:
        with LOG.open("rb") as f:
            f.seek(offset)
            data = f.read()
    complete = data[: data.rfind(b"\n") + 1]  # ignore a half-written last line
    segs: list[tuple[list[str], bool]] = []
    if complete:
        aliases = load_aliases()
        for raw in complete.decode("utf-8", "replace").splitlines():
            try:
                entry = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if entry.get("exit") == 127 or SECRET.search(entry.get("command", "")):
                continue
            segs += [(seg, piped) for seg, piped in segments(entry["command"], aliases) if countable(seg[0])]
    live_new: list[str] = []
    with store_txn() as store:
        for seg, piped in segs:
            if record(store, seg, "live", piped):
                live_new.append(seg[0])
        todo, left = due_lessons(store["commands"], live_new, args.backlog)
    OFFSET.write_text(str(offset + len(complete)))
    if not todo:
        if not args.auto:
            print(f"{len(segs)} command(s) read from the log. Nothing due.")
        return
    print(f"[{time.strftime('%F %T')}] {len(segs)} command(s) read, {len(set(live_new))} new; "
          f"writing {len(todo)} lesson(s), {left} left in backlog.")
    written = generate(todo, stop_on_error=True)
    notify(written)
    if not args.auto:
        print("Read them with: process.py read")


# ---------------------------------------------------------------- lesson / list / read / mark


def cmd_lesson(args) -> None:
    """Write the next lesson for the named commands now, regardless of what's due."""
    lock = run_lock()
    if not lock:
        sys.exit("A processor run is in progress. Try again in a minute.")
    todo = []
    with store_txn() as store:
        items = store["commands"]
        for cmd in args.cmds:
            if cmd not in items:
                if not shutil.which(cmd):
                    print(f"  ! {cmd}: not found on PATH, skipped", file=sys.stderr)
                    continue
                items[cmd] = new_item("manual")
                items[cmd]["count"] = 1
                items[cmd]["shapes"] = {cmd: 1}
            if items[cmd]["status"] == "dismissed":
                items[cmd]["status"] = "new"
            todo.append(cmd)
    generate(todo, stop_on_error=False)


def cmd_list(args) -> None:
    items = load_store()["commands"]
    print(f"{'status':11} {'lessons':>7} {'uses':>5} {'since':>5}  command")
    for cmd, it in sorted(items.items(), key=lambda kv: (kv[1]["status"], -kv[1]["count"])):
        if args.status and it["status"] != args.status:
            continue
        since = it["count"] - it["lessons"][-1]["count_at"] if it["lessons"] else ""
        print(f"{it['status']:11} {len(it['lessons']):7} {it['count']:5} {since:>5}  {cmd}")


def cmd_read(args) -> None:
    items = load_store()["commands"]
    rows = []
    for cmd, it in items.items():
        if not it["lessons"] or (not args.all and it["status"] not in {"new", "seen"}):
            continue
        for lsn in reversed(it["lessons"] if args.all else it["lessons"][-1:]):
            latest = lsn is it["lessons"][-1]
            rows.append((not (latest and it["status"] == "new"), -it["count"], -lsn["n"],
                         f"{cmd}\t#{lsn['n']}\t{it['status'] if latest else 'older'}\t{lsn['path']}"))
    if not rows:
        sys.exit("No lessons to read. They're written in the background, or run `process.py run`.")
    lines = "\n".join(r[-1] for r in sorted(rows))
    pick = subprocess.run(
        ["fzf", "--delimiter", "\t", "--with-nth", "1,2,3", "--preview", "cat {4}"],
        input=lines, stdout=subprocess.PIPE, text=True,
    ).stdout.strip()
    if not pick:
        return
    cmd, num, _status, path = pick.split("\t")
    pager = os.environ.get("PAGER", "less")
    subprocess.run([*shlex.split(pager), path])
    with store_txn() as store:
        it = store["commands"][cmd]
        if it["status"] == "new" and int(num[1:]) == len(it["lessons"]):
            it["status"] = "seen"
    print(f"{cmd}: `process.py mark {cmd} understood` writes the next lesson in the next run "
          "(or `dismissed` to stop the series).")


def cmd_mark(args) -> None:
    with store_txn() as store:
        if args.cmd not in store["commands"]:
            sys.exit(f"Unknown command: {args.cmd}")
        store["commands"][args.cmd]["status"] = args.status
    hint = {"understood": " Its next lesson is due in the next run.",
            "dismissed": " No more lessons for it."}.get(args.status, "")
    print(f"{args.cmd}: {args.status}.{hint}")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="action", required=True)
    s = sub.add_parser("seed")
    s.add_argument("--force", action="store_true", help="recount from history, keep statuses and lessons")
    s.set_defaults(func=cmd_seed)
    c = sub.add_parser("lesson", aliases=["card"], help="write the next lesson for specific commands now")
    c.add_argument("cmds", nargs="+")
    c.set_defaults(func=cmd_lesson)
    r = sub.add_parser("run")
    r.add_argument("-b", "--backlog", type=int, default=BACKLOG_PER_RUN,
                   help=f"backlog lessons per run (default {BACKLOG_PER_RUN})")
    r.add_argument("--auto", action="store_true", help="detached and quiet; used by the zsh hook")
    r.set_defaults(func=cmd_run)
    ls = sub.add_parser("list")
    ls.add_argument("status", nargs="?", choices=["new", "seen", "understood", "dismissed"])
    ls.set_defaults(func=cmd_list)
    rd = sub.add_parser("read")
    rd.add_argument("--all", action="store_true", help="include older lessons and understood/dismissed commands")
    rd.set_defaults(func=cmd_read)
    m = sub.add_parser("mark")
    m.add_argument("cmd")
    m.add_argument("status", choices=["new", "seen", "understood", "dismissed"])
    m.set_defaults(func=cmd_mark)
    args = p.parse_args()
    DATA.mkdir(parents=True, exist_ok=True, mode=0o700)
    args.func(args)


if __name__ == "__main__":
    main()

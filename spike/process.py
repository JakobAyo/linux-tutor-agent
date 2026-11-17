#!/usr/bin/env python3
"""M0 spike processor. Throwaway code: stdlib only, one file.

    process.py seed            import ~/.zsh_history as a learning backlog (ADR 0008)
    process.py run [-b N]      read new log lines, write cards for new commands + top N backlog
    process.py list            show items by status and use count
    process.py read            pick a card with fzf, open it in $PAGER, mark it seen
    process.py mark CMD STATUS set understood / dismissed / new

Spike-only defaults (not decisions, see spike/README.md): no `--help` calls, man pages
capped by size, Sonnet for every card, data in ~/.local/share/linux-tutor-spike/.
"""

from __future__ import annotations

import argparse
import collections
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
LOG, OFFSET, STORE, CARDS, USAGE = (
    DATA / "cmds.log",
    DATA / "offset",
    DATA / "store.json",
    DATA / "cards",
    DATA / "usage.jsonl",
)
HISTORY = Path(os.environ.get("HISTFILE", Path.home() / ".zsh_history"))

MODEL = "sonnet"
MAN_CAP = 30_000  # chars of man page sent to the model
LIVE_CAP = 10  # max cards for live-new commands per run

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


def single_flags(flags: list[str], docs: str = "") -> list[str]:
    """'-xeu' -> ['-x', '-e', '-u']; long flags unchanged. A single-dash word the docs mention
    as a whole (`find -iname`, `-type`) stays whole."""
    out = []
    for f in flags:
        if f.startswith("--") or len(f) == 2 or (docs and re.search(rf"(?<![\w-]){re.escape(f)}(?![\w-])", docs)):
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
        elif not kept_word and re.search(rf"(?<![\w-]){re.escape(t)}(?![\w-])", docs):
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


# ---------------------------------------------------------------- store


def load_store() -> dict:
    if STORE.exists():
        return json.loads(STORE.read_text())
    return {"commands": {}}


def save_store(store: dict) -> None:
    DATA.mkdir(parents=True, exist_ok=True, mode=0o700)
    tmp = STORE.with_suffix(".tmp")
    tmp.write_text(json.dumps(store, indent=1, sort_keys=True))
    tmp.replace(STORE)


def record(store: dict, seg: list[str], source: str, piped: bool = False) -> bool:
    """Count one use. Returns True if the command is new to the store."""
    cmd = seg[0]
    items = store["commands"]
    new = cmd not in items
    item = items.setdefault(
        cmd, {"status": "new", "source": source, "count": 0, "flags": {}, "shapes": {}, "card": None}
    )
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


def cmd_seed(args) -> None:
    old = load_store()["commands"]
    if old and not args.force:
        sys.exit(f"Store already seeded ({len(old)} commands). Use `seed --force` to recount "
                 "(keeps statuses and cards).")
    store: dict = {"commands": {}}
    aliases = load_aliases()
    n_lines = n_skipped = 0
    for line in history_entries(unmetafy(HISTORY.read_bytes())):
        n_lines += 1
        if SECRET.search(line):
            n_skipped += 1
            continue
        for seg, piped in segments(line, aliases):
            if countable(seg[0]):
                record(store, seg, "history", piped)
    for cmd, prev in old.items():  # keep what I already did with existing items
        if cmd in store["commands"]:
            store["commands"][cmd].update(status=prev["status"], card=prev["card"])
        else:
            store["commands"][cmd] = prev  # e.g. a live command not in history
    save_store(store)
    # Start the live log after the seed, so history isn't counted twice.
    OFFSET.write_text(str(LOG.stat().st_size if LOG.exists() else 0))
    items = store["commands"]
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


def man_page(cmd: str, sub: str | None) -> str:
    for page in ([f"{cmd}-{sub}"] if sub else []) + [cmd]:
        text = sh(["man", page])
        if text:
            return re.sub(r".\x08", "", text)  # strip overstrike (what `col -b` does)
    return ""


def man_excerpt(text: str, flags: list[str]) -> tuple[str, bool]:
    if len(text) <= MAN_CAP:
        return text, False
    head = text[:8_000]
    lines, picked = text.splitlines(), []
    for f in flags:
        pat = re.compile(rf"^\s+(\S+,\s+)*{re.escape(f)}(?![\w-])")
        for i, line in enumerate(lines):
            if pat.match(line):
                picked.append("\n".join(lines[i : i + 10]))
                break
    body = head + "\n\n[... trimmed ...]\n\n" + "\n\n".join(picked)
    return body[:MAN_CAP], True


def grounding(cmd: str, shape_str: str, used_flags: list[str]) -> dict:
    words = [t for t in shape_str.split()[1:] if WORD.match(t)]
    sub = words[0] if words else None
    man = man_page(cmd, sub)
    flags = single_flags(used_flags, man)  # every flag I've used, so the trimmed man page covers them
    excerpt, trimmed = man_excerpt(man, flags)
    tldr = sh(["tldr", "-m", cmd])
    path = shutil.which(cmd) or ""
    pkg = sh(["pacman", "-Qqo", path]).strip() if path else ""
    desc = ""
    if pkg:
        m = re.search(r"^Description\s*:\s*(.*)$", sh(["pacman", "-Qi", pkg]), re.M)
        desc = m.group(1) if m else ""
    return {
        "man": excerpt, "man_trimmed": trimmed, "tldr": tldr, "whatis": sh(["whatis", cmd]).strip(),
        "package": pkg, "package_desc": desc, "all_docs": man + "\n" + tldr,
    }


# ---------------------------------------------------------------- cards


PROMPT = """You write a short command card for a learner: CS background, little practical Linux.
They use Arch Linux, zsh, tmux. Skip basics. Explain the why and the concept, not only syntax.

How they actually use it (argument values masked as <arg>/<value>):
{usage}

Rules:
- Use ONLY flags and behaviour present in the local docs below. If unsure, say so.
- If the docs are missing or thin, say "local docs: none/limited" instead of guessing.
- If the command can destroy data or lock you out, add a one-line warning.
- Output Markdown only, no preamble, max ~35 lines, in this structure:

# {cmd}  (package: <package or unknown>)
One sentence: what it does.

## How you use it
Their most common invocation(s), then one bullet per flag/subcommand they used: what it does.
If they often pipe into it, say what that means for this command (it reads stdin).

## Variations
3-5 bullets: `command` - when you'd use it. Prefer useful flags they have NOT used yet,
and combinations with other commands (pipes) where that's how the command shines.

## Concept
2-4 sentences on the mechanism behind it.

## Related
Related commands, `man` pages, Arch Wiki page title.

--- LOCAL DOCS ---
whatis: {whatis}
package: {package} - {package_desc}

man page{trimmed}:
{man}

tldr page:
{tldr}
"""


def write_card(cmd: str, item: dict) -> Path | None:
    shapes = collections.Counter(item["shapes"]).most_common(5) or [(cmd, 1)]
    top_flags = [f for f, _ in collections.Counter(item["flags"]).most_common(15)]
    g = grounding(cmd, shapes[0][0], top_flags)
    docs = g["all_docs"]
    lines = [f"- `{redact(s, docs)}`  ({n}x)" for s, n in shapes]
    flags = collections.Counter()
    for f, n in item["flags"].items():
        for single in single_flags([f], docs):
            flags[single] += n
    if flags:
        lines.append("- flags used: " + ", ".join(f"{f} ({n}x)" for f, n in flags.most_common(10)))
    lines.append(f"- used {item['count']}x in total, {item.get('piped', 0)}x with input piped in")
    prompt = PROMPT.format(
        cmd=cmd, usage="\n".join(lines), whatis=g["whatis"] or "-", package=g["package"] or "unknown",
        package_desc=g["package_desc"] or "-", trimmed=" (trimmed to the parts for the flags used)"
        if g["man_trimmed"] else "", man=g["man"] or "(no man page)", tldr=g["tldr"] or "(no tldr page)",
    )
    t0 = time.monotonic()
    try:
        r = subprocess.run(
            ["claude", "-p", "--model", MODEL, "--tools", "", "--no-session-persistence",
             "--strict-mcp-config", "--output-format", "json"],
            input=prompt, capture_output=True, text=True, timeout=300, cwd=DATA,
        )
        result = json.loads(r.stdout)
        body = result.get("result", "").strip()
    except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError) as e:
        print(f"  ! {cmd}: claude -p failed ({e})", file=sys.stderr)
        return None
    if r.returncode != 0 or not body or result.get("is_error"):
        print(f"  ! {cmd}: claude -p error: {body[:200] or r.stderr[:200]}", file=sys.stderr)
        return None
    with USAGE.open("a") as f:
        f.write(json.dumps({"time": int(time.time()), "cmd": cmd, "model": MODEL,
                            "seconds": round(time.monotonic() - t0, 1),
                            "prompt_chars": len(prompt), "cost_usd": result.get("total_cost_usd")}) + "\n")
    unverified = invented_flags(body, cmd, g["all_docs"])
    footer = f"\n\n---\n*Grounding: man {'yes' if g['man'] else 'no'}, tldr {'yes' if g['tldr'] else 'no'}"
    footer += f"{', man trimmed' if g['man_trimmed'] else ''}. Model: {MODEL}.*"
    if unverified:
        footer += f"\n\n> **Unverified flags** (not found in local docs): {', '.join(sorted(unverified))}"
    CARDS.mkdir(parents=True, exist_ok=True)
    path = CARDS / f"{cmd}.md"
    path.write_text(body + footer + "\n")
    item["unverified"] = sorted(unverified)
    return path


def invented_flags(card: str, cmd: str, docs: str) -> set[str]:
    """Flags used with `cmd` in the card's code spans that the local docs never mention."""
    found = set()
    for span in re.findall(r"`([^`]+)`", card):
        toks = span.split()
        if cmd not in toks:
            continue
        for t in toks[toks.index(cmd) + 1 :]:
            if t in {"|", "&&", ";", "||"}:
                break
            if t.startswith("-") and t not in {"-", "--"}:
                f = t.split("=", 1)[0]
                for single in single_flags([f], docs):
                    if not re.search(rf"(?<![\w-]){re.escape(single)}(?![\w-])", docs):
                        found.add(single)
    return found


# ---------------------------------------------------------------- run


def cmd_run(args) -> None:
    store = load_store()
    if not store["commands"]:
        sys.exit("Store is empty. Run `process.py seed` first.")
    offset = int(OFFSET.read_text()) if OFFSET.exists() else 0
    live_new: list[str] = []
    if LOG.exists():
        aliases = load_aliases()
        with LOG.open("rb") as f:
            f.seek(offset)
            data = f.read()
        complete = data[: data.rfind(b"\n") + 1]  # ignore a half-written last line
        for raw in complete.decode("utf-8", "replace").splitlines():
            try:
                entry = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if entry.get("exit") == 127 or SECRET.search(entry.get("command", "")):
                continue
            for seg, piped in segments(entry["command"], aliases):
                if countable(seg[0]) and record(store, seg, "live", piped):
                    live_new.append(seg[0])
        offset += len(complete)
    save_store(store)
    OFFSET.write_text(str(offset))

    items = store["commands"]
    todo = [c for c in live_new if not items[c]["card"]][:LIVE_CAP]
    backlog = sorted(
        (c for c, it in items.items() if it["status"] == "new" and not it["card"] and c not in todo),
        key=lambda c: -items[c]["count"],
    )
    todo += backlog[: args.backlog]
    print(f"{len(live_new)} new command(s) from the log; writing {len(todo)} card(s) "
          f"({max(len(backlog) - args.backlog, 0)} left in backlog).")
    generate(store, todo)


def generate(store: dict, todo: list[str]) -> None:
    items = store["commands"]
    for cmd in todo:
        print(f"  {cmd} ...", end="", flush=True)
        path = write_card(cmd, items[cmd])
        if path:
            items[cmd]["card"] = str(path)
            warn = f"  (unverified: {', '.join(items[cmd]['unverified'])})" if items[cmd]["unverified"] else ""
            print(f" {path}{warn}")
        save_store(store)
    unread = sum(1 for it in items.values() if it["card"] and it["status"] == "new")
    print(f"{unread} unread card(s). Read them with: process.py read")


# ---------------------------------------------------------------- list / read / mark


def cmd_card(args) -> None:
    """Write (or rewrite) cards for the named commands, regardless of backlog order."""
    store = load_store()
    items = store["commands"]
    todo = []
    for cmd in args.cmds:
        if cmd not in items:
            if not shutil.which(cmd):
                print(f"  ! {cmd}: not found on PATH, skipped", file=sys.stderr)
                continue
            record(store, [cmd], "manual")
        items[cmd]["status"] = "new"
        todo.append(cmd)
    generate(store, todo)


def cmd_list(args) -> None:
    items = load_store()["commands"]
    for cmd, it in sorted(items.items(), key=lambda kv: (kv[1]["status"], -kv[1]["count"])):
        if args.status and it["status"] != args.status:
            continue
        card = "card" if it["card"] else "    "
        print(f"{it['status']:11} {card} {it['count']:5}  {cmd}")


def cmd_read(_args) -> None:
    store = load_store()
    items = store["commands"]
    cards = [c for c, it in items.items() if it["card"] and it["status"] in {"new", "seen"}]
    if not cards:
        sys.exit("No cards to read. Run `process.py run` first.")
    cards.sort(key=lambda c: (items[c]["status"] != "new", -items[c]["count"]))
    lines = "\n".join(f"{c}\t{items[c]['status']}" for c in cards)
    pick = subprocess.run(
        ["fzf", "--delimiter", "\t", "--with-nth", "1,2", "--preview", f"cat {CARDS}/{{1}}.md"],
        input=lines, capture_output=False, stdout=subprocess.PIPE, text=True,
    ).stdout.strip()
    if not pick:
        return
    cmd = pick.split("\t")[0]
    pager = os.environ.get("PAGER", "less")
    subprocess.run([*shlex.split(pager), items[cmd]["card"]])
    if items[cmd]["status"] == "new":
        items[cmd]["status"] = "seen"
        save_store(store)
    print(f"{cmd}: mark with `process.py mark {cmd} understood` (or dismissed).")


def cmd_mark(args) -> None:
    store = load_store()
    if args.cmd not in store["commands"]:
        sys.exit(f"Unknown command: {args.cmd}")
    store["commands"][args.cmd]["status"] = args.status
    save_store(store)
    print(f"{args.cmd}: {args.status}")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="action", required=True)
    s = sub.add_parser("seed")
    s.add_argument("--force", action="store_true", help="recount from history, keep statuses and cards")
    s.set_defaults(func=cmd_seed)
    c = sub.add_parser("card", help="write cards for specific commands now")
    c.add_argument("cmds", nargs="+")
    c.set_defaults(func=cmd_card)
    r = sub.add_parser("run")
    r.add_argument("-b", "--backlog", type=int, default=3, help="backlog cards per run (default 3)")
    r.set_defaults(func=cmd_run)
    ls = sub.add_parser("list")
    ls.add_argument("status", nargs="?", choices=["new", "seen", "understood", "dismissed"])
    ls.set_defaults(func=cmd_list)
    sub.add_parser("read").set_defaults(func=cmd_read)
    m = sub.add_parser("mark")
    m.add_argument("cmd")
    m.add_argument("status", choices=["new", "seen", "understood", "dismissed"])
    m.set_defaults(func=cmd_mark)
    args = p.parse_args()
    DATA.mkdir(parents=True, exist_ok=True, mode=0o700)
    args.func(args)


if __name__ == "__main__":
    main()

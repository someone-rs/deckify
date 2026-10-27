"""Command-line interface for deckify."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .parser import parse_deck
from .render import render_html
from .themes import DEFAULT_THEME, list_themes

DEMO_MD = """---
title: deckify demo
author: deckify
theme: midnight
---

# deckify

Turn Markdown into a beautiful slide deck.

One file in, one HTML file out — no build step, no server.

---

## Why you'll like it

- **Zero dependencies** — Python's standard library is all it needs
- **One self-contained file** — send it, host it, open it offline
- **Keyboard-first** — arrows, space, `N` for notes, `G` for the grid

---

## Code, just like this

```python
from deckify import parse_deck, render_html

deck = parse_deck(Path("talk.md").read_text())
Path("talk.html").write_text(render_html(deck))
```

---

## A tiny table

| Feature | deckify |
| ------- | ------- |
| Build step | None |
| Works offline | Yes |
| Speaker notes | Press `N` |

<!-- note: This is a speaker note. It never appears on the slide itself —
press N (or the Notes button) while presenting to read it. -->

---

# Thank you

Questions? The deck is just Markdown — edit and rebuild in seconds.
"""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="deckify",
        description="Turn a Markdown file into a self-contained HTML "
                    "slide deck.")
    parser.add_argument("input", nargs="?", type=Path,
                        help="Markdown source file (omit with --demo)")
    parser.add_argument("-o", "--output", type=Path, default=None,
                        help="Output HTML file (default: <input>.html)")
    parser.add_argument("--title", default=None,
                        help="Deck title (overrides front matter)")
    parser.add_argument("--author", default=None,
                        help="Deck author (overrides front matter)")
    parser.add_argument("--theme", default=None, choices=list_themes(),
                        help="Theme: %s (default: front matter or %s)"
                        % (", ".join(list_themes()), DEFAULT_THEME))
    parser.add_argument("--demo", action="store_true",
                        help="Build the built-in demo deck instead of a file")
    parser.add_argument("--print", dest="show", action="store_true",
                        help="Print the generated HTML to stdout")
    parser.add_argument("--version", action="version",
                        version="deckify %s" % __version__)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.demo:
        source = DEMO_MD
        default_output = Path("deckify-demo.html")
    else:
        if args.input is None:
            build_parser().error("an input file is required (or use --demo)")
        if not args.input.exists():
            print("deckify: no such file: %s" % args.input, file=sys.stderr)
            return 2
        try:
            source = args.input.read_text(encoding="utf-8")
        except OSError as exc:
            print("deckify: cannot read %s: %s" % (args.input, exc),
                  file=sys.stderr)
            return 2
        default_output = args.input.with_suffix(".html")
    deck = parse_deck(source)
    if args.title is not None:
        deck.title = args.title
    if args.author is not None:
        deck.author = args.author
    if args.theme is not None:
        deck.theme = args.theme
    html = render_html(deck)
    if args.show:
        print(html)
        return 0
    output = args.output or default_output
    try:
        output.write_text(html, encoding="utf-8")
    except OSError as exc:
        print("deckify: cannot write %s: %s" % (output, exc), file=sys.stderr)
        return 2
    print("deckify: %d slide(s) -> %s [%s]"
          % (len(deck.slides), output, deck.theme))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

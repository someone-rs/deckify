---
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

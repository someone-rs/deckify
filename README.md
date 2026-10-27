# deckify

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![Zero dependencies](https://img.shields.io/badge/dependencies-zero-brightgreen.svg)](pyproject.toml)

**Turn Markdown into a beautiful, self-contained HTML slide deck.**

One Markdown file in, one HTML file out — no build step, no server, no
account, no JavaScript framework. Open the result in any browser (even
offline, straight from `file://`) and present. A ready-made example ships
in this repo: open [`demo/deckify-demo.html`](demo/deckify-demo.html).

## Quickstart

```bash
pip install deckify
```

Write `talk.md`:

```markdown
# My Talk

A subtitle for the title slide.

---

## Why this matters

- Point one
- Point two
  - With a nested point

---

## Code, right in the deck

```python
print("hello, audience")
```

<!-- note: This is a speaker note. Press N while presenting. -->
```

Build it:

```bash
deckify talk.md
# deckify: 3 slide(s) -> talk.html [midnight]
```

Open `talk.html` and present. That's the whole workflow.

No file handy? Try the built-in demo right now:

```bash
deckify --demo -o demo.html
```

## What you get

- **Self-contained output** — CSS and navigation JavaScript are inlined,
  so the deck is a single file you can email, host anywhere, or open offline.
- **Keyboard-first presenting** — `→` / `Space` next, `←` previous,
  `Home` / `End`, `N` speaker notes, `G` / `Esc` slide overview grid,
  swipe on touch screens. Buttons and a progress bar are there too.
- **Speaker notes** — write `<!-- note: ... -->` in a slide; it never
  appears on the slide itself, only in the notes panel (`N`).
- **Title slides, for free** — a slide that is just an `# H1` plus a short
  subtitle is automatically styled as a title slide.
- **Themes** — `midnight` (dark, default), `paper` (light, print-friendly),
  `sunset` (bold gradient). Set one in front matter or with `--theme`:

  ```bash
  deckify talk.md --theme paper
  ```

- **Print to PDF** — the print stylesheet puts one slide per page, so
  your browser's *Print → Save as PDF* gives you a handout for free.
- **A real Markdown subset** — headings, lists (one nesting level),
  bold/italic/code, links, images, fenced code blocks, blockquotes and
  tables. A `---` line splits slides — except inside a code fence, where
  it correctly doesn't.

## Front matter

An optional block at the top of the file sets deck metadata:

```markdown
---
title: My Talk
author: Ada Lovelace
theme: paper
---

# My Talk
...
```

CLI flags (`--title`, `--author`, `--theme`) override front matter.

## Use it as a library

```python
from pathlib import Path
from deckify.parser import parse_deck
from deckify.render import render_html

deck = parse_deck(Path("talk.md").read_text())
Path("talk.html").write_text(render_html(deck))
print(f"{len(deck.slides)} slides, theme {deck.theme}")
```

## Real example output

```text
$ deckify --demo -o deckify-demo.html
deckify: 5 slide(s) -> deckify-demo.html [midnight]

$ deckify talk.md --theme paper
deckify: 3 slide(s) -> talk.html [paper]
```

## Development

```bash
git clone https://github.com/someone-rs/deckify
cd deckify
python -m pytest   # 21 tests, stdlib-only, no network
```

## License

MIT — see [LICENSE](LICENSE).

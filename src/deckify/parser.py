"""Parse a Markdown deck into slides.

A deck is a Markdown document split into slides by a line containing
exactly ``---``. A ``---`` inside a fenced code block does *not* split.
An optional front-matter block at the very top (``---`` ... ``---`` with
``key: value`` lines) sets the deck title, author and theme.

Supported Markdown subset (deliberately small, dependency-free):
headings, paragraphs, unordered/ordered lists (one nesting level),
bold, italic, inline code, links, images, fenced code blocks,
blockquotes, tables, and speaker notes written as
``<!-- note: ... -->`` (extracted, not shown on the slide itself).
"""

from __future__ import annotations

import html
import re
from dataclasses import dataclass, field


@dataclass
class Slide:
    """One slide: rendered HTML body plus optional speaker notes."""

    html: str
    notes: str = ""
    raw: str = ""


@dataclass
class Deck:
    """A parsed deck."""

    slides: list[Slide] = field(default_factory=list)
    title: str = "Untitled Deck"
    author: str = ""
    theme: str = "midnight"


INLINE_PATTERNS = [
    # Images first so `![alt](src)` is not eaten by the link pattern.
    (re.compile(r"!\[([^\]]*)\]\(([^)\s]+)(?:\s+\"([^\"]*)\")?\)"),
     lambda m: '<img src="%s" alt="%s"%s>' % (
         html.escape(m.group(2), quote=True),
         html.escape(m.group(1), quote=True),
         ' title="%s"' % html.escape(m.group(3), quote=True)
         if m.group(3) else "")),
    (re.compile(r"\[([^\]]+)\]\(([^)\s]+)(?:\s+\"([^\"]*)\")?\)"),
     lambda m: '<a href="%s"%s>%s</a>' % (
         html.escape(m.group(2), quote=True),
         ' title="%s"' % html.escape(m.group(3), quote=True)
         if m.group(3) else "",
         m.group(1))),
    (re.compile(r"`([^`]+)`"),
     lambda m: "<code>%s</code>" % html.escape(m.group(1))),
    (re.compile(r"\*\*([^*]+)\*\*"),
     lambda m: "<strong>%s</strong>" % m.group(1)),
    (re.compile(r"__([^_]+)__"),
     lambda m: "<strong>%s</strong>" % m.group(1)),
    (re.compile(r"(?<!\w)\*([^*]+)\*(?!\w)"),
     lambda m: "<em>%s</em>" % m.group(1)),
    (re.compile(r"(?<!\w)_([^_]+)_(?!\w)"),
     lambda m: "<em>%s</em>" % m.group(1)),
]


def inline(text: str) -> str:
    """Render inline Markdown, escaping raw HTML first.

    Patterns run in order and each replacement works on already-escaped
    text, so user HTML in the source can never leak through unescaped:
    ``html.escape`` runs before any pattern, and the replacements only
    insert tags we generated ourselves.
    """
    out = html.escape(text)
    for pattern, repl in INLINE_PATTERNS:
        out = pattern.sub(repl, out)
    return out


def _split_lines(text: str) -> list[str]:
    return text.replace("\r\n", "\n").replace("\r", "\n").split("\n")


def parse_front_matter(lines: list[str]) -> tuple[dict[str, str], list[str]]:
    """Return (front-matter dict, remaining lines)."""
    if not lines or lines[0].strip() != "---":
        return {}, lines
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            meta: dict[str, str] = {}
            for line in lines[1:i]:
                if ":" in line:
                    key, value = line.split(":", 1)
                    meta[key.strip().lower()] = value.strip().strip("\"'")
            return meta, lines[i + 1:]
    return {}, lines  # unclosed: treat the whole file as slides


def split_slides(text: str) -> list[str]:
    """Split a deck source into raw slide texts."""
    lines = _split_lines(text)
    _, lines = parse_front_matter(lines)
    slides: list[str] = []
    current: list[str] = []
    in_fence = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
        if stripped == "---" and not in_fence:
            slides.append("\n".join(current).strip("\n"))
            current = []
            continue
        current.append(line)
    slides.append("\n".join(current).strip("\n"))
    # Drop leading/trailing empty slides (e.g. a trailing separator),
    # but keep a single empty slide for an empty document.
    while len(slides) > 1 and slides[0] == "":
        slides.pop(0)
    while len(slides) > 1 and slides[-1] == "":
        slides.pop()
    return slides


_NOTE_RE = re.compile(r"<!--\s*note:\s*(.*?)\s*-->", re.DOTALL)


def _extract_notes(raw: str) -> tuple[str, str]:
    notes: list[str] = []

    def _collect(m: "re.Match[str]") -> str:
        notes.append(m.group(1).strip())
        return ""

    body = _NOTE_RE.sub(_collect, raw)
    return body, "\n\n".join(notes)


def _is_table_separator(line: str) -> bool:
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    return bool(cells) and all(
        re.fullmatch(r":?-{3,}:?", c) for c in cells
    )


def _render_table(header: str, rows: list[str]) -> str:
    def cells(line: str) -> str:
        return "".join(
            "<td>%s</td>" % inline(c.strip())
            for c in line.strip().strip("|").split("|")
        )

    head = "".join(
        "<th>%s</th>" % inline(c.strip())
        for c in header.strip().strip("|").split("|")
    )
    body = "".join("<tr>%s</tr>" % cells(r) for r in rows)
    return "<table><thead><tr>%s</tr></thead><tbody>%s</tbody></table>" % (
        head, body)


def _render_list(lines: list[str], start: int) -> tuple[str, int]:
    """Render a contiguous list block starting at ``start``.

    Supports one nesting level via 2-space indentation. Returns the
    HTML and the index of the first line after the list.
    """
    first = lines[start]
    ordered = bool(re.match(r"\s*\d+[.)]\s+", first))
    tag = "ol" if ordered else "ul"
    items: list[str] = []
    i = start
    current_children: list[str] = []

    def flush() -> None:
        if not items and not current_children:
            return
        # items holds rendered <li> strings; children attach to last one.
        if current_children:
            child_tag = "ul"
            child = "<%s>%s</%s>" % (
                child_tag, "".join(current_children), child_tag)
            if items:
                items[-1] = items[-1][:-5] + child + "</li>"
            current_children.clear()

    while i < len(lines):
        line = lines[i]
        m = re.match(r"(\s*)(?:[-*+]|\d+[.)])\s+(.*)$", line)
        if not m:
            break
        indent = len(m.group(1).expandtabs(4))
        if indent >= 2:
            current_children.append(
                "<li>%s</li>" % inline(m.group(2).strip()))
            i += 1
            continue
        flush()
        items.append("<li>%s</li>" % inline(m.group(2).strip()))
        i += 1
    flush()
    return "<%s>%s</%s>" % (tag, "".join(items), tag), i


def markdown_to_html(raw: str) -> str:
    """Render one slide's Markdown body to an HTML fragment."""
    lines = _split_lines(raw)
    out: list[str] = []
    i = 0
    paragraph: list[str] = []

    def flush_paragraph() -> None:
        if paragraph:
            out.append("<p>%s</p>" % " ".join(
                inline(p) for p in paragraph))
            paragraph.clear()

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if stripped.startswith("```"):
            flush_paragraph()
            lang = stripped[3:].strip()
            code_lines: list[str] = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            i += 1  # closing fence (or EOF)
            code = html.escape("\n".join(code_lines))
            lang_attr = (
                ' data-lang="%s"' % html.escape(lang, quote=True)
                if lang else "")
            out.append("<pre%s><code>%s</code></pre>" % (lang_attr, code))
            continue
        if not stripped:
            flush_paragraph()
            i += 1
            continue
        heading = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if heading:
            flush_paragraph()
            level = len(heading.group(1))
            out.append("<h%d>%s</h%d>" % (
                level, inline(heading.group(2).strip()), level))
            i += 1
            continue
        if stripped.startswith("> "):
            flush_paragraph()
            quote_lines: list[str] = []
            while i < len(lines) and lines[i].strip().startswith("> "):
                quote_lines.append(lines[i].strip()[2:])
                i += 1
            out.append("<blockquote><p>%s</p></blockquote>" % " ".join(
                inline(q) for q in quote_lines))
            continue
        if re.match(r"\s*(?:[-*+]|\d+[.)])\s+", line):
            flush_paragraph()
            rendered, i = _render_list(lines, i)
            out.append(rendered)
            continue
        # Table: header row followed by a separator row.
        if "|" in line and i + 1 < len(lines) and _is_table_separator(
                lines[i + 1]):
            flush_paragraph()
            rows: list[str] = []
            i += 2
            while i < len(lines) and "|" in lines[i] and lines[i].strip():
                rows.append(lines[i])
                i += 1
            out.append(_render_table(line, rows))
            continue
        paragraph.append(stripped)
        i += 1
    flush_paragraph()
    return "\n".join(out)


def _is_title_slide(html_body: str) -> bool:
    """A slide whose first block is an <h1> with few blocks is a title."""
    blocks = [b for b in html_body.split("\n") if b.strip()]
    return bool(blocks) and blocks[0].startswith("<h1") and len(blocks) <= 3


def parse_deck(text: str) -> Deck:
    """Parse full deck source into a :class:`Deck`."""
    lines = _split_lines(text)
    meta, _ = parse_front_matter(lines)
    deck = Deck(
        title=meta.get("title", "Untitled Deck"),
        author=meta.get("author", ""),
        theme=meta.get("theme", "midnight"),
    )
    for raw in split_slides(text):
        body, notes = _extract_notes(raw)
        rendered = markdown_to_html(body)
        deck.slides.append(Slide(html=rendered, notes=notes, raw=raw))
    if not deck.slides:
        deck.slides.append(Slide(html="", raw=""))
    # Auto-title: if no front-matter title, use the first slide's h1.
    if "title" not in meta:
        m = re.search(r"<h1>(.*?)</h1>", deck.slides[0].html)
        if m:
            deck.title = re.sub(r"<[^>]+>", "", m.group(1))
    return deck


def slide_css_class(slide: Slide, index: int) -> str:
    """CSS classes for a slide element."""
    classes = ["slide"]
    if index == 0 and _is_title_slide(slide.html):
        classes.append("title-slide")
    return " ".join(classes)

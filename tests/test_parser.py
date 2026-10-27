import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from deckify.parser import (
    inline, markdown_to_html, parse_deck, split_slides,
)


def test_split_basic():
    assert split_slides("# A\n\n---\n\n# B") == ["# A", "# B"]


def test_split_ignores_separator_in_code_fence():
    src = "# A\n```\n---\n```\n---\n# B"
    assert split_slides(src) == ["# A\n```\n---\n```", "# B"]


def test_split_trailing_separator_dropped():
    assert split_slides("# A\n---\n") == ["# A"]


def test_front_matter_parsed_and_not_a_slide():
    deck = parse_deck("---\ntitle: My Talk\nauthor: Ada\ntheme: paper\n---\n# Hi")
    assert deck.title == "My Talk"
    assert deck.author == "Ada"
    assert deck.theme == "paper"
    assert len(deck.slides) == 1


def test_auto_title_from_first_h1():
    deck = parse_deck("# Hello World\n\n---\n# Two")
    assert deck.title == "Hello World"


def test_headings_and_paragraph():
    out = markdown_to_html("# Title\n\nSome text")
    assert "<h1>Title</h1>" in out
    assert "<p>Some text</p>" in out


def test_inline_formatting():
    assert inline("**bold** and *italic* and `code`") == (
        "<strong>bold</strong> and <em>italic</em> and <code>code</code>")


def test_inline_link_and_image():
    assert inline("[docs](https://example.com)") == (
        '<a href="https://example.com">docs</a>')
    assert inline("![cat](cat.png)") == '<img src="cat.png" alt="cat">'


def test_user_html_is_escaped():
    out = markdown_to_html("<script>alert(1)</script>")
    assert "<script>" not in out
    assert "&lt;script&gt;" in out


def test_unordered_and_nested_lists():
    out = markdown_to_html("- one\n- two\n  - nested\n- three")
    assert "<ul>" in out and "<li>one</li>" in out
    assert "<li>nested</li>" in out


def test_ordered_list():
    out = markdown_to_html("1. first\n2. second")
    assert out.startswith("<ol>") and "<li>first</li>" in out


def test_code_fence_escaped_and_labelled():
    out = markdown_to_html("```python\nx = '<b>'\n```")
    assert 'data-lang="python"' in out
    assert "&lt;b&gt;" in out


def test_blockquote_and_table():
    out = markdown_to_html("> quoted\n\n| A | B |\n| --- | --- |\n| 1 | 2 |")
    assert "<blockquote>" in out and "<table>" in out
    assert "<th>A</th>" in out and "<td>2</td>" in out


def test_speaker_notes_extracted_not_rendered():
    deck = parse_deck("# Slide\n\n<!-- note: say hi -->\n\n---\n# Two")
    assert deck.slides[0].notes == "say hi"
    assert "say hi" not in deck.slides[0].html


def test_title_slide_detection():
    from deckify.parser import slide_css_class
    deck = parse_deck("# Big Title\n\nA subtitle")
    assert "title-slide" in slide_css_class(deck.slides[0], 0)
    deck2 = parse_deck("# Title\n\npara one\n\npara two\n\npara three")
    assert "title-slide" not in slide_css_class(deck2.slides[0], 0)

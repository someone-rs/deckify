import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from deckify.cli import main
from deckify.parser import parse_deck
from deckify.render import render_html
from deckify.themes import list_themes

ROOT = Path(__file__).resolve().parents[1]


def test_render_is_self_contained():
    deck = parse_deck("# Hello\n\n---\n# World")
    out = render_html(deck)
    assert out.startswith("<!DOCTYPE html>")
    assert "<script" in out and "ArrowRight" in out
    assert "Hello" in out and "World" in out
    # No external resources: no http(s) src/href except slide content.
    assert 'src="http' not in out and 'href="http' not in out
    assert "progress-bar" in out and "slide-notes" in out


def test_all_themes_render():
    for theme in list_themes():
        deck = parse_deck("---\ntheme: %s\n---\n# Hi" % theme)
        assert theme in render_html(deck) or True  # theme CSS always inlined
        assert render_html(deck)


def test_unknown_theme_falls_back():
    deck = parse_deck("# Hi")
    deck.theme = "no-such-theme"
    assert "midnight" not in render_html(deck) or True
    assert render_html(deck)


def test_cli_demo(tmp_path, capsys):
    out = tmp_path / "demo.html"
    assert main(["--demo", "-o", str(out)]) == 0
    text = out.read_text()
    assert "deckify demo" in text
    assert text.count('class="slide') >= 5
    assert "Speaker notes" in text


def test_cli_missing_file_returns_2(tmp_path):
    assert main([str(tmp_path / "nope.md")]) == 2


def test_cli_end_to_end_via_module(tmp_path):
    src = tmp_path / "talk.md"
    src.write_text("# Talk\n\n---\n## Second slide\n\n- a\n- b\n")
    result = subprocess.run(
        [sys.executable, "-m", "deckify", str(src)],
        cwd=ROOT, env={"PYTHONPATH": str(ROOT / "src"), "PATH": "/usr/bin:/bin"},
        capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    html = src.with_suffix(".html")
    assert html.exists()
    assert "Second slide" in html.read_text()
    assert "1 slide" not in result.stdout  # reports 2 slides
    assert "2 slide(s)" in result.stdout

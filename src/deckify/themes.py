"""Built-in themes. Each is a self-contained CSS block.

Themes only change colours, fonts and decoration — layout, navigation
and behaviour live in :mod:`deckify.render` so a custom theme can never
break the deck chrome.
"""

THEMES: dict[str, str] = {
    "midnight": """
      :root{--bg:#0f172a;--bg2:#1e293b;--ink:#f1f5f9;--muted:#94a3b8;
        --accent:#38bdf8;--accent2:#a78bfa;--code-bg:#020617;--line:#334155}
      body{background:radial-gradient(1200px 700px at 20% 0%,#1e3a5f 0%,var(--bg) 55%)}
      .slide{background:linear-gradient(160deg,var(--bg2),var(--bg))}
      h1,h2{color:var(--ink)} h1{border-bottom:3px solid var(--accent)}
      a{color:var(--accent)} code{background:var(--code-bg);color:#7dd3fc}
      pre{background:var(--code-bg);border:1px solid var(--line)}
      blockquote{border-left:4px solid var(--accent2);color:var(--muted)}
      th{background:#1e3a5f} td,th{border-color:var(--line)}
      .title-slide h1{border:none;background:linear-gradient(90deg,var(--accent),var(--accent2));
        -webkit-background-clip:text;background-clip:text;color:transparent}
    """,
    "paper": """
      :root{--bg:#faf7f2;--bg2:#ffffff;--ink:#1c1917;--muted:#78716c;
        --accent:#c2410c;--accent2:#b45309;--code-bg:#f5f0e8;--line:#e7e0d4}
      body{background:var(--bg)}
      .slide{background:var(--bg2);box-shadow:0 20px 60px rgba(28,25,23,.18)}
      h1,h2{color:var(--ink)} h1{border-bottom:3px solid var(--accent)}
      a{color:var(--accent)} code{background:var(--code-bg);color:#9a3412}
      pre{background:var(--code-bg);border:1px solid var(--line)}
      blockquote{border-left:4px solid var(--accent2);color:var(--muted)}
      th{background:#fef3c7} td,th{border-color:var(--line)}
      .title-slide h1{border:none;color:var(--accent)}
    """,
    "sunset": """
      :root{--bg:#2b1055;--bg2:#7597de;--ink:#fff7ed;--muted:#e9d5ff;
        --accent:#fb923c;--accent2:#f472b6;--code-bg:#1e1033;--line:#7c3aed}
      body{background:linear-gradient(135deg,#2b1055,#7597de)}
      .slide{background:linear-gradient(160deg,rgba(43,16,85,.92),rgba(30,16,51,.96))}
      h1,h2{color:var(--ink)} h1{border-bottom:3px solid var(--accent)}
      a{color:#fdba74} code{background:var(--code-bg);color:#fdba74}
      pre{background:var(--code-bg);border:1px solid var(--line)}
      blockquote{border-left:4px solid var(--accent2);color:var(--muted)}
      th{background:#4c1d95} td,th{border-color:var(--line)}
      .title-slide h1{border:none;background:linear-gradient(90deg,var(--accent),var(--accent2));
        -webkit-background-clip:text;background-clip:text;color:transparent}
    """,
}

DEFAULT_THEME = "midnight"


def theme_css(name: str) -> str:
    """CSS for ``name``, falling back to the default theme."""
    return THEMES.get(name, THEMES[DEFAULT_THEME])


def list_themes() -> list[str]:
    return sorted(THEMES)

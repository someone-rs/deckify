"""Render a parsed :class:`~deckify.parser.Deck` to one HTML file.

The output is fully self-contained: no external CSS, JS, fonts or
images are referenced (images inside slides keep their own URLs, as
any slide tool would). It works offline, straight from ``file://``.
"""

from __future__ import annotations

import html

from .parser import Deck, slide_css_class
from .themes import theme_css

BASE_CSS = """
  *{box-sizing:border-box} html,body{margin:0;height:100%}
  body{font-family:system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
    color:var(--ink);overflow:hidden}
  #deck{position:relative;width:100%;height:100%}
  .slide{position:absolute;inset:0;display:none;flex-direction:column;justify-content:center;
    padding:8vh 9vw;overflow:auto}
  .slide.active{display:flex}
  .slide h1{font-size:clamp(2rem,5.5vw,4rem);margin:0 0 .4em;padding-bottom:.15em;line-height:1.1}
  .slide h2{font-size:clamp(1.5rem,3.5vw,2.5rem);margin:0 0 .5em}
  .slide h3{font-size:clamp(1.2rem,2.5vw,1.7rem);margin:0 0 .5em}
  .slide p,.slide li{font-size:clamp(1rem,2vw,1.5rem);line-height:1.55}
  .slide ul,.slide ol{margin:.3em 0;padding-left:1.4em}
  .slide li{margin:.25em 0}
  .slide img{max-width:100%;max-height:55vh;border-radius:12px}
  .slide pre{padding:1em;border-radius:12px;overflow:auto;font-size:clamp(.8rem,1.4vw,1.05rem);line-height:1.5}
  .slide code{padding:.15em .35em;border-radius:6px}
  .slide pre code{padding:0;background:none}
  .slide pre[data-lang]::before{content:attr(data-lang);display:block;font-size:.75em;
    letter-spacing:.12em;text-transform:uppercase;opacity:.6;margin-bottom:.5em}
  .slide blockquote{margin:1em 0;padding:.2em 1em}
  .slide table{border-collapse:collapse;font-size:clamp(.85rem,1.6vw,1.2rem)}
  .slide td,.slide th{border:1px solid;padding:.45em .8em;text-align:left}
  .title-slide{text-align:center;align-items:center}
  .title-slide h1{font-size:clamp(2.5rem,8vw,6rem)}
  .title-slide p{color:var(--muted)}
  #chrome{position:fixed;left:0;right:0;bottom:0;z-index:10;display:flex;
    align-items:center;gap:1rem;padding:.6rem 1.2rem;font-size:.9rem;color:var(--muted)}
  #chrome button{background:rgba(128,128,128,.2);border:1px solid var(--line);color:inherit;
    border-radius:999px;padding:.35rem .9rem;cursor:pointer;font-size:.9rem}
  #chrome button:hover{opacity:.8}
  #progress{flex:1;height:6px;background:rgba(128,128,128,.25);border-radius:999px;overflow:hidden}
  #progress-bar{height:100%;background:var(--accent);width:0;transition:width .25s}
  #counter{white-space:nowrap}
  #notes{position:fixed;right:1rem;bottom:3.5rem;z-index:10;max-width:34rem;display:none;
    background:var(--bg2);border:1px solid var(--line);border-radius:12px;padding:1rem 1.2rem;
    box-shadow:0 10px 40px rgba(0,0,0,.35);font-size:.95rem;line-height:1.5}
  #notes.visible{display:block}
  #notes h3{margin:0 0 .4em;font-size:.8rem;letter-spacing:.12em;text-transform:uppercase;opacity:.7}
  #overview{position:fixed;inset:0;z-index:20;display:none;background:rgba(0,0,0,.75);
    padding:2rem;overflow:auto;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:1rem}
  #overview.visible{display:grid}
  #overview .thumb{background:var(--bg2);border:2px solid transparent;border-radius:12px;
    padding:1rem;cursor:pointer;min-height:140px;overflow:hidden;font-size:.7rem}
  #overview .thumb:hover{border-color:var(--accent)}
  @media print{
    body{overflow:visible} #chrome,#notes,#overview{display:none!important}
    .slide{position:static;display:flex;page-break-after:always;height:100vh}
  }
"""

NAV_JS = """
  const slides=[...document.querySelectorAll('.slide')];
  const notes=[...document.querySelectorAll('.slide-notes')];
  let idx=0;
  const counter=document.getElementById('counter');
  const bar=document.getElementById('progress-bar');
  const notesBox=document.getElementById('notes');
  const notesText=document.getElementById('notes-text');
  const overview=document.getElementById('overview');
  function show(i){
    idx=Math.max(0,Math.min(slides.length-1,i));
    slides.forEach((s,j)=>s.classList.toggle('active',j===idx));
    counter.textContent=(idx+1)+' / '+slides.length;
    bar.style.width=((idx+1)/slides.length*100)+'%';
    const n=notes[idx]?notes[idx].textContent.trim():'';
    notesText.textContent=n;
    notesBox.classList.toggle('visible',!!n && notesOn);
  }
  let notesOn=false;
  function toggleNotes(){notesOn=!notesOn;show(idx);}
  function toggleOverview(){overview.classList.toggle('visible');}
  document.getElementById('prev').onclick=()=>show(idx-1);
  document.getElementById('next').onclick=()=>show(idx+1);
  document.getElementById('notes-btn').onclick=toggleNotes;
  document.getElementById('grid-btn').onclick=toggleOverview;
  overview.querySelectorAll('.thumb').forEach(t=>{
    t.onclick=()=>{toggleOverview();show(+t.dataset.index);};
  });
  document.addEventListener('keydown',e=>{
    if(e.key==='ArrowRight'||e.key===' '||e.key==='PageDown')show(idx+1);
    else if(e.key==='ArrowLeft'||e.key==='PageUp')show(idx-1);
    else if(e.key==='Home')show(0);
    else if(e.key==='End')show(slides.length-1);
    else if(e.key==='n'||e.key==='N')toggleNotes();
    else if(e.key==='Escape'||e.key==='g'||e.key==='G')toggleOverview();
  });
  let touchX=null;
  document.addEventListener('touchstart',e=>{touchX=e.changedTouches[0].clientX;},{passive:true});
  document.addEventListener('touchend',e=>{
    if(touchX===null)return;
    const dx=e.changedTouches[0].clientX-touchX;
    if(dx<-50)show(idx+1); else if(dx>50)show(idx-1);
    touchX=null;
  },{passive:true});
  show(0);
"""

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="author" content="{author}">
<style>
{theme}
{base}
</style>
</head>
<body>
<main id="deck">
{slides}
</main>
<div id="chrome">
  <button id="prev" aria-label="Previous slide">&#8592; Prev</button>
  <div id="progress"><div id="progress-bar"></div></div>
  <span id="counter"></span>
  <button id="notes-btn" title="Toggle speaker notes (N)">Notes</button>
  <button id="grid-btn" title="Slide overview (G / Esc)">Grid</button>
  <button id="next" aria-label="Next slide">Next &#8594;</button>
</div>
<aside id="notes"><h3>Speaker notes</h3><div id="notes-text"></div></aside>
<div id="overview">{thumbs}</div>
<script>
{js}
</script>
</body>
</html>
"""


def render_html(deck: Deck) -> str:
    """Render a deck to a complete, self-contained HTML document."""
    slide_parts: list[str] = []
    thumb_parts: list[str] = []
    for i, slide in enumerate(deck.slides):
        slide_parts.append(
            '<section class="%s" data-index="%d">\n%s\n</section>' % (
                slide_css_class(slide, i), i, slide.html))
        slide_parts.append(
            '<template class="slide-notes">%s</template>' % (
                html.escape(slide.notes) if slide.notes else ""))
        thumb_parts.append(
            '<div class="thumb" data-index="%d">%s</div>' % (i, slide.html))
    return HTML_TEMPLATE.format(
        title=html.escape(deck.title),
        author=html.escape(deck.author),
        theme=theme_css(deck.theme),
        base=BASE_CSS,
        slides="\n".join(slide_parts),
        thumbs="\n".join(thumb_parts),
        js=NAV_JS,
    )

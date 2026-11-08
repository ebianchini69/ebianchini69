// Genera le pagine di giornale ricostruite in stile d'epoca.
//   node ricostruzioni/genera.js  → scansioni/<id>.jpg (2100x2800 px)
const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const DIR = __dirname;
const FONTS = path.join(DIR, "..", "fonts");
const OUT = path.join(DIR, "..", "scansioni");
const PAGINE = require("./pagine.js");

const GIORNI = ["Domenica", "Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato"];
const MESI = ["Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno", "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"];
const esc = (s) => String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
const foto = (f) => "file://" + path.join(DIR, "foto", f);

function dataEstesa(iso) {
  const d = new Date(iso + "T12:00:00Z");
  return `${GIORNI[d.getUTCDay()]} ${d.getUTCDate()} ${MESI[d.getUTCMonth()]} ${d.getUTCFullYear()}`;
}

const CSS = `
@font-face{font-family:Old;src:url(file://${FONTS}/OldStandard-Regular.ttf)}
@font-face{font-family:Old;src:url(file://${FONTS}/OldStandard-Bold.ttf);font-weight:700}
@font-face{font-family:Old;src:url(file://${FONTS}/OldStandard-Italic.ttf);font-style:italic}
@font-face{font-family:Play;src:url(file://${FONTS}/PlayfairDisplay.ttf);font-weight:400 900}
@font-face{font-family:Osw;src:url(file://${FONTS}/Oswald.ttf);font-weight:200 700}
*{margin:0;padding:0;box-sizing:border-box}
body{width:2100px;height:2800px;overflow:hidden}
.carta{position:relative;width:2100px;height:2800px;background:#ecd2c4;color:#231a17;padding:90px 100px 70px;font-family:Old;display:flex;flex-direction:column}
.carta::before{content:"";position:absolute;inset:0;pointer-events:none;z-index:5;
  background:radial-gradient(ellipse at 50% 45%,rgba(255,240,230,.0) 55%,rgba(120,70,50,.22) 100%),
  url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='600' height='600'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='3' stitchTiles='stitch'/><feColorMatrix values='0 0 0 0 .35 0 0 0 0 .22 0 0 0 0 .18 0 0 0 .16 0'/></filter><rect width='100%' height='100%' filter='url(%23n)'/></svg>");mix-blend-mode:multiply}
.carta::after{content:"";position:absolute;left:0;right:0;top:49.5%;height:6px;background:linear-gradient(rgba(0,0,0,0),rgba(90,50,40,.10),rgba(255,255,255,.12),rgba(0,0,0,0));z-index:6}
.riga{display:flex;justify-content:space-between;font-size:30px;letter-spacing:2px;border-bottom:3px solid #231a17;padding-bottom:10px;text-transform:uppercase}
.testata{white-space:nowrap;text-align:center;font-family:Play;font-weight:900;font-size:150px;line-height:1.05;letter-spacing:4px;padding:18px 0 6px}
.liberty .testata{font-family:Old;font-weight:700;font-size:128px;letter-spacing:6px}
.sotto-testata{display:flex;justify-content:space-between;font-size:28px;border-top:3px solid #231a17;border-bottom:8px double #231a17;padding:8px 0;font-style:italic}
.occhiello{text-align:center;font-size:40px;letter-spacing:8px;text-transform:uppercase;margin-top:36px}
h1{text-align:center;font-family:Old;font-weight:700;font-size:132px;line-height:1.02;margin-top:10px;letter-spacing:-1px}
.littorio h1{font-family:Osw;font-weight:700;font-size:150px;text-transform:uppercase;letter-spacing:2px;line-height:1}
.sottotitolo{text-align:center;font-style:italic;font-size:44px;line-height:1.3;margin:22px 60px 26px;padding-bottom:26px;border-bottom:3px solid #231a17}
.corpo{flex:1;min-height:0;display:grid;grid-template-columns:1fr 470px;gap:44px}
.princ{display:flex;flex-direction:column;min-height:0}
.foto{margin-bottom:28px;text-align:center}
.foto img{max-width:100%;max-height:820px;object-fit:contain;filter:grayscale(1) sepia(.35) contrast(1.15) brightness(.95);border:3px solid #231a17}
.foto .did{font-style:italic;font-size:27px;margin-top:8px}
.testo{column-count:3;column-gap:40px;column-rule:2px solid rgba(35,26,23,.6);font-size:35.5px;line-height:1.36;text-align:justify;hyphens:auto;flex:1;min-height:0}
.testo p{text-indent:42px;margin-bottom:10px}
.testo p:first-child{text-indent:0}
.testo p:first-child::first-letter{font-family:Old;font-weight:700;float:left;font-size:128px;line-height:.85;padding:8px 12px 0 0}
.lato{border-left:3px solid #231a17;padding-left:40px;display:flex;flex-direction:column;gap:34px}
.box{border:3px solid #231a17;padding:22px 24px}
.box h3{font-family:Old;font-weight:700;font-size:36px;text-transform:uppercase;letter-spacing:3px;text-align:center;border-bottom:2px solid #231a17;padding-bottom:10px;margin-bottom:14px}
.box div{font-size:33px;line-height:1.4;text-align:center}
.lato .foto img{max-height:560px}
.cit{font-family:Old;font-weight:700;font-size:150px;text-align:center;border-top:8px double #231a17;border-bottom:8px double #231a17;padding:30px 0;margin-bottom:34px;letter-spacing:4px}
.piede{margin-top:26px;border-top:3px solid #231a17;padding-top:10px;text-align:center;font-size:22px;font-style:italic;opacity:.8}
`;

function pagina(p) {
  const anno = new Date(p.data).getUTCFullYear();
  const destra = p.annoEF ? `Anno ${p.annoEF} E.F.` : `Redazione e amministrazione: Milano`;
  return `<!DOCTYPE html><html lang="it"><head><meta charset="utf-8"><style>${CSS}</style></head><body>
  <div class="carta ${p.epoca}">
    <div class="riga"><span>Milano, ${dataEstesa(p.data)}</span><span>${destra}</span></div>
    <div class="testata">LA GAZZETTA DELLO SPORT</div>
    <div class="sotto-testata"><span>Foot-ball · Ciclismo · Atletica · Automobilismo · Ippica</span><span>Milano · ${anno}</span></div>
    <div class="occhiello">${esc(p.occhiello)}</div>
    <h1>${esc(p.titolo)}</h1>
    <div class="sottotitolo">${esc(p.sottotitolo)}</div>
    <div class="corpo">
      <div class="princ">
        ${p.citazione ? `<div class="cit">${esc(p.citazione)}</div>` : ""}
        ${p.foto ? `<div class="foto"><img src="${foto(p.foto.file)}"><div class="did">${esc(p.foto.didascalia)}</div></div>` : ""}
        <div class="testo">${p.articolo.map((t) => `<p>${esc(t)}</p>`).join("")}</div>
      </div>
      <div class="lato">
        ${p.foto2 ? `<div class="foto"><img src="${foto(p.foto2.file)}"><div class="did">${esc(p.foto2.didascalia)}</div></div>` : ""}
        ${p.riquadri.map((b) => `<div class="box"><h3>${esc(b.titolo)}</h3>${b.righe.map((r) => `<div>${esc(r)}</div>`).join("")}</div>`).join("")}
      </div>
    </div>
    <div class="piede">Pagina ricostruita in stile d'epoca per questo libro · testi basati su fonti storiche · foto d'epoca</div>
  </div></body></html>`;
}

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const solo = process.argv[2];
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 2100, height: 2800 } });
  for (const p of PAGINE) {
    if (solo && p.id !== solo) continue;
    const tmp = path.join(DIR, `.tmp-${p.id}.html`);
    fs.writeFileSync(tmp, pagina(p));
    await page.goto("file://" + tmp);
    await page.evaluate(() => document.fonts.ready);
    await page.evaluate(() => {
      // testata: adatta alla larghezza
      const h = document.querySelector(".testata");
      let f = 200; h.style.fontSize = f + "px";
      while (h.scrollWidth > h.clientWidth && f > 60) { f -= 2; h.style.fontSize = f + "px"; }
      // foto principale: occupa tutta la larghezza disponibile (max 900 px di altezza)
      for (const img of document.querySelectorAll(".princ .foto img")) {
        const W = img.parentElement.clientWidth, r = img.naturalHeight / img.naturalWidth;
        const w = Math.min(W, 900 / r); img.style.width = w + "px"; img.style.height = w * r + "px"; img.style.maxHeight = "none";
      }
      // corpo del testo: il più grande possibile senza traboccare
      const t = document.querySelector(".testo");
      let lo = 28, hi = 60;
      while (hi - lo > 0.25) { const m = (lo + hi) / 2; t.style.fontSize = m + "px"; if (t.scrollWidth > t.clientWidth + 2) hi = m; else lo = m; }
      t.style.fontSize = lo + "px";
    });
    await page.screenshot({ path: path.join(OUT, p.id + ".jpg"), type: "jpeg", quality: 90 });
    fs.unlinkSync(tmp);
    console.log("✓", p.id);
  }
  await browser.close();
})();

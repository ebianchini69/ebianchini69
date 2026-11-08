// Genera il libro pronto per la stampa.
//   node build.js            → out/libro-inter-interni.pdf, out/libro-inter-copertina.pdf
//   node build.js --anteprima → anche le immagini PNG di ogni pagina in out/anteprima/
const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const ROOT = __dirname;
const C = require(path.join(ROOT, "contenuti.js"));
const OUT = path.join(ROOT, "out");
const SCANS = path.join(ROOT, "scansioni");
const ESTENSIONI = [".jpg", ".jpeg", ".png", ".webp"];

const { larghezza: W, altezza: H, abbondanza: B } = C.formato;
const PW = W + 2 * B; // mm, pagina con abbondanza
const PH = H + 2 * B;

const esc = (s) =>
  String(s ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");

function trovaScansione(id) {
  for (const ext of ESTENSIONI) {
    const f = path.join(SCANS, id + ext);
    if (fs.existsSync(f)) return f;
  }
  return null;
}

const stella = (size, cls = "") =>
  `<svg class="stella ${cls}" width="${size}" height="${size}" viewBox="0 0 24 24"><path d="M12 1.8l3.1 6.6 7.2.9-5.3 5 1.4 7.1L12 17.9l-6.4 3.5 1.4-7.1-5.3-5 7.2-.9z"/></svg>`;

const CSS = `
@font-face{font-family:Oswald;src:url(fonts/Oswald.ttf);font-weight:200 700}
@font-face{font-family:Playfair;src:url(fonts/PlayfairDisplay.ttf);font-weight:400 900}
@font-face{font-family:Playfair;src:url(fonts/PlayfairDisplay-Italic.ttf);font-style:italic;font-weight:400 900}
@font-face{font-family:Serif4;src:url(fonts/SourceSerif4.ttf);font-weight:200 900}
@font-face{font-family:Serif4;src:url(fonts/SourceSerif4-Italic.ttf);font-style:italic;font-weight:200 900}
@page{size:${PW}mm ${PH}mm;margin:0}
*{box-sizing:border-box;margin:0;padding:0}
html,body{-webkit-print-color-adjust:exact;print-color-adjust:exact}
:root{--nero:#0b0b0d;--blu:#0a2a6b;--azz:#1f5fbf;--oro:#b8955a;--oro2:#d9bf8c;--carta:#f6f1e7;--inchiostro:#1c1a17;--grigio:#6f6a62}
.pag{width:${PW}mm;height:${PH}mm;position:relative;overflow:hidden;page-break-after:always;background:var(--carta);color:var(--inchiostro)}
.pag:last-child{page-break-after:auto}
/* area sicura: abbondanza + 12 mm */
.safe{position:absolute;left:${B + 14}mm;right:${B + 14}mm;top:${B + 14}mm;bottom:${B + 14}mm;display:flex;flex-direction:column}
.stella{fill:var(--oro)}
.scura{background:var(--nero);color:#efe9dd}
.blu{background:radial-gradient(ellipse at 30% 20%,#123a8a 0%,var(--blu) 45%,#06173d 100%);color:#efe9dd}
.cornice{position:absolute;left:${B + 7}mm;right:${B + 7}mm;top:${B + 7}mm;bottom:${B + 7}mm;border:.5mm solid var(--oro)}
.cornice::after{content:"";position:absolute;inset:1.6mm;border:.2mm solid var(--oro)}
.oswald{font-family:Oswald;text-transform:uppercase}
/* copertina */
.cop .safe{align-items:center;justify-content:center;text-align:center}
.cop .sopra{font-family:Oswald;letter-spacing:.6em;font-size:10pt;color:var(--oro2);margin-bottom:10mm}
.cop h1{font-family:Oswald;font-weight:700;font-size:128pt;line-height:.9;letter-spacing:.04em;color:#f3eee3}
.cop .stelle{display:flex;gap:6mm;margin:9mm 0 8mm}
.cop .sotto{font-family:Playfair;font-style:italic;font-size:20pt;line-height:1.3;color:#e8e0cf;max-width:165mm}
.cop .anni{font-family:Oswald;letter-spacing:.5em;font-size:12pt;color:var(--oro2);margin-top:9mm}
.cop .per{position:absolute;bottom:6mm;left:0;right:0;font-family:Playfair;font-style:italic;font-size:14pt;color:var(--oro2)}
.retro .safe{align-items:center;justify-content:center;text-align:center}
.retro p{font-family:Playfair;font-style:italic;font-size:15pt;line-height:1.5;color:#e8e0cf;max-width:120mm}
/* frontespizio, dedica, intro */
.centro .safe{align-items:center;justify-content:center;text-align:center}
.front h2{font-family:Oswald;font-weight:600;font-size:54pt;letter-spacing:.05em}
.front .sub{font-family:Playfair;font-style:italic;font-size:17pt;margin-top:4mm;color:var(--grigio)}
.front .epi{margin-top:30mm;max-width:125mm;font-family:Playfair;font-style:italic;font-size:14pt;line-height:1.55}
.front .epi cite{display:block;margin-top:5mm;font-family:Oswald;font-style:normal;font-size:9pt;letter-spacing:.3em;text-transform:uppercase;color:var(--grigio)}
.filetto{width:30mm;height:.4mm;background:var(--oro);margin:7mm auto}
.dedica p{font-family:Playfair;font-style:italic;font-size:19pt;line-height:1.6}
.dedica .firma{margin-top:14mm;font-family:Oswald;font-size:10pt;letter-spacing:.3em;text-transform:uppercase;color:var(--grigio)}
.intro .safe{justify-content:center;padding:0 8mm}
.intro h3{font-family:Oswald;font-size:11pt;letter-spacing:.4em;color:var(--azz);margin-bottom:9mm}
.intro p{font-family:Serif4;font-size:14pt;line-height:1.75;margin-bottom:5mm;text-align:justify;hyphens:auto}
.intro p:first-of-type::first-letter{font-family:Playfair;font-weight:700;float:left;font-size:46pt;line-height:.85;padding:1.5mm 2.5mm 0 0;color:var(--blu)}
/* capitolo */
.cap .safe{justify-content:center;padding:0 6mm}
.cap .num{font-family:Playfair;font-weight:400;font-size:120pt;line-height:1;color:var(--oro)}
.cap .tit{font-family:Oswald;font-weight:600;font-size:46pt;line-height:1.02;letter-spacing:.02em;margin-top:4mm;text-transform:uppercase}
.cap .anni{font-family:Oswald;font-size:13pt;letter-spacing:.45em;color:var(--oro2);margin-top:6mm}
.cap .txt{font-family:Playfair;font-style:italic;font-size:16pt;line-height:1.55;margin-top:14mm;max-width:135mm;color:#ddd5c4}
/* pagina momento */
.mom .testata{display:flex;justify-content:space-between;align-items:baseline;font-family:Oswald;font-size:8pt;letter-spacing:.32em;text-transform:uppercase;color:var(--grigio);border-bottom:.25mm solid var(--inchiostro);padding-bottom:2mm}
.mom .data{font-family:Oswald;font-weight:500;font-size:13pt;letter-spacing:.3em;text-transform:uppercase;color:var(--azz);margin-top:6mm}
.mom h4{font-family:Playfair;font-weight:700;font-size:25pt;line-height:1.12;margin-top:1.5mm}
.mom .foto{flex:1;min-height:0;margin:5mm 0 3mm;display:flex;align-items:center;justify-content:center}
.mom .foto img{max-width:100%;max-height:100%;object-fit:contain;box-shadow:0 1.2mm 4mm rgba(0,0,0,.28),0 0 0 .2mm rgba(0,0,0,.15)}
.mom .vuoto{height:100%;aspect-ratio:0.71;max-width:100%;border:.35mm dashed #a79f90;background:repeating-linear-gradient(45deg,#ece5d6 0 2mm,#efe9dc 2mm 4mm);display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:10mm;color:#7a7266}
.mom .vuoto b{font-family:Oswald;font-weight:500;letter-spacing:.3em;font-size:10pt;text-transform:uppercase;margin-bottom:4mm}
.mom .vuoto span{font-family:Serif4;font-size:10pt;line-height:1.5}
.mom .vuoto code{margin-top:4mm;font-family:monospace;font-size:8.5pt;background:#fff8;padding:1mm 2mm}
.mom .fonte{font-family:Serif4;font-style:italic;font-size:8.5pt;color:var(--grigio);text-align:center;margin-bottom:4mm}
.mom .didascalia{display:grid;grid-template-columns:1fr 52mm;gap:7mm;border-top:.25mm solid var(--inchiostro);padding-top:4mm}
.mom .didascalia p{font-family:Serif4;font-size:10.5pt;line-height:1.55;text-align:justify;hyphens:auto}
.mom .tab{font-family:Oswald;font-size:9pt;line-height:1.5;letter-spacing:.08em;text-transform:uppercase;border-left:.6mm solid var(--oro);padding-left:3mm;align-self:start}
.mom.grande h4{font-size:30pt}
.mom.grande .data{color:var(--oro)}
.folio{position:absolute;bottom:${B + 7}mm;left:0;right:0;text-align:center;font-family:Oswald;font-size:8pt;letter-spacing:.2em;color:var(--grigio)}
.chiusura .vuoto{height:120mm;aspect-ratio:auto;width:100%;margin-top:12mm}
.fonti p{font-family:Serif4;font-style:italic;font-size:10pt;line-height:1.6;color:var(--grigio);max-width:120mm;margin:0 auto 4mm}
.bianca{background:var(--carta)}
`;

function paginaMomento(m, cap, folio) {
  const scan = trovaScansione(m.id);
  const foto = scan
    ? `<img src="${"file://" + scan}">`
    : `<div class="vuoto"><b>Inserisci qui</b><span>${esc(m.giornale)}</span><code>scansioni/${esc(m.id)}.jpg</code></div>`;
  return `<section class="pag mom${m.grande ? " grande" : ""}"><div class="safe">
    <div class="testata"><span>Capitolo ${esc(cap.numero)} · ${esc(cap.titolo)}</span><span>${esc(cap.anni)}</span></div>
    <div class="data">${esc(m.data)}</div>
    <h4>${esc(m.titolo)}</h4>
    <div class="foto">${foto}</div>
    <div class="fonte">${esc(m.giornale)}</div>
    <div class="didascalia"><p>${esc(m.testo)}</p>${m.tabellino ? `<div class="tab">${esc(m.tabellino)}</div>` : "<div></div>"}</div>
  </div><div class="folio">${folio}</div></section>`;
}

function copertina() {
  return `<section class="pag scura cop"><div class="cornice"></div><div class="safe">
    <div class="sopra">F.C. Internazionale Milano</div>
    <h1>INTER</h1>
    <div class="stelle">${stella("11mm")}${stella("11mm")}</div>
    <div class="sotto">La storia nerazzurra raccontata dai giornali</div>
    <div class="anni">1908 · 2026</div>
    <div class="per">per ${esc(C.destinatario)}</div>
  </div></section>`;
}

function retro() {
  return `<section class="pag scura retro"><div class="cornice"></div><div class="safe">
    ${stella("8mm")}<div class="filetto"></div>
    <p>«${esc(C.epigrafe.testo)}»</p>
    <div class="filetto"></div>
    <div class="oswald" style="font-size:9pt;letter-spacing:.35em;color:var(--oro2)">Esemplare unico · Natale 2026</div>
  </div></section>`;
}

function interni() {
  const p = [];
  let folio = 1;
  const add = (html) => {
    p.push(html);
    folio++;
  };
  // 1 frontespizio
  add(`<section class="pag centro front"><div class="safe">
    ${stella("7mm")}<h2>INTER</h2>
    <div class="sub">La storia nerazzurra raccontata dai giornali · 1908 – 2026</div>
    <div class="epi">«${esc(C.epigrafe.testo)}»<cite>${esc(C.epigrafe.autore)}</cite></div>
  </div></section>`);
  // 2 bianca (così la dedica cade su pagina destra)
  add(`<section class="pag bianca"></section>`);
  // 3 dedica
  add(`<section class="pag centro dedica"><div class="safe">
    ${C.dedica.map((r) => `<p>${esc(r)}</p>`).join("")}
    <div class="filetto"></div><div class="firma">${esc(C.firma)}</div>
  </div></section>`);
  // 4 introduzione
  add(`<section class="pag intro"><div class="safe">
    <h3 class="oswald">Prima di cominciare</h3>
    ${C.introduzione.map((t) => `<p>${esc(t)}</p>`).join("")}
  </div><div class="folio">${folio}</div></section>`);

  for (const cap of C.capitoli) {
    // apertura di capitolo sempre su pagina destra (dispari)
    if (folio % 2 === 0) add(`<section class="pag bianca"></section>`);
    add(`<section class="pag blu cap"><div class="cornice"></div><div class="safe">
      <div class="num">${esc(cap.numero)}</div>
      <div class="tit">${esc(cap.titolo)}</div>
      ${cap.anni ? `<div class="anni">${esc(cap.anni)}</div>` : ""}
      <div class="txt">${esc(cap.intro)}</div>
    </div></section>`);
    for (const m of cap.momenti) add(paginaMomento(m, cap, folio));
  }

  add(`<section class="pag chiusura"><div class="safe" style="align-items:center;justify-content:center;text-align:center">
    ${stella("8mm")}${stella("8mm")}
    <h4 style="font-family:Playfair;font-size:30pt;margin-top:6mm">${esc(C.chiusura.titolo)}</h4>
    <p style="font-family:Playfair;font-style:italic;font-size:14pt;margin-top:5mm;max-width:120mm;line-height:1.5">${esc(C.chiusura.testo)}</p>
    <div class="mom" style="width:100%"><div class="vuoto" style="height:120mm;width:100%;aspect-ratio:auto;margin-top:12mm"><b>Spazio libero</b><span>Per il prossimo ritaglio, un biglietto dello stadio, una foto.</span></div></div>
  </div><div class="folio">${folio}</div></section>`);

  // colophon: le pagine totali devono essere pari
  if ((p.length + 1) % 2 !== 0) add(`<section class="pag bianca"></section>`);
  add(`<section class="pag centro fonti"><div class="safe" style="justify-content:flex-end">
    ${C.fonti.map((t) => `<p>${esc(t)}</p>`).join("")}
  </div></section>`);
  return p;
}

const doc = (pagine) =>
  `<!DOCTYPE html><html lang="it"><head><meta charset="utf-8"><style>${CSS}</style></head><body>${pagine.join("\n")}</body></html>`;

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  fs.mkdirSync(SCANS, { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage();
  const anteprima = process.argv.includes("--anteprima");

  const lavori = [
    ["libro-inter-interni", interni()],
    ["libro-inter-copertina", [copertina(), retro()]],
  ];
  for (const [nome, pagine] of lavori) {
    const htmlPath = path.join(ROOT, `.${nome}.html`);
    fs.writeFileSync(htmlPath, doc(pagine));
    await page.goto("file://" + htmlPath);
    await page.evaluate(() => document.fonts.ready);
    await page.pdf({
      path: path.join(OUT, nome + ".pdf"),
      width: PW + "mm",
      height: PH + "mm",
      printBackground: true,
      preferCSSPageSize: true,
    });
    if (anteprima) {
      const dir = path.join(OUT, "anteprima");
      fs.mkdirSync(dir, { recursive: true });
      const pxW = Math.round((PW / 25.4) * 96);
      const pxH = Math.round((PH / 25.4) * 96);
      await page.setViewportSize({ width: pxW, height: pxH });
      const n = await page.locator("section.pag").count();
      for (let i = 0; i < n; i++) {
        await page
          .locator("section.pag")
          .nth(i)
          .screenshot({ path: path.join(dir, `${nome}-${String(i + 1).padStart(2, "0")}.png`) });
      }
    }
    fs.unlinkSync(htmlPath);
    console.log(`✓ ${nome}.pdf — ${pagine.length} pagine`);
  }
  await browser.close();

  // lista delle scansioni da recuperare
  const righe = ["# Scansioni da recuperare", "", "Metti ogni file nella cartella `scansioni/` con il nome indicato (jpg, png o webp), poi rilancia `node build.js`.", "", "| Fatto | File | Momento | Giornale da cercare |", "|---|---|---|---|"];
  for (const cap of C.capitoli)
    for (const m of cap.momenti)
      righe.push(`| ${trovaScansione(m.id) ? "✅" : "⬜"} | \`${m.id}.jpg\` | ${m.data} · ${m.titolo}${m.verificare ? " ⚠️ *da verificare*" : ""} | ${m.giornale} |`);
  fs.writeFileSync(path.join(ROOT, "SCANSIONI-DA-RECUPERARE.md"), righe.join("\n") + "\n");
  console.log("✓ SCANSIONI-DA-RECUPERARE.md aggiornato");
})();

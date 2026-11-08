// Proposte di rilegatura: render dei concept (copertina piana + mockup 3D) e tavola di presentazione PDF.
//   node rilegatura/genera.js
const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const DIR = __dirname;
const OUT = path.join(DIR, "out");
const FONTS = path.join(DIR, "..", "fonts");

// Palmarès (al 2026)
const SCUDETTI = [1910, 1920, 1930, 1938, 1940, 1953, 1954, 1963, 1965, 1966, 1971, 1980, 1989, 2006, 2007, 2008, 2009, 2010, 2021, 2024, 2026];
const CHAMPIONS = [1964, 1965, 2010];
const UEFA = [1991, 1994, 1998];
const MONDO = [1964, 1965, 2010];
const COPPA_ITALIA = [1939, 1978, 1982, 2005, 2006, 2010, 2011, 2022, 2023, 2026];

// ---------- icone (tratto pieno, per la stampa a caldo) ----------
const ICO = {
  stella: `<svg viewBox="0 0 24 24"><path d="M12 1.8l3.1 6.6 7.2.9-5.3 5 1.4 7.1L12 17.9l-6.4 3.5 1.4-7.1-5.3-5 7.2-.9z"/></svg>`,
  scudetto: `<svg viewBox="0 0 24 28"><path d="M2 2h20v9c0 7.5-5 12.5-10 15C7 23.5 2 18.5 2 11z" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M9 4.5h6v17.5c-1 .8-2 1.5-3 2-1-.5-2-1.2-3-2z"/></svg>`,
  champions: `<svg viewBox="0 0 32 36"><path d="M10 3h12v10c0 5-2.8 8-6 8s-6-3-6-8z"/><path d="M10 6C4 5 2 9 4 13s6 4 7 2M22 6c6-1 8 3 6 7s-6 4-7 2" fill="none" stroke="currentColor" stroke-width="2"/><path d="M14 21h4v6h-4zM9 27h14v3H9zM7 31h18v3H7z"/></svg>`,
  uefa: `<svg viewBox="0 0 28 36"><path d="M6 2h16l-2 14c-.5 4-3 6-6 6s-5.5-2-6-6z"/><path d="M12.5 22h3v6h-3zM8 28h12v3H8zM6 32h16v3H6z"/></svg>`,
  mondo: `<svg viewBox="0 0 32 36"><circle cx="16" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="2"/><ellipse cx="16" cy="12" rx="4.5" ry="10" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M6 12h20M8 6.5h16M8 17.5h16" stroke="currentColor" stroke-width="1.3"/><path d="M13 22h6v5h-6zM9 27h14v3H9zM7 31h18v3H7z"/></svg>`,
  coppa: `<svg viewBox="0 0 28 36"><path d="M5 2h18v4c0 7-3.5 11-9 11S5 13 5 6z"/><path d="M5 4C1 4 1 10 6 11M23 4c4 0 4 6-1 7" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M12 17h4v8h-4zM8 25h12v3H8zM6 29h16v4H6z"/></svg>`,
};
const icona = (k, cls = "") => `<span class="ico ${cls}">${ICO[k]}</span>`;

// ---------- materiali ----------
const NOISE = (op) =>
  `url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='400' height='400'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.75' numOctaves='4' stitchTiles='stitch'/><feColorMatrix values='0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 ${op} 0'/></filter><rect width='100%' height='100%' filter='url(%23n)'/></svg>")`;
const PELLE = (c) => `background:${NOISE(0.55)},radial-gradient(ellipse at 30% 25%,rgba(255,255,255,.10),rgba(0,0,0,.25) 80%),${c};background-blend-mode:multiply,normal,normal;`;
const TELA = (c) => `background:repeating-linear-gradient(0deg,rgba(255,255,255,.05) 0 1px,transparent 1px 3px),repeating-linear-gradient(90deg,rgba(0,0,0,.12) 0 1px,transparent 1px 3px),${NOISE(0.25)},${c};`;

const CSS = `
@font-face{font-family:Osw;src:url(file://${FONTS}/Oswald.ttf);font-weight:200 700}
@font-face{font-family:Play;src:url(file://${FONTS}/PlayfairDisplay.ttf);font-weight:400 900}
@font-face{font-family:Play;src:url(file://${FONTS}/PlayfairDisplay-Italic.ttf);font-style:italic}
@font-face{font-family:Old;src:url(file://${FONTS}/OldStandard-Bold.ttf);font-weight:700}
@font-face{font-family:Ser;src:url(file://${FONTS}/SourceSerif4.ttf)}
*{margin:0;padding:0;box-sizing:border-box}
body{background:#fff}
:root{--oro:linear-gradient(115deg,#8a6a2e 0%,#e9cf8a 22%,#b38b3f 40%,#f6e3a8 55%,#9c7633 75%,#d9b96c 100%)}
.oro{background:var(--oro);-webkit-background-clip:text;background-clip:text;color:transparent;filter:drop-shadow(0 .6px 0 rgba(0,0,0,.55)) drop-shadow(0 -.4px 0 rgba(255,255,255,.25))}
.ico{display:inline-block;color:#d8b768;filter:drop-shadow(0 .6px 0 rgba(0,0,0,.6))}
.ico svg{width:100%;height:100%;fill:currentColor;display:block}
.secco{color:rgba(0,0,0,.18);text-shadow:1px 1px 0 rgba(255,255,255,.16),-1px -1px 1px rgba(0,0,0,.6)}
/* copertina piana 600x850 */
.cop{position:relative;width:600px;height:850px;overflow:hidden;font-family:Osw;color:#e6cf93}
/* ---- A: Nerazzurro ---- */
.A{${TELA("#0d0d10")}}
.A .righe{position:absolute;left:0;right:0;top:300px;bottom:0;background:repeating-linear-gradient(90deg,#0d0d10 0 56px,#123d8f 56px 112px)}
.A .righe::after{content:"";position:absolute;inset:0;${PELLE("transparent").replace("background:", "background:")}mix-blend-mode:multiply;opacity:.9}
.A .righe::before{content:"";position:absolute;left:0;right:0;top:0;height:6px;background:var(--oro)}
.A .tit{position:absolute;top:58px;left:0;right:0;text-align:center}
.A .tit h1{font-weight:700;font-size:150px;letter-spacing:10px;line-height:1}
.A .stelle{display:flex;justify-content:center;gap:16px;margin-top:10px}
.A .stelle .ico{width:30px;height:30px}
.A .sub{font-size:15px;letter-spacing:9px;margin-top:12px}
.A .label{position:absolute;left:150px;right:150px;bottom:90px;height:120px;${PELLE("#0d0d10")};border:2px solid #b8955a;display:flex;flex-direction:column;align-items:center;justify-content:center;box-shadow:0 2px 6px rgba(0,0,0,.6)}
.A .label div:first-child{font-family:Play;font-style:italic;font-size:21px}
.A .label div:last-child{font-size:14px;letter-spacing:6px;margin-top:6px}
/* ---- B: La bacheca ---- */
.B{${PELLE("#0b0b0e")}}
.B .cornice{position:absolute;inset:22px;border:2px solid #b8955a}
.B .cornice::after{content:"";position:absolute;inset:6px;border:1px solid #b8955a}
.B h1{position:absolute;top:48px;left:0;right:0;text-align:center;font-weight:700;font-size:96px;letter-spacing:14px}
.B .sotto{position:absolute;top:176px;left:0;right:0;text-align:center;font-family:Play;font-style:italic;font-size:17px}
.B .griglia{position:absolute;top:220px;left:60px;right:60px;display:grid;grid-template-columns:repeat(7,1fr);row-gap:14px}
.B .cella{display:flex;flex-direction:column;align-items:center;font-size:12px;letter-spacing:1px}
.B .cella .ico{width:30px;height:35px;margin-bottom:3px}
.B .filetto{position:absolute;left:80px;right:80px;height:1px;background:#b8955a}
.B .trofei{position:absolute;left:50px;right:50px;display:flex;justify-content:space-around}
.B .tro{display:flex;flex-direction:column;align-items:center;font-size:11px;letter-spacing:1.5px;text-align:center}
.B .tro .ico{width:44px;height:50px;margin-bottom:6px}
.B .tro b{font-size:13px;letter-spacing:3px;font-weight:500;margin-bottom:2px}
.B .ci{position:absolute;left:40px;right:40px;text-align:center;font-size:10.5px;letter-spacing:1px;line-height:1.6}
.B .ci .ico{width:20px;height:25px;vertical-align:middle;margin:0 2px}
.B .piede{position:absolute;bottom:52px;left:0;right:0;text-align:center;font-size:13px;letter-spacing:10px}
/* ---- C: Prima pagina ---- */
.C{background:#ecd2c4}
.C .collage{position:absolute;inset:0;padding:18px 26px;font-family:Old;color:#2a1f1b;opacity:.92;columns:2;column-gap:22px;filter:contrast(1.05)}
.C .collage div{break-inside:avoid;border-bottom:1.5px solid #2a1f1b;padding:8px 0 10px;line-height:1.02}
.C .collage div:nth-child(3n){font-family:Osw;text-transform:uppercase}
.C .collage::after{content:"";position:absolute;inset:0;background:${NOISE(0.35)},radial-gradient(ellipse at 50% 50%,transparent 50%,rgba(110,60,40,.35));mix-blend-mode:multiply}
.C .etichetta{position:absolute;left:105px;right:105px;top:300px;height:250px;${PELLE("#0b0b0e")};border:3px solid #b8955a;box-shadow:0 6px 18px rgba(0,0,0,.55);display:flex;flex-direction:column;align-items:center;justify-content:center}
.C .etichetta h1{font-weight:700;font-size:92px;letter-spacing:10px;line-height:1}
.C .etichetta .s{font-family:Play;font-style:italic;font-size:17px;margin-top:10px}
.C .etichetta .a{font-size:13px;letter-spacing:8px;margin-top:10px}
.C .etichetta .stelle{display:flex;gap:10px;margin-top:10px}.C .etichetta .stelle .ico{width:20px;height:20px}
/* ---- D: Due stelle ---- */
.D{${TELA("#0c1f4a")}}
.D .anni{position:absolute;inset:34px;display:flex;flex-wrap:wrap;align-content:space-between;justify-content:space-between;font-size:15px;letter-spacing:2px}
.D .anni span{width:100%;text-align:center}
.D .bordo{position:absolute;inset:30px;border:1px solid rgba(0,0,0,.45);box-shadow:inset 1px 1px 0 rgba(255,255,255,.08)}
.D .stellone{position:absolute;top:250px;left:0;right:0;display:flex;justify-content:center;gap:40px}
.D .stellone .ico{width:150px;height:150px}
.D h1{position:absolute;top:455px;left:0;right:0;text-align:center;font-weight:600;font-size:64px;letter-spacing:22px}
.D .s{position:absolute;top:545px;left:0;right:0;text-align:center;font-family:Play;font-style:italic;font-size:18px}
.D .vert{position:absolute;top:70px;bottom:70px;width:30px;display:flex;flex-direction:column;justify-content:space-between;align-items:center;font-size:12px}
/* ---- dorso (spine) 70x850 ---- */
.dorso{width:70px;height:850px;position:relative;display:flex;flex-direction:column;align-items:center;justify-content:space-between;padding:40px 0;font-family:Osw;color:#e6cf93}
.dA{${PELLE("#0d0d10")}}.dB{${PELLE("#0b0b0e")}}.dC{${PELLE("#123d8f")}}.dD{${TELA("#0c1f4a")}}
.dorso .t{writing-mode:vertical-rl;transform:rotate(180deg);font-size:26px;letter-spacing:8px;font-weight:600}
.dorso .ico{width:18px;height:18px}
.dorso .nervi{width:100%;height:4px;background:var(--oro);opacity:.9}
/* ---- mockup ---- */
.scena{width:1400px;height:1000px;position:relative;background:radial-gradient(ellipse at 50% 35%,#f4f0ea,#cfc7bb 75%);overflow:hidden;font-family:Osw}
.scena .ombra{position:absolute;left:440px;top:880px;width:640px;height:60px;background:radial-gradient(ellipse,rgba(0,0,0,.45),transparent 70%);filter:blur(6px)}
.libro{position:absolute;left:430px;top:70px;width:600px;height:850px;transform-style:preserve-3d;transform:perspective(2600px) rotateY(-28deg) rotateX(4deg)}
.libro .f{position:absolute;inset:0;backface-visibility:hidden;border-radius:2px 6px 6px 2px;box-shadow:inset 6px 0 10px rgba(0,0,0,.35)}
.libro .s{position:absolute;left:-70px;top:0;width:70px;height:850px;transform-origin:right center;transform:rotateY(-90deg);filter:brightness(.85);backface-visibility:hidden}
.libro .p{backface-visibility:hidden;position:absolute;right:4px;top:6px;width:66px;height:838px;transform-origin:right center;transform:rotateY(90deg);background:repeating-linear-gradient(90deg,#f3eee4 0 2px,#dcd5c8 2px 3px)}
.libro .p.blu{background:repeating-linear-gradient(90deg,#1c4fae 0 2px,#143a85 2px 3px)}
.libro .nastri{position:absolute;bottom:-46px;left:250px;display:flex;gap:10px;transform:translateZ(-4px)}
.libro .nastri i{display:block;width:16px;height:60px;clip-path:polygon(0 0,100% 0,100% 100%,50% 82%,0 100%)}
`;

// ---------- copertine ----------
function copA() {
  return `<div class="cop A"><div class="righe"></div>
    <div class="tit"><h1 class="oro">INTER</h1><div class="stelle">${icona("stella")}${icona("stella")}</div><div class="sub oro">1908 · 2026</div></div>
    <div class="label"><div class="oro">La storia nerazzurra raccontata dai giornali</div><div class="oro">PER [NOME]</div></div></div>`;
}
function copB() {
  const sc = SCUDETTI.map((y) => `<div class="cella">${icona("scudetto")}<span class="oro">${y}</span></div>`).join("");
  const tro = (k, nome, anni) => `<div class="tro">${icona(k)}<b class="oro">${nome}</b><span class="oro">${anni.join(" · ")}</span></div>`;
  return `<div class="cop B"><div class="cornice"></div>
    <h1 class="oro">INTER</h1><div class="sotto oro">La storia nerazzurra raccontata dai giornali · 1908 – 2026</div>
    <div class="griglia">${sc}</div>
    <div class="filetto" style="top:425px"></div>
    <div class="trofei" style="top:450px">${tro("champions", "COPPA DEI CAMPIONI", CHAMPIONS)}${tro("uefa", "COPPA UEFA", UEFA)}${tro("mondo", "CAMPIONI DEL MONDO", MONDO)}</div>
    <div class="filetto" style="top:590px"></div>
    <div class="ci oro" style="top:612px">${COPPA_ITALIA.map((y) => `${icona("coppa")}`).join("")}</div>
    <div class="ci oro" style="top:650px">10 COPPE ITALIA<br>${COPPA_ITALIA.join(" · ")}</div>
    <div class="piede oro">${"PER [NOME]"}</div></div>`;
}
function copC() {
  const t = ["L'Inter «europea»!", "Solo Inter", "Inter alle stelle", "L'Inter campione dei campioni", "Finalmente il Fenomeno", "Pazzi per l'Inter", "Inter, la Coppa in un lampo", "21 di gloria", "Scudetto all'Inter a suon di gol", "Mondo Inter", "L'Inter ancora campione!", "Inter d'Italia", "Così il Trap creò una stella", "Inter: decimo scudetto", "Inter uno tituli", "Lacrime da campioni", "L'Internazionale campione d'Italia", "Inter e due"];
  const sz = [34, 46, 30, 26, 38, 30, 26, 44, 28, 36, 30, 40, 26, 32, 36, 28, 24, 40];
  return `<div class="cop C"><div class="collage">${t.map((x, i) => `<div style="font-size:${sz[i]}px">${x}</div>`).join("")}</div>
    <div class="etichetta"><h1 class="oro">INTER</h1><div class="stelle">${icona("stella")}${icona("stella")}</div><div class="s oro">La storia raccontata dai giornali</div><div class="a oro">1908 · 2026</div></div></div>`;
}
function copD() {
  const met = Math.ceil(SCUDETTI.length / 2);
  return `<div class="cop D"><div class="bordo"></div>
    <div class="vert" style="left:46px">${SCUDETTI.slice(0, met).map((y) => `<span class="secco">${y}</span>`).join("")}</div>
    <div class="vert" style="right:46px">${SCUDETTI.slice(met).map((y) => `<span class="secco">${y}</span>`).join("")}<span class="secco">★</span></div>
    <div class="stellone">${icona("stella")}${icona("stella")}</div>
    <h1 class="oro">INTER</h1><div class="s oro">La storia nerazzurra raccontata dai giornali</div></div>`;
}
const DORSI = {
  A: `<div class="dorso dA"><div class="nervi"></div>${icona("stella")}<div class="t oro">INTER · 1908–2026</div>${icona("stella")}<div class="nervi"></div></div>`,
  B: `<div class="dorso dB"><div class="nervi"></div><div class="t oro">INTER · LA STORIA NEI GIORNALI</div><div class="nervi"></div></div>`,
  C: `<div class="dorso dC"><div class="nervi"></div>${icona("stella")}<div class="t oro">INTER · 1908–2026</div>${icona("stella")}<div class="nervi"></div></div>`,
  D: `<div class="dorso dD">${icona("stella")}<div class="t oro">INTER</div>${icona("stella")}</div>`,
};
const COP = { A: copA, B: copB, C: copC, D: copD };
const TAGLIO = { A: "", B: "", C: "", D: "blu" };
const NASTRI = { A: ["#0d0d10", "#1c4fae"], B: ["#b8955a"], C: ["#1c4fae"], D: ["#0d0d10", "#1c4fae"] };

const CONCEPT = [
  {
    k: "A", nome: "Nerazzurro",
    idea: "La maglia diventa copertina: le strisce nere e azzurre salgono dal basso come su una divisa, la parte alta è nera con il titolo in oro.",
    spec: ["Tela da legatoria nera (es. Brillianta/Buckram) con riporto di pelle blu a strisce verticali", "Titolo «INTER», due stelle e date in oro a caldo (cliché in magnesio)", "Etichetta in pelle nera con dedica impressa in oro, incassata", "Dorso in pelle nera con nervi dorati", "Risguardi neri, nastri segnalibro nero e azzurro"],
  },
  {
    k: "B", nome: "La bacheca",
    idea: "Tutto il palmarès inciso in oro sulla copertina: i 21 scudetti con l'anno, le 3 Coppe dei Campioni, le 3 Coppe UEFA, i 3 titoli mondiali e le 10 Coppe Italia.",
    spec: ["Pelle nera pieno fiore (vacchetta o capra) su cartone da 3 mm", "Doratura a caldo con foglia oro 23 kt o lamina oro lucida: cornice, titolo, 21 scudetti con anno, trofei europei e mondiali, Coppe Italia", "Dorso tondo con titolo in oro, capitelli blu e neri cuciti a mano", "Cofanetto rivestito in tela blu, interno in velluto nero", "Nastro segnalibro oro"],
  },
  {
    k: "C", nome: "Prima pagina",
    idea: "Legatura alla bodoniana: dorso in pelle blu e piatti rivestiti di carta rosa con i titoli storici del libro. Al centro, un'etichetta nera con il titolo in oro.",
    spec: ["Mezza pelle blu Inter sul dorso e sugli angoli", "Piatti in carta rosa stampata con il collage dei titoli (stampa fine art, plastificazione opaca o vernice)", "Etichetta in pelle nera incassata, titolo e stelle in oro a caldo", "Risguardi con la prima pagina «Solo Inter» del 23 maggio 2010", "Cofanetto nero con titolo in oro sul dorso"],
  },
  {
    k: "D", nome: "Due stelle",
    idea: "Minimalismo da collezione: tela blu notte, due grandi stelle in oro e gli anni dei 21 scudetti impressi a secco lungo i bordi, visibili solo con la luce radente.",
    spec: ["Tela blu notte di alta grammatura", "Due stelle grandi e titolo in oro a caldo, con leggero rilievo (cliché in ottone a due livelli)", "Anni degli scudetti impressi a secco (senza colore) sui bordi", "Taglio dei fogli colorato di blu Inter", "Due nastri segnalibro nero e azzurro, risguardi neri con gli anni in blu"],
  },
];

function mockup(c) {
  const rot = c.k === "D" ? "rotateY(-28deg)" : "rotateY(30deg)";
  return `<div class="scena"><div class="ombra"></div><div class="libro" style="transform:perspective(2600px) ${rot} rotateX(4deg)">
    <div class="p ${TAGLIO[c.k]}"></div>
    <div class="s">${DORSI[c.k]}</div>
    <div class="f">${COP[c.k]()}</div>
    <div class="nastri">${NASTRI[c.k].map((x) => `<i style="background:${x}"></i>`).join("")}</div>
  </div></div>`;
}

const doc = (body, extra = "") => `<!DOCTYPE html><html lang="it"><head><meta charset="utf-8"><style>${CSS}${extra}</style></head><body>${body}</body></html>`;

const TAVOLA_CSS = `
@page{size:420mm 297mm;margin:0}
.tav{width:420mm;height:297mm;display:grid;grid-template-columns:240mm 1fr;page-break-after:always;background:#f6f1e7;font-family:Ser;color:#1c1a17}
.tav .img{background:#cfc7bb;display:flex;align-items:center;justify-content:center;overflow:hidden}
.tav .img img{width:100%;height:100%;object-fit:cover}
.tav .txt{padding:22mm 18mm;display:flex;flex-direction:column}
.tav .num{font-family:Osw;letter-spacing:.4em;font-size:11pt;color:#1f5fbf}
.tav h2{font-family:Play;font-size:40pt;margin:3mm 0 6mm}
.tav .idea{font-family:Play;font-style:italic;font-size:15pt;line-height:1.45;margin-bottom:8mm}
.tav li{font-size:11.5pt;line-height:1.5;margin:0 0 2.5mm 5mm}
.tav .piatta{margin-top:auto;display:flex;gap:6mm;align-items:flex-end}
.tav .piatta img{height:80mm;box-shadow:0 2mm 5mm rgba(0,0,0,.25)}
.tav .piatta span{font-size:9pt;color:#6f6a62;font-style:italic}
.cover{width:420mm;height:297mm;background:#0b0b0e;color:#e6cf93;display:flex;flex-direction:column;align-items:center;justify-content:center;page-break-after:always;font-family:Osw}
.cover h1{font-size:60pt;letter-spacing:.3em}
.cover p{font-family:Play;font-style:italic;font-size:18pt;margin-top:6mm;color:#ddd5c4}
`;

async function carica(page, html) {
  const f = path.join(OUT, ".tmp.html");
  fs.writeFileSync(f, html);
  await page.goto("file://" + f);
}

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ deviceScaleFactor: 2 });
  for (const c of CONCEPT) {
    await page.setViewportSize({ width: 600, height: 850 });
    await carica(page, doc(COP[c.k]()));
    await page.evaluate(() => document.fonts.ready);
    await page.screenshot({ path: path.join(OUT, `${c.k}-${c.nome.toLowerCase().replace(/ /g, "-")}-copertina.png`) });
    await page.setViewportSize({ width: 1400, height: 1000 });
    await carica(page, doc(mockup(c)));
    await page.evaluate(() => document.fonts.ready);
    await page.screenshot({ path: path.join(OUT, `${c.k}-${c.nome.toLowerCase().replace(/ /g, "-")}-mockup.png`) });
    console.log("✓", c.k, c.nome);
  }
  // tavola PDF A3 orizzontale
  const tav = [`<div class="cover"><h1>INTER</h1><p>Quattro proposte di rilegatura per un esemplare unico</p></div>`]
    .concat(CONCEPT.map((c, i) => {
      const base = `file://${OUT}/${c.k}-${c.nome.toLowerCase().replace(/ /g, "-")}`;
      return `<section class="tav"><div class="img"><img src="${base}-mockup.png"></div><div class="txt">
        <div class="num">PROPOSTA ${c.k}</div><h2>${c.nome}</h2><div class="idea">${c.idea}</div>
        <ul>${c.spec.map((s) => `<li>${s}</li>`).join("")}</ul>
        <div class="piatta"><img src="${base}-copertina.png"><span>Copertina in piano</span></div></div></section>`;
    }));
  const tmp = path.join(OUT, ".tavola.html");
  fs.writeFileSync(tmp, doc(tav.join(""), TAVOLA_CSS));
  await page.goto("file://" + tmp);
  await page.evaluate(() => document.fonts.ready);
  await page.pdf({ path: path.join(OUT, "proposte-rilegatura.pdf"), width: "420mm", height: "297mm", printBackground: true });
  fs.unlinkSync(tmp);
  fs.rmSync(path.join(OUT, ".tmp.html"), { force: true });
  console.log("✓ proposte-rilegatura.pdf");
  await browser.close();
})();

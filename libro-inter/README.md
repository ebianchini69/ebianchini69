# INTER — La storia nerazzurra raccontata dai giornali

Libro regalo (esemplare unico, uso privato) ispirato ai "newspaper history books":
la storia dell'Inter dal 1908 a oggi, una pagina di giornale dell'epoca per ogni grande momento.

## Cosa c'è
- `out/libro-inter-interni.pdf` — interni, A4 verticale con 3 mm di abbondanza, 54 pagine (pari, pronto per il fotolibro)
- `out/libro-inter-copertina.pdf` — fronte e retro della copertina
- `contenuti.js` — tutti i testi: nome del destinatario, dedica, didascalie. Si modifica solo questo.
- `SCANSIONI-DA-RECUPERARE.md` — checklist delle pagine di giornale da trovare, con il nome file da usare

## Come si completa
1. Sostituisci `[Nome]`, la dedica e la firma in `contenuti.js`; completa le pagine segnate ⚠️ (stagione 2025/26 e capitolo personale).
2. Recupera le scansioni (vedi checklist) e mettile in `scansioni/` con il nome indicato, es. `scansioni/1964-coppa-campioni.jpg`. Risoluzione consigliata: almeno 2000 px sul lato lungo.
3. Rigenera: `node build.js` (aggiungi `--anteprima` per avere i PNG di ogni pagina in `out/anteprima/`).

Le scansioni non vengono salvate nel repository (sono materiale coperto da diritti, uso privato).

## Stampa
Fotolibro a copertina rigida, carta opaca premium (es. Saal Digital Professional Line, Cewe Fotolibro Premium):
caricare il PDF degli interni pagina per pagina e la copertina come immagine di copertina. Se il formato scelto non è A4,
cambia `formato` in `contenuti.js` e rigenera.

Font: Oswald, Playfair Display, Source Serif 4 (SIL Open Font License).

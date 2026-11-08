# Diario di lavoro — Libro Inter, regalo di Natale 2026

Traccia completa di cosa è stato fatto, dove sono i file e cosa resta da fare.
Copia di tutto (PDF, immagini, questo diario) su Google Drive: cartella **"Libro Inter – Regalo Natale 2026"**.

## L'idea
Ispirazione: i "newspaper history books" di Historic Newspapers (es. *Formula 1 — as told in headlines*).
Versione Inter: libro premium, esemplare unico, la storia nerazzurra dal 1908 al 2026 raccontata con le pagine
dei giornali del giorno dopo. Uso strettamente privato (le pagine sono coperte da diritti degli editori).

## Cosa è stato fatto (8 novembre 2026)
1. **Impaginato del libro** (`build.js`, `contenuti.js`): A4 verticale con abbondanza 3 mm, 54 pagine, copertina nera/oro,
   9 capitoli con aperture blu, una pagina per momento (data, titolo, pagina di giornale, didascalia, tabellino).
2. **Ricerca delle pagine online** (dettaglio con link in `FONTI-PAGINE.md`):
   - **1953–2008**: pagine originali de *l'Unità* dall'archivio storico gratuito `archivio.unita.news`
     (scansioni a 300 dpi, qualità da stampa). Individuate scaricando tutte le pagine del giorno dopo e cercando
     nel testo le parole chiave (Inter, nerazzurri, scudetto, nomi dei giocatori), poi verificate a vista una per una.
   - **2009–2026**: prime pagine de *La Gazzetta dello Sport* dall'archivio di prime pagine `kiosko.net`
     (2009–2021 a ~760 px di larghezza, 2023–2026 a 1000–1400 px).
   - **1908–1940**: nessuna pagina disponibile online in qualità sufficiente (l'archivio La Stampa non risponde).
3. **Pagine ricostruite in stile d'epoca** per 1908, 1910, 1920, 1930, 1938, 1940 (`ricostruzioni/`):
   testata e impaginazione in stile Gazzetta d'epoca su carta rosa invecchiata, articoli scritti per il libro
   in italiano d'epoca, basati sui fatti delle voci Wikipedia delle singole stagioni, con le foto d'epoca delle squadre
   e di Meazza. In fondo a ogni pagina una riga dichiara che è una ricostruzione.
4. **Verifica dei fatti** sulle pagine trovate: corrette date e risultati (es. scudetto 1963 vinto il 5/5 nonostante
   Roma–Inter 3-0; 1971 con Inter–Foggia 5-0; 1989 con Inter–Napoli 2-1; Intercontinentale 1964 il 26/9 a Madrid).
5. **Stagione 2025/26**: Inter di Cristian Chivu campione d'Italia (21° scudetto, 3/5/2026, Inter–Parma 2-0)
   e vincitrice della Coppa Italia (13/5/2026, Lazio–Inter 0-2). Aggiunte le due prime pagine della Gazzetta.

## Stato attuale
- 35 momenti, **33 con pagina** (27 originali + 6 ricostruite). Mancano solo le 2 pagine personali
  (data di nascita del destinatario, "la nostra partita").
- Da personalizzare in `contenuti.js`: nome del destinatario, dedica, firma.

## Come rigenerare
```
node ricostruzioni/genera.js   # rigenera le 6 pagine d'epoca in scansioni/
node build.js --anteprima      # rigenera il PDF in out/ (+ PNG di controllo)
```
Le immagini (`scansioni/`, `ricostruzioni/foto/`) e i PDF (`out/`) NON sono nel repository (diritti):
sono su Google Drive.

## Prossimi passi
- [ ] Nome, dedica, firma, pagine personali
- [ ] Valutare le opzioni a pagamento per migliorare 1908–1940 e le Gazzette 2009–2021 (in corso di ricerca)
- [ ] Scelta tipografia/formato premium e ordine entro il 5 dicembre

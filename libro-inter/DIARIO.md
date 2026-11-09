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
3. **Pagine ricostruite in stile d'epoca** per 1908 (datata Gazzetta di mercoledì 11/3/1908), 1910, 1920, 1930, 1938, 1940 (`ricostruzioni/`):
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

## Opzioni a pagamento (ricerca dell'8/11/2026)
- **Biblioteca Braidense, Milano** (raccomandata per 1908–1940): scansioni dal microfilm della Gazzetta,
  €1,50 a JPG 300 dpi (€16 TIFF 400 dpi), uso privato non commerciale. Richiesta a b-brai.riproduzioni@cultura.gov.it,
  pagamento su pagonline.cultura.gov.it ("Pinacoteca di Brera" > "Servizi Braidense"); lavorano la settimana dopo il pagamento.
  Date da chiedere: 11/3/1908 (la Gazzetta nel 1908 usciva lun-mer-ven; fondazione lunedì 9/3) + 13/3/1908 di riserva,
  25/4/1910, 21/6/1920, 30/6/1930, 25/4/1938, 3/6/1940. Costo stimato €10–20. Bianco e nero (microfilm).
- **Corriere della Sera, Archivio storico** (Naviga+ €9,99/mese): tutte le edizioni dal 1876, consultazione online; download non verificato.
- **Gazzetta Digital Edition** (€7,99/mese): da verificare se l'archivio arriva al 2009 e permette di esportare le pagine.
- **Archivio La Stampa**: gratuito, ma irraggiungibile dai server cloud; provare da una connessione di casa in Italia.
- **Giornali originali** (eBay, in-vendita.it): nessun annuncio trovato per le nostre date, rischio ristampe.

## Rilegatura (8/11/2026)
Quattro proposte in `rilegatura/` (mockup + tavola A3 `proposte-rilegatura.pdf`): A Nerazzurro, B La bacheca
(palmarès in oro: 21 scudetti, 3 Coppe dei Campioni, 3 UEFA, 3 mondiali, 10 Coppe Italia), C Prima pagina, D Due stelle.
Raccomandazione: B + taglio blu e nastri da D + risguardi Gazzetta del Triplete da C. Senza stemma ufficiale (marchio).

## Legatori e stampatori a Milano (ricerca 8/11/2026)
1. **Legatoria Conti Borbone** (dal 1873, Bottega Storica, Ambrogino d'oro) — Via Giulio Romano 29 / ingresso Via Gaetana Agnesi 18,
   tel. 02 8645 0090, info@contiborbone.com. Prima scelta. Bozza email in Gmail.
2. **Legatoria Borghi** (stampa + rilegatura, pezzi singoli) — Via Gian Giacomo Mora 15, tel. 02 837 5649,
   info@legatoriaborghimilano.it. Alternativa "tutto in uno". Bozza email in Gmail.
3. **Legatoria d'Arte Giovanni Còdina** (dal 1951, altissimo livello) — Via Chianciano 4, tel. 02 645 3477: telefonare per verificare che sia attiva.
Stampatori fine art: **Fine M-art** (Via A. Buschi 9, 02 8969 5203, stampa@finemart.it), **Studio Fahrenheit** (Viale A. Doria 33, 02 2049 671).
Nota tecnica: far scegliere al legatore carta (fronte/retro) e cucitura prima di stampare; file allo stampatore entro il 20–25/11.

## Aggiornamento 9/11/2026
- Nuovo vincolo: consegna entro **3–4 dicembre** (dall'8/12 Elena non è disponibile). Brief inviato: mezza tela,
  piatti neri, dorso tela azzurra (#0068A8 / ~Pantone 3015 C), oro a caldo, 52 pagine, PDF pronti entro il 20/11.
- **Conti Borbone: ha rifiutato** (non riesce a consegnare entro il 4/12).
- **Legatoria Borghi**: info@legatoriaborghimilano.it non esiste (email respinta) → bozza reinviata a legatoriaborghimilano@gmail.com.
- **Morganti** (via Lanzone 1, 02 8645 2956): bozza pronta a morganti@morgantimilano.it.
- Braidense: richiesta inviata l'8/11, in attesa.

## Prossimi passi
- [ ] Nome, dedica, firma, pagine personali
- [ ] Richiesta alla Braidense per le pagine 1908–1940 (bozza email pronta in Gmail)
- [ ] Provare un mese di Gazzetta Digital Edition per le Gazzette 2009–2021 in alta risoluzione
- [ ] Scelta tipografia/formato premium e ordine entro il 5 dicembre

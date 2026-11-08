# Ada — co-teacher vocale per la lezione

Una co-docente AI che sta in aula con te: **ascolta** gli studenti, **risponde a voce**,
**si ricorda chi ha già parlato**, **prende appunti** e **ti passa la parola** quando la
domanda è tua (voti, esami, opinioni personali, cose fuori dal materiale).

Un solo file: `index.html`. Niente server, niente installazioni.

## Come funziona

| | |
|---|---|
| Orecchie | Riconoscimento vocale del browser (Chrome/Edge, italiano) |
| Cervello | Claude (Opus 5.5 di default, effort basso per rispondere in fretta) |
| Voce | Sintesi vocale del sistema, con tono che cambia a seconda di cosa le dici (entusiasta, riflessiva, divertita, empatica…) |
| Memoria | Studenti, domande, appunti e coda «per la docente» salvati nel browser |

## In aula, in 3 passi

1. **Apri la pagina in Chrome o Edge** sul portatile collegato al proiettore e alle casse.
   Per il microfono serve un indirizzo `https://` o `localhost`:
   ```bash
   cd co-teacher && python3 -m http.server 8000
   # poi apri http://localhost:8000
   ```
   (oppure trascina la cartella su Cloudflare Pages / Netlify Drop, come per gli altri progetti).
2. **Preparazione** → incolla la chiave API Anthropic (console.anthropic.com → API keys),
   carica scaletta/slide in testo, scrivi l'argomento, regola la voce. «Salva e vai in aula».
3. **In aula**:
   - tieni premuto **Spazio** (o il pallino) mentre lo studente parla, rilascia → Ada risponde;
   - **Mani libere**: ascolta sempre, ma risponde solo quando qualcuno dice «Ada…»;
   - **Esc** la interrompe; «Domanda alla classe» e «Riassunto» sono comandi per te;
   - quando passa la parola a te suona un *ding* e compare il riquadro arancione.

Il tab **Appunti** produce il verbale della lezione (punti chiave, domande aperte,
domande passate a te, studenti intervenuti, trascrizione) da copiare o scaricare in Markdown.

## Costi e sicurezza

- Una lezione di 2 ore con Opus 5.5 costa indicativamente 1–3 $; con Haiku 5.5 pochi centesimi.
  C'è un **tetto di spesa per sessione** (default 5 $) oltre il quale Ada si ferma.
- La chiave resta solo nel `localStorage` del tuo browser. Usa una chiave dedicata con un limite
  di spesa impostato nella Console, e non proiettare la schermata Preparazione mentre la incolli.
- Agli studenti conviene dirlo: «c'è una co-teacher AI che ascolta quando premo il tasto».

## Personalizzare

Nome, come chiama te, regole di passaggio e personalità si cambiano dalla Preparazione,
senza toccare il codice.

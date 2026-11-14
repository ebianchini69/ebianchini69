# Obiettivi e requisiti (dichiarati da Elena, 14/11/2026)

Stato: requisiti raccolti. Niente in esecuzione. Le scelte aperte sono in fondo.

## Instagram: salvati

| Area | Cosa voglio | Formato |
|---|---|---|
| Ricette | Tutte, nessuna esclusa | Scheda: ingredienti, passaggi, tempi, link |
| Fitness | Solo i più corti e i più efficaci | Libreria con misure: durata, tipo (forza, cardio, mobilità), zona del corpo, attrezzatura, livello |
| Microtest | Idee di lavoro, idee sulla parte monetaria, idee casa | Board con le idee raggruppate per tipologia |

Per ogni post: una prima scrematura (tenere, scartare, approfondire), anche ascoltando audio e video.

**Vincolo: niente Chrome.** Si lavora con export, API e strumenti in background.

## WhatsApp: solo la chat "memo"

- "Memo" è la chat con me stessa. È l'unica nel perimetro.
- Ci sono due tipi di contenuto:
  - **le posizioni del parcheggio**: dati di posizione. Proposta: escluderle dall'archivio e dalla board;
  - **le cose da approfondire**: entrano nella board, come secondo filtro.
- Accesso via server locale, già senza Chrome.

## Realtà tecnica di Instagram (da tenere presente)

- Nessuna API ufficiale dà accesso ai salvati di un account personale. L'API Basic Display è stata chiusa a dicembre 2024. La Graph API serve solo agli account business o creator e non espone i salvati.
- L'export ufficiale (JSON) dà l'elenco dei salvati e delle raccolte, ma non il contenuto dei post altrui: niente video, audio e di solito niente testo.
- Strada proposta senza Chrome e senza login:
  1. l'elenco viene dall'export, che Elena richiede ogni tanto (non è automatizzabile);
  2. il contenuto dei post pubblici si scarica in forma anonima, senza credenziali e senza passare dall'account di Elena;
  3. audio e video vengono trascritti in locale sul Mac.
- Rischio: Instagram blocca spesso gli accessi anonimi. Quanto funzioni si scopre solo con una prova su pochi link. I post che falliscono si segnalano, non si forzano.
- Esclusi: librerie non ufficiali che richiedono login o cookie (instagrapi, instaloader con sessione). Violano la regola 3 dell'handover e mettono a rischio l'account.

## Scelte aperte

1. Dove vive la board: archivio locale sul Mac, oppure Notion con vista board (già collegato), alimentato dall'archivio locale.
2. "Misure" del fitness: metriche del singolo allenamento (come sopra) o anche misure personali da tracciare.
3. Esclusione delle posizioni del parcheggio da "memo": da confermare.

# Biglietti da visita e firma Outlook (prototipo)

Pagina unica (`index.html`) per i colleghi Newchem:

- biglietto da visita digitale da salvare sul telefono (file `.vcf`, iPhone e Android) con QR sul retro;
- firma email per Outlook, coordinata con il biglietto cartaceo.

I dati inseriti restano nel browser di chi compila.

## Configurazione

In cima a `index.html` ci sono due blocchi:

- `AZIENDA`: nome, sito, colore, logo, sede legale;
- `SEDI`: indirizzo, telefono e fax di ogni sede (Pavia da completare).

## Link precompilati

`index.html?nome=Mario&cognome=Rossi&ruolo=Quality%20Manager&sede=verona&cell=...&email=...`

## Pubblicazione

Cloudflare Pages (build output directory: questa cartella), accesso limitato agli indirizzi
`@newchemspa.it` con Cloudflare Access.

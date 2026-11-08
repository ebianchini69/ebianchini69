# Backtest 100 EUR: ETF S&P 500 + Bitcoin

- **Cosa:** portafoglio misto tra iShares Core S&P 500 UCITS (`SXR8.DE`, in EUR) e Bitcoin (`BTC-EUR`).
- **Periodo:** gen 2018 – nov 2026.
- **Dati:** chiusure giornaliere da Yahoo Finance.
- **Riproduzione:** `python3 backtest/backtest.py`. Le tabelle complete sono in `risultati.md`, il grafico in `equity.png`.

## Regole (fissate prima di vedere i risultati)
- Il segnale si calcola sulla chiusura del giorno prima e si esegue alla chiusura di oggi, quindi senza informazioni dal futuro.
- **Pesi a volatilità inversa:** ogni mese ciascun asset pesa in proporzione a 1/volatilità a 90 giorni.
- **Trend filter:** l'asset si tiene solo se è sopra la sua media mobile a 200 giorni, altrimenti quella quota va in liquidità.
- **Costi, scenario basso:** 0,10% sugli ETF, 0,09% sulla crypto, più mezzo spread dello 0,05%.
- **Costi, scenario "Revolut Standard":** 0,25% con minimo 1 € sugli ETF. È un'ipotesi da verificare sul piano reale.

## Esito in sintesi
| Strategia | 100 € diventano | Max perdita | Sharpe |
|---|---:|---:|---:|
| Solo S&P 500 | 331 € | -34% | 0,89 |
| Solo BTC | 537 € | -80% | 0,62 |
| 50/50 ribilanciato | 599 € | -50% | 0,77 |
| **Volatilità inversa (~80/20) ribilanciato** | **539 €** | **-35%** | **1,07** |
| 50/50 + trend filter | 318 € | -39% | 0,65 |
| Vol. inversa + trend filter | 288 € | -28% | 0,89 |

Lo scenario di costi basso, con 0 € di imposte, è quello in tabella. Con un minimo di 1 € a operazione le strategie con il trend filter scendono a circa **126 €**: i costi si mangiano quasi tutto.

## Limiti
- **Il vincitore era noto in partenza:** sapevamo già che BTC sarebbe "sopravvissuto". Nel 2018 non era ovvio, e lo stesso test su altre crypto darebbe risultati molto peggiori.
- **Liquidità a rendimento 0, imposte escluse.** In Italia sono il 26% sulle plusvalenze da ETF; per le crypto l'aliquota è salita a partire dal 2026.
- **Nessuna verifica sui dati intraday:** il test non dice nulla su trading a minuti o millisecondi.

# Estensione: singole azioni (Piazza Affari e tech USA)
Si lancia con `python3 backtest/backtest_azioni.py`. Le tabelle sono in `risultati_azioni.md`, il grafico in `equity_azioni.png`.

- **Universo:** 23 grandi titoli italiani e 17 grandi tech USA, scelti come li si sarebbe scelti a fine 2017, inclusi quelli poi andati male.
- **Strategie:** ETF indice tenuto fermo, tutti i titoli a pesi uguali, momentum sui 5 titoli migliori, momentum con trend filter.

**Esito con costi bassi:**

| | ETF indice | Pesi uguali | Momentum top 5 | Momentum + trend |
|---|---:|---:|---:|---:|
| Italia: 100 € diventano | 307 € | 361 € | 323 € | 339 € (calo massimo -23%) |
| Tech USA: 100 € diventano | 469 € | 614 € | 915 € | 403 € |

Cosa si vede:
- **Tech USA:** il momentum batte l'indice in tutte e due le metà del periodo e con 3, 5, 7 o 10 titoli. Il suo Sharpe (0,92) è però pari a quello dell'ETF (0,95): rende di più perché rischia di più, non perché sceglie meglio. Su questi anni pesa molto Nvidia.
- **Italia:** il momentum non batte l'indice. Il trend filter dimezza il calo massimo.
- **Con il minimo di 1 € a operazione e 100 € di capitale le strategie su singoli titoli non sono eseguibili.** A pesi uguali nessuna operazione passa la soglia; il momentum finisce tra 43 e 191 €.

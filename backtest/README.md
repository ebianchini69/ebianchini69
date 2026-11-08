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

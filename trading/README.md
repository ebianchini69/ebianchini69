# Bot di trading – 100 €

**Strategia**, scelta col backtest in `../backtest` (2018–oggi: 100 € → circa 950 €, Sharpe 1,0, calo massimo -41%, anno peggiore -35%):
- 40%: 17 grandi tech USA a pesi uguali.
- 40%: i 5 tech con il momentum migliore (rendimento a 12 mesi escluso l'ultimo).
- 20%: Bitcoin.

Il portafoglio si ribilancia una volta al mese; ogni giorno il bot fa un controllo e manda il report del saldo.

**Broker:** [Alpaca](https://alpaca.markets).
- API aperta, senza commissioni sulle azioni USA, frazioni da 1 $.
- Accesso con chiavi API: nessun login giornaliero e nessun 2FA a ogni sessione.
- Da residente UE gli ETF americani non si possono comprare, per questo il "paniere" è fatto di singoli titoli.

**Limiti di sicurezza scritti nel codice:**
- Usa solo il budget di 100 €, anche se sul conto c'è di più.
- Niente leva, niente vendite allo scoperto, niente opzioni.
- Se il valore scende sotto la metà del massimo raggiunto, vende tutto e si ferma.

## Cosa serve da te (solo i passaggi che per legge o per sicurezza non posso fare io)
1. **Remote Control:** nell'app Claude desktop, Impostazioni → Claude Code → Remote Control, aggiungere una cartella (ad esempio `~/claude-trading-repo`) e accettare la richiesta di collegamento.
2. **Registrazione su Alpaca:** su app.alpaca.markets/signup con email e password. Il conto *paper* (soldi finti) è attivo subito.
3. **Chiavi API:** nella dashboard, su Paper, cliccare "Generate New Keys" e incollarle quando lo script lo chiede. Le chiavi non vanno mai scritte in chat.
4. **Conto reale:** completare la verifica d'identità (documento, selfie, questionario) e fare il bonifico di 100 €. Poi generare le chiavi *live* e incollarle allo stesso modo.

## Cosa fa Claude
- Clona il repository, esegue `bash setup_mac.sh paper`, verifica il primo ordine e il primo report.
- Ogni giorno controlla i report e interviene se qualcosa non va.
- Quando il conto reale è verificato e finanziato esegue `bash setup_mac.sh live` e disattiva il paper.

## Comandi
```
python3 bot.py status | run | report | halt | resume      # TRADING_ENV=paper|live
python3 test_bot.py                                        # test con broker finto
```
I report giornalieri sono in `~/claude-trading/reports/`; ogni sera arriva anche una notifica macOS.

## Da sapere
- **Tasse:** Alpaca è un broker estero, quindi il regime è dichiarativo. Plusvalenze e quadro RW vanno nella dichiarazione dei redditi.
- **Accesso dall'Italia:** l'apertura del conto reale per i residenti italiani va confermata in fase di registrazione. Se Alpaca non accetta il paese, il piano B è Interactive Brokers: richiede 2FA quotidiano e un adattatore del bot.

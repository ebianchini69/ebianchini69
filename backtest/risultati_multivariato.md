# Sistema multivariato (LightGBM, 21 segnali), test fuori campione 2019 -> oggi

Osservazioni: 132,317 (titolo x giorno). Correlazione media di rango previsione/realta' (IC): 0.031

|                                                  | Media giorno   | Giorni >= +10%   | Giorni in perdita   | Giorni fermi (nessun acquisto)   |   Mese tipico EUR | Mesi in guadagno   | Mesi a 500 EUR   | Anni positivi   |   100 EUR dal 2019 diventano |
|:-------------------------------------------------|:---------------|:-----------------|:--------------------|:---------------------------------|------------------:|:-------------------|:-----------------|:----------------|-----------------------------:|
| top 1 | costo 0.05%/lato | sempre                | +0.173%        | 2.53%            | 50%                 | 0%                               |             101.1 | 54%                | 0.00%            | 5/8             |                          448 |
| top 1 | costo 0.05%/lato | solo se stima > costi | +0.221%        | 2.33%            | 39%                 | 20%                              |             103.4 | 59%                | 0.00%            | 5/8             |                        1,478 |
| top 3 | costo 0.05%/lato | sempre                | +0.052%        | 1.06%            | 49%                 | 0%                               |             100.2 | 51%                | 0.00%            | 4/8             |                          106 |
| top 3 | costo 0.05%/lato | solo se stima > costi | +0.110%        | 1.11%            | 38%                 | 20%                              |             101.2 | 53%                | 0.00%            | 5/8             |                          332 |
| top 5 | costo 0.05%/lato | sempre                | +0.034%        | 0.51%            | 49%                 | 0%                               |             100.6 | 52%                | 0.00%            | 5/8             |                           94 |
| top 5 | costo 0.05%/lato | solo se stima > costi | +0.093%        | 0.66%            | 39%                 | 20%                              |             101.1 | 53%                | 0.00%            | 4/8             |                          274 |
| top 1 | costo 0.10%/lato | sempre                | +0.073%        | 2.48%            | 51%                 | 0%                               |              99   | 48%                | 0.00%            | 3/8             |                           62 |
| top 1 | costo 0.10%/lato | solo se stima > costi | +0.103%        | 2.03%            | 35%                 | 29%                              |             101.9 | 56%                | 0.00%            | 4/8             |                          169 |
| top 3 | costo 0.10%/lato | sempre                | -0.048%        | 0.96%            | 50%                 | 0%                               |              98.2 | 45%                | 0.00%            | 4/8             |                           15 |
| top 3 | costo 0.10%/lato | solo se stima > costi | +0.029%        | 1.22%            | 35%                 | 29%                              |             100.2 | 51%                | 0.00%            | 4/8             |                           67 |
| top 5 | costo 0.10%/lato | sempre                | -0.066%        | 0.51%            | 51%                 | 0%                               |              98.5 | 44%                | 0.00%            | 2/8             |                           13 |
| top 5 | costo 0.10%/lato | solo se stima > costi | +0.020%        | 0.91%            | 36%                 | 29%                              |             100.3 | 51%                | 0.00%            | 3/8             |                           63 |
| CONTROLLO: tutti i titoli, nessun modello        | -0.046%        | 0.10%            | 50%                 | 0%                               |              98.9 | 41%                | 0.00%            | 2/8             |                           30 |

Segnali piu' usati dal modello (ultimo anno):

|             |   importanza |
|:------------|-------------:|
| mkt_r5      |          602 |
| vix         |          533 |
| mkt_r1      |          523 |
| mkt_gap     |          488 |
| vix_chg     |          469 |
| btc_r1      |          378 |
| range_ieri  |          143 |
| dow         |          133 |
| vol21       |          129 |
| gap_rel     |          113 |
| r63         |          101 |
| dist_sma20  |           98 |
| dist_sma200 |           83 |
| gap         |           82 |
| intra_ieri  |           63 |
| vol5        |           58 |
| r21         |           52 |
| r1          |           43 |
| dist_sma50  |           42 |
| r5          |           40 |
| vol_ratio   |           27 |

## Verifica di robustezza (top 1, costo 0,05% per lato, solo se la stima supera i costi)
- I titoli più scelti sono MARA, RIOT, MDB, SMCI, MSTR e RGTI: titoli volatili e piccoli, dove lo spread reale all'apertura è più alto dello 0,05%.
- Rendimento per anno: +33%, +120%, +267%, -1%, -39%, +91%, -43%, -8% (dal 2019 al 2026). Molto instabile, e negativo negli ultimi due anni.
- Sulle sole 20 mega cap liquide il segnale non resiste: 100 € diventano 84 €.
- Miglior mese +87%, peggior mese -52%. Nessun mese arriva a 500 €.

"""
Laboratorio di strategie "fuori dagli schemi" misurate contro l'obiettivo di Elena:
+10% al giorno composto (100 -> 500 EUR in un mese).

Per ogni strategia: rendimento giornaliero netto (spread inclusi), poi
- % giorni >= +10%, % giorni in perdita
- su tutte le finestre di 21 giorni di borsa: mediana del valore finale di 100 EUR,
  % finestre in guadagno, % finestre che arrivano a 500 EUR (5x)
- valore finale sull'intero periodo.

Strategie:
 1  Gap fade: all'apertura compra il titolo con il gap ribassista piu' forte, vende in chiusura
 2  Gap momentum: compra il titolo con il gap rialzista piu' forte, vende in chiusura
 3  Notte: compra in chiusura i 17 grandi tech, vende all'apertura del giorno dopo
 4  Giorno: il contrario della 3 (compra all'apertura, vende in chiusura)
 5  Opening range breakout (5 min): titolo USA con la prima candela piu' forte, ingresso
    sulla rottura del suo massimo, stop al minimo della prima candela, uscita in chiusura
 6  "Demone di Shannon": 50% Bitcoin / 50% liquidita', ribilanciato ogni giorno
 7  Bitcoin con leva 3x giornaliera (come i prodotti a leva quotati)
 8  Lotteria ottimale: tutto su un evento binario con pagamento 5x (esempio teorico)

Uso:  python3 backtest/strategie.py
"""

import datetime as dtm
from pathlib import Path

import numpy as np
import pandas as pd

import intraday as I
import intraday2 as J
from backtest import fetch

OUT = Path(__file__).parent
TECH17 = ["AAPL", "MSFT", "AMZN", "GOOGL", "META", "INTC", "CSCO", "NVDA", "NFLX",
          "ADBE", "AVGO", "TXN", "QCOM", "ORCL", "IBM", "PYPL", "TSLA"]


def daily_panel():
    J.daily_10y()  # assicura la cache giornaliera
    d = {}
    for f in (OUT / "data" / "1d").glob("*.csv"):
        d[f.stem] = pd.read_csv(f, index_col=0, parse_dates=True)
    return d


def mats(d, names):
    names = [n for n in names if n in d]
    O = pd.DataFrame({t: d[t]["o"] for t in names})
    C = pd.DataFrame({t: d[t]["c"] for t in names}).reindex(O.index)
    return O, C


def summarize(r: pd.Series, label):
    r = r.dropna()
    eq = 100 * (1 + r).cumprod()
    w = (1 + r).rolling(21).apply(np.prod, raw=True).dropna() * 100
    return label, {
        "Giorni": len(r),
        "Periodo": f"{r.index[0]:%Y-%m} -> {r.index[-1]:%Y-%m}",
        "Media giorno": f"{r.mean():+.3%}",
        "Giorni >= +10%": f"{(r >= 0.10).mean():.2%}",
        "Giorni in perdita": f"{(r < 0).mean():.0%}",
        "Mese (21gg): mediana EUR": round(float(w.median()), 1),
        "Mesi in guadagno": f"{(w > 100).mean():.0%}",
        "Mesi a 500 EUR": f"{(w >= 500).mean():.2%}",
        "Finale sul periodo EUR": f"{eq.iloc[-1]:,.0f}",
    }


def gap_strats(d):
    out = []
    for grp, names, hs in (("USA", I.US, I.SPREAD["us"]), ("Europa", I.IT + I.EU, I.SPREAD["eu"])):
        O, C = mats(d, names)
        gap = (O / C.shift(1) - 1).dropna(how="all")
        intraday = (C / O - 1).reindex(gap.index)
        cost = 2 * hs
        dn = gap.idxmin(axis=1)
        up = gap.idxmax(axis=1)
        r_fade = pd.Series([intraday.at[i, t] for i, t in dn.items()], index=dn.index) - cost
        r_mom = pd.Series([intraday.at[i, t] for i, t in up.items()], index=up.index) - cost
        out.append(summarize(r_fade, f"1 Gap fade {grp}"))
        out.append(summarize(r_mom, f"2 Gap momentum {grp}"))
    return out


def night_day(d):
    O, C = mats(d, TECH17)
    cost = 2 * I.SPREAD["us"]
    night = (O / C.shift(1) - 1).mean(axis=1) - cost
    day = (C / O - 1).mean(axis=1) - cost
    return [summarize(night, "3 Notte tech USA"), summarize(day, "4 Giorno tech USA")]


def orb(d5):
    days = sorted({x for v in d5.values() for x in v.index.date if x.weekday() < 5})
    rets = {}
    hs = I.SPREAD["us"]
    for day in days:
        P = I.session_panel(d5, I.US, day, dtm.time(15, 30), dtm.time(21, 55))
        if P is None or len(P["c"]) < 10:
            continue
        o, h, l, c = P["o"], P["h"], P["l"], P["c"]
        first = c[0] / o[0] - 1
        if np.all(np.isnan(first)):
            continue
        t = int(np.nanargmax(first))
        if not first[t] > 0:
            rets[day] = 0.0
            continue
        hi, lo = h[0, t], l[0, t]
        r = 0.0
        for j in range(1, len(c)):
            if h[j, t] > hi:  # rottura: ingresso al massimo della prima candela
                e = hi * (1 + hs)
                x = None
                for k in range(j, len(c)):
                    if l[k, t] <= lo:
                        x = lo * (1 - hs)
                        break
                x = x or c[-1, t] * (1 - hs)
                r = x / e - 1
                break
        rets[day] = r
    return [summarize(pd.Series(rets, index=pd.to_datetime(list(rets))), "5 Opening range breakout USA (5 min)")]


def crypto():
    btc = fetch("BTC-EUR").loc["2016-01-01":]
    r = btc.pct_change().dropna()
    fee = 0.0009 + 0.0005
    shannon = 0.5 * r - fee * 0.5 * r.abs()  # ribilancio giornaliero: si scambia ~meta' della variazione
    lev = (3 * r - 3 * fee * r.abs()).clip(lower=-1)
    out = [summarize(r, "   Bitcoin comprato e tenuto"), summarize(shannon, "6 Demone di Shannon BTC/liquidita'")]
    out.append(summarize(lev, "7 Bitcoin leva 3x giornaliera"))
    return out


def lottery():
    # evento binario: 20% di probabilita' di moltiplicare per 5, 80% di perdere tutto
    rng = np.random.default_rng(0)
    wins = rng.random(100000) < 0.2
    return [("8 Lotteria ottimale (teorica, 1 giocata al mese)", {
        "Giorni": "-", "Periodo": "simulazione", "Media giorno": "-", "Giorni >= +10%": "-",
        "Giorni in perdita": "-", "Mese (21gg): mediana EUR": 0.0, "Mesi in guadagno": f"{wins.mean():.0%}",
        "Mesi a 500 EUR": f"{wins.mean():.0%}", "Finale sul periodo EUR": "0 dopo pochi mesi",
    })]


def main():
    d = daily_panel()
    d5 = {t: J.fetch_5m(t) for t in I.US}
    rows = gap_strats(d) + night_day(d) + orb(d5) + crypto() + lottery()
    df = pd.DataFrame(dict(rows)).T
    text = "# Laboratorio strategie contro l'obiettivo +10% al giorno\n\n" + df.to_markdown() + "\n"
    (OUT / "risultati_strategie.md").write_text(text)
    print(text)


if __name__ == "__main__":
    main()

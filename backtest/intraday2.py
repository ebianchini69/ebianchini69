"""
Variante richiesta da Elena: guadagno +0,5% / perdita -0,5% per operazione, e obiettivo
"tornare a casa con 101": si smette appena il giorno e' a +1% (o +0,5%), con o senza
perdita massima giornaliera dell'1%.

Tre livelli di dati:
  A) candele da 1 minuto, ultimi ~20 giorni di borsa (100 titoli)
  B) candele da 5 minuti, ultimi ~60 giorni di borsa (100 titoli)
  C) dati giornalieri, 10 anni: una sola operazione al giorno all'apertura sul titolo con il
     gap di apertura piu' alto. Con candele giornaliere non si sa se viene toccato prima il +0,5%
     o il -0,5%: si riportano entrambi i casi (prudente e ottimistico) e quanto spesso capita.

Uso:  python3 backtest/intraday2.py
"""

import datetime as dtm
import json
import random
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

import intraday as I
from backtest import fetch

OUT = Path(__file__).parent


def fetch_5m(t):
    f = OUT / "data" / "5m" / f"{t}.csv"
    f.parent.mkdir(parents=True, exist_ok=True)
    if f.exists() and time.time() - f.stat().st_mtime < 12 * 3600:
        return pd.read_csv(f, index_col=0, parse_dates=True)
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{t}?range=60d&interval=5m"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        r = json.load(urllib.request.urlopen(req, timeout=20))["chart"]["result"][0]
        q = r["indicators"]["quote"][0]
        idx = pd.to_datetime(r["timestamp"], unit="s", utc=True).tz_convert("Europe/Rome").tz_localize(None)
        df = pd.DataFrame({"o": q["open"], "h": q["high"], "l": q["low"], "c": q["close"]}, index=idx).dropna()
    except Exception:
        df = pd.DataFrame(columns=list("ohlc"))
    df = df[~df.index.duplicated()].sort_index()
    df.to_csv(f)
    return df


def build_panels(data, days):
    pn = {}
    for day in days:
        pn[(day, "eu")] = I.session_panel(data, I.IT + I.EU, day, dtm.time(9, 0), dtm.time(15, 25))
        pn[(day, "us")] = I.session_panel(data, I.US, day, dtm.time(15, 30), dtm.time(21, 55))
    return pn


def grid(data, label, bar_minutes):
    days = sorted({d for v in data.values() for d in v.index.date if d.weekday() < 5})
    pn = build_panels(data, days)
    rows = {}
    for markets, ml in ((("eu",), "Europa"), (("us",), "USA"), (("eu", "us"), "Eur+USA")):
        for wmin in (5, 15, 30):
            for dt_, dtl in ((None, "nessuno"), (0.005, "+0,5%"), (0.01, "+1%")):
                for ds, dsl in ((None, "no"), (0.01, "-1%")):
                    r = I.simulate(data, days, max(1, wmin // bar_minutes), 0.005, markets, tp=0.005,
                                   day_target=dt_, day_stop=ds, pn=pn)
                    rows[f"{ml} | {wmin}min | stop giorno a {dtl} | perdita max {dsl}"] = r
    df = pd.DataFrame(rows).T.sort_values("Finale EUR", ascending=False)
    finals = df["Finale EUR"].astype(float)
    best = df.index[0]
    # controllo casuale sulla configurazione migliore
    parts = best.split(" | ")
    markets = {"Europa": ("eu",), "USA": ("us",), "Eur+USA": ("eu", "us")}[parts[0]]
    wmin = int(parts[1].replace("min", ""))
    dt_ = {"nessuno": None, "+0,5%": 0.005, "+1%": 0.01}[parts[2].split(" a ")[1]]
    ds = {"no": None, "-1%": 0.01}[parts[3].split(" ")[-1]]
    rnd = [I.simulate(data, days, max(1, wmin // bar_minutes), 0.005, markets, pick="random", seed=s, tp=0.005,
                      day_target=dt_, day_stop=ds, pn=pn)["Finale EUR"] for s in range(20)]
    head = (f"\n## {label}: {len(days)} giorni ({days[0]} -> {days[-1]}), {len(data)} titoli\n\n"
            f"{len(df)} configurazioni: mediana {finals.median():.2f} EUR, min {finals.min():.2f}, max {finals.max():.2f}. "
            f"Stessa config della migliore ma titolo a caso (20 prove): media {np.mean(rnd):.2f} EUR "
            f"(min {min(rnd):.2f}, max {max(rnd):.2f}).\n\nLe 10 migliori e le 5 peggiori:\n\n")
    return head + pd.concat([df.head(10), df.tail(5)]).to_markdown() + "\n"


def daily_10y():
    tickers = I.US + I.IT + I.EU
    out = {}
    for t in tickers:
        try:
            url = (f"https://query1.finance.yahoo.com/v8/finance/chart/{t}?period1=1451606400"
                   f"&period2={int(time.time())}&interval=1d")
            f = OUT / "data" / "1d" / f"{t}.csv"
            f.parent.mkdir(parents=True, exist_ok=True)
            if f.exists():
                out[t] = pd.read_csv(f, index_col=0, parse_dates=True)
                continue
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            r = json.load(urllib.request.urlopen(req, timeout=20))["chart"]["result"][0]
            q = r["indicators"]["quote"][0]
            idx = pd.to_datetime(r["timestamp"], unit="s").normalize()
            df = pd.DataFrame({"o": q["open"], "h": q["high"], "l": q["low"], "c": q["close"]}, index=idx).dropna()
            df = df[~df.index.duplicated(keep="last")]
            df.to_csv(f)
            out[t] = df
        except Exception:
            pass
    res = {}
    for group, names, hs in (("Europa", I.IT + I.EU, I.SPREAD["eu"]), ("USA", I.US, I.SPREAD["us"])):
        O = pd.DataFrame({t: out[t]["o"] for t in names if t in out})
        H = pd.DataFrame({t: out[t]["h"] for t in names if t in out}).reindex(O.index)
        L = pd.DataFrame({t: out[t]["l"] for t in names if t in out}).reindex(O.index)
        C = pd.DataFrame({t: out[t]["c"] for t in names if t in out}).reindex(O.index)
        gap = O / C.shift(1) - 1
        gap = gap.dropna(how="all")
        pick = gap.idxmax(axis=1).dropna()
        rets = {"prudente": [], "ottimistico": []}
        both = 0
        for d, t in pick.items():
            e = O.at[d, t] * (1 + hs)
            up, dn = H.at[d, t] >= e * 1.005, L.at[d, t] <= e * 0.995
            both += up and dn
            close_r = C.at[d, t] * (1 - hs) / e - 1
            for k in rets:
                if up and dn:
                    r = -0.005 - hs if k == "prudente" else 0.005
                elif up:
                    r = 0.005
                elif dn:
                    r = -0.005 - hs
                else:
                    r = close_r
                rets[k].append(r)
        for k, v in rets.items():
            v = np.array(v)
            eq = 100 * np.cumprod(1 + v)
            res[f"{group} | {k}"] = {
                "Giorni": len(v), "Finale EUR": round(eq[-1], 2), "Media giorno": f"{v.mean():+.3%}",
                "Giorni in perdita": f"{(v < 0).mean():.0%}",
                "Giorni con +0,5% e -0,5% entrambi toccati": f"{both / len(v):.0%}",
            }
    return f"\n## Dati giornalieri dal 2016: 1 operazione al giorno sul gap d'apertura piu' alto\n\n" + pd.DataFrame(res).T.to_markdown() + "\n"


def main():
    d1 = I.load()
    with ThreadPoolExecutor(8) as ex:
        d5 = dict(zip(I.US + I.IT + I.EU, ex.map(fetch_5m, I.US + I.IT + I.EU)))
    d5 = {k: v for k, v in d5.items() if len(v) > 500}
    text = "# Guadagno +0,5% / perdita -0,5% con obiettivo giornaliero (capitale 100 EUR)\n"
    text += grid(d1, "A) Candele da 1 minuto", 1)
    I.PANELS.clear()
    text += grid(d5, "B) Candele da 5 minuti", 5)
    text += daily_10y()
    (OUT / "risultati_intraday2.md").write_text(text)
    print(text)


if __name__ == "__main__":
    main()

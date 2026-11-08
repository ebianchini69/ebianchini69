"""
Sistema multivariato (machine learning) per il trading giornaliero sulle azioni USA.

Ogni giorno, all'apertura, il modello stima il rendimento apertura -> chiusura di ciascuno
dei ~60 titoli USA usando solo informazioni disponibili in quel momento:
  titolo:   gap di apertura (assoluto e relativo al mercato), rendimenti 1/5/21/63 giorni,
            rendimento intraday di ieri, volatilita' 5/21 giorni, escursione di ieri,
            distanza dalle medie mobili 20/50/200, volume di ieri rispetto alla media 20 giorni
  mercato:  gap medio di tutti i titoli, rendimento medio di ieri e degli ultimi 5 giorni
  altri:    VIX (livello e variazione), rendimento di Bitcoin del giorno prima
  calendario: giorno della settimana
Poi compra i titoli con la stima migliore (solo se supera i costi) e vende in chiusura.

Validazione walk-forward: per ogni anno dal 2019 il modello e' addestrato solo sugli anni
precedenti e valutato sull'anno che non ha mai visto. Nessuna informazione dal futuro.

Uso:  python3 backtest/multivariato.py
"""

import json
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import lightgbm as lgb
import numpy as np
import pandas as pd

import intraday as I

OUT = Path(__file__).parent
CACHE = OUT / "data" / "1dv"


def fetch_daily(t):
    CACHE.mkdir(parents=True, exist_ok=True)
    f = CACHE / f"{t}.csv"
    if f.exists() and time.time() - f.stat().st_mtime < 24 * 3600:
        return pd.read_csv(f, index_col=0, parse_dates=True)
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{t}?period1=1420070400&period2={int(time.time())}&interval=1d"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        r = json.load(urllib.request.urlopen(req, timeout=20))["chart"]["result"][0]
        q = r["indicators"]["quote"][0]
        idx = pd.to_datetime(r["timestamp"], unit="s").normalize()
        df = pd.DataFrame({"o": q["open"], "h": q["high"], "l": q["low"], "c": q["close"], "v": q["volume"]}, index=idx)
        df = df.dropna()
        df = df[(df[["o", "h", "l", "c"]] > 0).all(axis=1)]
        df = df[~df.index.duplicated(keep="last")]
    except Exception:
        df = pd.DataFrame(columns=list("ohlcv"))
    df.to_csv(f)
    return df


def build():
    with ThreadPoolExecutor(8) as ex:
        raw = dict(zip(I.US, ex.map(fetch_daily, I.US)))
    vix = fetch_daily("^VIX")["c"]
    btc = fetch_daily("BTC-USD")["c"]
    O = pd.DataFrame({t: d["o"] for t, d in raw.items() if len(d)})
    H = pd.DataFrame({t: d["h"] for t, d in raw.items() if len(d)}).reindex(O.index)
    L = pd.DataFrame({t: d["l"] for t, d in raw.items() if len(d)}).reindex(O.index)
    C = pd.DataFrame({t: d["c"] for t, d in raw.items() if len(d)}).reindex(O.index)
    V = pd.DataFrame({t: d["v"] for t, d in raw.items() if len(d)}).reindex(O.index)
    # gli split rendono i gap enormi e falsi: le variazioni giornaliere oltre il 60% si scartano
    r = C.pct_change()
    gap = O / C.shift(1) - 1
    bad = (gap.abs() > 0.6) | (r.abs() > 0.6)
    y = C / O - 1  # obiettivo: rendimento apertura -> chiusura di oggi

    f = {}
    f["gap"] = gap
    f["gap_rel"] = gap.sub(gap.mean(axis=1), axis=0)
    for n in (1, 5, 21, 63):
        f[f"r{n}"] = C.shift(1) / C.shift(1 + n) - 1
    f["intra_ieri"] = (C / O - 1).shift(1)
    f["vol5"] = r.rolling(5).std().shift(1)
    f["vol21"] = r.rolling(21).std().shift(1)
    f["range_ieri"] = ((H - L) / C).shift(1)
    for n in (20, 50, 200):
        f[f"dist_sma{n}"] = (C / C.rolling(n).mean() - 1).shift(1)
    f["vol_ratio"] = (V / V.rolling(20).mean()).shift(1)
    mkt = {
        "mkt_gap": gap.mean(axis=1),
        "mkt_r1": r.mean(axis=1).shift(1),
        "mkt_r5": (C.shift(1) / C.shift(6) - 1).mean(axis=1),
        "vix": vix.reindex(O.index).ffill().shift(1),
        "vix_chg": vix.pct_change().reindex(O.index).ffill().shift(1),
        "btc_r1": btc.pct_change().reindex(O.index).ffill().shift(1),
        "dow": pd.Series(O.index.dayofweek, index=O.index),
    }
    rows = []
    for name, df in f.items():
        rows.append(df.stack(future_stack=True).rename(name))
    X = pd.concat(rows, axis=1)
    X["y"] = y.stack(future_stack=True)
    X["bad"] = bad.stack(future_stack=True)
    X = X.reset_index(names=["date", "ticker"])
    for k, s in mkt.items():
        X[k] = X["date"].map(s)
    X = X[~X["bad"].astype(bool)].drop(columns="bad").dropna()
    return X


FEATURES = None


def walk_forward(X):
    global FEATURES
    FEATURES = [c for c in X.columns if c not in ("date", "ticker", "y")]
    preds = []
    for year in range(2019, X["date"].dt.year.max() + 1):
        train = X[X["date"].dt.year < year]
        test = X[X["date"].dt.year == year]
        m = lgb.LGBMRegressor(n_estimators=300, learning_rate=0.03, num_leaves=15, min_child_samples=200,
                              subsample=0.8, subsample_freq=1, colsample_bytree=0.8, verbose=-1)
        m.fit(train[FEATURES], train["y"].clip(-0.1, 0.1))
        t = test[["date", "ticker", "y"]].copy()
        t["pred"] = m.predict(test[FEATURES])
        preds.append(t)
        if year == X["date"].dt.year.max():
            imp = pd.Series(m.feature_importances_, index=FEATURES).sort_values(ascending=False)
    return pd.concat(preds), imp


def evaluate(P, k, cost_side, only_positive):
    out = []
    for d, g in P.groupby("date"):
        g = g.nlargest(k, "pred")
        if only_positive:
            g = g[g["pred"] > 2 * cost_side]
        out.append((d, (g["y"].mean() - 2 * cost_side) if len(g) else 0.0))
    s = pd.Series(dict(out)).sort_index()
    w = (1 + s).rolling(21).apply(np.prod, raw=True).dropna() * 100
    yearly = (1 + s).groupby(s.index.year).prod() - 1
    return {
        "Media giorno": f"{s.mean():+.3%}",
        "Giorni >= +10%": f"{(s >= 0.10).mean():.2%}",
        "Giorni in perdita": f"{(s < 0).mean():.0%}",
        "Giorni fermi (nessun acquisto)": f"{(s == 0).mean():.0%}",
        "Mese tipico EUR": round(float(w.median()), 1),
        "Mesi in guadagno": f"{(w > 100).mean():.0%}",
        "Mesi a 500 EUR": f"{(w >= 500).mean():.2%}",
        "Anni positivi": f"{(yearly > 0).sum()}/{len(yearly)}",
        "100 EUR dal 2019 diventano": f"{100 * (1 + s).prod():,.0f}",
    }


def main():
    X = build()
    P, imp = walk_forward(X)
    ic = P.groupby("date").apply(lambda g: g["pred"].corr(g["y"], method="spearman")).mean()
    rows = {}
    for cost in (0.0005, 0.001):
        for k in (1, 3, 5):
            for pos in (False, True):
                lab = f"top {k} | costo {cost:.2%}/lato | " + ("solo se stima > costi" if pos else "sempre")
                rows[lab] = evaluate(P, k, cost, pos)
    # controllo: tutti i titoli a pesi uguali ogni giorno (nessuna previsione)
    base = P.groupby("date")["y"].mean() - 0.001
    rows["CONTROLLO: tutti i titoli, nessun modello"] = evaluate(
        P.assign(pred=0.0).groupby("date").head(100), 100, 0.0005, False)
    text = (
        f"# Sistema multivariato (LightGBM, {len(FEATURES)} segnali), test fuori campione 2019 -> oggi\n\n"
        f"Osservazioni: {len(X):,} (titolo x giorno). Correlazione media di rango previsione/realta' (IC): {ic:.3f}\n\n"
        + pd.DataFrame(rows).T.to_markdown()
        + "\n\nSegnali piu' usati dal modello (ultimo anno):\n\n"
        + imp.to_frame("importanza").to_markdown() + "\n"
    )
    (OUT / "risultati_multivariato.md").write_text(text)
    print(text)


if __name__ == "__main__":
    main()

"""
Backtest portafoglio misto: ETF tradizionale (S&P 500 UCITS, EUR) + crypto (BTC in EUR).

Regole fissate PRIMA di guardare i risultati (niente ottimizzazione dei parametri):
- Capitale iniziale 100 EUR, frazioni di quota ammesse.
- Segnale calcolato sulla chiusura del giorno t-1, eseguito alla chiusura del giorno t
  (nessuna informazione dal futuro).
- Trend filter: si tiene l'asset solo se il prezzo e' sopra la media mobile a 200 giorni
  di trading (ETF) / 200 giorni di calendario (crypto, che scambia 7 giorni su 7);
  altrimenti quella quota resta in liquidita' (rendimento 0, ipotesi prudente).
- Pesi a volatilita' inversa: volatilita' realizzata a 90 giorni, pesi ricalcolati
  ogni mese.
- Ribilanciamento mensile (primo giorno di borsa del mese) + quando cambia un segnale.
  Si opera solo se lo scostamento dal peso obiettivo supera il 5% del portafoglio,
  oppure se cambia un segnale.
- Costi: due scenari (vedi COST_SCENARIOS).

Uso:  python3 backtest/backtest.py
"""

import json
import time
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

OUT = Path(__file__).parent
START = "2018-01-01"
CAPITAL = 100.0

ASSETS = {
    "ETF": "SXR8.DE",  # iShares Core S&P 500 UCITS ETF (Acc), Xetra, EUR
    "CRYPTO": "BTC-EUR",
}

# Costi per operazione: commissione percentuale con minimo in EUR + mezzo spread.
COST_SCENARIOS = {
    "costi_bassi": {  # broker low-cost / ordini oltre la soglia del minimo
        "ETF": {"pct": 0.0010, "min": 0.0, "half_spread": 0.0005},
        "CRYPTO": {"pct": 0.0009, "min": 0.0, "half_spread": 0.0005},  # Revolut X taker
    },
    "costi_revolut_standard": {  # 0,25% con minimo 1 EUR sulle azioni/ETF oltre la quota gratuita
        "ETF": {"pct": 0.0025, "min": 1.0, "half_spread": 0.0005},
        "CRYPTO": {"pct": 0.0009, "min": 0.0, "half_spread": 0.0005},
    },
}


def fetch(ticker: str) -> pd.Series:
    cache = OUT / "data" / f"{ticker}.csv"
    if cache.exists() and time.time() - cache.stat().st_mtime < 12 * 3600:
        s = pd.read_csv(cache, index_col=0, parse_dates=True).iloc[:, 0]
        return s
    url = (
        f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
        f"?period1=1262304000&period2={int(time.time())}&interval=1d&events=div,split"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    d = json.load(urllib.request.urlopen(req, timeout=20))["chart"]["result"][0]
    idx = pd.to_datetime(d["timestamp"], unit="s").normalize()
    adj = d["indicators"].get("adjclose", [{}])[0].get("adjclose") or d["indicators"]["quote"][0]["close"]
    s = pd.Series(adj, index=idx, name=ticker, dtype=float).dropna()
    s = s[~s.index.duplicated(keep="last")]
    cache.parent.mkdir(exist_ok=True)
    s.to_csv(cache)
    return s


def load_prices():
    raw = {k: fetch(t) for k, t in ASSETS.items()}
    cal = pd.date_range(START, max(s.index.max() for s in raw.values()), freq="D")
    px = pd.DataFrame({k: s.reindex(cal).ffill() for k, s in raw.items()}).dropna()
    # giorni in cui ciascun mercato era effettivamente aperto
    open_ = pd.DataFrame({k: px.index.isin(s.index) for k, s in raw.items()}, index=px.index)
    # segnali sui dati nativi di ciascun asset, poi riportati sul calendario comune
    trend, vol = {}, {}
    for k, s in raw.items():
        trend[k] = (s > s.rolling(200).mean()).reindex(cal).ffill()
        r = s.pct_change()
        ann = np.sqrt(252 if k == "ETF" else 365)
        vol[k] = (r.rolling(90).std() * ann).reindex(cal).ffill()
    trend = pd.DataFrame(trend).loc[px.index].fillna(False).astype(bool)
    vol = pd.DataFrame(vol).loc[px.index]
    return px, open_, trend, vol


def target_weights(strategy, date, trend_prev, vol_prev):
    if strategy["alloc"] == "fixed":
        w = pd.Series(strategy["weights"], dtype=float)
    else:  # volatilita' inversa
        iv = 1.0 / vol_prev
        w = iv / iv.sum()
    if strategy["trend"]:
        w = w * trend_prev.astype(float)  # la quota fuori trend resta in liquidita'
    return w


def run(strategy, px, open_, trend, vol, costs):
    cash, units = CAPITAL, pd.Series(0.0, index=px.columns)
    fees_paid, n_trades = 0.0, 0
    hist = []
    prev_month, prev_sig = None, None
    for i, date in enumerate(px.index):
        p = px.loc[date]
        value = cash + (units * p).sum()
        if i == 0:
            hist.append(value)
            continue
        t_prev, v_prev = trend.iloc[i - 1], vol.iloc[i - 1]
        sig = tuple(t_prev) if strategy["trend"] else None
        new_month = date.month != prev_month and bool(open_.loc[date, "ETF"])
        sig_change = prev_sig is not None and sig != prev_sig
        if (new_month or sig_change or i == 1) and not v_prev.isna().any():
            w = target_weights(strategy, date, t_prev, v_prev)
            cur_w = units * p / value
            for k in px.columns:
                if not open_.loc[date, k]:
                    continue  # mercato chiuso (ETF nel weekend): si riprova al prossimo giorno utile
                diff = w[k] - cur_w[k]
                flip = sig_change and (t_prev[k] != trend.iloc[i - 2][k] if i >= 2 else False)
                if abs(diff) < 0.05 and not flip and i != 1:
                    continue
                notional = diff * value
                if abs(notional) < 0.01:
                    continue
                c = costs[k]
                fee = max(c["min"], c["pct"] * abs(notional)) + c["half_spread"] * abs(notional)
                if notional > 0:  # acquisto: la commissione si paga dalla liquidita'
                    notional = min(notional, cash - fee)
                    if notional <= 0:
                        continue
                units[k] += notional / p[k]
                cash -= notional + fee
                fees_paid += fee
                n_trades += 1
            if new_month:
                prev_month = date.month
        prev_sig = sig
        hist.append(cash + (units * p).sum())
    eq = pd.Series(hist, index=px.index)
    return eq, fees_paid, n_trades


def stats(eq, fees, trades):
    r = eq.pct_change().dropna()
    years = (eq.index[-1] - eq.index[0]).days / 365.25
    cagr = (eq.iloc[-1] / eq.iloc[0]) ** (1 / years) - 1
    vol = r.std() * np.sqrt(365)
    dd = (eq / eq.cummax() - 1).min()
    yearly = eq.resample("YE").last().pct_change()
    yearly.iloc[0] = eq.resample("YE").last().iloc[0] / eq.iloc[0] - 1
    return {
        "Finale EUR": round(eq.iloc[-1], 2),
        "Rend. annuo": f"{cagr:.1%}",
        "Volatilita'": f"{vol:.1%}",
        "Max drawdown": f"{dd:.1%}",
        "Sharpe (rf=0)": round((r.mean() * 365) / (r.std() * np.sqrt(365)), 2),
        "Anno peggiore": f"{yearly.min():.1%}",
        "Operazioni": trades,
        "Costi EUR": round(fees, 2),
    }, yearly


STRATEGIES = {
    "B&H 100% S&P 500": {"alloc": "fixed", "weights": {"ETF": 1.0, "CRYPTO": 0.0}, "trend": False},
    "B&H 100% BTC": {"alloc": "fixed", "weights": {"ETF": 0.0, "CRYPTO": 1.0}, "trend": False},
    "50/50 ribil. mensile": {"alloc": "fixed", "weights": {"ETF": 0.5, "CRYPTO": 0.5}, "trend": False},
    "Vol. inversa ribil. mensile": {"alloc": "invvol", "trend": False},
    "50/50 + trend filter": {"alloc": "fixed", "weights": {"ETF": 0.5, "CRYPTO": 0.5}, "trend": True},
    "Vol. inversa + trend filter": {"alloc": "invvol", "trend": True},
}


def main():
    px, open_, trend, vol = load_prices()
    # i primi 200 giorni servono a calcolare la media mobile: il backtest parte dopo
    first = max(trend.index[0], vol.dropna().index[0])
    px, open_, trend, vol = (x.loc[first:] for x in (px, open_, trend, vol))

    report = [f"Periodo: {px.index[0].date()} -> {px.index[-1].date()}  |  capitale iniziale {CAPITAL:.0f} EUR\n"]
    curves, yearly_tables = {}, {}
    for scen, costs in COST_SCENARIOS.items():
        rows = {}
        for name, strat in STRATEGIES.items():
            eq, fees, n = run(strat, px, open_, trend, vol, costs)
            rows[name], yr = stats(eq, fees, n)
            if scen == "costi_bassi":
                curves[name] = eq
                yearly_tables[name] = yr
        df = pd.DataFrame(rows).T
        report.append(f"\n## Scenario: {scen}\n\n" + df.to_markdown() + "\n")

    yt = pd.DataFrame(yearly_tables)
    yt.index = yt.index.year
    report.append("\n## Rendimento per anno (scenario costi bassi)\n\n" + yt.map(lambda x: f"{x:.0%}").to_markdown() + "\n")

    # peso medio a volatilita' inversa
    iv = 1 / vol
    w = iv.div(iv.sum(axis=1), axis=0)
    report.append(
        f"\nPeso medio crypto con volatilita' inversa: {w['CRYPTO'].mean():.0%} "
        f"(min {w['CRYPTO'].min():.0%}, max {w['CRYPTO'].max():.0%}); "
        f"volatilita' media annua ETF {vol['ETF'].mean():.0%}, BTC {vol['CRYPTO'].mean():.0%}\n"
    )
    # test fuori campione: due sotto-periodi separati
    for a, b in (("2018-08-01", "2022-12-31"), ("2023-01-01", None)):
        sl = slice(a, b)
        rows = {}
        for name, strat in STRATEGIES.items():
            eq, fees, n = run(strat, px.loc[sl], open_.loc[sl], trend.loc[sl], vol.loc[sl], COST_SCENARIOS["costi_bassi"])
            rows[name] = stats(eq, fees, n)[0]
        report.append(f"\n## Sotto-periodo {a} -> {b or 'oggi'} (costi bassi)\n\n" + pd.DataFrame(rows).T.to_markdown() + "\n")

    text = "".join(report)
    (OUT / "risultati.md").write_text(text)
    print(text)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(11, 6))
    for name, eq in curves.items():
        ax.plot(eq.index, eq.values, label=name, lw=2.2 if "trend" in name else 1.2)
    ax.set_yscale("log")
    ax.set_ylabel("Valore portafoglio (EUR, scala log)")
    ax.set_title("100 EUR investiti - S&P 500 UCITS + BTC, scenario costi bassi")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "equity.png", dpi=130)


if __name__ == "__main__":
    main()

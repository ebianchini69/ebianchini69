"""
Backtest su singole azioni: Piazza Affari (grandi capitalizzazioni) e tech USA (Nasdaq/NYSE).

Universo scelto "come a fine 2017": i grandi nomi di allora, inclusi quelli andati male
(Telecom Italia, Saipem, Intel, IBM, PayPal...), per non scegliere i vincitori col senno di poi.
Restano esclusi i titoli poi tolti dal listino (Atlantia, Luxottica, CNH, Exor), di cui Yahoo
non ha piu' i dati: questo favorisce un po' le strategie su singoli titoli.

Strategie (decise prima di vedere i risultati):
- ETF indice comprato e tenuto (iShares FTSE MIB / Invesco Nasdaq-100, entrambi in EUR).
- Equipesato: tutti i titoli con lo stesso peso, ribilanciamento mensile.
- Momentum top 5: ogni mese i 5 titoli col rendimento migliore negli ultimi 12 mesi
  escluso l'ultimo (classico "12-1"), pesi uguali.
- Momentum top 5 + trend filter: come sopra, ma tutto in liquidita' quando l'ETF indice
  e' sotto la media mobile a 200 giorni.
Segnali calcolati con i dati fino al giorno prima, esecuzione alla chiusura.
Titoli USA convertiti in EUR al cambio giornaliero (costo del cambio non incluso).

Uso:  python3 backtest/backtest_azioni.py
"""

from pathlib import Path

import numpy as np
import pandas as pd

from backtest import CAPITAL, fetch

OUT = Path(__file__).parent
START = "2018-01-01"
TOP_N = 5
THRESHOLD = 0.02  # si opera solo se lo scostamento supera il 2% del portafoglio

UNIVERSES = {
    "Italia (FTSE MIB)": {
        "etf": "IMIB.MI",
        "usd": False,
        "tickers": [
            "ENI.MI", "ENEL.MI", "ISP.MI", "UCG.MI", "G.MI", "TIT.MI", "STLAM.MI", "RACE.MI",
            "SRG.MI", "TRN.MI", "PST.MI", "MB.MI", "MONC.MI", "PRY.MI", "STMMI.MI", "LDO.MI",
            "TEN.MI", "PIRC.MI", "SPM.MI", "BAMI.MI", "BMED.MI", "A2A.MI", "REC.MI",
        ],
    },
    "Tech USA": {
        "etf": "EQQQ.DE",
        "usd": True,
        "tickers": [
            "AAPL", "MSFT", "AMZN", "GOOGL", "META", "INTC", "CSCO", "NVDA", "NFLX",
            "ADBE", "AVGO", "TXN", "QCOM", "ORCL", "IBM", "PYPL", "TSLA",
        ],
    },
}

COSTS = {
    "costi_bassi": {"pct": 0.0010, "min": 0.0, "half_spread": 0.0005},
    "costi_revolut_standard": {"pct": 0.0025, "min": 1.0, "half_spread": 0.0005},
}


def load(universe):
    stocks = pd.DataFrame({t: fetch(t) for t in universe["tickers"]})
    stocks = stocks[stocks.index.dayofweek < 5].sort_index()
    if universe["usd"]:
        fx = fetch("EURUSD=X").reindex(stocks.index).ffill()  # USD per 1 EUR
        stocks = stocks.div(fx, axis=0)
    etf = fetch(universe["etf"]).reindex(stocks.index).ffill()
    stocks = stocks.ffill(limit=5)
    return stocks, etf


def run(stocks, etf, mode, cost):
    px = stocks.loc[START:]
    etf_px = etf.loc[START:]
    trend_ok = (etf > etf.rolling(200).mean()).shift(1).loc[START:]
    mom = (stocks.shift(21) / stocks.shift(252) - 1).shift(1).loc[START:]  # dati fino a ieri

    cols = list(px.columns) + ["ETF"]
    units = pd.Series(0.0, index=cols)
    cash, fees, trades = CAPITAL, 0.0, 0
    hist, prev_month = [], None
    for date in px.index:
        p = pd.concat([px.loc[date], pd.Series({"ETF": etf_px.loc[date]})]).fillna(0.0)
        value = cash + (units * p).sum()
        if date.month != prev_month:
            prev_month = date.month
            w = pd.Series(0.0, index=cols)
            avail = px.loc[date].dropna().index
            if mode == "etf":
                w["ETF"] = 1.0
            elif mode == "equal":
                w[avail] = 1.0 / len(avail)
            else:
                m = mom.loc[date, avail].dropna()
                top = m.nlargest(TOP_N).index
                if mode == "momentum" or bool(trend_ok.loc[date]):
                    w[top] = 1.0 / len(top)
            cur = units * p / value
            # prima le vendite (liberano liquidita'), poi gli acquisti
            for k in sorted(cols, key=lambda k: w[k] - cur[k]):
                diff = w[k] - cur[k]
                if abs(diff) < THRESHOLD and not (w[k] == 0 and units[k] > 0):
                    continue
                if p[k] <= 0:
                    continue
                notional = diff * value
                fee = max(cost["min"], cost["pct"] * abs(notional)) + cost["half_spread"] * abs(notional)
                full_exit = w[k] == 0 and units[k] > 0
                if fee > 0.10 * abs(notional) and not full_exit:
                    continue  # nessun trader sensato paga piu' del 10% di commissione
                if full_exit and fee >= abs(notional):
                    continue  # posizione troppo piccola anche per uscire: resta in portafoglio
                if notional > 0:
                    notional = min(notional, cash - fee)
                    if notional <= 0:
                        continue
                units[k] += notional / p[k]
                cash -= notional + fee
                fees += fee
                trades += 1
        hist.append(cash + (units * p).sum())
    return pd.Series(hist, index=px.index), fees, trades


def stats(eq, fees, trades):
    r = eq.pct_change().dropna()
    years = (eq.index[-1] - eq.index[0]).days / 365.25
    yearly = eq.resample("YE").last().pct_change()
    yearly.iloc[0] = eq.resample("YE").last().iloc[0] / eq.iloc[0] - 1
    return {
        "Finale EUR": round(eq.iloc[-1], 2),
        "Rend. annuo": f"{(eq.iloc[-1] / eq.iloc[0]) ** (1 / years) - 1:.1%}",
        "Volatilita'": f"{r.std() * np.sqrt(252):.1%}",
        "Max drawdown": f"{(eq / eq.cummax() - 1).min():.1%}",
        "Sharpe (rf=0)": round(r.mean() / r.std() * np.sqrt(252), 2),
        "Anno peggiore": f"{yearly.min():.1%}",
        "Operazioni": trades,
        "Costi EUR": round(fees, 2),
    }, yearly


MODES = {
    "ETF indice (compra e tieni)": "etf",
    "Equipesato, ribil. mensile": "equal",
    f"Momentum top {TOP_N}": "momentum",
    f"Momentum top {TOP_N} + trend filter": "momentum_trend",
}


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    out = []
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))
    for ax, (uname, u) in zip(axes, UNIVERSES.items()):
        stocks, etf = load(u)
        out.append(f"\n# {uname}  ({len(u['tickers'])} titoli, benchmark {u['etf']})\n")
        for cname, cost in COSTS.items():
            rows, yearly = {}, {}
            for label, mode in MODES.items():
                eq, fees, n = run(stocks, etf, mode, cost)
                rows[label], yearly[label] = stats(eq, fees, n)
                if cname == "costi_bassi":
                    ax.plot(eq.index, eq.values, label=label, lw=2 if "ETF" in label else 1.3)
            out.append(f"\n## {cname}\n\n" + pd.DataFrame(rows).T.to_markdown() + "\n")
            if cname == "costi_bassi":
                yt = pd.DataFrame(yearly)
                yt.index = yt.index.year
                out.append("\nRendimento per anno (costi bassi):\n\n" + yt.map(lambda x: f"{x:.0%}").to_markdown() + "\n")
        # titoli scelti dal momentum nell'ultimo mese, per trasparenza
        mom = (stocks.shift(21) / stocks.shift(252) - 1).iloc[-1].dropna().nlargest(TOP_N)
        out.append("\nTop momentum oggi: " + ", ".join(f"{k} {v:+.0%}" for k, v in mom.items()) + "\n")
        ax.set_title(f"{uname}: 100 EUR dal 2018 (costi bassi)")
        ax.set_yscale("log")
        ax.grid(alpha=0.3)
        ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "equity_azioni.png", dpi=130)

    text = f"Periodo dal {START} a oggi, capitale {CAPITAL:.0f} EUR\n" + "".join(out)
    (OUT / "risultati_azioni.md").write_text(text)
    print(text)


if __name__ == "__main__":
    main()

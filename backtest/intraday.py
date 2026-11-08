"""
Test della strategia "apertura + scalping 1%" su dati al minuto (ultime ~4 settimane, Yahoo).

Regole (proposte da Elena):
- all'apertura di ogni mercato si guarda un radar di ~100 titoli;
- dopo i primi W minuti si compra il titolo con la crescita maggiore dall'apertura;
- si vende appena guadagna l'1% (ordine limite), poi si ricompra subito il titolo che
  in quel momento cresce di piu' dall'apertura, e cosi' via fino a fine sessione;
- varianti: senza stop loss, stop a -1%, stop a -0,5%;
- sessione Europa 9:00-15:25 (ora italiana), poi sessione USA 15:30-21:55, stesso capitale;
- 100 EUR di partenza, guadagni reinvestiti ogni giorno.

Ipotesi di esecuzione (favorevoli alla strategia):
- ingresso alla chiusura della candela da 1 minuto + mezzo spread;
- l'uscita a +1% e' un ordine limite: eseguito al prezzo esatto se il massimo della candela lo tocca;
- se nella stessa candela si toccano sia lo stop sia il target, si assume lo stop (prudente);
- zero commissioni (come Alpaca per le azioni USA; in Europa con 100 EUR ci sarebbero minimi a ordine).

Controllo: stesse regole ma titolo scelto a caso, per misurare se la selezione "del mattino" serve.

Uso:  python3 backtest/intraday.py
"""

import json
import random
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

OUT = Path(__file__).parent
CACHE = OUT / "data" / "1m"

US = """AAPL MSFT NVDA AMZN GOOGL META TSLA AVGO AMD NFLX ADBE CRM ORCL INTC CSCO QCOM TXN MU AMAT LRCX
KLAC MRVL PLTR SMCI COIN MSTR SHOP UBER ABNB SNOW CRWD PANW NET DDOG ZS MDB TEAM NOW INTU PYPL
HOOD SOFI RIVN LCID ARM DELL HPE ANET APP RBLX U AFRM UPST IONQ RGTI SOUN TSM BABA MARA RIOT""".split()
IT = """ENI.MI ENEL.MI ISP.MI UCG.MI G.MI TIT.MI STLAM.MI RACE.MI SRG.MI TRN.MI PST.MI MB.MI MONC.MI
PRY.MI STMMI.MI LDO.MI TEN.MI PIRC.MI SPM.MI BAMI.MI BMED.MI A2A.MI REC.MI""".split()
EU = """ASML.AS SAP.DE IFX.DE SIE.DE ALV.DE DTE.DE MBG.DE MC.PA AIR.PA SU.PA BNP.PA TTE.PA SAN.MC
IBE.MC ITX.MC BBVA.MC ADYEN.AS""".split()

SPREAD = {"us": 0.0003, "eu": 0.0005}  # mezzo spread per lato sugli ordini a mercato
TP = 0.01


def fetch_1m(t):
    CACHE.mkdir(parents=True, exist_ok=True)
    f = CACHE / f"{t}.csv"
    if f.exists() and time.time() - f.stat().st_mtime < 12 * 3600:
        return pd.read_csv(f, index_col=0, parse_dates=True)
    now = int(time.time())
    parts = []
    for back in (28, 21, 14, 7):
        p1, p2 = now - back * 86400, now - (back - 7) * 86400
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{t}?period1={p1}&period2={p2}&interval=1m"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            r = json.load(urllib.request.urlopen(req, timeout=20))["chart"]["result"][0]
            q = r["indicators"]["quote"][0]
            idx = pd.to_datetime(r["timestamp"], unit="s", utc=True).tz_convert("Europe/Rome")
            parts.append(pd.DataFrame({"o": q["open"], "h": q["high"], "l": q["low"], "c": q["close"]}, index=idx))
        except Exception:
            pass
    df = pd.concat(parts).dropna() if parts else pd.DataFrame(columns=list("ohlc"))
    df = df[~df.index.duplicated()].sort_index()
    df.index = df.index.tz_localize(None)
    df.to_csv(f)
    return df


def load():
    with ThreadPoolExecutor(8) as ex:
        data = dict(zip(US + IT + EU, ex.map(fetch_1m, US + IT + EU)))
    return {k: v for k, v in data.items() if len(v) > 1000}


def session_panel(data, tickers, day, start, end):
    """Matrici numpy minuto x titolo (open/high/low/close) per una sessione."""
    frames = {}
    for t in tickers:
        if t not in data:
            continue
        d = data[t]
        d = d[(d.index.date == day) & (d.index.time >= start) & (d.index.time <= end)]
        if len(d) > 30:
            frames[t] = d
    if not frames:
        return None
    idx = sorted(set().union(*[f.index for f in frames.values()]))
    names = list(frames)
    P = {k: pd.DataFrame({t: frames[t][k] for t in names}).reindex(idx).ffill().to_numpy() for k in "ohlc"}
    first_open = pd.DataFrame(P["o"]).bfill().to_numpy()[0]
    P["growth"] = P["c"] / first_open - 1
    P["names"] = names
    return P


def run_session(P, capital, warmup, stop, half_spread, pick="momentum", rng=None, tp=TP, day_start=None, day_target=None, day_stop=None):
    c, h, l, g = P["c"], P["h"], P["l"], P["growth"]
    n = len(c)
    i = warmup
    trades = []
    day_start = day_start or capital
    while i < n - 2:
        if day_target and capital >= day_start * (1 + day_target):
            break  # obiettivo del giorno raggiunto: si va a casa
        if day_stop and capital <= day_start * (1 - day_stop):
            break  # perdita massima del giorno raggiunta
        row = g[i]
        valid = np.where(~np.isnan(row))[0]
        if not len(valid):
            i += 1
            continue
        t = valid[np.argmax(row[valid])] if pick == "momentum" else rng.choice(list(valid))
        entry = c[i, t] * (1 + half_spread)
        tp_px, sl = entry * (1 + tp), entry * (1 - stop) if stop else None
        exit_px, j = None, i + 1
        while j < n - 1:
            if sl is not None and l[j, t] <= sl:
                exit_px = sl * (1 - half_spread)
                break
            if h[j, t] >= tp_px:
                exit_px = tp_px
                break
            j += 1
        if exit_px is None:  # fine sessione: si chiude a mercato
            exit_px = c[n - 1, t] * (1 - half_spread)
            j = n - 1
        r = exit_px / entry - 1
        capital *= 1 + r
        trades.append(r)
        i = j + 1  # si reinveste dal minuto successivo
    return capital, trades


PANELS = {}


def panels(data, days):
    import datetime as dtm
    if not PANELS:
        for day in days:
            PANELS[(day, "eu")] = session_panel(data, IT + EU, day, dtm.time(9, 0), dtm.time(15, 25))
            PANELS[(day, "us")] = session_panel(data, US, day, dtm.time(15, 30), dtm.time(21, 55))
    return PANELS


def simulate(data, days, warmup, stop, markets, pick="momentum", seed=0, tp=TP, day_target=None, day_stop=None, pn=None):
    rng = random.Random(seed)
    pn = pn or panels(data, days)
    cap, daily, all_trades = 100.0, [], []
    for day in days:
        start_cap = cap
        for m in ("eu", "us"):
            P = pn[(day, m)]
            if m not in markets or P is None:
                continue
            cap, tr = run_session(P, cap, warmup, stop, SPREAD[m], pick, rng, tp, start_cap, day_target, day_stop)
            all_trades += tr
        daily.append(cap / start_cap - 1)
    d = np.array(daily)
    tr = np.array(all_trades)
    return {
        "Finale EUR": round(cap, 2),
        "Giorni": len(d),
        "Media giorno": f"{d.mean():+.2%}",
        "Giorni >= +10%": int((d >= 0.10).sum()),
        "Giorni in perdita": int((d < 0).sum()),
        "Giorni >= +1%": int((d >= 0.01).sum()),
        "Giorno migliore": f"{d.max():+.1%}",
        "Giorno peggiore": f"{d.min():+.1%}",
        "Operazioni/giorno": round(len(tr) / max(len(d), 1), 1),
        "% operazioni vinte": f"{(tr > 0).mean():.0%}" if len(tr) else "-",
    }


def main():
    data = load()
    days = sorted({d for v in data.values() for d in v.index.date if d.weekday() < 5})
    print(f"Titoli con dati: {len(data)} | giorni di borsa: {len(days)} ({days[0]} -> {days[-1]})\n")
    rows = {}
    for markets, mlabel in ((("us",), "USA"), (("eu",), "Europa"), (("eu", "us"), "Europa+USA")):
        for warmup in (5, 15, 30):
            for stop, slabel in ((None, "nessuno"), (0.01, "-1%"), (0.005, "-0,5%")):
                rows[f"{mlabel} | dopo {warmup} min | stop {slabel}"] = simulate(data, days, warmup, stop, markets)
    # controllo: stesse regole, titolo scelto a caso (media di 20 estrazioni)
    ctrl = {}
    for stop, slabel in ((None, "nessuno"), (0.01, "-1%"), (0.005, "-0,5%")):
        finals = [simulate(data, days, 15, stop, ("eu", "us"), pick="random", seed=s)["Finale EUR"] for s in range(20)]
        ctrl[f"CASUALE Europa+USA | dopo 15 min | stop {slabel}"] = {
            "Finale EUR (media 20 prove)": round(float(np.mean(finals)), 2),
            "min": min(finals), "max": max(finals),
        }
    df = pd.DataFrame(rows).T.sort_values("Finale EUR", ascending=False)
    text = (
        f"Dati al minuto: {len(data)} titoli, {len(days)} giorni di borsa ({days[0]} -> {days[-1]}), capitale 100 EUR\n\n"
        + df.to_markdown() + "\n\n## Controllo: titolo scelto a caso\n\n" + pd.DataFrame(ctrl).T.to_markdown() + "\n"
    )
    (OUT / "risultati_intraday.md").write_text(text)
    print(text)


if __name__ == "__main__":
    main()

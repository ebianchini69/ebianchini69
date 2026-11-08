#!/usr/bin/env python3
"""
Lotteria dichiarata: UNA giocata da 100 EUR su un'opzione call USA, obiettivo 500 EUR.

Regole (scelte da Elena, consapevole che il valore atteso e' negativo e che l'esito piu'
probabile e' perdere i 100 EUR):
- si compra una sola volta un'opzione call con scadenza tra 20 e 45 giorni;
- tra tutte quelle che costano al massimo il budget, si sceglie quella con la probabilita'
  stimata piu' alta (volatilita' implicita, modello lognormale) di valere 5 volte il prezzo pagato;
- appena il valore della posizione arriva a 5x si vende: gioco vinto, fine;
- se non arriva a 5x, si vende quel che resta a 1 giorno dalla scadenza: gioco finito;
- nessuna seconda giocata senza un nuovo comando esplicito ("nuova").

Limiti scritti nel codice: solo acquisto di call (mai vendita allo scoperto), spesa massima = budget,
vendita solo della quantita' posseduta.

Comandi (TRADING_ENV=paper|live):
  python3 lotteria.py gioca    sceglie e compra (solo a mercato USA aperto, solo se non gia' giocato)
  python3 lotteria.py controlla  vende se 5x raggiunto o se manca 1 giorno alla scadenza
  python3 lotteria.py report   saldo del giorno (file + notifica)
  python3 lotteria.py status
"""

import datetime as dt
import json
import math
import sys
import urllib.parse
from pathlib import Path

import bot

UNDERLYINGS = ["QQQ", "SPY", "NVDA", "TSLA", "AAPL", "AMD", "META", "MSFT", "AMZN", "AVGO"]
MULTIPLE = 5.0
DTE_MIN, DTE_MAX = 20, 45
MAX_SPREAD = 0.15  # scarta opzioni con forbice denaro/lettera oltre il 15%
EXIT_DTE = 1
DATA_URL = "https://data.alpaca.markets"
STATE_FILE = bot.HOME / f"lotteria-{bot.ENV}.json"


def ncdf(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def prob_multiple(S, K, premium, iv, days, multiple=MULTIPLE):
    """Probabilita' (lognormale, senza drift) che a scadenza la call valga multiple x premio."""
    if iv is None or iv <= 0 or days <= 0 or S <= 0:
        return 0.0
    target_px = K + multiple * premium
    T = days / 365.0
    d = (math.log(S / target_px) - 0.5 * iv * iv * T) / (iv * math.sqrt(T))
    return ncdf(d)


class Data:
    """Dati di mercato Alpaca (quotazioni opzioni e prezzo del sottostante)."""

    def __init__(self, api):
        self.api = api

    def _get(self, path):
        old = self.api.base
        self.api.base = DATA_URL
        try:
            return self.api._req("GET", path)
        finally:
            self.api.base = old

    def price(self, sym):
        return float(self._get(f"/v2/stocks/{sym}/trades/latest?feed=iex")["trade"]["p"])

    def calls(self, sym, today):
        q = urllib.parse.urlencode({
            "feed": "indicative", "type": "call", "limit": 1000,
            "expiration_date_gte": str(today + dt.timedelta(days=DTE_MIN)),
            "expiration_date_lte": str(today + dt.timedelta(days=DTE_MAX)),
        })
        out, token = {}, None
        while True:
            r = self._get(f"/v1beta1/options/snapshots/{sym}?{q}" + (f"&page_token={token}" if token else ""))
            out.update(r.get("snapshots", {}))
            token = r.get("next_page_token")
            if not token:
                return out


def parse_occ(symbol):
    """Es. NVDA261218C00200000 -> (NVDA, 2026-12-18, 200.0)."""
    root = symbol[:-15]
    exp = dt.datetime.strptime(symbol[-15:-9], "%y%m%d").date()
    strike = int(symbol[-8:]) / 1000
    return root, exp, strike


def choose(data, budget_usd, today):
    best = None
    for u in UNDERLYINGS:
        try:
            S = data.price(u)
            snaps = data.calls(u, today)
        except Exception as e:
            bot.log(f"lotteria: dati non disponibili per {u}: {e}")
            continue
        for occ, s in snaps.items():
            q = s.get("latestQuote") or {}
            ask, bid = float(q.get("ap") or 0), float(q.get("bp") or 0)
            if ask <= 0 or bid <= 0 or (ask - bid) / ask > MAX_SPREAD:
                continue
            qty = int(budget_usd // (ask * 100))
            if qty < 1:
                continue
            _, exp, K = parse_occ(occ)
            days = (exp - today).days
            p = prob_multiple(S, K, ask, s.get("impliedVolatility"), days)
            cand = {"symbol": occ, "underlying": u, "strike": K, "expiry": str(exp), "ask": ask,
                    "bid": bid, "qty": qty, "cost": round(qty * ask * 100, 2), "prob": p, "spot": S}
            if best is None or p > best["prob"]:
                best = cand
    return best


def load():
    return json.loads(STATE_FILE.read_text()) if STATE_FILE.exists() else None


def save(s):
    bot.HOME.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(s, indent=2))


def position_value(api, symbol):
    for p in api.positions():
        if p["symbol"] == symbol:
            return float(p["market_value"]), float(p["qty"])
    return 0.0, 0.0


def gioca(api, data, fx, today=None, force_new=False):
    today = today or dt.date.today()
    s = load()
    if s and not force_new:
        bot.log(f"lotteria: gia' giocata ({s['status']}), nessun nuovo acquisto")
        return s
    if not api.clock()["is_open"]:
        bot.log("lotteria: mercato USA chiuso, si gioca alla prossima apertura")
        return None
    budget_usd = round(bot.BUDGET_EUR * (fx or 1.08), 2)
    budget_usd = min(budget_usd, float(api.account()["cash"]))
    c = choose(data, budget_usd, today)
    if not c:
        bot.log("lotteria: nessuna opzione adatta trovata")
        return None
    assert c["cost"] <= budget_usd + 1e-6
    o = api._req("POST", "/v2/orders", {
        "symbol": c["symbol"], "qty": str(c["qty"]), "side": "buy", "type": "limit",
        "limit_price": f"{c['ask']:.2f}", "time_in_force": "day",
    })
    o = bot.wait_fill(api, o["id"], timeout=120)
    if o["status"] != "filled":
        bot.log(f"lotteria: ordine non eseguito ({o['status']}), si riprova al prossimo giro")
        return None
    paid = float(o["filled_avg_price"]) * float(o["filled_qty"]) * 100
    s = {**c, "paid_usd": round(paid, 2), "target_usd": round(paid * MULTIPLE, 2), "fx": fx,
         "start": str(today), "status": "in gioco", "history": []}
    save(s)
    msg = (f"Comprate {c['qty']} call {c['underlying']} strike {c['strike']} scad. {c['expiry']} "
           f"per {paid:.2f} USD. Probabilita' stimata di 5x: {c['prob']:.0%}")
    bot.log("lotteria: " + msg)
    bot.notify("Lotteria: giocata", msg)
    return s


def controlla(api, today=None):
    today = today or dt.date.today()
    s = load()
    if not s or s["status"] != "in gioco":
        return s
    value, qty = position_value(api, s["symbol"])
    days_left = (dt.date.fromisoformat(s["expiry"]) - today).days
    reason = None
    if value >= s["target_usd"]:
        reason, final = "VINTO: 5x raggiunto", "vinto"
    elif days_left <= EXIT_DTE:
        reason, final = "scadenza vicina: si vende il residuo", "finito"
    if reason and qty > 0:
        if not api.clock()["is_open"]:
            bot.log("lotteria: " + reason + " ma mercato chiuso, si vende alla riapertura")
            return s
        o = api._req("POST", "/v2/orders", {
            "symbol": s["symbol"], "qty": str(int(qty)), "side": "sell", "type": "market", "time_in_force": "day",
        })
        o = bot.wait_fill(api, o["id"], timeout=120)
        got = float(o.get("filled_avg_price") or 0) * float(o.get("filled_qty") or 0) * 100
        s.update(status=final, sold_usd=round(got, 2), end=str(today))
        save(s)
        bot.log(f"lotteria: {reason}, incassati {got:.2f} USD")
        bot.notify("Lotteria", f"{reason}: {got:.2f} USD")
    elif reason and qty == 0:  # nulla da vendere (es. scaduta senza valore)
        s.update(status="finito", sold_usd=0.0, end=str(today))
        save(s)
    return s


def report(api, fx):
    s = load()
    if not s:
        bot.log("lotteria: non ancora giocata")
        return
    fx = fx or s.get("fx") or 1.08
    if s["status"] == "in gioco":
        value, _ = position_value(api, s["symbol"])
    else:
        value = s.get("sold_usd", 0.0)
    eur = value / fx
    today = str(dt.date.today())
    s["history"] = [h for h in s["history"] if h["date"] != today] + [{"date": today, "value_eur": round(eur, 2)}]
    save(s)
    text = (f"# Lotteria {today} ({bot.ENV})\n\n**Valore: {eur:.2f} EUR** su 100 EUR giocati "
            f"(obiettivo 500)\n\n{s['qty']} call {s['underlying']} strike {s['strike']} scadenza {s['expiry']}, "
            f"stato: {s['status']}\n")
    bot.REPORTS.mkdir(parents=True, exist_ok=True)
    (bot.REPORTS / f"{today}-lotteria-{bot.ENV}.md").write_text(text)
    bot.log(f"lotteria report: {eur:.2f} EUR ({s['status']})")
    bot.notify(f"Lotteria: {eur:.2f} EUR", f"Stato: {s['status']}, obiettivo 500 EUR")


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "status"
    api = bot.Alpaca(*bot.credentials())
    fx = bot.eurusd()
    if cmd == "gioca":
        gioca(api, Data(api), fx)
    elif cmd == "nuova":
        gioca(api, Data(api), fx, force_new=True)
    elif cmd == "controlla":
        if not load():
            gioca(api, Data(api), fx)
        controlla(api)
    elif cmd == "report":
        report(api, fx)
    else:
        print(json.dumps(load(), indent=2))


if __name__ == "__main__":
    main(sys.argv)

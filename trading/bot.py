#!/usr/bin/env python3
"""
Bot di trading su Alpaca: 40% paniere tech USA a pesi uguali, 40% momentum top 5, 20% Bitcoin.
Strategia scelta col backtest in ../backtest (2018-oggi: Sharpe ~1,0, calo massimo ~-41%).

Comandi:
  python3 bot.py run      controlli giornalieri + ribilanciamento mensile (a mercato USA aperto)
  python3 bot.py report   saldo di fine giornata (file in reports/ + notifica macOS)
  python3 bot.py status   stato attuale
  python3 bot.py halt     ferma il bot e vende tutto
  python3 bot.py resume   riattiva il bot dopo uno stop

Limiti non modificabili da riga di comando:
- usa solo il budget iniziale (100 EUR) e i suoi guadagni, anche se sul conto c'e' di piu';
- solo acquisti a contanti: niente leva, niente vendite allo scoperto, niente opzioni;
- se il valore scende sotto il 50% del massimo raggiunto vende tutto e si ferma.

Chiavi API: dal Portachiavi macOS (servizi claude-trading-<env>-key-id / -secret)
oppure dalle variabili d'ambiente APCA_API_KEY_ID / APCA_API_SECRET_KEY.
Ambiente: TRADING_ENV=paper (default) oppure live.
"""

import datetime as dt
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

# ---------------------------------------------------------------- configurazione
TECH = [
    "AAPL", "MSFT", "AMZN", "GOOGL", "META", "INTC", "CSCO", "NVDA", "NFLX",
    "ADBE", "AVGO", "TXN", "QCOM", "ORCL", "IBM", "PYPL", "TSLA",
]
CRYPTO = "BTC/USD"
WEIGHTS = {"basket": 0.40, "momentum": 0.40, "crypto": 0.20}
TOP_N = 5
BUDGET_EUR = 100.0
KILL_DRAWDOWN = 0.50  # stop totale se il valore scende sotto il 50% del massimo
MIN_ORDER_USD = 1.0  # minimo Alpaca per ordini frazionari
REBAL_TOLERANCE = 0.02  # non si tocca una posizione se lo scostamento e' < 2% del valore
MAX_ORDERS_PER_RUN = 40

ENV = os.environ.get("TRADING_ENV", "paper")
BASE_URL = {"paper": "https://paper-api.alpaca.markets", "live": "https://api.alpaca.markets"}[ENV]
HOME = Path(os.environ.get("TRADING_HOME", Path.home() / "claude-trading"))
STATE_FILE = HOME / f"state-{ENV}.json"
REPORTS = HOME / "reports"
LOG_FILE = HOME / "bot.log"


def log(msg):
    line = f"{dt.datetime.now():%Y-%m-%d %H:%M:%S} [{ENV}] {msg}"
    print(line)
    HOME.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def notify(title, text):
    if sys.platform == "darwin":
        safe = text.replace('"', "'")
        subprocess.run(["osascript", "-e", f'display notification "{safe}" with title "{title}"'], check=False)


# ---------------------------------------------------------------- chiavi e API
def keychain(service):
    try:
        out = subprocess.run(
            ["security", "find-generic-password", "-s", service, "-w"],
            capture_output=True, text=True, check=True,
        )
        return out.stdout.strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None


def credentials():
    kid = os.environ.get("APCA_API_KEY_ID") or keychain(f"claude-trading-{ENV}-key-id")
    sec = os.environ.get("APCA_API_SECRET_KEY") or keychain(f"claude-trading-{ENV}-secret")
    if not kid or not sec:
        sys.exit(f"Chiavi Alpaca ({ENV}) mancanti: eseguire setup_mac.sh")
    return kid, sec


class Alpaca:
    def __init__(self, key_id, secret, base_url=BASE_URL):
        self.h = {"APCA-API-KEY-ID": key_id, "APCA-API-SECRET-KEY": secret, "Content-Type": "application/json"}
        self.base = base_url

    def _req(self, method, path, body=None):
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(self.base + path, data=data, headers=self.h, method=method)
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                raw = r.read()
                return json.loads(raw) if raw else None
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"{method} {path} -> {e.code}: {e.read().decode()[:300]}") from None

    def account(self):
        return self._req("GET", "/v2/account")

    def clock(self):
        return self._req("GET", "/v2/clock")

    def positions(self):
        return self._req("GET", "/v2/positions")

    def asset(self, symbol):
        return self._req("GET", "/v2/assets/" + urllib.parse.quote(symbol, safe=""))

    def order(self, symbol, side, notional):
        crypto = "/" in symbol
        body = {
            "symbol": symbol, "side": side, "type": "market",
            "notional": f"{notional:.2f}", "time_in_force": "gtc" if crypto else "day",
        }
        return self._req("POST", "/v2/orders", body)

    def close(self, symbol):
        return self._req("DELETE", "/v2/positions/" + urllib.parse.quote(symbol.replace("/", ""), safe=""))

    def get_order(self, oid):
        return self._req("GET", f"/v2/orders/{oid}")


# ---------------------------------------------------------------- dati di mercato (stessa fonte del backtest)
def yahoo_closes(ticker, days=420):
    p2 = int(time.time())
    p1 = p2 - days * 86400
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?period1={p1}&period2={p2}&interval=1d"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    d = json.load(urllib.request.urlopen(req, timeout=20))["chart"]["result"][0]
    adj = d["indicators"].get("adjclose", [{}])[0].get("adjclose") or d["indicators"]["quote"][0]["close"]
    return [x for x in adj if x is not None]


def momentum_top(n=TOP_N, closes=yahoo_closes):
    scores = {}
    for t in TECH:
        try:
            c = closes(t)
            if len(c) >= 253:
                scores[t] = c[-22] / c[-253] - 1  # 12 mesi escluso l'ultimo
        except Exception as e:  # un titolo senza dati non blocca il bot
            log(f"dati mancanti per {t}: {e}")
    return sorted(scores, key=scores.get, reverse=True)[:n], scores


def eurusd(closes=yahoo_closes):
    try:
        return closes("EURUSD=X", days=10)[-1]
    except Exception:
        return None


# ---------------------------------------------------------------- stato
def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return None


def save_state(s):
    HOME.mkdir(parents=True, exist_ok=True)
    tmp = STATE_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(s, indent=2))
    tmp.replace(STATE_FILE)


def init_state(api, fx):
    acct = api.account()
    budget_usd = round(BUDGET_EUR * (fx or 1.08), 2)
    budget_usd = min(budget_usd, float(acct["cash"]))  # mai piu' di quanto c'e' davvero
    s = {
        "env": ENV, "start": str(dt.date.today()), "budget_usd": budget_usd, "fx_start": fx,
        "cash": budget_usd, "hwm": budget_usd, "halted": False, "last_rebalance": None, "history": [],
    }
    log(f"stato inizializzato: budget {budget_usd} USD (= {BUDGET_EUR} EUR)")
    return s


# ---------------------------------------------------------------- logica
def managed_positions(api):
    universe = set(TECH) | {CRYPTO.replace("/", "")}
    return {p["symbol"]: float(p["market_value"]) for p in api.positions() if p["symbol"] in universe}


def managed_value(state, pos):
    return state["cash"] + sum(pos.values())


def targets(value, top, crypto_ok):
    w = {}
    crypto_w = WEIGHTS["crypto"] if crypto_ok else 0.0
    spare = WEIGHTS["crypto"] - crypto_w  # se la crypto non e' disponibile va sul paniere
    for t in TECH:
        w[t] = w.get(t, 0) + (WEIGHTS["basket"] + spare) / len(TECH)
    for t in top:
        w[t] = w.get(t, 0) + WEIGHTS["momentum"] / len(top)
    if crypto_ok:
        w[CRYPTO.replace("/", "")] = crypto_w
    return {k: v * value for k, v in w.items()}


def wait_fill(api, oid, timeout=90):
    end = time.time() + timeout
    while time.time() < end:
        o = api.get_order(oid)
        if o["status"] in ("filled", "canceled", "expired", "rejected"):
            return o
        time.sleep(2)
    return api.get_order(oid)


def filled_usd(o):
    q, p = o.get("filled_qty"), o.get("filled_avg_price")
    return float(q) * float(p) if q and p else 0.0


def execute(api, state, symbol, side, usd, full_close=False):
    order_sym = CRYPTO if symbol == CRYPTO.replace("/", "") else symbol
    if full_close:
        o = api.close(order_sym)
    else:
        o = api.order(order_sym, side, usd)
    o = wait_fill(api, o["id"])
    got = filled_usd(o)
    state["cash"] += got if side == "sell" else -got
    log(f"{side} {order_sym} richiesti {usd:.2f} USD, eseguiti {got:.2f} USD ({o['status']})")
    return got


def rebalance(api, state, market_open, top, crypto_ok):
    pos = managed_positions(api)
    value = managed_value(state, pos)
    tgt = targets(value, top, crypto_ok)
    acct_cash = float(api.account()["cash"])
    sells, buys = [], []
    for sym in set(tgt) | set(pos):
        diff = tgt.get(sym, 0.0) - pos.get(sym, 0.0)
        if abs(diff) < max(MIN_ORDER_USD, REBAL_TOLERANCE * value) and not (tgt.get(sym, 0) == 0 and pos.get(sym)):
            continue
        is_crypto = sym == CRYPTO.replace("/", "")
        if not is_crypto and not market_open:
            continue  # azioni solo a mercato aperto
        (sells if diff < 0 else buys).append((sym, diff))
    n = 0
    for sym, diff in sorted(sells, key=lambda x: x[1]):
        if n >= MAX_ORDERS_PER_RUN:
            break
        full = tgt.get(sym, 0.0) == 0
        execute(api, state, sym, "sell", -diff, full_close=full)
        n += 1
    for sym, diff in sorted(buys, key=lambda x: -x[1]):
        if n >= MAX_ORDERS_PER_RUN:
            break
        acct_cash = float(api.account()["cash"])
        usd = min(diff, state["cash"] * 0.995, acct_cash * 0.995)  # margine per arrotondamenti
        if usd < MIN_ORDER_USD:
            continue
        execute(api, state, sym, "buy", usd)
        n += 1
    return n


def liquidate(api, state, reason):
    for sym in managed_positions(api):
        try:
            execute(api, state, sym, "sell", 0, full_close=True)
        except RuntimeError as e:
            log(f"errore vendendo {sym}: {e}")
    state["halted"] = True
    log(f"BOT FERMATO: {reason}")
    notify("Trading bot FERMATO", reason)


def cmd_run(api, state):
    if state["halted"]:
        log("bot fermo: nessuna operazione (usa 'resume' per riattivarlo)")
        return
    pos = managed_positions(api)
    value = managed_value(state, pos)
    state["hwm"] = max(state["hwm"], value)
    if value < (1 - KILL_DRAWDOWN) * state["hwm"]:
        liquidate(api, state, f"valore {value:.2f} USD sotto il {1 - KILL_DRAWDOWN:.0%} del massimo {state['hwm']:.2f}")
        return
    month = dt.date.today().strftime("%Y-%m")
    market_open = bool(api.clock()["is_open"])
    if state["last_rebalance"] == month:
        log(f"controllo ok: valore {value:.2f} USD, ribilanciamento gia' fatto questo mese")
        return
    try:
        crypto_ok = bool(api.asset(CRYPTO).get("tradable"))
    except RuntimeError:
        crypto_ok = False
    top, scores = momentum_top()
    log("momentum top: " + ", ".join(f"{t} {scores[t]:+.0%}" for t in top) + f" | crypto disponibile: {crypto_ok}")
    n = rebalance(api, state, market_open, top, crypto_ok)
    if market_open:
        state["last_rebalance"] = month
    log(f"ribilanciamento: {n} ordini" + ("" if market_open else " (mercato azioni chiuso: azioni al prossimo giro)"))


def cmd_report(api, state, fx):
    pos = managed_positions(api)
    value = managed_value(state, pos)
    fx = fx or state.get("fx_start") or 1.08
    eur = value / fx
    prev = state["history"][-1]["value_eur"] if state["history"] else BUDGET_EUR
    today = str(dt.date.today())
    state["history"] = [h for h in state["history"] if h["date"] != today]
    state["history"].append({"date": today, "value_usd": round(value, 2), "value_eur": round(eur, 2)})
    lines = [
        f"# Report {today} ({ENV})",
        "",
        f"**Valore: {eur:.2f} EUR** ({value:.2f} USD, cambio {fx:.4f})",
        f"Oggi: {eur - prev:+.2f} EUR | dall'inizio ({state['start']}): {eur - BUDGET_EUR:+.2f} EUR ({eur / BUDGET_EUR - 1:+.1%})",
        f"Liquidita': {state['cash']:.2f} USD | stato: {'FERMO' if state['halted'] else 'attivo'}",
        "",
        "| Titolo | Valore USD |",
        "|---|---:|",
    ] + [f"| {k} | {v:.2f} |" for k, v in sorted(pos.items(), key=lambda x: -x[1])]
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / f"{today}-{ENV}.md").write_text("\n".join(lines) + "\n")
    log(f"report: {eur:.2f} EUR ({eur - BUDGET_EUR:+.2f} dall'inizio)")
    notify(f"Trading {ENV}: {eur:.2f} EUR", f"Oggi {eur - prev:+.2f} EUR, dall'inizio {eur / BUDGET_EUR - 1:+.1%}")


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "status"
    api = Alpaca(*credentials())
    fx = eurusd()
    state = load_state() or init_state(api, fx)
    try:
        if cmd == "run":
            cmd_run(api, state)
        elif cmd == "report":
            cmd_report(api, state, fx)
        elif cmd == "halt":
            liquidate(api, state, "fermato a mano")
        elif cmd == "resume":
            state["halted"] = False
            pos = managed_positions(api)
            state["hwm"] = managed_value(state, pos)
            log("bot riattivato")
        else:
            pos = managed_positions(api)
            print(json.dumps({**{k: v for k, v in state.items() if k != "history"},
                              "value_usd": round(managed_value(state, pos), 2), "positions": pos}, indent=2))
    finally:
        save_state(state)


if __name__ == "__main__":
    main(sys.argv)

"""Test della lotteria con broker e dati finti. Uso: python3 test_lotteria.py"""
import datetime as dt
import os
import tempfile
import unittest
import uuid

os.environ["TRADING_HOME"] = tempfile.mkdtemp()
import bot  # noqa: E402
import lotteria as L  # noqa: E402

bot.notify = lambda *a: None
TODAY = dt.date(2026, 11, 9)
EXP = TODAY + dt.timedelta(days=30)


def occ(root, strike):
    return f"{root}{EXP:%y%m%d}C{int(strike * 1000):08d}"


class FakeData:
    def __init__(self):
        self.spot = {"NVDA": 200.0, "QQQ": 600.0}

    def price(self, u):
        if u not in self.spot:
            raise RuntimeError("nessun dato")
        return self.spot[u]

    def calls(self, u, today):
        if u == "NVDA":
            return {
                occ("NVDA", 230): {"latestQuote": {"ap": 0.95, "bp": 0.90}, "impliedVolatility": 0.55},
                occ("NVDA", 260): {"latestQuote": {"ap": 0.20, "bp": 0.18}, "impliedVolatility": 0.60},
                occ("NVDA", 200): {"latestQuote": {"ap": 9.00, "bp": 8.80}, "impliedVolatility": 0.50},  # troppo cara
                occ("NVDA", 300): {"latestQuote": {"ap": 0.05, "bp": 0.01}, "impliedVolatility": 0.70},  # forbice larga
            }
        return {occ("QQQ", 640): {"latestQuote": {"ap": 1.00, "bp": 0.97}, "impliedVolatility": 0.20}}


class FakeApi:
    def __init__(self):
        self.cash, self.open, self.pos, self.orders, self.mark = 100000.0, True, {}, [], {}

    def account(self):
        return {"cash": str(self.cash)}

    def clock(self):
        return {"is_open": self.open}

    def positions(self):
        return [{"symbol": k, "qty": str(q), "market_value": str(q * self.mark[k] * 100)} for k, q in self.pos.items() if q]

    def _req(self, method, path, body=None):
        assert method == "POST" and path == "/v2/orders"
        qty = float(body["qty"])
        if body["side"] == "buy":
            price = float(body["limit_price"])
            assert qty * price * 100 <= self.cash
            self.pos[body["symbol"]] = self.pos.get(body["symbol"], 0) + qty
            self.mark[body["symbol"]] = price
        else:
            assert qty <= self.pos.get(body["symbol"], 0), "vendita oltre il posseduto"
            price = self.mark[body["symbol"]]
            self.pos[body["symbol"]] -= qty
        oid = str(uuid.uuid4())
        self.orders.append({"id": oid, "status": "filled", "filled_qty": str(qty), "filled_avg_price": str(price), **body})
        return self.orders[-1]

    def get_order(self, oid):
        return next(o for o in self.orders if o["id"] == oid)


class T(unittest.TestCase):
    def setUp(self):
        if L.STATE_FILE.exists():
            L.STATE_FILE.unlink()

    def test_scelta_entro_budget_e_filtri(self):
        c = L.choose(FakeData(), 110.0, TODAY)
        self.assertLessEqual(c["cost"], 110.0)
        self.assertNotIn("C00200000", c["symbol"])  # troppo cara
        self.assertNotIn("C00300000", c["symbol"])  # forbice troppo larga
        self.assertGreater(c["prob"], 0)

    def test_sceglie_probabilita_massima(self):
        d = FakeData()
        c = L.choose(d, 110.0, TODAY)
        probs = []
        for u in ("NVDA", "QQQ"):
            for o, s in d.calls(u, TODAY).items():
                q = s["latestQuote"]
                if (q["ap"] - q["bp"]) / q["ap"] <= L.MAX_SPREAD and q["ap"] * 100 <= 110:
                    _, e, k = L.parse_occ(o)
                    probs.append(L.prob_multiple(d.spot[u], k, q["ap"], s["impliedVolatility"], (e - TODAY).days))
        self.assertAlmostEqual(c["prob"], max(probs))

    def test_una_sola_giocata(self):
        api = FakeApi()
        s = L.gioca(api, FakeData(), 1.10, TODAY)
        self.assertEqual(s["status"], "in gioco")
        self.assertLessEqual(s["paid_usd"], 110.0)
        n = len(api.orders)
        L.gioca(api, FakeData(), 1.10, TODAY)
        self.assertEqual(len(api.orders), n)

    def test_mercato_chiuso_non_compra(self):
        api = FakeApi()
        api.open = False
        self.assertIsNone(L.gioca(api, FakeData(), 1.10, TODAY))
        self.assertEqual(api.orders, [])

    def test_vende_a_5x(self):
        api = FakeApi()
        s = L.gioca(api, FakeData(), 1.10, TODAY)
        api.mark[s["symbol"]] = s["ask"] * 4
        self.assertEqual(L.controlla(api, TODAY)["status"], "in gioco")
        api.mark[s["symbol"]] = s["ask"] * 5.1
        s2 = L.controlla(api, TODAY)
        self.assertEqual(s2["status"], "vinto")
        self.assertEqual(api.orders[-1]["side"], "sell")
        self.assertEqual(api.pos[s["symbol"]], 0)

    def test_vende_residuo_a_scadenza(self):
        api = FakeApi()
        s = L.gioca(api, FakeData(), 1.10, TODAY)
        api.mark[s["symbol"]] = s["ask"] * 0.3
        s2 = L.controlla(api, EXP - dt.timedelta(days=1))
        self.assertEqual(s2["status"], "finito")
        self.assertGreater(s2["sold_usd"], 0)

    def test_parse_occ(self):
        self.assertEqual(L.parse_occ("NVDA261218C00200000"), ("NVDA", dt.date(2026, 12, 18), 200.0))
        self.assertEqual(L.parse_occ("QQQ261218C00640500")[2], 640.5)


if __name__ == "__main__":
    unittest.main(verbosity=2)

"""Test del bot con un broker finto: nessuna chiamata di rete. Uso: python3 test_bot.py"""
import os
import tempfile
import unittest
import uuid

os.environ["TRADING_HOME"] = tempfile.mkdtemp()
import bot  # noqa: E402

bot.notify = lambda *a: None


class FakeAlpaca:
    def __init__(self, cash=100000.0, prices=None, open_=True, crypto=True):
        self.cash, self.open, self.crypto = cash, open_, crypto
        self.prices = prices or {**{t: 100.0 for t in bot.TECH}, "BTCUSD": 50000.0}
        self.qty, self.orders = {}, {}

    def account(self):
        return {"cash": str(self.cash)}

    def clock(self):
        return {"is_open": self.open}

    def asset(self, s):
        return {"tradable": self.crypto}

    def positions(self):
        return [{"symbol": k, "market_value": str(q * self.prices[k])} for k, q in self.qty.items() if q > 1e-12]

    def _fill(self, sym, side, usd):
        sym = sym.replace("/", "")
        q = usd / self.prices[sym]
        self.qty[sym] = self.qty.get(sym, 0) + (q if side == "buy" else -q)
        self.cash += -usd if side == "buy" else usd
        oid = str(uuid.uuid4())
        self.orders[oid] = {"id": oid, "status": "filled", "filled_qty": str(q), "filled_avg_price": str(self.prices[sym])}
        return self.orders[oid]

    def order(self, sym, side, notional):
        assert notional >= bot.MIN_ORDER_USD, notional
        if side == "buy":
            assert notional <= self.cash, "acquisto oltre la liquidita' del conto"
        return self._fill(sym, side, notional)

    def close(self, sym):
        s = sym.replace("/", "")
        return self._fill(s, "sell", self.qty.get(s, 0) * self.prices[s])

    def get_order(self, oid):
        return self.orders[oid]


TOP = ["NVDA", "AVGO", "TSLA", "META", "AAPL"]


def fresh(api, fx=1.10):
    return bot.init_state(api, fx)


class T(unittest.TestCase):
    def setUp(self):
        bot.momentum_top = lambda: (TOP, {t: 0.5 for t in TOP})

    def test_usa_solo_il_budget(self):
        api = FakeAlpaca(cash=100000)
        st = fresh(api)
        self.assertAlmostEqual(st["budget_usd"], 110.0)
        bot.cmd_run(api, st)
        invested = sum(float(p["market_value"]) for p in api.positions())
        self.assertLessEqual(invested, 110.0 + 1e-6)
        self.assertGreater(invested, 105.0)
        self.assertAlmostEqual(invested + st["cash"], 110.0, places=6)

    def test_pesi(self):
        api = FakeAlpaca()
        st = fresh(api)
        bot.cmd_run(api, st)
        pos = bot.managed_positions(api)
        self.assertAlmostEqual(pos["BTCUSD"] / 110.0, 0.20, delta=0.01)
        self.assertAlmostEqual(pos["NVDA"] / 110.0, 0.4 / 17 + 0.4 / 5, delta=0.01)
        self.assertAlmostEqual(pos["IBM"] / 110.0, 0.4 / 17, delta=0.01)

    def test_conto_piccolo_mai_oltre_la_liquidita(self):
        api = FakeAlpaca(cash=50.0)  # conto reale con meno del budget
        st = fresh(api)
        self.assertEqual(st["budget_usd"], 50.0)
        bot.cmd_run(api, st)
        self.assertGreaterEqual(api.cash, 0)

    def test_mercato_chiuso_solo_crypto(self):
        api = FakeAlpaca(open_=False)
        st = fresh(api)
        bot.cmd_run(api, st)
        self.assertEqual(set(bot.managed_positions(api)), {"BTCUSD"})
        self.assertIsNone(st["last_rebalance"])
        api.open = True
        bot.cmd_run(api, st)
        self.assertEqual(len(bot.managed_positions(api)), 18)

    def test_crypto_non_disponibile_va_sul_paniere(self):
        api = FakeAlpaca(crypto=False)
        st = fresh(api)
        bot.cmd_run(api, st)
        pos = bot.managed_positions(api)
        self.assertNotIn("BTCUSD", pos)
        self.assertAlmostEqual(pos["IBM"] / 110.0, 0.6 / 17, delta=0.01)

    def test_un_solo_ribilanciamento_al_mese(self):
        api = FakeAlpaca()
        st = fresh(api)
        bot.cmd_run(api, st)
        n = len(api.orders)
        bot.cmd_run(api, st)
        self.assertEqual(len(api.orders), n)

    def test_stop_di_emergenza(self):
        api = FakeAlpaca()
        st = fresh(api)
        bot.cmd_run(api, st)
        for k in api.prices:
            api.prices[k] *= 0.45  # crollo del 55%
        bot.cmd_run(api, st)
        self.assertTrue(st["halted"])
        self.assertEqual(bot.managed_positions(api), {})
        n = len(api.orders)
        bot.cmd_run(api, st)  # fermo: non fa piu' nulla
        self.assertEqual(len(api.orders), n)

    def test_calo_normale_non_ferma(self):
        api = FakeAlpaca()
        st = fresh(api)
        bot.cmd_run(api, st)
        for k in api.prices:
            api.prices[k] *= 0.65  # -35%, come marzo 2020
        bot.cmd_run(api, st)
        self.assertFalse(st["halted"])

    def test_report(self):
        api = FakeAlpaca()
        st = fresh(api)
        bot.cmd_run(api, st)
        bot.cmd_report(api, st, 1.10)
        self.assertAlmostEqual(st["history"][-1]["value_eur"], 100.0, delta=0.5)


if __name__ == "__main__":
    unittest.main(verbosity=2)

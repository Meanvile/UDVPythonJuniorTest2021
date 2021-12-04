import aiohttp
from aiohttp import web
import asyncio
import requests
import json
import redis
from bs4 import BeautifulSoup
import unittest


class App:
    def __init__(self):
        self.r = redis.StrictRedis(host='localhost', port=6379, db=1,
                                   encoding='utf-8')
        self.m = Methods(self.r)

    async def init(self):
        app = web.Application()

        app.router.add_get("/convert", self.m.currency_exchange)
        app.router.add_post("/database", self.m.update_amount)

        return app


class Methods:
    def __init__(self, red, test=False):
        self.r = red
        self.d = Data()
        self.test = test

    async def currency_exchange(self, request=None):
        in_curr = request.rel_url.query['from'] if not self.test else "RUR"
        out_curr = request.rel_url.query['to'] if not self.test else "USD"
        amount = request.rel_url.query['amount'] if not self.test else 4200

        self.d.value = (float(amount) / float(
            self.d.curr[str(in_curr)])) * float(
            self.d.curr[str(out_curr)])

        self.d.values.append(self.d.value)

        return web.Response(
            text="Your {0} {1} currency will be {2} {3}".format(amount,
                                                                in_curr,
                                                                self.d.value,
                                                                out_curr),
            content_type='json')

    async def update_amount(self, request=None, mrg='1'):
        merge = request.rel_url.query['merge'] if not self.test else mrg

        try:
            data = json.loads(self.r.get('value').decode('utf-8'))
        except Exception as e:
            data = {'value': []}

        if data is None:
            data = {'value': []}

        if merge == '1':
            data['value'].append(self.d.value)
            self.r.set('value', json.dumps(data))
        else:
            data['value'] = data['value'][1:]
            self.r.set('value', json.dumps(data))

        return web.Response(text=str(data), content_type='json')


class Data:
    def __init__(self):
        self.value = 0
        self.curr_links = {
            "RUR": 'https://www.google.com/search?sxsrf=ALeKk01NWm6viYijAo3HXYOEQUyDEDtFEw%3A1584716087546&source=hp&ei=N9l0XtDXHs716QTcuaXoAg&q=%D0%B4%D0%BE%D0%BB%D0%BB%D0%B0%D1%80+%D0%BA+%D1%80%D1%83%D0%B1%D0%BB%D1%8E&oq=%D0%B4%D0%BE%D0%BB%D0%BB%D0%B0%D1%80+&gs_l=psy-ab.3.0.35i39i70i258j0i131l4j0j0i131l4.3044.4178..5294...1.0..0.83.544.7......0....1..gws-wiz.......35i39.5QL6Ev1Kfk4',
            "EUR": "https://www.google.com/search?q=доллар+к+евро",
            "GBP": "https://www.google.com/search?q=доллар+к+фунту&hs=g7y&sxsrf=AOaemvKl-vzesVpUDIvhYIwi2_ffBfq0yw%3A1638645887598&ei=f8CrYY7lI8r4qwHk5piIAQ&oq=доллар+к+aeyne&gs_lcp=Cgdnd3Mtd2l6EAEYADIJCAAQDRBGEIICMgQIABANMgQIABANMgQIABANMgYIABANEB4yBggAEA0QHjIICAAQDRAFEB4yCAgAEA0QBRAeMggIABANEAUQHjIICAAQDRAFEB46BwgAEEcQsAM6BwgAELADEEM6BAgjECc6CggAEIAEEIcCEBQ6BQgAEIAEOgkIIxAnEEYQggI6BwgAEIAEEAo6DggAEIAEELEDEIMBEMkDOggIABCABBCxAzoGCAAQFhAeOggIABAWEAoQHjoICAAQChABECpKBAhBGABQpAJYsx5gyKcGaAFwAngAgAGtAYgB8AmSAQMwLjmYAQCgAQHIAQrAAQE",
            "JPY": "https://www.google.com/search?q=доллар+к+японской+йене&sxsrf=AOaemvLrqL-aTubquQfxMfBD2dhkzJ_P9A%3A1638646418060&ei=ksKrYaWIA-jKrgTM4bToBQ&oq=доллар+к+zgjycrjq+&gs_lcp=Cgdnd3Mtd2l6EAMYADIJCAAQDRBGEIICMgQIABANMgYIABAWEB4yBggAEBYQHjIGCAAQFhAeOgcIABBHELADOgcIABCwAxBDOgQIIxAnOgoIABCABBCHAhAUOgUIABCABDoJCCMQJxBGEIICOg4IABCABBCxAxCDARDJAzoICAAQgAQQsQM6BAgAEEM6BAgAEAI6CggAEBYQChAeECo6CAgAEA0QBRAeSgQIQRgAUEJY2BtgmyxoAXACeACAAbwBiAHjDpIBBDAuMTSYAQCgAQHIAQrAAQE"}
        self.values = []
        try:
            self.curr = {"RUR": self.get_curr("RUR"),
                         "EUR": self.get_curr("EUR"),
                         "GBP": self.get_curr("GBP"), "USD": 1.0,
                         "JPY": self.get_curr("JPY")}
        except Exception as e:
            self.curr = {'RUR': 73.97, 'EUR': 0.88, 'GBP': 0.76, 'USD': 1.0,
                         'JPY': 112.8}

    def get_curr(self, currency):
        full_page = requests.get(self.curr_links[currency])

        soup = BeautifulSoup(full_page.content, 'html.parser')

        convert = soup.findAll("div", {"class": "BNeawe", "class": "iBp4i",
                                       "class": "AP7Wnd"})
        return float(".".join(convert[0].text.split()[0].split(",")))


class Test(unittest.TestCase):
    def test_get_curr(self):
        d = Data()
        rur = d.get_curr("RUR")

        self.assertTrue(rur)

    def test_currency_exchange(self):
        r = redis.StrictRedis(host='localhost', port=6379, db=2,
                              encoding='utf-8')
        m = Methods(r, True)
        m.d.curr['RUR'] = 73.97

        try:
            asyncio.run(m.currency_exchange())
        except Exception as e:
            pass

        self.assertEqual(m.d.value, 56.7797755846965)

    def test_update_amount_merge_1(self):
        r = redis.StrictRedis(host='localhost', port=6379, db=2,
                              encoding='utf-8')
        m = Methods(r, True)
        m.d.value = 12.10

        try:
            asyncio.run(m.update_amount())
        except Exception as e:
            pass

        val = json.loads(r.get('value').decode('utf-8'))

        r.set('value', json.dumps(val['value'][1:]))

        self.assertEqual(val['value'][-1], 12.10)

    def test_update_amount_merge_0(self):
        r = redis.StrictRedis(host='localhost', port=6379, db=2,
                              encoding='utf-8')
        data = {'value': []}
        data['value'].append(12.10)
        r.set('value', json.dumps(data))
        m = Methods(r, True)

        try:
            asyncio.run(m.update_amount(mrg="0"))
        except Exception as e:
            pass

        val = json.loads(r.get('value').decode('UTF-8'))

        self.assertEqual(val, {'value': []})


if __name__ == '__main__':
    unittest.main(exit=False)
    application = App()
    web.run_app(application.init(), port=8000)

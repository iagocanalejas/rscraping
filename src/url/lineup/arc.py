import requests
from parsel import Selector

from ai_django.ai_core.utils.strings import whitespaces_clean
from src.url.lineup import LineupUrlParser
from src.utils.models import Datasource, LineUpItem


class ARCLineupUrlParser(LineupUrlParser, source=Datasource.ARC):
    DATASOURCE = Datasource.ARC
    _HEADERS = {
        'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
        'Cache-Control': 'max-age=0'
    }

    def parse_page(self, url: str) -> LineUpItem:
        selector = Selector(requests.get(url=url, headers=self._HEADERS).text)

        race = whitespaces_clean(selector.xpath('//*[@id="main"]/div[2]/div[1]/h2/a/text()').get()).upper()
        club = whitespaces_clean(selector.xpath('//*[@id="main"]/div[2]/div[2]/div[1]/div[2]/div/h2/a/text()').get()).upper()
        coach = whitespaces_clean(selector.xpath('//*[@id="regatas_hojas_impresion"]/table/tbody/tr[7]/td[2]/div/p/text()').get()).upper()
        delegate = whitespaces_clean(selector.xpath('//*[@id="regatas_hojas_impresion"]/table/tbody/tr[7]/td[1]/div/p/text()').get()).upper()
        coxswain = whitespaces_clean(selector.xpath('//*[@id="regatas_hojas_impresion"]/table/tbody/tr[13]/td[4]/div/div/p/a/text()').get()).upper()
        bow = whitespaces_clean(selector.xpath('//*[@id="regatas_hojas_impresion"]/table/tbody/tr[2]/td/div/div/p/a/text()').get()).upper()

        starboard = [
            whitespaces_clean(selector.xpath('//*[@id="regatas_hojas_impresion"]/table/tbody/tr[12]/td[5]/div/p/a/text()').get()).upper(),
            whitespaces_clean(selector.xpath('//*[@id="regatas_hojas_impresion"]/table/tbody/tr[11]/td[5]/div/p/a/text()').get()).upper(),
            whitespaces_clean(selector.xpath('//*[@id="regatas_hojas_impresion"]/table/tbody/tr[10]/td[5]/div/p/a/text()').get()).upper(),
            whitespaces_clean(selector.xpath('//*[@id="regatas_hojas_impresion"]/table/tbody/tr[9]/td[4]/div/p/a/text()').get()).upper(),
            whitespaces_clean(selector.xpath('//*[@id="regatas_hojas_impresion"]/table/tbody/tr[8]/td[5]/div/p/a/text()').get()).upper(),
            whitespaces_clean(selector.xpath('//*[@id="regatas_hojas_impresion"]/table/tbody/tr[7]/td[5]/div/p/a/text()').get()).upper(),
        ]

        larboard = [
            whitespaces_clean(selector.xpath('//*[@id="regatas_hojas_impresion"]/table/tbody/tr[12]/td[4]/div/p/a/text()').get()).upper(),
            whitespaces_clean(selector.xpath('//*[@id="regatas_hojas_impresion"]/table/tbody/tr[11]/td[4]/div/p/a/text()').get()).upper(),
            whitespaces_clean(selector.xpath('//*[@id="regatas_hojas_impresion"]/table/tbody/tr[10]/td[4]/div/p/a/text()').get()).upper(),
            whitespaces_clean(selector.xpath('//*[@id="regatas_hojas_impresion"]/table/tbody/tr[9]/td[3]/div/p/a/text()').get()).upper(),
            whitespaces_clean(selector.xpath('//*[@id="regatas_hojas_impresion"]/table/tbody/tr[8]/td[4]/div/p/a/text()').get()).upper(),
            whitespaces_clean(selector.xpath('//*[@id="regatas_hojas_impresion"]/table/tbody/tr[7]/td[4]/div/p/a/text()').get()).upper(),
        ]

        substitute = [
            selector.xpath('//*[@id="regatas_hojas_impresion"]/table/tbody/tr[10]/td[1]/div/p/a/text()').get(),
            selector.xpath('//*[@id="regatas_hojas_impresion"]/table/tbody/tr[10]/td[2]/div/p/a/text()').get(),
            selector.xpath('//*[@id="regatas_hojas_impresion"]/table/tbody/tr[11]/td[1]/div/p/a/text()').get(),
            selector.xpath('//*[@id="regatas_hojas_impresion"]/table/tbody/tr[11]/td[2]/div/p/a/text()').get(),
            selector.xpath('//*[@id="regatas_hojas_impresion"]/table/tbody/tr[12]/td[1]/div/p/a/text()').get(),
            selector.xpath('//*[@id="regatas_hojas_impresion"]/table/tbody/tr[12]/td[2]/div/p/a/text()').get(),
            selector.xpath('//*[@id="regatas_hojas_impresion"]/table/tbody/tr[13]/td[1]/div/p/a/text()').get(),
            selector.xpath('//*[@id="regatas_hojas_impresion"]/table/tbody/tr[13]/td[2]/div/p/a/text()').get(),
        ]

        return LineUpItem(
            race=race,
            club=club,
            coach=coach,
            delegate=delegate,
            coxswain=coxswain,
            starboard=starboard,
            larboard=larboard,
            substitute=[whitespaces_clean(s).upper() for s in substitute if s],
            bow=bow,
        )

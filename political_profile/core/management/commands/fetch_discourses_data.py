import time
from concurrent import futures
from datetime import datetime

import pytz
import requests
from bs4 import BeautifulSoup as HtmlParser
from django.conf import settings
from django.core.management.base import BaseCommand

from political_profile.core.models import Discourse, Congressman

DISCOURSE_URL = 'http://www.camara.leg.br/internet/sitaqweb/DiscursosDeputado.asp'

FIELDS = 'date', 'session', 'phase', 'speaker', 'time', 'summary'

RETRIES = 6

TZ = pytz.timezone(settings.TIME_ZONE)


class Command(BaseCommand):
    help = 'Fetches congressman discourse data'

    def __fetch_congressman_discourses(self, congressman):
        session = requests.Session()

        params = {
            'txOrador': congressman.name,
            'txUF': congressman.state,
            'txPartido': '',
            'dtinicio': '01/02/2015',
            'dtfim': '31/01/ 2019',
            'Campoordenacao': 'dtSessao',
            'tipoordenacao': 'DESC',
            'Pagesize': '9999'
        }

        r = session.get(DISCOURSE_URL, params=params)
        parsed = HtmlParser(r.content, 'html.parser', from_encoding='utf-8')
        if 'Nenhum discurso encontrado..' in parsed.get_text():
            return []

        t = parsed.select('table.tabela-padrao-bootstrap')[0]
        rows = t.select('tr')

        discourses = []
        curr_row = None

        for row in rows:
            if curr_row is None:
                curr_row = {}

            cols = row.select('td')
            if row.has_attr('class'):
                values = [c.get_text().strip() for c in cols]
                curr_row.update({k: v for k, v in zip(FIELDS, values)})
            elif row.has_attr('id'):
                col = cols[0]
                curr_row['summary'] = col.get_text().strip()

                date_time = curr_row['date'] + ' ' + curr_row['time'][:-1]
                date_time = datetime.strptime(date_time, '%d/%m/%Y %H:%M')
                curr_row['pronounced_at'] = TZ.localize(date_time)

                del curr_row['speaker']
                del curr_row['date']
                del curr_row['time']

                curr_row['congressman_id'] = congressman.id
                discourses.append(Discourse(**curr_row))
                curr_row = None

        Discourse.objects.bulk_create(discourses)

    def __process_congressman(self, congressman):
        success = False
        attempt = RETRIES
        while attempt > 0 and not success:
            try:
                self.__fetch_congressman_discourses(congressman)
                success = True
            except Exception:
                attempt -= 1
                time.sleep((RETRIES - attempt) ** 1.5)
        if not success:
            self.stderr.write('Failed ' + congressman.name)
        else:
            self.stdout.write('Got ' + congressman.name)

    def handle(self, *args, **options):
        congressman_list = list(Congressman.objects.all())
        with futures.ThreadPoolExecutor(max_workers=10) as executor:
            f_congress = {executor.submit(self.__process_congressman, c): c for c in congressman_list}
            for f in futures.as_completed(f_congress):
                pass

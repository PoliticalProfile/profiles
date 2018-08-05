# -*- coding: utf-8 -*-
import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup as HtmlParser
from django.core.management.base import BaseCommand
from lxml_to_dict import lxml_to_dict
from zeep import Client

from political_profile.core.management.commands import treat_str, treat_date, fetch_url, DATE_FORMAT, execute, \
    perform_soap
from political_profile.core.models import Congressman, Proposition, Vote

CONGRESSMAN_URL = 'http://www.camara.leg.br/internet/Deputado/dep_Detalhe.asp'
BASE_URL = 'http://www.camara.leg.br/internet/deputado/RelVotacoes.asp'
WSDL_URL = 'http://www.camara.gov.br/SitCamaraWS/Proposicoes.asmx?wsdl'

PROPOSITION_URL_PATTERN = r'Sigla=(.+)&Numero=(\d+)&Ano=(\d+)'


class Command(BaseCommand):
    help = 'Fetches votes'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__session = requests.Session()
        self.__client = Client(WSDL_URL)

    def handle(self, *args, **options):
        congressman_list = list(Congressman.objects.all())[::-1]
        execute(congressman_list, self.__process)

    def __process(self, congressman):
        self.stdout.write('{} - Listing votes.'.format(congressman.name))
        try:
            self.__process_votes_page(congressman)
        except Exception as e:
            self.stderr.write(e)

    def __process_votes_page(self, congressman):
        r = fetch_url(self.__session, BASE_URL, params={
            'nuLegislatura': congressman.mandate_id,
            'nuMatricula': congressman.matriculation_id,
            'dtInicio': '01/01/2015',
            'dtFim': '30/12/2018'
        })

        parsed = HtmlParser(r.content, 'html.parser', from_encoding='utf-8')
        c_date, c_title, c_presence, c_reason = None, None, None, None

        votes = parsed.select('table > tr')
        for d in votes:
            if d.has_attr('class'):
                c_date, c_title, c_presence, c_reason = Command.__extract_info_from_header(d)
                self.stdout.write('{} - {} - {}'.format(c_date, c_title, c_presence))
            else:
                session, proposition_link, vote = Command.__extract_info_from_item(d)

                if proposition_link is None:
                    continue

                p_info = Command.__extract_proposition_metadata(proposition_link)
                if Command.__can_skip_row(p_info, congressman, c_date):
                    continue

                try:
                    proposition_id = self.__resolve_proposition_id(proposition_link)
                except KeyError:
                    continue

                Vote.objects.create(
                    proposition_id=proposition_id,
                    congressman=congressman,
                    vote=vote,
                    session_code=c_title,
                    session_date=c_date,
                    presence=c_presence,
                    absence_reason=c_reason
                )

    def __resolve_proposition_id(self, raw_url):
        type_, number, year = Command.__extract_proposition_metadata(raw_url)
        response = perform_soap(self.__client.service.ObterProposicao, **{
            'tipo': type_,
            'numero': number,
            'ano': year
        })
        proposition = lxml_to_dict(response)['proposicao']
        return Command.__create_proposition(type_, number, year, proposition)

    @staticmethod
    def __create_proposition(type_, number, year, data):
        p, _ = Proposition.objects.get_or_create(id=int(data['idProposicao']))
        d = {
            'id': int(data['idProposicao']),
            'name': treat_str(data['nomeProposicao']),
            'type_code': treat_str(type_),
            'type_name': treat_str(data['tipoProposicao']),
            'number': int(number),
            'year': int(year),
            'status': treat_str(data['Situacao']),
            'proposed_at': treat_date(data['DataApresentacao']),
        }
        Proposition.objects.filter(id=p.id).update(**d)
        return p.id

    @staticmethod
    def __extract_info_from_header(row):
        header_cols = row.select('td')
        date = header_cols[0].get_text().strip()
        date = datetime.strptime(date, DATE_FORMAT).date()
        title = header_cols[1].get_text().strip()
        presence = header_cols[2].get_text().strip()
        absence_reason = header_cols[4].get_text().strip()
        if absence_reason == '---':
            absence_reason = ''

        return date, title, presence, absence_reason

    @staticmethod
    def __extract_info_from_item(row):
        rows = row.select('td')
        session = rows[1]
        session_link = session.find('a')
        vote = rows[3].get_text().strip()
        if vote == '---':
            vote = None

        proposition_link = None
        if session_link is not None and session_link.has_attr('href'):
            proposition_link = session_link['href']

        return session, proposition_link, vote

    @staticmethod
    def __can_skip_row(proposition_info, congressman, vote_date):
        if proposition_info is not None and len(proposition_info) > 0:
            type_, number, year = proposition_info
            return Vote.objects.filter(
                congressman=congressman,
                session_date=vote_date,
                proposition__type_code=type_,
                proposition__number=int(number),
                proposition__year=int(year)).exists()
        return False

    @staticmethod
    def __extract_proposition_metadata(url):
        occrs = re.findall(PROPOSITION_URL_PATTERN, url)
        if len(occrs) > 0:
            fields = occrs[0]
            return fields[0], int(fields[1]), int(fields[2])
        return None

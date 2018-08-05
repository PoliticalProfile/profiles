import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from zeep import Client

from political_profile.core.management.commands import encode_gender
from political_profile.core.models import Congressman

# Search URLS
CONGRESSMAN_URL = 'http://www.camara.leg.br/internet/Deputado/dep_Detalhe.asp'
SEARCH_URL = 'http://www2.camara.leg.br/deputados/pesquisa'
DETAILED_BASE_URL = 'https://dadosabertos.camara.leg.br/api/v2/deputados'

CONGRESSMAN_LIST_WSDL = 'http://www.camara.gov.br/SitCamaraWS/Deputados.asmx?wsdl'

# Parsing auxiliary info
PATTERN = r'(.*?)\|(\d+)%\d+!(\S{2})=(.*?)\?(\d+)'

# API required header
HEADERS = {'Accept': 'application/json'}

FIELDS = {
    'ideCadastro': ('id', int),
    'codOrcamento': ('budget_id', int),
    'condicao': 'condition',
    'matricula': ('matriculation_id', int),
    'idParlamentar': ('registration_id', int),
    'nome': 'name',
    'nomeParlamentar': 'legal_name',
    'urlFoto': 'photo_url',
    'sexo': ('gender', encode_gender),
    'uf': 'state',
    'partido': 'party',
    'fone': 'phone_number',
    'email': 'email',
}


class Command(BaseCommand):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__session = requests.Session()
        self.__author_map = self.__build_author_id_map()
        self.__client = Client(CONGRESSMAN_LIST_WSDL)

    def handle(self, *args, **options):
        self.stdout.write('Fecthing basic congressman data...')
        self.__fetch_basic_congressman_data()
        self.stdout.write('Done!')

        self.stdout.write('Fecthing detailed congressman data...')
        self.__fetch_detailed_congressman_data()
        self.stdout.write('Done!')

    def __map_to_dict(self, congressman_xml):
        return {f.tag: f.text for f in congressman_xml}

    def __build_author_id_map(self):
        r = self.__session.get(SEARCH_URL)
        fields = 'name', 'author_id', 'state', 'party', 'congressman_id'
        parsed = BeautifulSoup(r.text, 'html.parser')
        select = parsed.select('#deputado')[0]
        options = select.find_all('option')
        congressman_map = {}

        for option in options:
            value_str = option['value']
            if not re.match(PATTERN, value_str):
                continue

            values = re.findall(PATTERN, value_str)[0]
            c = {k: v for k, v in zip(fields, values)}
            c['congressman_id'] = int(c['congressman_id'])
            c['author_id'] = int(c['author_id'])
            congressman_map[c['congressman_id']] = c['author_id']
        return congressman_map

    def __fetch_basic_congressman_data(self):
        congressmen = self.__client.service.ObterDeputados()

        to_be_created = []
        for congressman in congressmen:
            congressman_obj = {}

            xml_data = self.__map_to_dict(congressman)
            for key, field in FIELDS.items():
                target_field, transformer = None, None
                if type(field) == tuple:
                    target_field, transformer = field
                else:
                    target_field = field

                value = xml_data[key]
                if transformer is not None and value is not None:
                    value = transformer(value)

                congressman_obj[target_field] = value
            congressman_obj['author_id'] = self.__author_map[congressman_obj['id']]
            congressman_obj['profile_url'] = '{}?id={}'.format(CONGRESSMAN_URL, congressman_obj['id'])
            to_be_created.append(Congressman(**congressman_obj))
        Congressman.objects.bulk_create(to_be_created)

    def __fetch_detailed_congressman_data(self):
        for c in list(Congressman.objects.all()):
            self.stdout.write(' - {}'.format(c.name))
            url = '{}/{}'.format(DETAILED_BASE_URL, c.id)
            r = self.__session.get(url, headers=HEADERS).json()['dados']

            c.legal_name = r['nomeCivil']
            c.name = r['ultimoStatus']['nome']
            c.mandate_id = r['ultimoStatus']['idLegislatura']
            c.birth_city = r['municipioNascimento']
            c.birth_state = r['ufNascimento']
            c.birh_date = datetime.strptime(r['dataNascimento'], '%Y-%m-%d').date()
            c.scholarity = r['escolaridade']
            c.gender = r['sexo']
            c.cpf = r['cpf']
            c.save()

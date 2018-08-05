from django.core.management.base import BaseCommand
from lxml_to_dict import lxml_to_dict
from zeep import Client

from political_profile.core.management.commands import perform_soap, execute
from political_profile.core.models import Proposition, PropositionTag

WSDL_URL = 'http://www.camara.gov.br/SitCamaraWS/Proposicoes.asmx?wsdl'


class Command(BaseCommand):
    help = 'Fetches propositions details.'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__client = Client(WSDL_URL)

    def handle(self, *args, **options):
        self.stdout.write('Starting to fetch all proposition details...')
        propositions = list(Proposition.objects.filter(file_url__isnull=True))
        execute(propositions, self.__fetch_proposition_details)
        self.stdout.write('Done!')

    def __fetch_proposition_details(self, proposition):
        self.stdout.write(' - {}'.format(proposition.id))
        response = perform_soap(self.__client.service.ObterProposicaoPorID, idProp=str(proposition.id))
        proposition_json = Command.__extract_proposition_objs(response)
        proposition_fields = Command.__transform_proposition_to_obj(proposition_json)

        tags = proposition_json['Indexacao']
        if tags is not None:
            tags = tags.split(',')
            tags = [t.strip() for t in tags]
            tags = [t[0].upper() + t[1:] for t in tags if len(t) > 0]
            if tags[-1].endswith('.'):
                tags[-1] = tags[-1][:-1]

            for tag in tags:
                t, _ = PropositionTag.objects.get_or_create(tag=tag)
                proposition.tags.add(t)

        Proposition.objects.filter(id=proposition.id).update(**proposition_fields)

    @staticmethod
    def __extract_proposition_objs(soap_response):
        proposition = lxml_to_dict(soap_response)
        return proposition['proposicao']

    @staticmethod
    def __transform_proposition_to_obj(p):
        return {
            'file_url': p['LinkInteiroTeor'],
            'subject': p['tema'],
            'summary': p['Ementa'],
            'detailed_summary': p['ExplicacaoEmenta']
        }

from django.conf import settings
from django.core.management.base import BaseCommand
from lxml_to_dict import lxml_to_dict
from pytz import timezone
from zeep import Client

from political_profile.core.management.commands import treat_str, treat_date, perform_soap
from political_profile.core.models import Congressman, Proposition

TZ = timezone(settings.TIME_ZONE)

WSDL_URL = 'http://www.camara.gov.br/SitCamaraWS/Proposicoes.asmx?wsdl'


class Command(BaseCommand):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__client = Client(WSDL_URL)

    def handle(self, *args, **options):
        self.stdout.write('Starting to fetch all propositions...')
        congressmen = list(Congressman.objects.all())
        for congressman in congressmen:
            self.stdout.write(' - {}'.format(congressman.name))
            self.__fetch_propositions_for_congressman(congressman)
        self.stdout.write('Done!')

    def __fetch_propositions_for_congressman(self, congressman):
        congressman_name = congressman.name.replace('\'', ' ')
        response = perform_soap(self.__client.service.ListarProposicoes, parteNomeAutor=congressman_name)
        propositions = Command.__extract_proposition_objs(response)

        if congressman.propositions.count() == len(propositions):
            self.stdout.write(' - Skipping...')
            return

        for proposition in propositions:
            proposition_obj = Command.__transform_xml_to_object(proposition)
            p, created = Proposition.objects.get_or_create(id=proposition_obj['id'])
            if created:
                Proposition.objects.filter(id=p.id).update(**proposition_obj)
            p.congressmen.add(congressman)

    @staticmethod
    def __extract_proposition_objs(soap_response):
        propositions = lxml_to_dict(soap_response)
        if 'erro' in propositions:
            return []
        return [propositions['proposicoes'][k] for k in propositions['proposicoes'].keys()]

    @staticmethod
    def __transform_xml_to_object(p_xml):
        return {
            'id': int(p_xml['id']),
            'name': treat_str(p_xml['nome']),
            'type_code': treat_str(p_xml['tipoProposicao']['sigla']),
            'type_name': treat_str(p_xml['tipoProposicao']['nome']),
            'number': int(p_xml['numero']) if p_xml['numero'] is not None else None,
            'year': int(p_xml['ano']) if p_xml['ano'] is not None else None,
            'summary': treat_str(p_xml['txtEmenta']),
            'detailed_summary': treat_str(p_xml['txtExplicacaoEmenta']),
            'status': treat_str(p_xml['ultimoDespacho']['txtDespacho']),
            'numberer_code': treat_str(p_xml['orgaoNumerador']['sigla']),
            'numberer_name': treat_str(p_xml['orgaoNumerador']['nome']),
            'proposed_at': treat_date(p_xml['datApresentacao']),
        }

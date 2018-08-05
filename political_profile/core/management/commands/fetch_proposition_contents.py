from io import BytesIO

import PyPDF2
import requests
from django.core.management.base import BaseCommand

from political_profile.core.management.commands import fetch_url, execute
from political_profile.core.models import Proposition


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__session = requests.Session()

    def handle(self, *args, **options):
        self.__session = requests.Session()
        self.stdout.write('Listing all pending propositions...')
        propositions = self.__fetch_pending_propositions()
        self.stdout.write('{} propositions pending'.format(len(propositions)))
        execute(propositions, self.__fetch_proposition_contents)

    def __fetch_pending_propositions(self):
        return list(Proposition.objects.filter(
            file_url__isnull=False,
            full_content__isnull=True
        ))

    def __fetch_proposition_contents(self, proposition):
        file_url = proposition.file_url
        contents = self.__fetch_pdf_contents(file_url)
        proposition.full_content = contents
        proposition.save()

    def __fetch_pdf_contents(self, url):
        self.stdout.write(' - Fetching file from {}'.format(url))
        contents = fetch_url(self.__session, url).content
        file_ = BytesIO(contents)
        pdf = PyPDF2.PdfFileReader(file_)
        return ''.join([pdf.getPage(p).extractText() for p in range(pdf.getNumPages())])

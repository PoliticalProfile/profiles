import time
from concurrent import futures
from datetime import datetime

import pytz
from django.conf import settings

DATE_FORMAT = '%d/%m/%Y'
TIMESTAMP_FORMAT = '%d/%m/%Y %H:%M:%S'

TZ = pytz.timezone(settings.TIME_ZONE)

RETRIES = 10
EXP_WAIT = 1.5
MAX_WORKERS = 5

def encode_gender(gender):
    if gender is None:
        return None

    if gender in ('m', 'masc', 'masculino'):
        return 'M'
    return 'F'


def treat_date(str_):
    if str_ is None:
        return None

    if ' ' in str_:
        r = datetime.strptime(str_, TIMESTAMP_FORMAT)
    else:
        r = datetime.strptime(str_, DATE_FORMAT)
    return TZ.localize(r)


def treat_str(s):
    return s.strip() if s is not None else None


def fetch_url(session, url, **kwargs):
    retried, success = RETRIES, False
    while retried > 0 and not success:
        try:
            r = session.get(url, **kwargs)
            if r.status_code == 200:
                return r
        except Exception:
            retried -= 1
            time.sleep((RETRIES - retried) ** EXP_WAIT)


def perform_soap(method, **kwargs):
    retries = RETRIES
    while retries > 0:
        try:
            return method(**kwargs)
        except:
            retries -= 1
            time.sleep((RETRIES - retries) ** EXP_WAIT)


def execute(iterator, process, max_workers=MAX_WORKERS):
    with futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        f_congress = {executor.submit(process, c): c for c in iterator}
        for f in futures.as_completed(f_congress):
            pass

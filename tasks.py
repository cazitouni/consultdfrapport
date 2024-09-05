from rapport import create_pdf
from decouple import config
from celery import Celery

import requests

celery_app = Celery(
    'tasks',
    broker=config('CELERY_REDIS'),
    backend=config('CELERY_REDIS')
)

@celery_app.task
def fetch_parcelle_data(parcelle, token):
    headers = {
        "accept": "application/json",
        "Authorization": f"token {token}"
    }
    if len(parcelle[0:5]) != 5:
        return 404
    response = requests.get(f'https://apidf-preprod.cerema.fr/ff/geoparcelles?code_insee={parcelle[0:5]}&fields=all&idpar={parcelle}', headers=headers, timeout=10)
    if response.status_code == 401:
        return 401
    elif response.status_code == 403:
        return 403
    elif response.status_code != 200:
        return 404
    parcelle_data = response.json()
    if not parcelle_data or 'features' not in parcelle_data or not parcelle_data['features']:
        return 404
    proprietaire_data = requests.get(f'https://apidf-preprod.cerema.fr/ff/proprios?code_insee={parcelle[0:5]}&fields=all&idprocpte={parcelle_data["features"][0]["properties"]["idprocpte"]}', headers=headers, timeout=10).json()
    locaux_data = requests.get(f'https://apidf-preprod.cerema.fr/ff/locaux?code_insee={parcelle[0:5]}&fields=all&idpar={parcelle}}', headers=headers, timeout=10).json()
    return create_pdf(parcelle_data['features'][0], proprietaire_data.get("results", []), locaux_data.get("results", []))

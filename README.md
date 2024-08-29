# ConsultDF : Rapport parcellaire

En lien avec l'[API foncier](https://consultdf.cerema.fr/consultdf/services/apidf) de l'outil ConsultDF, cette API permet l'édition de rapport parcellaire. 

Pour ce faire il suffit d'être inscrit sur la plateforme et de disposer d'un [jeton d'authentification ](https://consultdf.cerema.fr/consultdf/services/apidf/token)ainsi que d'un numéro de parcelle. 

## Installation

Pourt fonctionner l'API a besoin au préalable d'un serveur [valkey]((https://github.com/valkey-io/valkey)

Cloner le dépôt :
```
git clone https://github.com/cazitouni/consultdfrapport.git && cd consultdfrapport
```

Définir les paramètres dans un fichier .env
```
QGIS_REQUEST_URL= URL du serveur wms pour la carte, defaut : https://igp.metrotopic.net/project/6e34ee01e0f879920d7957d59eb67148/?SERVICE=WMS
WMS_LAYER= couche wms de la carte, defaut : fond_ign
VALKEY_HOST=Hôte du serveur valkey, defaut : localhost
RATE_LIMIT=limite de requêtes, defaut : 50
PERIOD= période de la limite en secondes, defaut : 60
CELERY_REDIS= URL valkey pour celery, defaut : redis://localhost:6379/0
```

Installer les dependances python 
```
pip install -r requirements.txt
```

lancer celery
```
celery  -A tasks.celery_app worker --loglevel=info
```

lancer l'API
```
uvicorn app:app --host 0.0.0.0 --port 7777 --reload
```

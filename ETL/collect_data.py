import earthaccess
import requests
import boto3
import json
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

# --- Configuration ---
EARTHDATA_USERNAME = os.getenv("EARTHDATA_USER")
EARTHDATA_PASSWORD = os.getenv("EARTHDATA_PASS")
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')
S3_BUCKET = "skypionners"
OPENAQ_API_URL = "https://api.openaq.org/v3"
OPENAQ_API_KEY = os.getenv('API_KEY_OPENAQ')

# --- Authentification et Headers ---
try:
    auth = earthaccess.login() # Utilise les variables d'environnement
    print("Authentification Earthdata réussie.")
except Exception as e:
    print(f"Erreur d'authentification Earthdata: {e}")
    exit(1)

# Headers pour OpenAQ v3
headers = {
    "accept": "application/json", # Header recommandé par la doc v3
    "X-API-Key": OPENAQ_API_KEY
}

# --- Fonctions de Collecte Corrigées ---

def collect_tempo_data():
    """Étape 1 : Collecte des données TEMPO (NO2 L3, version V03)"""
    try:
        # - CORRIGÉ : Utilisation d'une période passée pour garantir la disponibilité des données
        start_time = "2025-06-01"
        end_time = "2025-06-08"
        print(f"Recherche de données TEMPO pour la période : {start_time} à {end_time}")
        
        results = earthaccess.search_data(
            short_name="TEMPO_NO2_L3",
            version="V03",
            temporal=(start_time, end_time),
            bounding_box=(-125, 24, -66, 50), # Couvre les États-Unis
            cloud_hosted=True,
            count=10
        )
        
        if not results:
            print("Aucun résultat pour TEMPO. Vérifiez les dates et le statut sur https://search.earthdata.nasa.gov.")
            return []
        
        print(f"Nombre de granules TEMPO trouvés: {len(results)}")
        files = earthaccess.download(results, local_path="./tempo_data")
        return [str(f) for f in files] # S'assurer que les chemins sont des chaînes de caractères
    except Exception as e:
        print(f"Erreur lors de la collecte TEMPO: {e}")
        return []

def collect_openaq_data():
    """Étape 2 : Collecte des données OpenAQ v3 (récentes + historiques)"""
    # - CORRIGÉ : Toute la fonction est réécrite pour utiliser l'API v3
    try:
        # Identifier les stations (locations) au lieu des capteurs
        locations_url = f"{OPENAQ_API_URL}/locations"
        params = {
            "country": "US",
            "parameter": ["pm25", "no2", "o3"],
            "limit": 10, # On prend 10 stations pour l'exemple
            "has_geo": "true"
        }
        response = requests.get(locations_url, headers=headers, params=params)
        response.raise_for_status()
        
        locations = response.json().get("results", [])
        location_ids = [loc["id"] for loc in locations]
        print(f"Stations (locations) trouvées (US, PM2.5/NO2/O3): {len(location_ids)}")

        if not location_ids:
            return None

        # Collecter les mesures pour ces stations
        data_collection = {"recent": [], "historical": []}
        measurements_url = f"{OPENAQ_API_URL}/measurements"

        # Données récentes (dernières 24h)
        params_recent = {
            "location_id": location_ids,
            "date_from": (datetime.utcnow() - timedelta(hours=24)).isoformat(),
            "date_to": datetime.utcnow().isoformat(),
            "limit": 5000
        }
        response_recent = requests.get(measurements_url, headers=headers, params=params_recent)
        response_recent.raise_for_status()
        data_collection["recent"] = response_recent.json().get("results", [])
        print(f"  -> {len(data_collection['recent'])} mesures récentes collectées.")

        # Données historiques (pour un mois en 2024)
        params_historical = {
            "location_id": location_ids,
            "date_from": "2024-06-01T00:00:00Z",
            "date_to": "2024-06-30T23:59:59Z",
            "limit": 5000
        }
        response_historical = requests.get(measurements_url, headers=headers, params=params_historical)
        response_historical.raise_for_status()
        data_collection["historical"] = response_historical.json().get("results", [])
        print(f"  -> {len(data_collection['historical'])} mesures historiques collectées.")
        
        return data_collection
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la collecte OpenAQ: {e.response.text}")
        return None

def collect_merra2_data():
    """Étape 3 : Collecte des données MERRA-2"""
    try:
        # - CORRIGÉ : Utilisation d'une période passée pour garantir la disponibilité des données
        start_time = "2025-06-01"
        end_time = "2025-09-08"
        print(f"Recherche de données MERRA-2 pour la période : {start_time} à {end_time}")
        
        results = earthaccess.search_data(
            short_name="M2T1NXSLV",
            version="5.12.4", # Spécifier la version est une bonne pratique
            temporal=(start_time, end_time),
            bounding_box=(-125, 24, -66, 50),
            cloud_hosted=True,
            count=10
        )
        
        if not results:
            print("Aucun résultat pour MERRA-2. Vérifiez les dates.")
            return []
        
        print(f"Nombre de granules MERRA-2 trouvés: {len(results)}")
        files = earthaccess.download(results, local_path="./merra2_data")
        return [str(f) for f in files]
    except Exception as e:
        print(f"Erreur lors de la collecte MERRA-2: {e}")
        return []

def upload_to_s3(file_path, s3_key):
    """Étape 4 : Stockage dans AWS S3"""
    if not (AWS_ACCESS_KEY and AWS_SECRET_KEY):
        print(f"Variables AWS non configurées, upload de {file_path} ignoré.")
        return
    try:
        s3_client = boto3.client("s3", aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)
        s3_client.upload_file(file_path, S3_BUCKET, s3_key)
        print(f"Uploadé {file_path} vers s3://{S3_BUCKET}/{s3_key}")
    except Exception as e:
        print(f"Erreur S3: {e}")

# --- Pipeline Principal ---
def main():
    print(f"Début de la collecte à {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}...")
    
    # Collecte TEMPO
    tempo_files = collect_tempo_data()
    for file in tempo_files:
        upload_to_s3(file, f"tempo/{os.path.basename(file)}")
    
    # Collecte OpenAQ v3
    openaq_data = collect_openaq_data()
    if openaq_data:
        # Sauvegarde données récentes
        recent_file = f"openaq_recent_{datetime.now().strftime('%Y%m%d')}.json"
        with open(recent_file, "w") as f:
            json.dump(openaq_data["recent"], f, indent=2)
        upload_to_s3(recent_file, f"openaq/recent/{recent_file}")
        
        # Sauvegarde données historiques
        historical_file = f"openaq_historical_{datetime.now().strftime('%Y%m%d')}.json"
        with open(historical_file, "w") as f:
            json.dump(openaq_data["historical"], f, indent=2)
        upload_to_s3(historical_file, f"openaq/historical/{historical_file}")
    
    # Collecte MERRA-2
    merra2_files = collect_merra2_data()
    for file in merra2_files:
        upload_to_s3(file, f"merra2/{os.path.basename(file)}")
    
    print("Collecte terminée. Vérifiez ./tempo_data, ./merra2_data, et les fichiers JSON générés.")

if __name__ == "__main__":
    main()
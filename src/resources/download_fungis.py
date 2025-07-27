from flask_restful import Resource
import os
import requests
from urllib.parse import quote
from flasgger import swag_from

BASE_DIR = os.path.dirname(__file__)
DATASET_DIR = os.path.join(BASE_DIR, '..', 'dataset')

ESPECIES = {
    'morchella': [
        ('Morchella tridentina', 100),
    ],
    'no_morchella': [
        ('Gyromitra antarctica', 20),
        ('Laccaria', 20),
        ('Cortinarius', 20),
        ('Clitocybe', 20),
        ('Galerina', 20)
    ]
}
# acumula las urls de las imagenes en una lista
def fetch_images(scientific_name, cantidad):
    results = []
    per_page = 30
    pages = (cantidad // per_page) + 1

    for page in range(1, pages + 1):
        url = f"https://api.inaturalist.org/v1/observations?taxon_name={quote(scientific_name)}&photos=true&quality_grade=research&per_page={per_page}&page={page}"
        resp = requests.get(url)
        if resp.status_code != 200:
            break

        data = resp.json().get('results', [])
        for obs in data:
            photos = obs.get('photos', [])
            for photo in photos:
                if 'url' in photo:
                    url = photo['url'].replace('square', 'large')  # mejor resolución
                    results.append(url)
                    if len(results) >= cantidad:
                        return results
    return results

# guarda las imagenes en la carpeta /dataset
def save_images(urls, folder_name, especie_prefix):
    os.makedirs(folder_name, exist_ok=True)
    for idx, url in enumerate(urls):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                extension = url.split('.')[-1].split('?')[0]
                path = os.path.join(folder_name, f"{especie_prefix}_{idx}.{extension}")
                with open(path, 'wb') as f:
                    f.write(response.content)
        except Exception as e:
            print(f"Error al guardar {url}: {e}")

# endpoint para descargar imagenes de hongos
class DownloadImages(Resource):
    @swag_from('../flasgger/download_fungis.yml')
    def post(self):
        for categoria, especies in ESPECIES.items():
            folder_path = os.path.join(DATASET_DIR, categoria)
            for nombre_especie, cantidad in especies:
                print(f"🔍 Descargando {cantidad} de {nombre_especie}...")
                urls = fetch_images(nombre_especie, cantidad)
                especie_clean = nombre_especie.replace(' ', '_')
                save_images(urls, folder_path, especie_clean)
        return {'message': 'Descarga completada'}, 200

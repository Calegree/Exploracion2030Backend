from flask_restful import Resource
import os
import requests
from urllib.parse import quote
from flasgger import swag_from
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import shutil

BASE_DIR = os.path.dirname(__file__)
DATASET_DIR = os.path.join(BASE_DIR, '..', 'dataset')

ESPECIES = {
    'morchella': [
        ('Morchella tridentina', 400),
        ('Morchella andinensis', 20),
        ('Morchella aysenina', 20),
    ],
    'no_morchella': [
        ('Gyromitra antarctica', 20),
        ('Gyromitra esculenta', 20),
        ('Verpa spp.', 20),
        ('Helvella spp.', 20),
        ('Discomycetes', 20),
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
        try:
            resp = requests.get(url, timeout=10)
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
        except Exception as e:
            print(f"Error al obtener URLs de página {page}: {e}")
            break
    return results

# guarda una sola imagen (para uso en paralelo)
def save_single_image(url, folder_name, especie_prefix, idx):
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            extension = url.split('.')[-1].split('?')[0]
            if not extension or len(extension) > 4:
                extension = 'jpg'
            path = os.path.join(folder_name, f"{especie_prefix}_{idx}.{extension}")
            with open(path, 'wb') as f:
                f.write(response.content)
            return True
    except Exception as e:
        print(f"❌ Error al guardar {url}: {e}")
        return False

# guarda las imagenes en la carpeta /dataset usando ThreadPoolExecutor
def save_images(urls, folder_name, especie_prefix):
    os.makedirs(folder_name, exist_ok=True)
    
    # Usar ThreadPoolExecutor para descargas paralelas
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {
            executor.submit(save_single_image, url, folder_name, especie_prefix, idx): idx
            for idx, url in enumerate(urls)
        }
        
        success_count = 0
        for future in as_completed(futures):
            if future.result():
                success_count += 1
        
        print(f"✅ Descargadas {success_count}/{len(urls)} imágenes de {especie_prefix}")

# Función para ejecutar la descarga en background
def download_images_background():
    try:
        # Limpiar contenido de la carpeta dataset sin eliminar la carpeta raíz
        if os.path.exists(DATASET_DIR):
            print(f"🗑️ Limpiando contenido de: {DATASET_DIR}")
            for item in os.listdir(DATASET_DIR):
                item_path = os.path.join(DATASET_DIR, item)
                if os.path.isfile(item_path):
                    os.unlink(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
        else:
            print(f"📁 Creando carpeta: {DATASET_DIR}")
            os.makedirs(DATASET_DIR, exist_ok=True)
        
        for categoria, especies in ESPECIES.items():
            folder_path = os.path.join(DATASET_DIR, categoria)
            for nombre_especie, cantidad in especies:
                print(f"🔍 Descargando {cantidad} de {nombre_especie}...")
                urls = fetch_images(nombre_especie, cantidad)
                especie_clean = nombre_especie.replace(' ', '_')
                save_images(urls, folder_path, especie_clean)
        print("🎉 Descarga completada exitosamente")
    except Exception as e:
        print(f"❌ Error durante la descarga: {e}")

# endpoint para descargar imagenes de hongos
class DownloadImages(Resource):
    @swag_from('../flasgger/download_fungis.yml')
    def post(self):
        # Iniciar la descarga en un thread separado para no bloquear el worker
        thread = threading.Thread(target=download_images_background, daemon=True)
        thread.start()
        
        return {
            'message': 'Descarga iniciada en segundo plano. La carpeta dataset será recreada. Revisa los logs para ver el progreso.',
            'status': 'processing'
        }, 202

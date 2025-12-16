from flask_restful import Resource
import os
import requests
from urllib.parse import quote
from flasgger import swag_from
from concurrent.futures import ThreadPoolExecutor, as_completed
import shutil

BASE_DIR = os.path.dirname(__file__)
DATASET_DIR = os.path.join(BASE_DIR, '..', 'dataset')

# Configuración balanceada: 500 Morchella, 500 No-Morchella
ESPECIES_BALANCED_500 = {
    'morchella': [
        ('Morchella esculenta', 100),
        ('Morchella tridentina', 100),
        ('Morchella andinensis', 25),
        ('Morchella aysenina', 6),
        ('Morchella', 269),  # Morchella spp sin ID específico
    ],
    'no_morchella': [
        ('Gyromitra esculenta', 100),
        ('Gyromitra antarctica', 80),
        ('Helvella lacunosa', 70),
        ('Helvella crispa', 70),
        ('Verpa bohemica', 60),
        ('Cortinarius', 40),
        ('Laccaria', 40),
        ('Clitocybe', 40),
    ]
}

def fetch_images(scientific_name, cantidad):
    """Obtiene URLs de imágenes desde iNaturalist"""
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
                    url = photo['url'].replace('square', 'large')
                    results.append(url)
                    if len(results) >= cantidad:
                        return results
    return results

def purge_dataset():
    """Elimina y recrea la estructura del dataset"""
    try:
        if os.path.isdir(DATASET_DIR):
            for sub in ['morchella', 'no_morchella']:
                subpath = os.path.join(DATASET_DIR, sub)
                if os.path.isdir(subpath):
                    shutil.rmtree(subpath, ignore_errors=True)
        else:
            os.makedirs(DATASET_DIR, exist_ok=True)
        
        os.makedirs(os.path.join(DATASET_DIR, 'morchella'), exist_ok=True)
        os.makedirs(os.path.join(DATASET_DIR, 'no_morchella'), exist_ok=True)
        print("🧹 Dataset purgado y recreado")
    except Exception as e:
        print(f"⚠️ Error purgando dataset: {e}")

def download_single_image(url, folder_name, especie_prefix, idx):
    """Descarga una imagen individual"""
    try:
        response = requests.get(url, timeout=15, stream=True)
        if response.status_code == 200:
            extension = url.split('.')[-1].split('?')[0]
            if not extension or len(extension) > 5:
                extension = 'jpg'
            path = os.path.join(folder_name, f"{especie_prefix}_{idx}.{extension}")
            with open(path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            return True, f"✓ Imagen {idx} guardada"
        else:
            return False, f"✗ Error HTTP {response.status_code} para imagen {idx}"
    except requests.exceptions.Timeout:
        return False, f"✗ Timeout descargando imagen {idx}"
    except Exception as e:
        return False, f"✗ Error en imagen {idx}: {str(e)[:50]}"

def save_images(urls, folder_name, especie_prefix, max_workers=5):
    """Guarda imágenes con concurrencia"""
    os.makedirs(folder_name, exist_ok=True)
    successful = 0
    failed = 0
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(download_single_image, url, folder_name, especie_prefix, idx): idx
            for idx, url in enumerate(urls)
        }
        
        for future in as_completed(futures):
            success, message = future.result()
            if success:
                successful += 1
            else:
                failed += 1
    
    return successful, failed

class DownloadBalanced500(Resource):
    @swag_from('../flasgger/download_balanced_500.yml')
    def post(self):
        """
        Descarga dataset balanceado: 500 Morchella + 500 No-Morchella
        Sobrescribe la carpeta dataset existente
        """
        try:
            print("🧹 Purgando dataset anterior...")
            purge_dataset()
            
            print("📥 Iniciando descarga de dataset balanceado (500-500)...")
            
            total_downloaded = {'morchella': 0, 'no_morchella': 0}
            total_failed = {'morchella': 0, 'no_morchella': 0}
            
            for folder, especies_list in ESPECIES_BALANCED_500.items():
                folder_path = os.path.join(DATASET_DIR, folder)
                
                for especie_name, cantidad in especies_list:
                    print(f"🔍 Buscando {cantidad} imágenes de {especie_name}...")
                    urls = fetch_images(especie_name, cantidad)
                    
                    if not urls:
                        print(f"⚠️ No se encontraron imágenes para {especie_name}")
                        continue
                    
                    print(f"💾 Guardando {len(urls)} imágenes de {especie_name}...")
                    prefix = especie_name.replace(' ', '_')
                    successful, failed = save_images(urls, folder_path, prefix)
                    
                    total_downloaded[folder] += successful
                    total_failed[folder] += failed
                    
                    print(f"✅ {especie_name}: {successful} guardadas, {failed} fallidas")
            
            summary = {
                'status': 'success',
                'message': 'Dataset balanceado 500-500 descargado',
                'statistics': {
                    'morchella': {
                        'downloaded': total_downloaded['morchella'],
                        'failed': total_failed['morchella']
                    },
                    'no_morchella': {
                        'downloaded': total_downloaded['no_morchella'],
                        'failed': total_failed['no_morchella']
                    },
                    'total': total_downloaded['morchella'] + total_downloaded['no_morchella']
                }
            }
            
            print(f"\\n🎉 Descarga completada:")
            print(f"   Morchella: {total_downloaded['morchella']} imágenes")
            print(f"   No-Morchella: {total_downloaded['no_morchella']} imágenes")
            print(f"   Total: {summary['statistics']['total']} imágenes")
            
            return summary, 200
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error descargando dataset: {str(e)}'
            }, 500

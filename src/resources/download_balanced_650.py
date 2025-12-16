from flask_restful import Resource
import os
import requests
from urllib.parse import quote
from flasgger import swag_from
from concurrent.futures import ThreadPoolExecutor, as_completed
import shutil

BASE_DIR = os.path.dirname(__file__)
DATASET_DIR = os.path.join(BASE_DIR, '..', 'dataset')

# Configuración balanceada: 650 Morchella, 650 No-Morchella
ESPECIES_BALANCED_650 = {
    'morchella': [
        ('Morchella andinensis', 25),
        ('Morchella aysenina', 6),
        ('Morchella tridentina', 100),
        ('Morchella esculenta', 100),
        ('Morchella', 419),  # Morchella spp sin ID específico (resto hasta 650)
    ],
    'no_morchella': [
        # Ascomicetes (Gyromitra, Helvella, etc.) - 330 fotos
        ('Gyromitra esculenta', 90),
        ('Gyromitra antarctica', 70),
        ('Helvella lacunosa', 60),
        ('Helvella crispa', 60),
        ('Verpa bohemica', 50),
        
        # Agaricales comunes (Amanita, Agaricus, etc.) - 160 fotos
        ('Amanita muscaria', 50),
        ('Amanita phalloides', 40),
        ('Agaricus campestris', 40),
        ('Agaricus bisporus', 30),
        
        # Hongos de bosque patagónico (Boletus, Suillus, etc.) - 90 fotos
        ('Boletus edulis', 40),
        ('Suillus luteus', 30),
        ('Lactarius deliciosus', 20),
        
        # Políporos y hongos de madera - 40 fotos
        ('Trametes versicolor', 15),
        ('Ganoderma lucidum', 13),
        ('Fomes fomentarius', 12),
        
        # Gasteroides y otras formas - 30 fotos
        ('Lycoperdon perlatum', 12),
        ('Calvatia gigantea', 10),
        ('Phallus impudicus', 8),
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

class DownloadBalanced650(Resource):
    @swag_from('../flasgger/download_balanced_650.yml')
    def post(self):
        """
        Descarga dataset balanceado: 650 Morchella + 650 No-Morchella
        
        Morchella (650 fotos):
        - 25 Morchella andinensis
        - 6 Morchella aysenina
        - 100 Morchella tridentina
        - 100 Morchella esculenta
        - 419 Morchella spp (sin ID específico)
        
        No-Morchella (650 fotos) - Diversidad amplia:
        - Ascomicetes: Gyromitra, Helvella, Verpa (330 fotos)
        - Agaricales: Amanita, Agaricus (160 fotos)
        - Boletus patagónicos: Boletus, Suillus, Lactarius (90 fotos)
        - Políporos: Trametes, Ganoderma, Fomes (40 fotos)
        - Gasteroides: Lycoperdon, Calvatia, Phallus (30 fotos)
        
        Sobrescribe la carpeta dataset existente
        """
        try:
            print("🧹 Purgando dataset anterior...")
            purge_dataset()
            
            print("📥 Iniciando descarga de dataset balanceado (650-650)...")
            
            total_downloaded = {'morchella': 0, 'no_morchella': 0}
            total_failed = {'morchella': 0, 'no_morchella': 0}
            species_detail = {'morchella': {}, 'no_morchella': {}}
            
            for folder, especies_list in ESPECIES_BALANCED_650.items():
                folder_path = os.path.join(DATASET_DIR, folder)
                
                for especie_name, cantidad in especies_list:
                    print(f"🔍 Buscando {cantidad} imágenes de {especie_name}...")
                    urls = fetch_images(especie_name, cantidad)
                    
                    if not urls:
                        print(f"⚠️ No se encontraron imágenes para {especie_name}")
                        species_detail[folder][especie_name] = {'downloaded': 0, 'failed': 0}
                        continue
                    
                    print(f"💾 Guardando {len(urls)} imágenes de {especie_name}...")
                    prefix = especie_name.replace(' ', '_')
                    successful, failed = save_images(urls, folder_path, prefix)
                    
                    total_downloaded[folder] += successful
                    total_failed[folder] += failed
                    species_detail[folder][especie_name] = {
                        'downloaded': successful,
                        'failed': failed,
                        'target': cantidad
                    }
                    
                    print(f"✅ {especie_name}: {successful} guardadas, {failed} fallidas")
            
            summary = {
                'status': 'success',
                'message': 'Dataset balanceado 650-650 descargado',
                'statistics': {
                    'morchella': {
                        'downloaded': total_downloaded['morchella'],
                        'failed': total_failed['morchella'],
                        'target': 650,
                        'species': species_detail['morchella']
                    },
                    'no_morchella': {
                        'downloaded': total_downloaded['no_morchella'],
                        'failed': total_failed['no_morchella'],
                        'target': 650,
                        'species': species_detail['no_morchella']
                    },
                    'total': total_downloaded['morchella'] + total_downloaded['no_morchella'],
                    'target_total': 1300
                }
            }
            
            print(f"\n🎉 Descarga completada:")
            print(f"   Morchella: {total_downloaded['morchella']}/650 imágenes")
            print(f"   No-Morchella: {total_downloaded['no_morchella']}/650 imágenes")
            print(f"   Total: {summary['statistics']['total']}/1300 imágenes")
            
            return summary, 200
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error descargando dataset: {str(e)}'
            }, 500

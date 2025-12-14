from flask_restful import Resource
import os
import requests
from urllib.parse import quote
from flasgger import swag_from
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import shutil

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

# purga segura del dataset
def purge_dataset():
    try:
        if os.path.isdir(DATASET_DIR):
            # eliminar subcarpetas específicas
            for sub in ['morchella', 'no_morchella']:
                subpath = os.path.join(DATASET_DIR, sub)
                if os.path.isdir(subpath):
                    shutil.rmtree(subpath, ignore_errors=True)
        else:
            os.makedirs(DATASET_DIR, exist_ok=True)
        # recrear estructura base
        os.makedirs(os.path.join(DATASET_DIR, 'morchella'), exist_ok=True)
        os.makedirs(os.path.join(DATASET_DIR, 'no_morchella'), exist_ok=True)
        print("🧹 Dataset purgado: morchella/ y no_morchella/ reiniciados")
    except Exception as e:
        print(f"⚠️ Error purgando dataset: {e}")

# descarga una sola imagen
def download_single_image(url, folder_name, especie_prefix, idx):
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

# guarda las imagenes en la carpeta /dataset con concurrencia
def save_images(urls, folder_name, especie_prefix, max_workers=5):
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
                print(message)
    
    print(f"  ✓ Descargadas: {successful} | ✗ Fallidas: {failed}")
    return successful, failed

# endpoint para descargar imagenes de hongos
class DownloadImages(Resource):
    @swag_from('../flasgger/download_fungis.yml')
    def post(self):
        start_time = time.time()
        total_success = 0
        total_failed = 0
        resultados = []
        # purgar dataset antes de descargar
        purge_dataset()
        
        try:
            for categoria, especies in ESPECIES.items():
                folder_path = os.path.join(DATASET_DIR, categoria)
                for nombre_especie, cantidad in especies:
                    print(f"\n🔍 Descargando {cantidad} imágenes de {nombre_especie}...")
                    try:
                        urls = fetch_images(nombre_especie, cantidad)
                        print(f"  📥 Encontradas {len(urls)} URLs")
                        
                        if urls:
                            especie_clean = nombre_especie.replace(' ', '_')
                            success, failed = save_images(urls, folder_path, especie_clean, max_workers=5)
                            total_success += success
                            total_failed += failed
                            resultados.append({
                                'especie': nombre_especie,
                                'categoria': categoria,
                                'exitosas': success,
                                'fallidas': failed
                            })
                        else:
                            print(f"  ⚠️ No se encontraron imágenes para {nombre_especie}")
                            resultados.append({
                                'especie': nombre_especie,
                                'categoria': categoria,
                                'exitosas': 0,
                                'fallidas': 0,
                                'mensaje': 'No se encontraron imágenes'
                            })
                    except Exception as e:
                        print(f"  ❌ Error procesando {nombre_especie}: {str(e)}")
                        resultados.append({
                            'especie': nombre_especie,
                            'categoria': categoria,
                            'exitosas': 0,
                            'fallidas': cantidad,
                            'error': str(e)[:100]
                        })
            
            elapsed_time = time.time() - start_time
            print(f"\n✅ Proceso completado en {elapsed_time:.2f} segundos")
            print(f"📊 Total exitosas: {total_success} | Total fallidas: {total_failed}")
            
            return {
                'message': 'Descarga completada',
                'tiempo_segundos': round(elapsed_time, 2),
                'total_exitosas': total_success,
                'total_fallidas': total_failed,
                'detalle': resultados
            }, 200
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            print(f"\n❌ Error general en descarga: {str(e)}")
            return {
                'error': 'Error en el proceso de descarga',
                'detalle': str(e),
                'tiempo_segundos': round(elapsed_time, 2),
                'total_exitosas': total_success,
                'total_fallidas': total_failed
            }, 500

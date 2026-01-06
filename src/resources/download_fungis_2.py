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

# Configuración del dataset balanceado
ESPECIES = {
    'morchella': [
        ('Morchella andinensis', 25),
        ('Morchella aysenina', 6),
        ('Morchella tridentina', 100),
        ('Morchella esculenta', 100),
        ('Morchella', 169),  # 400 - (25+6+100+100) = 169 restantes de Morchella spp
    ],
    'no_morchella': [
        # 🔴 Ascomicetes (parecidos morfológicamente)
        ('Gyromitra esculenta', 9),
        ('Gyromitra antarctica', 9),
        ('Verpa bohemica', 9),
        ('Helvella lacunosa', 9),
        ('Helvella crispa', 9),
        ('Helvella elastica', 9),
        ('Otidea onotica', 9),
        ('Peziza varia', 9),
        ('Scutellinia scutellata', 9),
        ('Sarcoscypha coccinea', 9),
        
        # 🍄 Agaricales (sombrero clásico)
        ('Amanita muscaria', 9),
        ('Amanita rubescens', 9),
        ('Amanita gemmata', 9),
        ('Agaricus campestris', 9),
        ('Agaricus arvensis', 9),
        ('Macrolepiota procera', 9),
        ('Chlorophyllum rachodes', 9),
        ('Lepiota cristata', 9),
        ('Tricholoma equestre', 9),
        ('Tricholoma terreum', 9),
        
        # 🍄 Géneros MUY comunes en Chile
        ('Cortinarius magellanicus', 9),
        ('Cortinarius', 9),
        ('Entoloma necopinatum', 9),
        ('Entoloma', 9),
        ('Mycena', 9),
        ('Clitocybe', 9),
        ('Hygrocybe', 9),
        ('Hygrophorus', 9),
        ('Laccaria laccata', 9),
        ('Laccaria', 9),
        
        # 🌲 Hongos de bosque patagónico
        ('Boletus loyo', 9),
        ('Suillus luteus', 9),
        ('Suillus granulatus', 9),
        ('Leccinum', 9),
        ('Russula', 9),
        ('Lactarius deliciosus', 9),
        ('Lactarius', 9),
        ('Ramaria', 9),
        ('Clavaria', 9),
        ('Clavariadelphus', 9),
        
        # 🪵 Poliporos y hongos de madera
        ('Ganoderma applanatum', 9),
        ('Fomes fomentarius', 9),
        ('Trametes versicolor', 9),
        ('Polyporus arcularius', 9),
        ('Lenzites betulina', 9),
        ('Phellinus', 9),
        ('Inonotus', 9),
        
        # 💨 Gasteroides (formas raras, buen negativo)
        ('Lycoperdon perlatum', 9),
        ('Lycoperdon', 9),
        ('Calvatia gigantea', 9),
        ('Scleroderma citrinum', 9),
        ('Geastrum fornicatum', 9),
        ('Geastrum', 9),
        
        # 🍄 Otros comunes en iNaturalist
        ('Coprinus comatus', 9),
        ('Coprinellus micaceus', 9),
        ('Psilocybe', 9),
        ('Panaeolus', 9),
        ('Hypholoma fasciculare', 9),
        ('Pholiota', 9),
        ('Armillaria mellea', 9),
        
        # 🌿 Extra patagónicos / frecuentes
        ('Pleurotus ostreatus', 10),
        ('Hohenbuehelia', 10),
        ('Clitopilus prunulus', 10),
        ('Pseudoclitocybe', 10),
        ('Tulostoma', 10),
        ('Poronia', 10),
        ('Dacrymyces palmatus', 10),
        ('Tremella mesenterica', 10),
        ('Exidia', 10),
        ('Ascocoryne sarcoides', 10),
    ]
}

# Acumula las URLs de las imágenes en una lista
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
            print(f"  ⚠️ Error fetching page {page}: {str(e)[:50]}")
            break
    
    return results

# Purga segura del dataset antes de descargar
def purge_dataset():
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
        print("🧹 Dataset purgado: morchella/ y no_morchella/ reiniciados")
    except Exception as e:
        print(f"⚠️ Error purgando dataset: {e}")

# Descarga una sola imagen
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

# Guarda las imágenes en la carpeta /dataset con concurrencia
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

# Endpoint para descargar dataset balanceado de hongos
class DownloadImages2(Resource):
    @swag_from('../flasgger/download_fungis_2.yml')
    def post(self):
        start_time = time.time()
        total_success = 0
        total_failed = 0
        resultados = []
        
        # Purgar dataset al inicio siempre
        purge_dataset()
        
        # Validar cantidades
        total_morchella = sum(cantidad for _, cantidad in ESPECIES['morchella'])
        total_no_morchella = sum(cantidad for _, cantidad in ESPECIES['no_morchella'])
        
        print(f"\n{'='*60}")
        print(f"🍄 INICIANDO DESCARGA DE DATASET BALANCEADO")
        print(f"{'='*60}")
        print(f"📊 Target: {total_morchella} Morchella + {total_no_morchella} NO-Morchella")
        print(f"📊 Total especies: {len(ESPECIES['morchella']) + len(ESPECIES['no_morchella'])}")
        print(f"{'='*60}\n")
        
        try:
            for categoria, especies in ESPECIES.items():
                folder_path = os.path.join(DATASET_DIR, categoria)
                categoria_success = 0
                categoria_failed = 0
                
                print(f"\n{'─'*60}")
                print(f"📁 CATEGORÍA: {categoria.upper()}")
                print(f"{'─'*60}")
                
                for nombre_especie, cantidad in especies:
                    print(f"\n🔍 [{nombre_especie}] Solicitando {cantidad} imágenes...")
                    try:
                        urls = fetch_images(nombre_especie, cantidad)
                        print(f"  📥 Encontradas {len(urls)} URLs")
                        
                        if urls:
                            especie_clean = nombre_especie.replace(' ', '_').replace('/', '-')
                            success, failed = save_images(urls, folder_path, especie_clean, max_workers=4)
                            total_success += success
                            total_failed += failed
                            categoria_success += success
                            categoria_failed += failed
                            resultados.append({
                                'especie': nombre_especie,
                                'categoria': categoria,
                                'solicitadas': cantidad,
                                'encontradas': len(urls),
                                'exitosas': success,
                                'fallidas': failed
                            })
                            time.sleep(0.5)  # ⬅️ AÑADIR: Pausa entre especies
                        else:
                            print(f"  ⚠️ No se encontraron imágenes para {nombre_especie}")
                            resultados.append({
                                'especie': nombre_especie,
                                'categoria': categoria,
                                'solicitadas': cantidad,
                                'encontradas': 0,
                                'exitosas': 0,
                                'fallidas': 0,
                                'mensaje': 'No se encontraron imágenes'
                            })
                    except Exception as e:
                        print(f"  ❌ Error procesando {nombre_especie}: {str(e)}")
                        resultados.append({
                            'especie': nombre_especie,
                            'categoria': categoria,
                            'solicitadas': cantidad,
                            'exitosas': 0,
                            'fallidas': cantidad,
                            'error': str(e)[:100]
                        })
                
                print(f"\n{'─'*60}")
                print(f"📊 RESUMEN {categoria.upper()}: ✓ {categoria_success} exitosas | ✗ {categoria_failed} fallidas")
                print(f"  ✅ Total categoría: {categoria_success} exitosas | {categoria_failed} fallidas")
                time.sleep(1)  # ⬅️ AÑADIR: Pausa entre categorías
            
            elapsed_time = time.time() - start_time
            print(f"\n{'='*60}")
            print(f"✅ PROCESO COMPLETADO EN {elapsed_time:.2f} SEGUNDOS")
            print(f"{'='*60}")
            print(f"📊 TOTAL EXITOSAS: {total_success}")
            print(f"📊 TOTAL FALLIDAS: {total_failed}")
            print(f"📊 TASA DE ÉXITO: {(total_success/(total_success+total_failed)*100):.1f}%")
            print(f"{'='*60}\n")
            
            return {
                'message': 'Descarga completada',
                'tiempo_segundos': round(elapsed_time, 2),
                'total_exitosas': total_success,
                'total_fallidas': total_failed,
                'tasa_exito': round(total_success/(total_success+total_failed)*100, 2) if (total_success+total_failed) > 0 else 0,
                'morchella_target': total_morchella,
                'no_morchella_target': total_no_morchella,
                'detalle': resultados
            }, 200
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            print(f"\n❌ ERROR GENERAL EN DESCARGA: {str(e)}")
            return {
                'error': 'Error en el proceso de descarga',
                'detalle': str(e),
                'tiempo_segundos': round(elapsed_time, 2),
                'total_exitosas': total_success,
                'total_fallidas': total_failed
            }, 500

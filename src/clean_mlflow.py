import os
import shutil
import mlflow

def clean_mlflow():
    """Limpia archivos corruptos de MLflow y reinicia la configuración"""
    print("🧹 Limpiando MLflow...")
    
    # Eliminar directorio mlruns corrupto
    if os.path.exists("mlruns"):
        try:
            shutil.rmtree("mlruns")
            print("✅ Directorio mlruns eliminado")
        except Exception as e:
            print(f"⚠️ Error eliminando mlruns: {e}")
    
    # Eliminar base de datos SQLite
    if os.path.exists("mlflow.db"):
        try:
            os.remove("mlflow.db")
            print("✅ Base de datos mlflow.db eliminada")
        except Exception as e:
            print(f"⚠️ Error eliminando mlflow.db: {e}")
    
    # Eliminar archivo model_info.json si existe
    if os.path.exists("model_info.json"):
        try:
            os.remove("model_info.json")
            print("✅ model_info.json eliminado")
        except Exception as e:
            print(f"⚠️ Error eliminando model_info.json: {e}")
    
    # Crear nuevo experimento
    try:
        mlflow.set_tracking_uri("sqlite:///mlflow.db")
        mlflow.set_experiment("morchella_detection")
        print("✅ Nuevo experimento 'morchella_detection' creado")
        print("✅ MLflow configurado correctamente")
    except Exception as e:
        print(f"❌ Error configurando MLflow: {e}")
        return False
    
    return True

def verify_cleanup():
    """Verifica que la limpieza fue exitosa"""
    print("\n🔍 Verificando limpieza...")
    
    # Verificar que mlruns no existe
    if not os.path.exists("mlruns"):
        print("✅ Directorio mlruns eliminado correctamente")
    else:
        print("❌ Directorio mlruns aún existe")
    
    # Verificar que mlflow.db se creó
    if os.path.exists("mlflow.db"):
        print("✅ Nueva base de datos mlflow.db creada")
    else:
        print("❌ Base de datos mlflow.db no se creó")
    
    # Verificar experimento
    try:
        experiments = mlflow.search_experiments()
        if len(experiments) > 0:
            print(f"✅ Experimentos disponibles: {len(experiments)}")
            for exp in experiments:
                print(f"   - {exp.name} (ID: {exp.experiment_id})")
        else:
            print("❌ No se encontraron experimentos")
    except Exception as e:
        print(f"❌ Error verificando experimentos: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando limpieza de MLflow...")
    print("=" * 50)
    
    success = clean_mlflow()
    
    if success:
        verify_cleanup()
        print("\n" + "=" * 50)
        print("🎉 Limpieza completada exitosamente!")
        print("\n📝 Próximos pasos:")
        print("1. Ejecuta: python train_model.py")
        print("2. Ejecuta: mlflow ui")
        print("3. Abre http://localhost:5000 en tu navegador")
    else:
        print("\n❌ La limpieza no se completó correctamente")
        print("Intenta ejecutar el script nuevamente") 
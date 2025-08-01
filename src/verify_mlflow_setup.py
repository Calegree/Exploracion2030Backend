import mlflow
import sqlite3
import os
from datetime import datetime

def verify_mlflow_setup():
    """
    Verifica que MLflow esté configurado correctamente con SQLite
    """
    print("Verificando configuracion de MLflow...")
    print("=" * 50)
    
    # Verificar tracking URI
    tracking_uri = mlflow.get_tracking_uri()
    print(f"Tracking URI: {tracking_uri}")
    
    if "sqlite" in tracking_uri:
        print("SQLite configurado correctamente")
    else:
        print("SQLite no esta configurado")
        return False
    
    # Verificar base de datos SQLite
    db_path = "mlflow.db"
    if os.path.exists(db_path):
        print(f"Base de datos encontrada: {db_path}")
        
        # Verificar que la base de datos es accesible
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print(f"Base de datos accesible. Tablas: {len(tables)}")
            conn.close()
        except Exception as e:
            print(f"Error accediendo a la base de datos: {e}")
            return False
    else:
        print(f"Base de datos no encontrada: {db_path}")
        print("   Se creara automaticamente al ejecutar el primer experimento")
    
    # Verificar experimentos
    try:
        experiments = mlflow.search_experiments()
        print(f"Experimentos disponibles: {len(experiments)}")
        
        for exp in experiments:
            print(f"   - {exp.name} (ID: {exp.experiment_id})")
            
            # Verificar runs en cada experimento
            runs = mlflow.search_runs(experiment_names=[exp.name])
            print(f"     Runs: {len(runs)}")
            
    except Exception as e:
        print(f"Error verificando experimentos: {e}")
        return False
    
    # Verificar que no hay directorio mlruns (deberia usar SQLite)
    if os.path.exists("mlruns"):
        print("Directorio mlruns encontrado - esto puede causar conflictos")
        print("   Recomendacion: ejecutar clean_mlflow.py")
    else:
        print("No hay directorio mlruns (correcto para SQLite)")
    
    print("=" * 50)
    print("Verificacion completada")
    return True

def test_mlflow_connection():
    """
    Prueba la conexion con MLflow
    """
    print("\nProbando conexion con MLflow...")
    
    try:
        # Intentar crear un experimento de prueba
        test_exp_name = "test_connection"
        mlflow.set_experiment(test_exp_name)
        
        with mlflow.start_run(run_name="test_run"):
            mlflow.log_param("test_param", "test_value")
            mlflow.log_metric("test_metric", 0.5)
            mlflow.set_tag("test_tag", "test")
        
        print("Conexion con MLflow exitosa")
        
        # Limpiar experimento de prueba
        try:
            mlflow.delete_experiment(mlflow.get_experiment_by_name(test_exp_name).experiment_id)
            print("Experimento de prueba eliminado")
        except:
            pass
            
        return True
        
    except Exception as e:
        print(f"Error en conexion con MLflow: {e}")
        return False

if __name__ == "__main__":
    print("Iniciando verificacion de MLflow...")
    
    # Configurar MLflow
    mlflow.set_tracking_uri("sqlite:///mlflow.db")
    
    # Verificar configuracion
    setup_ok = verify_mlflow_setup()
    
    if setup_ok:
        # Probar conexion
        connection_ok = test_mlflow_connection()
        
        if connection_ok:
            print("\nTodo esta configurado correctamente!")
            print("\nProximos pasos:")
            print("1. Ejecuta: python train_model.py")
            print("2. Ejecuta: mlflow ui")
            print("3. Abre http://localhost:5000 en tu navegador")
        else:
            print("\nHay problemas con la conexion de MLflow")
    else:
        print("\nLa configuracion de MLflow no es correcta")
        print("Ejecuta: python clean_mlflow.py") 
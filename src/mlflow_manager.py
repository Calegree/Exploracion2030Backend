import mlflow
import os
import json
from datetime import datetime

class MLflowManager:
    def __init__(self, tracking_uri="sqlite:///mlflow.db"):
        mlflow.set_tracking_uri(tracking_uri)
        self.experiment_name = "morchella_detection"
        
    def list_experiments(self):
        """
        Lista todos los experimentos
        """
        experiments = mlflow.search_experiments()
        return [exp for exp in experiments]
    
    def list_runs(self, experiment_name=None):
        """
        Lista todas las ejecuciones de un experimento
        """
        if experiment_name is None:
            experiment_name = self.experiment_name
            
        runs = mlflow.search_runs(
            experiment_names=[experiment_name],
            order_by=["start_time DESC"]
        )
        return runs
    
    def get_best_run(self, metric="val_accuracy", experiment_name=None):
        """
        Obtiene la mejor ejecución basada en una métrica
        """
        if experiment_name is None:
            experiment_name = self.experiment_name
            
        runs = mlflow.search_runs(
            experiment_names=[experiment_name],
            order_by=[f"metrics.{metric} DESC"],
            max_results=1
        )
        
        if len(runs) > 0:
            return runs.iloc[0]
        return None
    
    def register_model(self, run_id, model_name="morchella_model"):
        """
        Registra un modelo en el registro de modelos
        """
        model_uri = f"runs:/{run_id}/model"
        mlflow.register_model(model_uri, model_name)
        print(f"✅ Modelo registrado: {model_name}")
    
    def load_registered_model(self, model_name="morchella_model", version=None):
        """
        Carga un modelo registrado
        """
        if version:
            model_uri = f"models:/{model_name}/{version}"
        else:
            model_uri = f"models:/{model_name}/latest"
            
        model = mlflow.keras.load_model(model_uri)
        return model
    
    def export_model_info(self, output_file="model_info.json"):
        """
        Exporta información del modelo a un archivo JSON
        """
        best_run = self.get_best_run()
        
        if best_run is not None:
            model_info = {
                "run_id": best_run["run_id"],
                "active_run_id": best_run["run_id"],   # <-- clave añadida
                "experiment_id": best_run["experiment_id"],
                "start_time": best_run["start_time"].isoformat(),
                "end_time": best_run["end_time"].isoformat(),
                "metrics": {
                    "val_accuracy": best_run["metrics.val_accuracy"],
                    "val_loss": best_run["metrics.val_loss"]
                },
                "params": {
                    "img_size": best_run["params.img_size"],
                    "batch_size": best_run["params.batch_size"],
                    "epochs": best_run["params.epochs"],
                    "learning_rate": best_run["params.learning_rate"]
                }
            }
            
            with open(output_file, 'w') as f:
                json.dump(model_info, f, indent=2)
            
            print(f"✅ Información del modelo exportada a: {output_file}")
            return model_info
        else:
            print("❌ No se encontraron ejecuciones")
            return None

def main():
    """
    Función principal para gestionar MLflow
    """
    manager = MLflowManager()
    
    print("🔍 Experimentos disponibles:")
    experiments = manager.list_experiments()
    for exp in experiments:
        print(f"  - {exp.name} (ID: {exp.experiment_id})")
    
    print("\n📊 Últimas ejecuciones:")
    runs = manager.list_runs()
    if len(runs) > 0:
        for i, run in runs.head(5).iterrows():
            print(f"  - Run {run['run_id'][:8]}... | Accuracy: {run['metrics.val_accuracy']:.4f} | Loss: {run['metrics.val_loss']:.4f}")
    
    print("\n🏆 Mejor ejecución:")
    best_run = manager.get_best_run()
    if best_run is not None:
        print(f"  - Run ID: {best_run['run_id']}")
        print(f"  - Accuracy: {best_run['metrics.val_accuracy']:.4f}")
        print(f"  - Loss: {best_run['metrics.val_loss']:.4f}")
        
        # Registrar el mejor modelo
        manager.register_model(best_run['run_id'])
        
        # Exportar información
        manager.export_model_info()

if __name__ == "__main__":
    main()
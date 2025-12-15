"""
Logger automático de Model Cards en MLflow/MinIO

Este módulo se encarga de:
1. Generar el Model Card (.qmd)
2. Compilarlo a HTML con Quarto
3. Guardar ambos en MLflow como artifacts
4. Todo automáticamente al terminar el entrenamiento
"""

import os
import json
import subprocess
from pathlib import Path
from datetime import datetime
import mlflow
from mlflow.tracking import MlflowClient


class ModelCardMLflowLogger:
    """Maneja la generación y logging automático de Model Cards en MLflow"""
    
    def __init__(self, run_id: str, model_type: str, dataset_path: str):
        """
        Args:
            run_id: ID del run actual en MLflow
            model_type: Tipo de modelo (ej: 'EfficientNetB0', 'MobileNetV2')
            dataset_path: Ruta al dataset
        """
        self.run_id = run_id
        self.model_type = model_type
        self.dataset_path = dataset_path
        self.client = MlflowClient()
        
        # Directorio temporal para los archivos
        self.temp_dir = Path("/tmp/model_cards_temp")
        self.temp_dir.mkdir(exist_ok=True)
    
    def log_model_card_to_mlflow(self):
        """
        Genera y sube el Model Card (QMD + HTML + PDF) a MLflow
        """
        try:
            print("📋 Generando Model Card...")
            
            # Obtener información del run
            run_info = self._get_run_info()
            
            # Generar QMD
            qmd_path = self._create_qmd_file(run_info)
            print(f"✅ QMD generado: {qmd_path}")
            
            # Compilar a HTML con Quarto
            html_path = self._compile_to_html(qmd_path)
            if html_path != qmd_path:
                print(f"✅ HTML compilado: {html_path}")
            else:
                print(f"⚠️ No se compiló a HTML (Quarto no disponible)")
                html_path = None
            
            # Compilar a PDF con Quarto
            pdf_path = self._compile_to_pdf(qmd_path)
            if pdf_path and pdf_path != qmd_path:
                print(f"✅ PDF compilado: {pdf_path}")
            else:
                print(f"⚠️ No se compiló a PDF (Quarto no disponible)")
                pdf_path = None
            
            # Subir a MLflow
            self._upload_to_mlflow(qmd_path, html_path, pdf_path)
            
            print(f"✅ Model Card guardado en MLflow como artifact (QMD + HTML + PDF)")
            
        except Exception as e:
            print(f"⚠️ Error generando Model Card: {e}")
            import traceback
            traceback.print_exc()
    
    def _get_run_info(self) -> dict:
        """Obtiene toda la información del run actual"""
        run = self.client.get_run(self.run_id)
        
        return {
            'params': run.data.params,
            'metrics': run.data.metrics,
            'tags': run.data.tags,
            'start_time': datetime.fromtimestamp(run.info.start_time / 1000),
            'end_time': datetime.fromtimestamp(run.info.end_time / 1000) if run.info.end_time else None,
        }
    
    def _count_dataset_images(self) -> dict:
        """Cuenta imágenes en el dataset"""
        import glob
        
        morchella_path = os.path.join(self.dataset_path, 'morchella')
        no_morchella_path = os.path.join(self.dataset_path, 'no_morchella')
        
        morchella_count = len(
            glob.glob(os.path.join(morchella_path, '*.jpg')) +
            glob.glob(os.path.join(morchella_path, '*.jpeg')) +
            glob.glob(os.path.join(morchella_path, '*.png'))
        )
        
        no_morchella_count = len(
            glob.glob(os.path.join(no_morchella_path, '*.jpg')) +
            glob.glob(os.path.join(no_morchella_path, '*.jpeg')) +
            glob.glob(os.path.join(no_morchella_path, '*.png'))
        )
        
        return {
            'morchella': morchella_count,
            'no_morchella': no_morchella_count,
            'total': morchella_count + no_morchella_count
        }
    
    def _create_qmd_file(self, run_info: dict) -> str:
        """Crea el archivo .qmd del Model Card"""
        
        params = run_info['params']
        metrics = run_info['metrics']
        dataset_info = self._count_dataset_images()
        
        # Obtener matriz de confusión
        cm_data = self._get_confusion_matrix()
        
        # Construir contenido QMD
        qmd_content = self._build_qmd_content(
            run_info, params, metrics, dataset_info, cm_data
        )
        
        # Guardar QMD
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        qmd_filename = f"model_card_{self.model_type}_{timestamp}.qmd"
        qmd_path = self.temp_dir / qmd_filename
        
        with open(qmd_path, 'w', encoding='utf-8') as f:
            f.write(qmd_content)
        
        return str(qmd_path)
    
    def _build_qmd_content(self, run_info, params, metrics, dataset_info, cm_data) -> str:
        """Construye el contenido del archivo Quarto"""
        
        timestamp = run_info['start_time'].strftime('%Y-%m-%d %H:%M:%S')
        duration = (run_info['end_time'] - run_info['start_time']).total_seconds() / 60 if run_info['end_time'] else 0
        
        # Información de métricas
        accuracy = metrics.get('val_accuracy', 0)
        precision = metrics.get('val_precision', 0)
        recall = metrics.get('val_recall', 0)
        f1 = metrics.get('val_f1_score', 0)
        loss = metrics.get('val_loss', 0)
        
        qmd = f"""---
title: "Model Card: {self.model_type}"
subtitle: "Morchella Detection Classification Model"
date: "{timestamp}"
format:
  html:
    theme: cosmo
    toc: true
    toc-depth: 2
    number-sections: true
    code-fold: true
    embed-resources: true
---

## 🎯 Model Overview

**Model Name:** {self.model_type}  
**Task:** Binary Image Classification (Morchella vs Non-Morchella)  
**Run ID:** `{self.run_id}`  
**Training Date:** {timestamp}  
**Training Duration:** {duration:.1f} minutos  

---

## 📊 Performance Metrics

| Metric | Value |
|--------|-------|
| **Accuracy** | {accuracy:.4f} ({accuracy*100:.2f}%) |
| **Precision** | {precision:.4f} ({precision*100:.2f}%) |
| **Recall** | {recall:.4f} ({recall*100:.2f}%) |
| **F1-Score** | {f1:.4f} |
| **Validation Loss** | {loss:.4f} |

"""
        
        # Matriz de confusión
        if cm_data and len(cm_data) >= 2:
            tn, fp = cm_data[0][0], cm_data[0][1]
            fn, tp = cm_data[1][0], cm_data[1][1]
            
            qmd += f"""
### 🔲 Confusion Matrix

```
                         Pred: No Morchella | Pred: Morchella
Actual: No Morchella              {tn:3d}              {fp:3d}
Actual: Morchella                 {fn:3d}              {tp:3d}
```

**Error Analysis:**

| Type | Count | Meaning |
|------|-------|---------|
| **True Negatives (TN)** | {tn} | Correctly identified as NOT Morchella ✅ |
| **False Positives (FP)** | {fp} | Incorrectly identified as Morchella ❌ |
| **False Negatives (FN)** | {fn} | Incorrectly identified as NOT Morchella ❌ |
| **True Positives (TP)** | {tp} | Correctly identified as Morchella ✅ |

"""
        
        # Dataset information
        qmd += f"""
## 📦 Dataset Information

| Class | Count |
|-------|-------|
| Morchella | {dataset_info['morchella']} |
| No-Morchella | {dataset_info['no_morchella']} |
| **Total** | **{dataset_info['total']}** |

Imbalance ratio: {dataset_info['no_morchella']/max(dataset_info['morchella'], 1):.1f}:1

---

## ⚙️ Training Configuration

| Parameter | Value |
|-----------|-------|
| Model Architecture | {params.get('model_type', 'N/A')} |
| Image Size | {params.get('img_size', 'N/A')}×{params.get('img_size', 'N/A')} |
| Batch Size | {params.get('batch_size', 'N/A')} |
| Epochs Trained | {params.get('epochs', 'N/A')} |
| Learning Rate | {params.get('learning_rate', 'N/A')} |
| Optimizer | Adam |
| Loss Function | Binary Crossentropy |
| Early Stopping | Yes (patience=5) |
| Data Augmentation | Yes |

---

## ⚠️ Model Limitations

### Known Issues
- Performance varies with lighting conditions
- Limited to trained Morchella species
- May confuse with similar fungi (Giromitra)
- Performance on immature/damaged specimens unclear

### Recommendations
- ✅ Use as part of ensemble with expert review
- ✅ Suitable for API predictions (non-critical)
- ❌ NOT for critical food safety decisions alone
- ✅ Retrain regularly with new data

---

## 📌 MLflow Run Information

- **Run ID:** {self.run_id}
- **Model Type:** {self.model_type}
- **Dataset Size:** {dataset_info['total']} images

---

*Generated automatically at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*Stored in MLflow as artifact: model_cards/*
"""
        
        return qmd
    
    def _get_confusion_matrix(self):
        """Obtiene la matriz de confusión desde MLflow"""
        try:
            artifacts = self.client.list_artifacts(self.run_id, "confusion_matrix")
            for artifact in artifacts:
                if artifact.path.endswith('confusion_matrix.json'):
                    local_path = self.client.download_artifacts(self.run_id, artifact.path)
                    with open(local_path, 'r') as f:
                        return json.load(f).get('confusion_matrix')
        except Exception as e:
            pass
        return None
    
    def _compile_to_html(self, qmd_path: str) -> str:
        """Compila el .qmd a HTML usando Quarto"""
        try:
            # Verificar que Quarto está instalado
            result = subprocess.run(['quarto', '--version'], capture_output=True, text=True)
            if result.returncode != 0:
                print("⚠️ Quarto no está instalado - guardando solo QMD")
                return qmd_path
            
            # Compilar con Quarto
            print(f"🔨 Compilando a HTML...")
            result = subprocess.run(
                ['quarto', 'render', qmd_path, '--to', 'html'],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                html_path = qmd_path.replace('.qmd', '.html')
                return html_path
            else:
                print(f"⚠️ Error compilando Quarto")
                return qmd_path
        
        except FileNotFoundError:
            print("⚠️ Quarto no encontrado")
            return qmd_path
        except subprocess.TimeoutExpired:
            print("⚠️ Timeout compilando Quarto")
            return qmd_path
        except Exception as e:
            print(f"⚠️ Error en compilación: {e}")
            return qmd_path
    
    def _compile_to_pdf(self, qmd_path: str):
        """Compila el .qmd a PDF usando Quarto"""
        try:
            # Verificar que Quarto está instalado
            result = subprocess.run(['quarto', '--version'], capture_output=True, text=True)
            if result.returncode != 0:
                print("⚠️ Quarto no está instalado - PDF no se generará")
                return None
            
            # Verificar que pandoc está disponible (requerido para PDF)
            result = subprocess.run(['pandoc', '--version'], capture_output=True, text=True)
            if result.returncode != 0:
                print("⚠️ Pandoc no disponible - PDF no se generará")
                return None
            
            # Compilar con Quarto a PDF
            print(f"📄 Compilando a PDF...")
            result = subprocess.run(
                ['quarto', 'render', qmd_path, '--to', 'pdf'],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                pdf_path = qmd_path.replace('.qmd', '.pdf')
                return pdf_path
            else:
                print(f"⚠️ Error compilando Quarto a PDF")
                return None
        
        except FileNotFoundError:
            print("⚠️ Quarto/Pandoc no encontrado")
            return None
        except subprocess.TimeoutExpired:
            print("⚠️ Timeout compilando PDF")
            return None
        except Exception as e:
            print(f"⚠️ Error en compilación PDF: {e}")
            return None
    
    def _upload_to_mlflow(self, qmd_path: str, html_path: str = None, pdf_path: str = None):
        """Sube el Model Card a MLflow como artifacts"""
        
        try:
            # Log QMD
            mlflow.log_artifact(qmd_path, artifact_path="model_cards")
            print(f"✅ QMD subido a MLflow/MinIO")
            
            # Log HTML si existe
            if html_path and os.path.exists(html_path):
                mlflow.log_artifact(html_path, artifact_path="model_cards")
                print(f"✅ HTML subido a MLflow/MinIO")
            
            # Log PDF si existe
            if pdf_path and os.path.exists(pdf_path):
                mlflow.log_artifact(pdf_path, artifact_path="model_cards")
                print(f"✅ PDF subido a MLflow/MinIO")
        
        except Exception as e:
            print(f"⚠️ Error subiendo a MLflow: {e}")


def log_model_card_automatic(run_id: str, model_type: str, dataset_path: str):
    """
    Función principal para generar y loguear Model Card automáticamente
    
    Úsalo en tus scripts de entrenamiento:
    ```python
    from model_card_mlflow_logger import log_model_card_automatic
    
    # Al final del entrenamiento, dentro del run de MLflow:
    log_model_card_automatic(run_id, 'EfficientNetB0', 'src/dataset')
    ```
    """
    logger = ModelCardMLflowLogger(run_id, model_type, dataset_path)
    logger.log_model_card_to_mlflow()

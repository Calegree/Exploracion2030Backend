"""
Generador automático de Model Cards en Quarto para modelos de clasificación de Morchella

Este módulo:
1. Extrae métricas y parámetros de MLflow
2. Obtiene información del dataset
3. Genera un documento Quarto (.qmd) profesional con el Model Card
4. Incluye tablas, gráficos y análisis del modelo
"""

import os
import json
import mlflow
from mlflow.tracking import MlflowClient
from datetime import datetime
from pathlib import Path


def get_run_info(run_id: str):
    """
    Obtiene toda la información de un run de MLflow
    
    Returns:
        dict: Parámetros, métricas, tags y artifacts del run
    """
    client = MlflowClient()
    run = client.get_run(run_id)
    
    return {
        'params': run.data.params,
        'metrics': run.data.metrics,
        'tags': run.data.tags,
        'start_time': datetime.fromtimestamp(run.info.start_time / 1000),
        'end_time': datetime.fromtimestamp(run.info.end_time / 1000) if run.info.end_time else None,
    }


def get_confusion_matrix_data(run_id: str):
    """
    Obtiene la matriz de confusión desde los artifacts de MLflow
    
    Returns:
        dict o None: Matriz de confusión en formato dict
    """
    try:
        client = MlflowClient()
        artifacts = client.list_artifacts(run_id, "confusion_matrix")
        
        # Buscar archivo JSON de confusión
        for artifact in artifacts:
            if artifact.path.endswith('confusion_matrix.json'):
                local_path = client.download_artifacts(run_id, artifact.path)
                with open(local_path, 'r', encoding='utf-8') as f:
                    return json.load(f).get('confusion_matrix')
    except Exception as e:
        print(f"⚠️ No se pudo cargar matriz de confusión: {e}")
    
    return None


def calculate_metrics_from_confusion_matrix(cm):
    """
    Calcula métricas adicionales a partir de la matriz de confusión
    
    Args:
        cm: [[TN, FP], [FN, TP]]
    
    Returns:
        dict: Métricas calculadas
    """
    if cm is None or len(cm) < 2:
        return {}
    
    TN, FP = cm[0][0], cm[0][1]
    FN, TP = cm[1][0], cm[1][1]
    
    total = TN + FP + FN + TP
    
    metrics = {
        'accuracy': (TP + TN) / total if total > 0 else 0,
        'precision_morchella': TP / (TP + FP) if (TP + FP) > 0 else 0,
        'recall_morchella': TP / (TP + FN) if (TP + FN) > 0 else 0,
        'precision_no_morchella': TN / (TN + FN) if (TN + FN) > 0 else 0,
        'recall_no_morchella': TN / (TN + FP) if (TN + FP) > 0 else 0,
        'tn': TN,
        'fp': FP,
        'fn': FN,
        'tp': TP,
    }
    
    # F1-score
    if metrics['precision_morchella'] + metrics['recall_morchella'] > 0:
        metrics['f1_morchella'] = 2 * (metrics['precision_morchella'] * metrics['recall_morchella']) / (
            metrics['precision_morchella'] + metrics['recall_morchella']
        )
    
    if metrics['precision_no_morchella'] + metrics['recall_no_morchella'] > 0:
        metrics['f1_no_morchella'] = 2 * (metrics['precision_no_morchella'] * metrics['recall_no_morchella']) / (
            metrics['precision_no_morchella'] + metrics['recall_no_morchella']
        )
    
    return metrics


def count_dataset_images(dataset_path: str):
    """
    Cuenta las imágenes en el dataset
    """
    import glob
    
    morchella_path = os.path.join(dataset_path, 'morchella')
    no_morchella_path = os.path.join(dataset_path, 'no_morchella')
    
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
    
    return morchella_count, no_morchella_count


def create_model_card_qmd(run_id: str, dataset_path: str, output_dir: str = None):
    """
    Genera un archivo Quarto (.qmd) con el Model Card
    
    Args:
        run_id: ID del run en MLflow
        dataset_path: Ruta al directorio del dataset
        output_dir: Directorio donde guardar el archivo (default: model_cards/)
    
    Returns:
        str: Ruta del archivo generado
    """
    
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), '..', 'model_cards')
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Obtener información del run
    run_info = get_run_info(run_id)
    params = run_info['params']
    metrics = run_info['metrics']
    tags = run_info['tags']
    
    # Información del dataset
    try:
        morchella_count, no_morchella_count = count_dataset_images(dataset_path)
    except:
        morchella_count, no_morchella_count = 0, 0
    
    # Matriz de confusión
    cm = get_confusion_matrix_data(run_id)
    calculated_metrics = calculate_metrics_from_confusion_matrix(cm)
    
    # Obtener modelo base
    model_type = tags.get('base_model', params.get('model_type', 'Unknown'))
    
    # Nombre del archivo
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"model_card_{model_type}_{timestamp}.qmd"
    filepath = os.path.join(output_dir, filename)
    
    # Crear contenido Quarto
    qmd_content = f"""---
title: "Model Card: {model_type} - Morchella Classifier"
author: "Morchella Detection Project"
date: "{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
format:
  html:
    toc: true
    toc-depth: 3
    code-fold: true
    theme: cosmo
    css: model-card-style.css
---

## 1. Model Overview

**Model ID:** `{run_id}`

**Model Type:** {model_type}

**Task:** Binary Image Classification (Morchella vs No-Morchella)

**Created:** {run_info['start_time'].strftime('%Y-%m-%d %H:%M:%S')}

**Status:** ✅ Completed

---

## 2. Model Description

### Architecture
- **Base Model:** {model_type}
- **Transfer Learning:** {params.get('transfer_learning', 'Yes')}
- **Fine-tuning:** Last layers unfrozen
- **Input Size:** {params.get('img_size', 224)}×{params.get('img_size', 224)} pixels
- **Output:** Binary classification (Sigmoid activation)

### Key Features
- Pre-trained weights from ImageNet
- Data augmentation enabled
- Early stopping enabled
- Learning rate reduction on plateau

---

## 3. Dataset

### Statistics
| Metric | Value |
|--------|-------|
| Morchella Images | {morchella_count} |
| No-Morchella Images | {no_morchella_count} |
| **Total** | **{morchella_count + no_morchella_count}** |
| Imbalance Ratio | {no_morchella_count/morchella_count if morchella_count > 0 else 0:.2f}:1 |

### Train/Val/Test Split
| Set | Size |
|-----|------|
| Training | {params.get('train_split', '70%')} |
| Validation | {params.get('val_split', '15%')} |
| Test | {params.get('test_split', '15%')} |

### Preprocessing & Augmentation
- **Normalization:** [0, 1] (pixel values divided by 255)
- **Augmentation Strategy:** 
  - Rotation: ±30°
  - Horizontal/Vertical Flip: Yes
  - Zoom: 0.2
  - Shear: 0.15
  - Width/Height Shift: 0.2

---

## 4. Training Configuration

### Hyperparameters

| Parameter | Value |
|-----------|-------|
| Batch Size | {params.get('batch_size', 'N/A')} |
| Learning Rate | {params.get('learning_rate', 'N/A')} |
| Optimizer | Adam |
| Loss Function | Binary Crossentropy |
| Epochs | {params.get('epochs', 'N/A')} |
| Early Stopping | Yes (patience=5) |
| Dropout Rate | {params.get('dropout_rate', 'N/A')} |

### Training Metrics Over Time
- Final Training Accuracy: {metrics.get('val_accuracy', 0):.4f}
- Final Validation Loss: {metrics.get('val_loss', 0):.4f}

---

## 5. Performance Metrics

### Overall Performance

| Metric | Score |
|--------|-------|
| **Accuracy** | {calculated_metrics.get('accuracy', 0):.4f} ({calculated_metrics.get('accuracy', 0)*100:.2f}%) |
| **F1-Score (Morchella)** | {calculated_metrics.get('f1_morchella', 0):.4f} |
| **F1-Score (No-Morchella)** | {calculated_metrics.get('f1_no_morchella', 0):.4f} |

### Per-Class Metrics

#### Morchella Detection
| Metric | Value |
|--------|-------|
| Precision | {calculated_metrics.get('precision_morchella', 0):.4f} |
| Recall | {calculated_metrics.get('recall_morchella', 0):.4f} |
| F1-Score | {calculated_metrics.get('f1_morchella', 0):.4f} |

> **Precision (Morchella):** Of all images classified as Morchella, {calculated_metrics.get('precision_morchella', 0)*100:.1f}% were actually Morchella.

> **Recall (Morchella):** The model correctly identifies {calculated_metrics.get('recall_morchella', 0)*100:.1f}% of actual Morchella images.

#### No-Morchella Detection
| Metric | Value |
|--------|-------|
| Precision | {calculated_metrics.get('precision_no_morchella', 0):.4f} |
| Recall | {calculated_metrics.get('recall_no_morchella', 0):.4f} |
| F1-Score | {calculated_metrics.get('f1_no_morchella', 0):.4f} |

> **Precision (No-Morchella):** Of all images classified as No-Morchella, {calculated_metrics.get('precision_no_morchella', 0)*100:.1f}% were actually No-Morchella.

> **Recall (No-Morchella):** The model correctly identifies {calculated_metrics.get('recall_no_morchella', 0)*100:.1f}% of actual No-Morchella images.

---

## 6. Confusion Matrix Analysis

### Raw Counts

```
                 Predicted: No-Morchella | Predicted: Morchella
Actual: No-Morchella        {calculated_metrics.get('tn', 0)}                  |           {calculated_metrics.get('fp', 0)}
Actual: Morchella           {calculated_metrics.get('fn', 0)}                  |           {calculated_metrics.get('tp', 0)}
```

### Error Analysis

- **True Negatives (TN):** {calculated_metrics.get('tn', 0)} - Correctly identified Non-Morchella
- **False Positives (FP):** {calculated_metrics.get('fp', 0)} - Non-Morchella misidentified as Morchella
- **False Negatives (FN):** {calculated_metrics.get('fn', 0)} - Morchella misidentified as Non-Morchella
- **True Positives (TP):** {calculated_metrics.get('tp', 0)} - Correctly identified Morchella

### Error Interpretation

| Error Type | Count | Impact |
|-----------|-------|--------|
| **False Positives** | {calculated_metrics.get('fp', 0)} | 🟡 Medium - Suggests look-alike fungi |
| **False Negatives** | {calculated_metrics.get('fn', 0)} | 🔴 High - Misses actual Morchella |

---

## 7. Model Strengths & Weaknesses

### ✅ Strengths

- Uses {model_type}, a modern efficient architecture
- Transfer learning from ImageNet
- Data augmentation to prevent overfitting
- Early stopping prevents overtraining

### ⚠️ Weaknesses & Limitations

1. **Class Imbalance:** The dataset has significantly more No-Morchella images
2. **Limited Dataset Size:** Consider collecting more Morchella samples
3. **Lighting Sensitivity:** Trained primarily on outdoor images
4. **False Negatives:** {calculated_metrics.get('fn', 0)} missed Morchella cases
5. **Similar Fungi:** May confuse with Giromitra or other morels

---

## 8. Use Cases & Recommendations

### ✅ Recommended Use
- API endpoint for user submissions
- Mobile app predictions
- Citizen science validation tool
- Field observation confirmation

### ❌ Not Recommended For
- Exclusive determination (always confirm with expert)
- Specimens with poor lighting
- Damaged or decomposed samples
- Real-time video processing without post-processing

### Risk Considerations
⚠️ **Food Safety:** Never rely solely on this model for culinary decisions.
Always have expert verification before consumption.

---

## 9. Bias & Fairness

### Known Issues
- Training data may have geographic bias (Latin America focus)
- Limited diversity in Morchella species representation
- Lighting conditions may not cover all real-world scenarios

### Recommendations
- Test with diverse lighting conditions
- Validate with local Morchella experts
- Collect seasonal variations data

---

## 10. Technical Details

### Environment
- Framework: TensorFlow/Keras
- Python Version: 3.10+
- MLflow Version: Latest

### Files & Artifacts
- Model File: `model_morchella_{model_type}.keras`
- Run ID: `{run_id}`
- Training Date: {run_info['start_time'].strftime('%Y-%m-%d')}

### Reproducibility
To reproduce this model:

```bash
# Set MLflow tracking URI
export MLFLOW_TRACKING_URI=http://mlflow:5001

# Train the model
docker-compose exec api python src/train.py --model {model_type.lower()}
```

---

## 11. Model Comparison

### {model_type} vs Alternatives

| Feature | {model_type} | MobileNetV2 | Custom CNN |
|---------|--------|-----------|-----------|
| Efficiency | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| Accuracy | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| Training Time | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |

---

## 12. Changelog

| Version | Date | Changes |
|---------|------|---------|
| v1.0 | {datetime.now().strftime('%Y-%m-%d')} | Initial Model Card generation |

---

## 13. Contact & Questions

For questions about this model:
- Check MLflow UI at `http://localhost:5001`
- Review training logs: `mlruns/{run_id}`
- Contact: Morchella Detection Project Team

---

## Appendix: Full Parameter Dump

```json
{json.dumps(params, indent=2)}
```

---

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**MLflow Run ID:** `{run_id}`
"""
    
    # Escribir archivo
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(qmd_content)
    
    print(f"✅ Model Card generado: {filepath}")
    return filepath


def generate_model_card_from_latest_run(dataset_path: str, model_type: str = None):
    """
    Genera un Model Card del último run completado
    
    Args:
        dataset_path: Ruta al dataset
        model_type: Tipo de modelo (opcional, se intenta detectar)
    
    Returns:
        str: Ruta del archivo generado
    """
    
    client = MlflowClient()
    
    # Obtener el último run del experimento
    experiment = mlflow.get_experiment_by_name("morchella_detection")
    if not experiment:
        raise ValueError("No se encontró el experimento 'morchella_detection'")
    
    runs = client.search_runs(
        experiment_ids=[experiment.experiment_id],
        order_by=["attributes.start_time DESC"],
        max_results=1
    )
    
    if not runs:
        raise ValueError("No hay runs completados en el experimento")
    
    run_id = runs[0].info.run_id
    print(f"🎯 Generando Model Card para run: {run_id}")
    
    return create_model_card_qmd(run_id, dataset_path)


if __name__ == "__main__":
    # Ejemplo de uso
    import sys
    
    if len(sys.argv) > 1:
        run_id = sys.argv[1]
        dataset_path = os.path.join(os.path.dirname(__file__), 'dataset')
        create_model_card_qmd(run_id, dataset_path)
    else:
        dataset_path = os.path.join(os.path.dirname(__file__), 'dataset')
        generate_model_card_from_latest_run(dataset_path)

#!/usr/bin/env python3
"""
Utilidades para compilar, listar y comparar Model Cards

Proporciona comandos para:
- Listar todos los Model Cards generados
- Compilar un Model Card a HTML
- Compilar todos los Model Cards
- Ver comparativa de modelos
"""

import os
import sys
import glob
import subprocess
from pathlib import Path
from datetime import datetime


def get_model_cards_dir():
    """Obtiene el directorio de Model Cards"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    return os.path.join(project_dir, 'model_cards')


def list_model_cards():
    """Lista todos los Model Cards generados"""
    model_cards_dir = get_model_cards_dir()
    
    if not os.path.exists(model_cards_dir):
        print("❌ No se encontró el directorio de Model Cards")
        return []
    
    qmd_files = sorted(glob.glob(os.path.join(model_cards_dir, 'model_card_*.qmd')))
    
    if not qmd_files:
        print("📭 No hay Model Cards generados aún")
        return []
    
    print(f"\n📊 Model Cards disponibles ({len(qmd_files)}):\n")
    
    for i, filepath in enumerate(qmd_files, 1):
        filename = os.path.basename(filepath)
        stat = os.stat(filepath)
        size = stat.st_size / 1024  # KB
        mtime = datetime.fromtimestamp(stat.st_mtime)
        
        print(f"{i}. {filename}")
        print(f"   📅 Fecha: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   📏 Tamaño: {size:.1f} KB")
        print()
    
    return qmd_files


def compile_model_card(qmd_file=None):
    """
    Compila un Model Card a HTML
    
    Args:
        qmd_file: Ruta del archivo .qmd (si es None, compila el más reciente)
    """
    
    if qmd_file is None:
        model_cards_dir = get_model_cards_dir()
        qmd_files = sorted(glob.glob(os.path.join(model_cards_dir, 'model_card_*.qmd')))
        
        if not qmd_files:
            print("❌ No hay Model Cards para compilar")
            return False
        
        qmd_file = qmd_files[-1]  # El más reciente
    
    if not os.path.exists(qmd_file):
        print(f"❌ Archivo no encontrado: {qmd_file}")
        return False
    
    print(f"🔨 Compilando {os.path.basename(qmd_file)}...")
    
    # Verificar que Quarto está instalado
    try:
        result = subprocess.run(
            ['quarto', 'render', qmd_file],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            html_file = qmd_file.replace('.qmd', '.html')
            print(f"✅ Compilación exitosa!")
            print(f"📄 HTML generado: {html_file}")
            print(f"🌐 Para abrir en navegador: open {html_file}")
            return True
        else:
            print(f"❌ Error en compilación:")
            print(result.stderr)
            return False
            
    except FileNotFoundError:
        print("❌ Quarto no está instalado")
        print("💡 Instala Quarto desde: https://quarto.org/docs/get-started/")
        return False


def compile_all_model_cards():
    """Compila todos los Model Cards a HTML"""
    model_cards_dir = get_model_cards_dir()
    qmd_files = sorted(glob.glob(os.path.join(model_cards_dir, 'model_card_*.qmd')))
    
    if not qmd_files:
        print("📭 No hay Model Cards para compilar")
        return
    
    print(f"🔨 Compilando {len(qmd_files)} Model Cards...\n")
    
    success_count = 0
    for i, qmd_file in enumerate(qmd_files, 1):
        print(f"[{i}/{len(qmd_files)}] {os.path.basename(qmd_file)}")
        if compile_model_card(qmd_file):
            success_count += 1
        print()
    
    print(f"✅ Compilación completada: {success_count}/{len(qmd_files)} exitosos")


def create_comparison_document():
    """
    Crea un documento de comparación de todos los modelos
    """
    model_cards_dir = get_model_cards_dir()
    qmd_files = sorted(glob.glob(os.path.join(model_cards_dir, 'model_card_*.qmd')))
    
    if len(qmd_files) < 2:
        print("⚠️ Se necesitan al menos 2 modelos para comparar")
        return False
    
    print(f"📊 Creando documento de comparación para {len(qmd_files)} modelos...")
    
    # Crear documento Quarto de comparación
    comparison_content = """---
title: "Comparativa de Modelos - Morchella Classifier"
author: "Morchella Detection Project"
date: """ + f'"{datetime.now().strftime("%Y-%m-%d")}"' + """
format:
  html:
    toc: true
    toc-depth: 2
    theme: cosmo
    css: model-card-style.css
---

## Resumen Ejecutivo

Este documento compara los modelos de clasificación de Morchella entrenados.

### Modelos Evaluados

"""
    
    # Extracto de los Model Cards
    model_info = []
    for qmd_file in qmd_files:
        filename = os.path.basename(qmd_file)
        # Intentar extraer información
        with open(qmd_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # Extraer títulos y métricas (simplificado)
            if "EfficientNetB0" in content:
                model_type = "EfficientNetB0"
            elif "MobileNetV2" in content:
                model_type = "MobileNetV2"
            else:
                model_type = "Unknown"
            
            model_info.append({
                'file': filename,
                'type': model_type,
                'path': qmd_file
            })
    
    for i, info in enumerate(model_info, 1):
        comparison_content += f"\n{i}. **{info['type']}** ({info['file']})"
    
    comparison_content += """

---

## Tabla Comparativa

| Métrica | """ + " | ".join([m['type'] for m in model_info]) + """ |
|---------|""" + "|".join(["---|"]*len(model_info)) + """
| Dataset Morchella | ? | ? |
| Dataset No-Morchella | ? | ? |
| Accuracy | ? | ? |
| Precision (Morchella) | ? | ? |
| Recall (Morchella) | ? | ? |
| F1-Score (Morchella) | ? | ? |
| Precision (No-Morchella) | ? | ? |
| Recall (No-Morchella) | ? | ? |

---

## Análisis Detallado

### Arquitectura

"""
    
    for info in model_info:
        comparison_content += f"\n#### {info['type']}\n"
        comparison_content += f"Ver detalles en: [{info['file']}]({info['file'].replace('.qmd', '.html')})\n"
    
    comparison_content += """

---

## Recomendaciones

- **Para velocidad:** MobileNetV2
- **Para precisión:** EfficientNetB0
- **Para equilibrio:** Depende de los resultados específicos

---

## Próximos Pasos

1. Revisar los Model Cards individuales para análisis detallado
2. Evaluar trade-offs entre precisión y velocidad
3. Decidir cuál modelo usar en producción
4. Configurar threshold de decisión según el caso de uso

---

**Generado:** """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    comparison_file = os.path.join(model_cards_dir, 'model_comparison.qmd')
    
    with open(comparison_file, 'w', encoding='utf-8') as f:
        f.write(comparison_content)
    
    print(f"✅ Documento de comparación creado: {comparison_file}")
    print(f"💡 Compílalo con: quarto render {comparison_file}")
    return True


def main():
    """Función principal con CLI"""
    
    if len(sys.argv) < 2:
        print("""
╔════════════════════════════════════════════════════════════╗
║    🍄 Utilidades de Model Cards - Morchella Detection    ║
╚════════════════════════════════════════════════════════════╝

Uso: python model_card_utils.py <comando> [opciones]

Comandos:

  list              Lista todos los Model Cards generados
  
  compile [archivo] Compila un Model Card a HTML
                    - Si no se especifica archivo, compila el más reciente
  
  compile-all       Compila todos los Model Cards a HTML
  
  compare           Crea un documento comparativo de modelos
  
  open [archivo]    Abre un Model Card en HTML (requiere navegador)

Ejemplos:

  python model_card_utils.py list
  python model_card_utils.py compile
  python model_card_utils.py compile-all
  python model_card_utils.py compare

        """)
        return
    
    command = sys.argv[1].lower()
    
    if command == 'list':
        list_model_cards()
    
    elif command == 'compile':
        if len(sys.argv) > 2:
            compile_model_card(sys.argv[2])
        else:
            compile_model_card()
    
    elif command == 'compile-all':
        compile_all_model_cards()
    
    elif command == 'compare':
        create_comparison_document()
    
    elif command == 'open':
        if len(sys.argv) > 2:
            html_file = sys.argv[2]
        else:
            model_cards_dir = get_model_cards_dir()
            html_files = sorted(glob.glob(os.path.join(model_cards_dir, 'model_card_*.html')))
            if not html_files:
                print("❌ No hay archivos HTML. Compila primero con: python model_card_utils.py compile-all")
                return
            html_file = html_files[-1]
        
        if os.path.exists(html_file):
            import webbrowser
            webbrowser.open('file://' + os.path.abspath(html_file))
            print(f"🌐 Abriendo {os.path.basename(html_file)}...")
        else:
            print(f"❌ Archivo no encontrado: {html_file}")
    
    else:
        print(f"❌ Comando desconocido: {command}")
        print("Usa 'python model_card_utils.py' sin argumentos para ver ayuda")


if __name__ == '__main__':
    main()

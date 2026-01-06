#!/usr/bin/env python3
"""
Script de ejemplo que demuestra la generación de Model Cards

Uso:
    python example_generate_model_card.py <run_id>
    
O sin argumentos para usar el último run:
    python example_generate_model_card.py
"""

import sys
import os

def main():
    # Agregar el directorio src al path
    src_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, src_dir)
    
    from model_card_generator import generate_model_card_from_latest_run
    
    dataset_path = os.path.join(src_dir, 'dataset')
    
    if len(sys.argv) > 1:
        run_id = sys.argv[1]
        print(f"📋 Generando Model Card para run: {run_id}")
        from model_card_generator import create_model_card_qmd
        model_card_path = create_model_card_qmd(run_id, dataset_path)
    else:
        print("📋 Generando Model Card del último run...")
        model_card_path = generate_model_card_from_latest_run(dataset_path)
    
    print("\n" + "="*60)
    print("✅ Model Card generado exitosamente!")
    print("="*60)
    print(f"\n📄 Archivo: {model_card_path}")
    print(f"\n🔨 Para compilar a HTML:")
    print(f"   quarto render {model_card_path}")
    print(f"\n📚 Documentación:")
    print(f"   Ver model_cards/README.md")
    print("="*60 + "\n")

if __name__ == '__main__':
    main()

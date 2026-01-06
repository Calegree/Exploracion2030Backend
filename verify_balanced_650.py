#!/usr/bin/env python3
"""
Script de prueba para el endpoint /download/balanced_650
Verifica la configuración antes de ejecutar la descarga completa
"""

import sys

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

def verify_configuration():
    """Verifica que la configuración del dataset sea correcta"""
    
    print("=" * 60)
    print("🔍 VERIFICACIÓN DE CONFIGURACIÓN - Dataset Balanceado 650")
    print("=" * 60)
    
    # Verificar totales
    total_morchella = sum(qty for _, qty in ESPECIES_BALANCED_650['morchella'])
    total_no_morchella = sum(qty for _, qty in ESPECIES_BALANCED_650['no_morchella'])
    
    print(f"\n📊 TOTALES:")
    print(f"   Morchella: {total_morchella} imágenes")
    print(f"   No-Morchella: {total_no_morchella} imágenes")
    print(f"   Total general: {total_morchella + total_no_morchella} imágenes")
    
    # Verificar Morchella
    print(f"\n🍄 MORCHELLA ({total_morchella} fotos):")
    for especie, qty in ESPECIES_BALANCED_650['morchella']:
        print(f"   • {especie}: {qty} fotos")
    
    # Verificar No-Morchella por grupos
    print(f"\n🚫 NO-MORCHELLA ({total_no_morchella} fotos):")
    
    # Definir grupos
    grupos = {
        'Ascomicetes': ['Gyromitra esculenta', 'Gyromitra antarctica', 'Helvella lacunosa', 
                        'Helvella crispa', 'Verpa bohemica'],
        'Agaricales': ['Amanita muscaria', 'Amanita phalloides', 'Agaricus campestris', 
                       'Agaricus bisporus'],
        'Boletus patagónicos': ['Boletus edulis', 'Suillus luteus', 'Lactarius deliciosus'],
        'Políporos': ['Trametes versicolor', 'Ganoderma lucidum', 'Fomes fomentarius'],
        'Gasteroides': ['Lycoperdon perlatum', 'Calvatia gigantea', 'Phallus impudicus']
    }
    
    # Crear diccionario de especies para búsqueda rápida
    especies_dict = {especie: qty for especie, qty in ESPECIES_BALANCED_650['no_morchella']}
    
    for grupo, especies in grupos.items():
        total_grupo = sum(especies_dict.get(esp, 0) for esp in especies)
        print(f"\n   {grupo} ({total_grupo} fotos):")
        for especie in especies:
            if especie in especies_dict:
                print(f"      • {especie}: {especies_dict[especie]} fotos")
    
    # Validaciones
    print(f"\n✅ VALIDACIONES:")
    
    validations = []
    
    if total_morchella == 650:
        validations.append(("Morchella total = 650", "✓"))
    else:
        validations.append((f"Morchella total = {total_morchella} (esperado: 650)", "✗"))
    
    if total_no_morchella == 650:
        validations.append(("No-Morchella total = 650", "✓"))
    else:
        validations.append((f"No-Morchella total = {total_no_morchella} (esperado: 650)", "✗"))
    
    if total_morchella + total_no_morchella == 1300:
        validations.append(("Total general = 1300", "✓"))
    else:
        validations.append((f"Total general = {total_morchella + total_no_morchella} (esperado: 1300)", "✗"))
    
    # Verificar distribución específica de Morchella
    morchella_dict = {especie: qty for especie, qty in ESPECIES_BALANCED_650['morchella']}
    expected = {
        'Morchella andinensis': 25,
        'Morchella aysenina': 6,
        'Morchella tridentina': 100,
        'Morchella esculenta': 100,
        'Morchella': 419
    }
    
    for especie, qty_esperada in expected.items():
        qty_actual = morchella_dict.get(especie, 0)
        if qty_actual == qty_esperada:
            validations.append((f"{especie} = {qty_esperada}", "✓"))
        else:
            validations.append((f"{especie} = {qty_actual} (esperado: {qty_esperada})", "✗"))
    
    # Mostrar validaciones
    for validation, status in validations:
        print(f"   {status} {validation}")
    
    # Resultado final
    all_passed = all(status == "✓" for _, status in validations)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ CONFIGURACIÓN CORRECTA - Listo para descargar")
        print("\nPara descargar el dataset, ejecuta:")
        print("  curl -X POST http://localhost:5000/download/balanced_650")
        print("\nO con docker-compose:")
        print("  docker-compose exec api curl -X POST http://localhost:5000/download/balanced_650")
    else:
        print("❌ CONFIGURACIÓN INCORRECTA - Revisar cantidades")
        return False
    
    print("=" * 60)
    return all_passed

if __name__ == "__main__":
    success = verify_configuration()
    sys.exit(0 if success else 1)

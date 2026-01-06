#!/bin/bash
# Script de instalación de Quarto para diferentes sistemas operativos

echo "🔧 Instalador de Quarto para Model Card Generation"
echo "=================================================="

# Detectar sistema operativo
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "📦 Detectado: Linux"
    
    # Detectar distribución
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO=$ID
    fi
    
    case $DISTRO in
        ubuntu|debian)
            echo "📥 Ubuntu/Debian detectado. Instalando Quarto..."
            sudo apt-get update
            sudo apt-get install -y quarto
            ;;
        fedora)
            echo "📥 Fedora detectado. Instalando Quarto..."
            sudo dnf install -y quarto
            ;;
        arch)
            echo "📥 Arch Linux detectado. Instalando Quarto..."
            sudo pacman -S quarto
            ;;
        *)
            echo "⚠️ Distribución no reconocida. Descargando instalador..."
            curl -fsSL https://quarto.org/docs/get-started/ | grep -o 'href="[^"]*linux[^"]*"' | head -1
            ;;
    esac

elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "📦 Detectado: macOS"
    
    # Verificar si Homebrew está instalado
    if ! command -v brew &> /dev/null; then
        echo "🍺 Instalando Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    
    echo "📥 Instalando Quarto con Homebrew..."
    brew install quarto

elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    echo "📦 Detectado: Windows"
    echo "🌐 Abre en tu navegador: https://quarto.org/docs/get-started/"
    echo "📥 Descarga e instala el ejecutable"

else
    echo "❓ Sistema operativo no reconocido"
    echo "🌐 Descarga Quarto desde: https://quarto.org/docs/get-started/"
fi

echo ""
echo "✅ Verificando instalación..."
sleep 1

if command -v quarto &> /dev/null; then
    QUARTO_VERSION=$(quarto --version)
    echo "✅ Quarto instalado correctamente: $QUARTO_VERSION"
    echo ""
    echo "🚀 Ahora puedes usar:"
    echo "   python src/model_card_utils.py compile-all"
else
    echo "❌ Quarto no se encuentra en el PATH"
    echo "💡 Intenta reiniciar tu terminal o añade Quarto a tu PATH"
fi

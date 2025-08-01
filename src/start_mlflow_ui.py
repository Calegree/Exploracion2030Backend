import subprocess
import os
import sys
import time
import webbrowser
from threading import Timer

def start_mlflow_ui():
    """
    Inicia el servidor MLflow UI
    """
    print("🚀 Iniciando MLflow UI...")
    print("=" * 50)
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists("mlflow.db"):
        print("⚠️ Base de datos mlflow.db no encontrada")
        print("   Ejecuta primero: python train_model.py")
        return False
    
    # Configurar el comando para iniciar MLflow UI
    cmd = [
        sys.executable, "-m", "mlflow", "ui",
        "--backend-store-uri", "sqlite:///mlflow.db",
        "--host", "0.0.0.0",
        "--port", "5000"
    ]
    
    print(f"📊 Comando: {' '.join(cmd)}")
    print("🌐 URL: http://localhost:5000")
    print("⏳ Iniciando servidor...")
    
    try:
        # Iniciar el servidor
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Esperar un momento para que el servidor se inicie
        time.sleep(3)
        
        # Verificar si el proceso sigue ejecutándose
        if process.poll() is None:
            print("✅ Servidor MLflow iniciado correctamente")
            print("🌐 Abriendo navegador en 5 segundos...")
            
            # Abrir navegador después de 5 segundos
            def open_browser():
                try:
                    webbrowser.open("http://localhost:5000")
                    print("✅ Navegador abierto")
                except Exception as e:
                    print(f"⚠️ No se pudo abrir el navegador: {e}")
                    print("   Abre manualmente: http://localhost:5000")
            
            Timer(5.0, open_browser).start()
            
            print("\n📝 Información del servidor:")
            print("   - URL: http://localhost:5000")
            print("   - Base de datos: mlflow.db")
            print("   - Para detener: Ctrl+C")
            
            try:
                # Mantener el proceso ejecutándose
                process.wait()
            except KeyboardInterrupt:
                print("\n🛑 Deteniendo servidor...")
                process.terminate()
                process.wait()
                print("✅ Servidor detenido")
            
            return True
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Error iniciando servidor:")
            print(f"   STDOUT: {stdout}")
            print(f"   STDERR: {stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_mlflow_installation():
    """
    Verifica que MLflow esté instalado
    """
    try:
        import mlflow
        print("✅ MLflow instalado correctamente")
        return True
    except ImportError:
        print("❌ MLflow no está instalado")
        print("   Instala con: pip install mlflow")
        return False

if __name__ == "__main__":
    print("🔍 Verificando instalación...")
    
    if check_mlflow_installation():
        start_mlflow_ui()
    else:
        print("❌ No se puede iniciar MLflow UI")
        sys.exit(1) 
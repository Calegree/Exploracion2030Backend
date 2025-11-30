import h5py, json, traceback
from tensorflow import keras
fp = '/app/src/model_uploads/model_morchella.h5'

print("TF / Keras versions:", keras.backend.backend(), keras.__version__)
try:
    import tensorflow as tf
    print("tensorflow.__version__:", tf.__version__)
except Exception:
    pass

try:
    with h5py.File(fp, 'r') as f:
        print("Top-level keys:", list(f.keys()))
        if 'model_config' in f.attrs:
            cfg = f.attrs['model_config']
            if isinstance(cfg, bytes): cfg = cfg.decode()
            print("model_config: (first 1000 chars)\n", cfg[:1000])
            try:
                j = json.loads(cfg)
                print("model_config type keys:", list(j.keys())[:20])
            except Exception as e:
                print("no se pudo parsear model_config:", e)
        else:
            print("No model_config en attrs")

    # Intentar cargar con keras (capturamos excepción completa)
    try:
        m = keras.models.load_model(fp, compile=False)
        print("Modelo cargado OK. Summary:")
        m.summary()
    except Exception:
        print("Error cargando con keras.load_model():")
        traceback.print_exc()
except FileNotFoundError:
    print("Archivo no encontrado:", fp)
except Exception:
    traceback.print_exc()
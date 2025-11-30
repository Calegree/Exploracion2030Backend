import h5py, json, traceback
fp = '/app/src/model_uploads/model_morchella.h5'
try:
    with h5py.File(fp, 'r') as f:
        print('Top-level keys:', list(f.keys()))
        if 'model_config' in f.attrs:
            print('model_config in attrs')
            print(type(f.attrs['model_config']))
        elif 'model_config' in f:
            print('model_config dataset present; length:', len(f['model_config']))
            data = f['model_config'][()]
            if isinstance(data, bytes):
                data = data.decode()
            try:
                cfg = json.loads(data)
                print('model_config keys:', list(cfg.keys()))
            except Exception as e:
                print('no se pudo parsear model_config:', e)
        else:
            print('No model_config encontrado -> probablemente es archivo de pesos (weights-only).')
except FileNotFoundError:
    print('Archivo no encontrado:', fp)
except Exception:
    traceback.print_exc()
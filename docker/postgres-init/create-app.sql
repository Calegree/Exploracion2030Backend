-- crear tablas de la app (idempotente)
CREATE TABLE IF NOT EXISTS uploaded_models (
  id SERIAL PRIMARY KEY,
  name TEXT,
  path TEXT,
  size BIGINT,
  uploaded_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS active_model (
  id SERIAL PRIMARY KEY,
  model_name TEXT,
  run_id TEXT,
  local_path TEXT,
  size BIGINT,
  uploaded_at TIMESTAMP DEFAULT now(),
  set_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS prediction_counts (
  id SERIAL PRIMARY KEY,
  morchella BIGINT NOT NULL DEFAULT 0,
  no_morchella BIGINT NOT NULL DEFAULT 0,
  last_updated TIMESTAMP
);
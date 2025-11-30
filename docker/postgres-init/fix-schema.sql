-- Añadir columnas esperadas por la app (idempotente)
ALTER TABLE uploaded_models ADD COLUMN IF NOT EXISTS name TEXT;
ALTER TABLE uploaded_models ADD COLUMN IF NOT EXISTS size BIGINT;
ALTER TABLE uploaded_models ADD COLUMN IF NOT EXISTS uploaded_at TIMESTAMP;

ALTER TABLE active_model ADD COLUMN IF NOT EXISTS model_name TEXT;
ALTER TABLE active_model ADD COLUMN IF NOT EXISTS size BIGINT;
ALTER TABLE active_model ADD COLUMN IF NOT EXISTS uploaded_at TIMESTAMP;
ALTER TABLE active_model ADD COLUMN IF NOT EXISTS set_at TIMESTAMP;

-- Si existe created_at, usarlo para uploaded_at cuando no haya valor
DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'active_model' AND column_name = 'created_at'
  ) THEN
    UPDATE active_model SET uploaded_at = created_at WHERE uploaded_at IS NULL;
  END IF;

  IF EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'uploaded_models' AND column_name = 'created_at'
  ) THEN
    UPDATE uploaded_models SET uploaded_at = created_at WHERE uploaded_at IS NULL;
  END IF;
END
$$;
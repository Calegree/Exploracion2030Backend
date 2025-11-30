-- create-mlflow.sql: crear role y otorgar permisos al esquema public de la BD morchellappdb
-- Se ejecuta durante la inicialización del volumen (solo la primera vez).

DO
$$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'mlflow') THEN
    CREATE ROLE mlflow LOGIN PASSWORD 'mlflowpass';
  END IF;
END
$$;

-- Estamos ejecutando el script conectado a la BD definida por POSTGRES_DB (morchellappdb),
-- por tanto las siguientes sentencias actúan sobre esa BD.
ALTER SCHEMA public OWNER TO mlflow;
GRANT USAGE, CREATE ON SCHEMA public TO mlflow;
GRANT CONNECT ON DATABASE morchellappdb TO mlflow;
GRANT ALL PRIVILEGES ON DATABASE morchellappdb TO mlflow;
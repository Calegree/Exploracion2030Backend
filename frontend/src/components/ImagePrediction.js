import React, { useState } from 'react';
import axios from 'axios';

export default function ImagePrediction() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/predict';

  const onFileChange = (e) => {
    setFile(e.target.files[0]);
    setResult(null);
    setError(null);
  };

  const onSubmit = async (e) => {
    e.preventDefault();
    if (!file) return setError('Selecciona una imagen');
    setLoading(true);
    setError(null);

    const form = new FormData();
    // El backend acepta la clave 'imagen' según prediction.py
    form.append('imagen', file, file.name);

    try {
      const resp = await axios.post(API_URL, form, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setResult(resp.data);
    } catch (err) {
      setError(err.response?.data || err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h3>Analizar imagen</h3>
      <form onSubmit={onSubmit}>
        <input type="file" accept="image/*" onChange={onFileChange} />
        <button type="submit" disabled={loading}>Analizar</button>
      </form>
      {loading && <p>Analizando...</p>}
      {error && <pre style={{color:'red'}}>{JSON.stringify(error, null, 2)}</pre>}
      {result && <pre>{JSON.stringify(result, null, 2)}</pre>}
    </div>
  );
}

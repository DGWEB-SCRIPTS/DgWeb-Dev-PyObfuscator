import React, { useState, useEffect, useRef } from 'react';
import './App.css';

function App() {
const [code, setCode] = useState('');
const [key, setKey] = useState('');
const [result, setResult] = useState('');
const [mode, setMode] = useState('encrypt');
const [showMenu, setShowMenu] = useState(false);
const [loading, setLoading] = useState(false);
const [statusMsg, setStatusMsg] = useState('');
const dropdownRef = useRef(null);

const API_URL = "https://dgweb-dev-pyobfuscator.onrender.com/";

useEffect(() => {
const timer = setTimeout(() => {
setKey('');
}, 100);
return () => clearTimeout(timer);
}, []);

useEffect(() => {
const clickOutside = (e) => {
if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
setShowMenu(false);
}
};
document.addEventListener('mousedown', clickOutside);
return () => document.removeEventListener('mousedown', clickOutside);
}, []);

// 🔥 retry automático (resolve Render dormindo)
const fetchWithRetry = async (url, options, retries = 2) => {
try {
const res = await fetch(url, options);
if (!res.ok) throw new Error("Erro na resposta");
return res;
} catch (err) {
if (retries > 0) {
setStatusMsg("Acordando servidor...");
await new Promise(r => setTimeout(r, 3000));
return fetchWithRetry(url, options, retries - 1);
}
throw err;
}
};

const handleProcess = async () => {
if (!code || !key || loading) return;

setLoading(true);
setResult('');
setStatusMsg("Conectando com servidor...");

try {
  const res = await fetchWithRetry(API_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      mode: mode === 'encrypt' ? 'encode' : 'decode',
      codigo: code,
      senha: key,
    }),
  });

  const data = await res.json();

  setResult(
    data.ofuscado ||
    data.desofuscado ||
    data.message ||
    'Sem resposta do servidor'
  );

  setStatusMsg("");

} catch (err) {
  console.error('Erro API:', err);
  setStatusMsg("Erro ao conectar com a API.");
}

setLoading(false);

};

return (
<div className="app-wrapper">
<div className="main-card">

    <header>
      <h1>DgWeb Dev <span>PyObfuscator</span></h1>
      <p className="subtitle">Segurança de elite para Python.</p>
    </header>

    {/* STATUS */}
    {statusMsg && (
      <div style={{ marginBottom: '10px', color: '#aaa' }}>
        {statusMsg}
      </div>
    )}

    {/* SENHA */}
    <div className="input-group">
      <label>Chave Mestre</label>
      <input
        type="password"
        className="input-field"
        placeholder="Sua chave..."
        value={key}
        onChange={(e) => setKey(e.target.value)}
      />
    </div>

    {/* CÓDIGO */}
    <div className="input-group">
      <label>{mode === 'encrypt' ? "Script Original" : "Script Ofuscado"}</label>
      <textarea
        className="textarea-field"
        placeholder="Cole seu código..."
        value={code}
        onChange={(e) => setCode(e.target.value)}
      />
    </div>

    {/* BOTÃO */}
    <div className="action-container" ref={dropdownRef}>
      <div className="split-btn-group">

        <button
          className={`btn-primary ${mode === 'decrypt' ? 'decrypt-mode' : ''}`}
          onClick={handleProcess}
          disabled={loading || !code || !key}
        >
          {loading
            ? "Processando..."
            : mode === 'encrypt'
              ? "Criptografar"
              : "Descriptografar"}
        </button>

        <button
          className="btn-toggle"
          onClick={() => setShowMenu(!showMenu)}
        >
          {showMenu ? "▲" : "▼"}
        </button>

      </div>

      {showMenu && (
        <div className="dropdown-menu">
          <div
            className="dropdown-item"
            onClick={() => { setMode('encrypt'); setShowMenu(false); }}
          >
            Criptografar
          </div>

          <div
            className="dropdown-item"
            onClick={() => { setMode('decrypt'); setShowMenu(false); }}
          >
            Descriptografar
          </div>
        </div>
      )}
    </div>

    {/* RESULTADO */}
    {result && (
      <div className="result-section">
        <div className="result-header">
          <span>Resultado</span>

          <button
            className="copy-link"
            onClick={() => {
              navigator.clipboard.writeText(result);
              alert("Copiado!");
            }}
          >
            COPIAR
          </button>
        </div>

        <div className="output-box">
          {result}
        </div>
      </div>
    )}

    <footer>
      <p>© 2026 DgWeb Dev</p>
    </footer>

  </div>
</div>

);
}

export default App;

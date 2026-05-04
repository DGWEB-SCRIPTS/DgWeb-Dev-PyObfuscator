import React, { useState, useEffect, useRef } from 'react';
import './App.css';

function App() {
  const [code, setCode] = useState('');
  const [key, setKey] = useState('');
  const [result, setResult] = useState('');
  const [mode, setMode] = useState('encrypt');
  const [showMenu, setShowMenu] = useState(false);
  const [loading, setLoading] = useState(false);
  const dropdownRef = useRef(null);

  // limpa chave ao iniciar
  useEffect(() => {
    const timer = setTimeout(() => {
      setKey('');
    }, 100);
    return () => clearTimeout(timer);
  }, []);

  // fecha dropdown ao clicar fora
  useEffect(() => {
    const clickOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setShowMenu(false);
      }
    };
    document.addEventListener('mousedown', clickOutside);
    return () => document.removeEventListener('mousedown', clickOutside);
  }, []);

  const handleProcess = async () => {
    if (!code || !key || loading) return;

    setLoading(true);
    setResult('');

    try {
      // 🔥 UM ÚNICO ENDPOINT (serverless Vercel)
      const endpoint = '/api/vm';

      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          mode: mode === 'encrypt' ? 'encode' : 'decode',
          codigo: code,
          senha: key,
        }),
      });

      const data = await res.json();

      // 🔥 resposta robusta
      setResult(
        data.ofuscado ||
        data.desofuscado ||
        data.message ||
        'Sem resposta do servidor'
      );

    } catch (err) {
      console.error('Erro API:', err);
      alert('Erro na conexão com a API.');
    }

    setLoading(false);
  };

  return (
    <div className="app-wrapper">
      <div className="main-card">

        <header>
          <svg className="py-icon" viewBox="0 0 448 512" fill="currentColor">
            <path d="M439.8 200.5c-7.7-30.9-22.3-54.2-53.4-54.2h-40.1v47.4c0 36.8-31.2 67.8-67.8 67.8H172.7c-29.2 0-53.4 25-53.4 54.3v101.8c0 29 25.2 46 53.4 54.3 33.8 9.9 66.3 11.7 106.8 0 26.9-7.8 53.4-23.5 53.4-54.3v-40.7H226.2v-13.6h160.2c31.1 0 42.6-21.7 53.4-54.2 11.2-33.5 10.7-65.7 0-108.6z"/>
          </svg>
          <h1>DgWeb Dev <span>PyObfuscator</span></h1>
          <p className="subtitle">Segurança de elite para desenvolvedores Python.</p>
        </header>

        {/* SENHA */}
        <div className="input-group">
          <label>Chave Mestre</label>
          <input
            type="password"
            className="input-field"
            placeholder="Sua chave de criptografia..."
            value={key}
            autoComplete="new-password"
            name="pwd_secure"
            onChange={(e) => setKey(e.target.value)}
          />
        </div>

        {/* CÓDIGO */}
        <div className="input-group">
          <label>{mode === 'encrypt' ? "Script Original" : "Script Ofuscado"}</label>
          <textarea
            className="textarea-field"
            placeholder="Cole seu código aqui..."
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
                  ? "Criptografar Agora"
                  : "Descriptografar Agora"}
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
                Modo Criptografar
              </div>

              <div
                className="dropdown-item"
                onClick={() => { setMode('decrypt'); setShowMenu(false); }}
              >
                Modo Descriptografar
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
                COPIAR CÓDIGO
              </button>
            </div>

            <div className="output-box">
              {result}
            </div>
          </div>
        )}

        <footer>
          <p>
            © 2026 DgWeb Dev PyObfuscator |
            <a href="https://github.com/DGWEB-SCRIPTS" target="_blank" rel="noreferrer">
              GitHub Oficial
            </a>
          </p>
        </footer>

      </div>
    </div>
  );
}

export default App;

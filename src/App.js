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

  // Truque para limpar o campo após o carregamento inicial (Garante que comece vazio)
  useEffect(() => {
    const timer = setTimeout(() => {
      setKey('');
    }, 100);
    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    const clickOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) setShowMenu(false);
    };
    document.addEventListener('mousedown', clickOutside);
    return () => document.removeEventListener('mousedown', clickOutside);
  }, []);

  const handleProcess = async () => {
    if (!code || !key) return;
    setLoading(true);
    try {
      const endpoint = mode === 'encrypt' ? '/api/obfuscate' : '/api/decrypt';
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ codigo: code, senha: key }),
      });
      const data = await res.json();
      setResult(data.ofuscado || data.original || '');
    } catch (err) {
      alert("Conexão interrompida.");
    }
    setLoading(false);
  };

  return (
    <div className="app-wrapper">
      <div className="main-card">
        <header>
          <svg className="py-icon" viewBox="0 0 448 512" fill="currentColor">
            <path d="M439.8 200.5c-7.7-30.9-22.3-54.2-53.4-54.2h-40.1v47.4c0 36.8-31.2 67.8-67.8 67.8H172.7c-29.2 0-53.4 25-53.4 54.3v101.8c0 29 25.2 46 53.4 54.3 33.8 9.9 66.3 11.7 106.8 0 26.9-7.8 53.4-23.5 53.4-54.3v-40.7H226.2v-13.6h160.2c31.1 0 42.6-21.7 53.4-54.2 11.2-33.5 10.7-65.7 0-108.6zM286.2 404c11.1 0 20.1 9.1 20.1 20.3 0 11.3-9 20.4-20.1 20.4-11 0-20.1-9.1-20.1-20.4 .1-11.2 9.1-20.3 20.1-20.3zM167.8 248.1h106.8c29.7 0 53.4-24.5 53.4-54.3V91.9c0-29-24.4-50.7-53.4-55.6-35.8-5.9-74.7-5.6-106.8 0-45.2 7.8-53.4 24.7-53.4 55.6v40.7h106.9v13.6H53.4c-31.3 0-41.1 23.3-53.4 54.2-11.2 28.5-10.8 59 0 108.6 7.6 30.7 19.5 54.2 53.4 54.2h40.1v-106.9c0-30.6 25-53.2 54.3-53.2zM146.9 108.8c0-11.1 9-20.1 20.1-20.1s20.1 9 20.1 20.1c0 11.1-9 20.1-20.1 20.1s-20.1-9-20.1-20.1z"/>
          </svg>
          <h1>DgWeb Dev <span>PyObfuscator</span></h1>
          <p className="subtitle">Segurança de elite para desenvolvedores Python.</p>
        </header>

        {/* INPUT DE SENHA COM BLOQUEIO DE AUTOFILL */}
        <div className="input-group">
          <label>Chave Mestre</label>
          <input 
            type="password" 
            className="input-field"
            placeholder="Sua chave de criptografia..." 
            value={key}
            autoComplete="new-password"
            name={`pwd_${Math.random()}`} // Nome aleatório para confundir o navegador
            onChange={(e) => setKey(e.target.value)}
          />
        </div>

        <div className="input-group">
          <label>{mode === 'encrypt' ? "Script Original" : "Script Ofuscado"}</label>
          <textarea 
            className="textarea-field"
            placeholder="Cole seu código aqui..."
            value={code}
            onChange={(e) => setCode(e.target.value)}
          />
        </div>

        <div className="action-container" ref={dropdownRef}>
          <div className="split-btn-group">
            <button className={`btn-primary ${mode === 'decrypt' ? 'decrypt-mode' : ''}`} onClick={handleProcess}>
              {loading ? "Processando..." : mode === 'encrypt' ? "Criptografar Agora" : "Descriptografar Agora"}
            </button>
            <button className="btn-toggle" onClick={() => setShowMenu(!showMenu)}>
              {showMenu ? "▲" : "▼"}
            </button>
          </div>

          {showMenu && (
            <div className="dropdown-menu">
              <div className="dropdown-item" onClick={() => {setMode('encrypt'); setShowMenu(false)}}>Modo Criptografar</div>
              <div className="dropdown-item" onClick={() => {setMode('decrypt'); setShowMenu(false)}}>Modo Descriptografar</div>
            </div>
          )}
        </div>

        {result && (
          <div className="result-section">
            <div className="result-header">
              <span>Resultado</span>
              <button className="copy-link" onClick={() => {navigator.clipboard.writeText(result); alert("Copiado!")}}>COPIAR CÓDIGO</button>
            </div>
            <div className="output-box">{result}</div>
          </div>
        )}

        <footer>
          <p>© 2026 DgWeb Dev PyObfuscator | <a href="https://github.com/DGWEB-SCRIPTS" target="_blank" rel="noreferrer">GitHub Oficial</a></p>
        </footer>
      </div>
    </div>
  );
}

export default App;
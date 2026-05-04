# ---------------------------------------------------------
# PROJECT: DgWeb Dev PyObfuscator (v4.0 - Maze Engine)
# AUTHOR: DgWeb Dev
# GITHUB: https://github.com/DGWEB-SCRIPTS
# ---------------------------------------------------------

from http.server import BaseHTTPRequestHandler
import json
import base64
import random
import string
import zlib

def random_id(length=12):
    """Gera nomes de variáveis que parecem hashes para confundir a leitura."""
    return 'dg_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = json.loads(self.rfile.read(content_length).decode())
        
        codigo_original = body.get("codigo", "")
        
        # MODO LABIRINTO (Maze Engine)
        try:
            # 1. Preparação: Compressão e Encoding Base64
            # Isso mata a análise estática imediata.
            payload_comprimido = base64.b85encode(zlib.compress(codigo_original.encode())).decode()
            
            # 2. Geração de Identificadores Aleatórios (Obscuridade)
            var_data = random_id()    # Armazena o código comprimido
            var_exec = random_id()    # Nome da função de execução
            var_logic = random_id()   # Variável de controle inútil
            var_junk = random_id()    # Função de código morto
            
            # 3. Injeção de Código Morto e Lógica Inútil (Opaque Predicates)
            # Criamos verificações que sempre são verdadeiras, mas parecem complexas.
            junk_math = [
                f"sum(int(x) for x in str({random.randint(1000, 9999)})) > 0",
                f"(lambda x: x*x)({random.randint(1,10)}) >= 0",
                f"'{random_id(5)}' != '{random_id(6)}'"
            ]

            # 4. Reconstrução Dinâmica do Stub (O Labirinto)
            maze_stub = f"""# ██████╗  ██████╗ ██╗    ██╗███████╗██████╗ 
# ██╔══██╗██╔════╝ ██║    ██║██╔════╝██╔══██╗
# ██║  ██║██║  ███╗██║ █╗ ██║█████╗  ██████╔╝
# ██║  ██║██║   ██║██║███╗██║██╔══╝  ██╔══██╗
# ██████╔╝╚██████╔╝╚███╔███╔╝███████╗██████╔╝
# ╚═════╝  ╚═════╝  ╚══╝╚══╝ ╚══════╝╚═════╝ 
# DgWeb Dev PyObfuscator | Functional Maze Mode

import base64 as _dg_b
import zlib as _dg_z

def {var_junk}(*args):
    # Código morto para confundir depuradores
    _l = list(args)
    return _l[::-1] if len(_l) > 10 else _l

{var_logic} = {random.randint(100, 500)}

def {var_exec}():
    # Opaque Predicate: Verificação que sempre passa mas polui o fluxo
    if {random.choice(junk_math)}:
        {var_data} = "{payload_comprimido}"
        try:
            # Reconstrução em Runtime
            _p = _dg_z.decompress(_dg_b.b85decode({var_data}))
            exec(_p, globals())
        except Exception as _e:
            pass
    else:
        # Caminho falso (Dead Code Path)
        print("CRITICAL_ERR: " + str({var_logic}))

if __name__ == "__main__":
    {var_junk}({var_logic}, {random.randint(1,100)})
    {var_exec}()
"""
            resultado = maze_stub

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"ofuscado": resultado}).encode())

        except Exception as e:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": f"Maze Engine Failure: {str(e)}"}).encode())
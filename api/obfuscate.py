from http.server import BaseHTTPRequestHandler
import json, base64, random, string, zlib, re, hashlib, time

# --- CONFIGURAÇÕES DE IDENTIDADE ---
ENGINE_NAME = "DgWeb Dev Engine"
BANNER = f"""# ██████╗  ██████╗ ██╗    ██╗███████╗██████╗ 
# ██╔══██╗██╔════╝ ██║    ██║██╔════╝██╔══██╗
# ██║  ██║██║  ███╗██║ █╗ ██║█████╗  ██████╔╝
# ██║  ██║██║   ██║██║███╗██║██╔══╝  ██╔══██╗
# ██████╔╝╚██████╔╝╚███╔███╔╝███████╗██████╔╝
# ╚═════╝  ╚═════╝  ╚══╝╚══╝ ╚══════╝╚═════╝ 
# {ENGINE_NAME} | Progressive Labyrinth v6.0"""

ERR_AUTH = f"Erro: Senha incorreta. Acesso negado pela {ENGINE_NAME}."

class handler(BaseHTTPRequestHandler):
    def _log(self, msg):
        """Simula log de progresso no backend."""
        print(f"[{ENGINE_NAME}] {msg}")
        time.sleep(0.1) # Delay leve para estabilidade na geração

    def dg_rand_id(self, n=12):
        return 'dg_' + "".join(random.choices(string.ascii_lowercase + string.digits, k=n))

    def generate_junk_chunk(self, lines=50):
        """Gera um bloco de código inútil de forma controlada."""
        chunk = []
        for _ in range(lines):
            var_name = self.dg_rand_id(10)
            chunk.append(f"{var_name} = lambda x: x[::-1] if isinstance(x, str) else x * {random.randint(1,5)}")
        return "\n".join(chunk)

    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(content_length).decode())
            code_in = body.get("codigo", "")
            pass_in = body.get("senha", "")
            
            # Hash persistente para esteganografia
            secret_hash = hashlib.sha256(pass_in.encode()).hexdigest()[:24]

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            # --- MODO DESCRIPTOGRAFAR (RECONSTRUÇÃO SEGURA) ---
            if "decrypt" in self.path:
                self._log("Iniciando reversão...")
                fragments = re.findall(r'dg_[a-z0-9]{12}\s*=\s*["\']([A-Za-z0-9!#$%&()*+,-./:;<=>?@^_`{|}~]{5,})["\']', code_in)
                m_hash = re.search(r'dg_[a-z0-9]{16}\s*=\s*["\']([a-f0-9]{24})["\']', code_in)
                
                if fragments and m_hash:
                    if m_hash.group(1) == secret_hash:
                        self._log("Senha validada. Reconstruindo...")
                        full_payload = "".join([f for f in fragments if len(f) > 20])
                        res = zlib.decompress(base64.b85decode(full_payload)).decode()
                    else:
                        res = ERR_AUTH
                else:
                    res = "# Erro: Assinatura DgWeb nao localizada no labirinto."
                
                self.wfile.write(json.dumps({"ofuscado": res}).encode())
                return

            # --- MODO OFUSCAR (GERAÇÃO PROGRESSIVA POR CHUNKS) ---
            self._log("Gerando base...")
            full_output = [BANNER, "import base64, zlib, sys, hashlib"]
            
            self._log("Aplicando camadas de encoding...")
            payload = base64.b85encode(zlib.compress(code_in.encode())).decode()
            
            # Fragmentação do payload em 4 partes para maior complexidade
            chunk_size = len(payload) // 4
            parts = [payload[i:i+chunk_size] for i in range(0, len(payload), chunk_size)]
            v_parts = [self.dg_rand_id() for _ in range(len(parts))]
            
            self._log("Inserindo junk code de volume...")
            full_output.append(self.generate_junk_chunk(60))
            
            self._log("Escondendo fragmentos e honeypots...")
            # Embaralha a ordem de definição das partes e do hash
            defs = [f'{v_parts[i]} = "{parts[i]}"' for i in range(len(parts))]
            v_pass_var = self.dg_rand_id(16)
            defs.append(f'{v_pass_var} = "{secret_hash}"')
            defs.append(f'RSA_KEY_MOCK = "{self.dg_rand_id(32)}"')
            random.shuffle(defs)
            full_output.extend(defs)

            self._log("Construindo lógica de execução indireta...")
            v_builder = self.dg_rand_id()
            v_main = self.dg_rand_id()
            
            # Camada de reconstrução em runtime
            logic_chunk = f"""
def {v_builder}(*a):
    return zlib.decompress(base64.b85decode("".join(a)))

def {v_main}():
    try:
        if (lambda x: x**2)(5) > 0:
            _raw = {v_builder}({", ".join(v_parts)})
            # Execução via getattr para ocultar 'exec'
            getattr(sys.modules['__main__'], '__builtins__')['exec'](_raw, globals())
    except: pass
"""
            full_output.append(logic_chunk)
            full_output.append(self.generate_junk_chunk(40))

            self._log("Finalizando e estabilizando código...")
            full_output.append(f'if __name__ == "__main__": {v_main}()')
            full_output.append(self.generate_junk_chunk(80))

            # Concatenação final controlada
            final_code = "\n".join(full_output)
            
            self.wfile.write(json.dumps({"ofuscado": final_code}).encode())
            self._log("Sucesso: Maze Engine concluída.")

        except Exception as e:
            self.send_response(200)
            self.wfile.write(json.dumps({"error": f"Erro na geração progressiva: {str(e)}"}).encode())

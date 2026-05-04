from http.server import BaseHTTPRequestHandler
import json, base64, random, string, zlib, re, hashlib

# --- CONFIGURAÇÕES DE IDENTIDADE ---
ENGINE_NAME = "DgWeb Dev Engine"
BANNER = f"""# ██████╗  ██████╗ ██╗    ██╗███████╗██████╗ 
# ██╔══██╗██╔════╝ ██║    ██║██╔════╝██╔══██╗
# ██║  ██║██║  ███╗██║ █╗ ██║█████╗  ██████╔╝
# ██║  ██║██║   ██║██║███╗██║██╔══╝  ██╔══██╗
# ██████╔╝╚██████╔╝╚███╔███╔╝███████╗██████╔╝
# ╚═════╝  ╚═════╝  ╚══╝╚══╝ ╚══════╝╚═════╝ 
# {ENGINE_NAME} | Ultra Labyrinth v5.0"""

ERR_AUTH = f"Erro: Senha incorreta. Acesso negado pela {ENGINE_NAME}."

def dg_rand_id(n=12):
    return 'dg_' + "".join(random.choices(string.ascii_lowercase + string.digits, k=n))

def generate_junk_cluster(count=100):
    """Gera ruído estrutural para dificultar análise estática."""
    junk = []
    for _ in range(count):
        name = dg_rand_id(10)
        junk.append(f"{name} = lambda x: x[::-1] if isinstance(x, str) else x * {random.randint(1,5)}")
        junk.append(f"def {dg_rand_id(8)}(): return {random.randint(100, 999)}")
    return "\n".join(junk)

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(content_length).decode())
            code_in = body.get("codigo", "")
            pass_in = body.get("senha", "")
            
            # Hash para esteganografia no código gerado
            secret_hash = hashlib.sha256(pass_in.encode()).hexdigest()[:24]

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            # --- MODO DESCRIPTOGRAFAR (RECONSTRUÇÃO DE FRAGMENTOS) ---
            if "decrypt" in self.path:
                # Busca todos os fragmentos escondidos no código
                fragments = re.findall(r'dg_[a-z0-9]{12}\s*=\s*["\']([A-Za-z0-9!#$%&()*+,-./:;<=>?@^_`{|}~]{5,})["\']', code_in)
                m_hash = re.search(r'dg_[a-z0-9]{16}\s*=\s*["\']([a-f0-9]{24})["\']', code_in)
                
                if fragments and m_hash:
                    if m_hash.group(1) == secret_hash:
                        # O último fragmento longo geralmente é o payload, ou a soma deles
                        full_payload = "".join([f for f in fragments if len(f) > 15])
                        res = zlib.decompress(base64.b85decode(full_payload)).decode()
                    else:
                        res = ERR_AUTH
                else:
                    res = "# Erro: Fragmentos de seguranca nao localizados."
                
                self.wfile.write(json.dumps({"ofuscado": res}).encode())
                return

            # --- MODO OFUSCAR (FRAGMENTAÇÃO E EXECUÇÃO INDIRETA) ---
            payload = base64.b85encode(zlib.compress(code_in.encode())).decode()
            
            # Fragmentação do payload em 3 partes
            p_size = len(payload) // 3
            parts = [payload[:p_size], payload[p_size:p_size*2], payload[p_size*2:]]
            v_parts = [dg_rand_id() for _ in range(3)]
            
            # IDs de Execução
            v_main, v_loader, v_builder = dg_rand_id(), dg_rand_id(), dg_rand_id()
            v_pass_var = dg_rand_id(16)
            
            # Honeypots e Pistas Falsas
            honeypots = [
                f"def secure_validate(): return '{dg_rand_id(32)}'",
                f"{v_pass_var} = \"{secret_hash}\"", # Hash real camuflado
                f"GLOBAL_KEY = '{hashlib.md5(pass_in.encode()).hexdigest()}'"
            ]
            random.shuffle(honeypots)

            # Construção do Labyrinth Code
            labyrinth = f"""{BANNER}
import base64, zlib, sys

{generate_junk_cluster(80)}

{v_parts[0]} = "{parts[0]}"
{v_parts[1]} = "{parts[1]}"
{honeypots[0]}
{v_parts[2]} = "{parts[2]}"
{honeypots[1]}

def {v_builder}(*args):
    # Reconstrução não linear dos fragmentos
    _r = "".join(args)
    return zlib.decompress(base64.b85decode(_r))

{honeypots[2]}
{generate_junk_cluster(50)}

def {v_loader}(target):
    # Execução indireta via getattr para evitar detecção de 'exec'
    _e = getattr(sys.modules['__main__'], '__builtins__')['exec']
    _e(target, globals())

def {v_main}():
    # Máquina de estados simples para gatilho de execução
    _step = {random.randint(1, 100)}
    if (_step * 2) > _step:
        _final = {v_builder}({v_parts[0]}, {v_parts[1]}, {v_parts[2]})
        {v_loader}(_final)

{generate_junk_cluster(100)}

if __name__ == "__main__":
    {v_main}()

{generate_junk_cluster(200)}
"""
            self.wfile.write(json.dumps({"ofuscado": labyrinth}).encode())

        except Exception as e:
            self.send_response(200)
            self.wfile.write(json.dumps({"error": f"Falha no motor: {str(e)}"}).encode())

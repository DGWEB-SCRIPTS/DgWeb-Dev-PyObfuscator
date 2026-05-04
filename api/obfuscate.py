from http.server import BaseHTTPRequestHandler
import json
import base64
import random
import string
import zlib
import re
import hashlib

def random_id(length=12):
    return 'dg_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(content_length).decode())
            input_code = body.get("codigo", "")
            senha = body.get("senha", "")
            
            # Gera um hash da senha para verificação invisível
            pass_hash = hashlib.sha256(senha.encode()).hexdigest()[:16]
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            if "decrypt" in self.path:
                try:
                    # 1. Busca o Payload (Código)
                    match_code = re.search(r'["\']([A-Za-z0-9!#$%&()*+,-./:;<=>?@^_`{|}~]{20,})["\']', input_code)
                    # 2. Busca o Hash invisível escondido no junk code
                    match_hash = re.search(r'dg_[a-z0-9]{12}\s*=\s*["\']([a-f0-9]{16})["\']', input_code)
                    
                    if match_code and match_hash:
                        found_hash = match_hash.group(1)
                        if found_hash == pass_hash:
                            data = match_code.group(1)
                            res = zlib.decompress(base64.b85decode(data)).decode()
                        else:
                            res = "# Erro: Senha incorreta. Acesso negado pela Maze Engine."
                    else:
                        res = "# Erro: Assinatura de seguranca nao encontrada."
                except:
                    res = "# Erro: Falha critica na reversao."
                
                self.wfile.write(json.dumps({"ofuscado": res}).encode())
                return

            # OFUSCAÇÃO
            payload = base64.b85encode(zlib.compress(input_code.encode())).decode()
            v1, v2, v3, v4, v_sec = random_id(), random_id(), random_id(), random_id(), random_id()
            
            # O hash da senha fica camuflado como se fosse apenas mais uma variável de lixo
            junk_vars = [
                f"{random_id()} = \"{random_id(16)}\"",
                f"{v_sec} = \"{pass_hash}\"", 
                f"{random_id()} = {random.randint(1000, 9999)}"
            ]
            random.shuffle(junk_vars)

            maze_stub = f"""# ██████╗  ██████╗ ██╗    ██╗███████╗██████╗ 
# ██╔══██╗██╔════╝ ██║    ██║██╔════╝██╔══██╗
# ██║  ██║██║  ███╗██║ █╗ ██║█████╗  ██████╔╝
# ██║  ██║██║   ██║██║███╗██║██╔══╝  ██╔══██╗
# ██████╔╝╚██████╔╝╚███╔███╔╝███████╗██████╔╝
# ╚═════╝  ╚═════╝  ╚══╝╚══╝ ╚══════╝╚═════╝ 
# DgWeb Dev PyObfuscator | Functional Maze Mode

import base64 as _dg_b
import zlib as _dg_z

{junk_vars[0]}
def {v4}(*args):
    return list(args)[::-1] if len(args) > 10 else list(args)

{junk_vars[1]}
{v3} = {random.randint(100, 500)}
{junk_vars[2]}

def {v2}():
    if (lambda x: x*x)({random.randint(1,10)}) >= 0:
        {v1} = "{payload}"
        try: exec(_dg_z.decompress(_dg_b.b85decode({v1})), globals())
        except: pass

if __name__ == "__main__":
    {v2}()
"""
            self.wfile.write(json.dumps({"ofuscado": maze_stub}).encode())

        except Exception as e:
            self.send_response(200)
            self.wfile.write(json.dumps({"error": str(e)}).encode())

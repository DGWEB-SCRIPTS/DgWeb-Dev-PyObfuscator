from http.server import BaseHTTPRequestHandler
import json
import base64
import random
import string
import zlib
import re

def random_id(length=12):
    return 'dg_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(content_length).decode())
            input_code = body.get("codigo", "")
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            if "decrypt" in self.path:
                try:
                    match = re.search(r'["\']([A-Za-z0-9!#$%&()*+,-./:;<=>?@^_`{|}~]+)["\']', input_code)
                    if match:
                        data = match.group(1)
                        original = zlib.decompress(base64.b85decode(data)).decode()
                        res = original
                    else:
                        res = "# Erro: Padrao Maze nao encontrado."
                except:
                    res = "# Erro: Falha na reversao."
                
                self.wfile.write(json.dumps({"ofuscado": res}).encode())
                return

            payload = base64.b85encode(zlib.compress(input_code.encode())).decode()
            v1, v2, v3, v4 = random_id(), random_id(), random_id(), random_id()
            
            junk_math = [
                f"sum(int(x) for x in str({random.randint(1000, 9999)})) > 0",
                f"(lambda x: x*x)({random.randint(1,10)}) >= 0"
            ]

            maze_stub = f"""# ██████╗  ██████╗ ██╗    ██╗███████╗██████╗ 
# ██╔══██╗██╔════╝ ██║    ██║██╔════╝██╔══██╗
# ██║  ██║██║  ███╗██║ █╗ ██║█████╗  ██████╔╝
# ██║  ██║██║   ██║██║███╗██║██╔══╝  ██╔══██╗
# ██████╔╝╚██████╔╝╚███╔███╔╝███████╗██████╔╝
# ╚═════╝  ╚═════╝  ╚══╝╚══╝ ╚══════╝╚═════╝ 
# DgWeb Dev PyObfuscator | Functional Maze Mode

import base64 as _dg_b
import zlib as _dg_z

def {v4}(*args):
    _l = list(args)
    return _l[::-1] if len(_l) > 10 else _l

{v3} = {random.randint(100, 500)}

def {v2}():
    if {random.choice(junk_math)}:
        {v1} = "{payload}"
        try:
            exec(_dg_z.decompress(_dg_b.b85decode({v1})), globals())
        except:
            pass
    else:
        print("ERR: " + str({v3}))

if __name__ == "__main__":
    {v4}({v3}, {random.randint(1,100)})
    {v2}()
"""
            self.wfile.write(json.dumps({"ofuscado": maze_stub}).encode())

        except Exception as e:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

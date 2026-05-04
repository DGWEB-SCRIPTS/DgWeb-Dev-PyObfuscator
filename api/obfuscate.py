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
    return 'dg_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = json.loads(self.rfile.read(content_length).decode())
        
        codigo_original = body.get("codigo", "")
        
        try:
            payload_comprimido = base64.b85encode(zlib.compress(codigo_original.encode())).decode()
            
            v_1 = random_id()
            v_2 = random_id()
            v_3 = random_id()
            v_4 = random_id()
            
            junk_math = [
                f"sum(int(x) for x in str({random.randint(1000, 9999)})) > 0",
                f"(lambda x: x*x)({random.randint(1,10)}) >= 0",
                f"len('{random_id(5)}') != len('{random_id(10)}')"
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

def {v_4}(*args):
    _l = list(args)
    return _l[::-1] if len(_l) > 10 else _l

{v_3} = {random.randint(100, 500)}

def {v_2}():
    if {random.choice(junk_math)}:
        {v_1} = "{payload_comprimido}"
        try:
            exec(_dg_z.decompress(_dg_b.b85decode({v_1})), globals())
        except:
            pass
    else:
        print(f"ERR: {{ {v_3} }}")

if __name__ == "__main__":
    {v_4}({v_3}, {random.randint(1,100)})
    {v_2}()
"""
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({{"ofuscado": maze_stub}}).encode())

        except Exception as e:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(json.dumps({{"error": str(e)}}).encode())

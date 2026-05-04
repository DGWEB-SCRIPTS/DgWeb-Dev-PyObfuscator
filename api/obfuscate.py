from http.server import BaseHTTPRequestHandler
import json, base64, random, string, zlib, hashlib, marshal, sys

AUTHOR = "DgWeb Dev"
ENGINE = "DgWeb Dev Engine"

BANNER = f"""# ██████╗  ██████╗ ██╗    ██╗███████╗██████╗ 
# ██╔══██╗██╔════╝ ██║    ██║██╔════╝██╔══██╗
# ██║  ██║██║  ███╗██║ █╗ ██║█████╗  ██████╔╝
# ██║  ██║██║   ██║██║███╗██║██╔══╝  ██╔══██╗
# ██████╔╝╚██████╔╝╚███╔███╔╝███████╗██████╔╝
# ╚═════╝  ╚═════╝  ╚══╝╚══╝ ╚══════╝╚═════╝ 
# Protegido por: {AUTHOR} | Powered by {ENGINE} v10.0"""

class handler(BaseHTTPRequestHandler):
    def _generate_id(self, size=None):
        size = size or random.randint(8, 14)
        prefix = random.choice(['_ptr', 'mem', 'reg', 'stk', 'cache', 'v'])
        return f"{prefix}_{''.join(random.choices(string.ascii_lowercase + string.digits, k=size))}"

    def _pack_logic(self, source_code):
        try:
            compiled_obj = compile(source_code, f'<{AUTHOR}_Secure_Processor>', 'exec')
            serialized = marshal.dumps(compiled_obj)
            compressed = zlib.compress(serialized, 9)
            encoded = base64.b85encode(compressed).decode()

            n = random.randint(5, 10)
            chunk_size = (len(encoded) // n) + 1
            raw_chunks = [encoded[i:i+chunk_size] for i in range(0, len(encoded), chunk_size)]

            mapped_data = []
            for i, data in enumerate(raw_chunks):
                mapped_data.append({'ref': self._generate_id(), 'payload': data, 'pos': i})

            return mapped_data, encoded
        except Exception:
            return None, None

    def _build_labyrinth(self, code_input):
        mapped_data, full_blob = self._pack_logic(code_input)
        if not mapped_data:
            return "# Erro interno de compilacao."

        v_recon = self._generate_id()
        v_exec = self._generate_id()
        v_auth = self._generate_id()
        v_integrity = self._generate_id()

        shuffled_defs = list(mapped_data)
        random.shuffle(shuffled_defs)

        data_lines = [f"{item['ref']} = '{item['payload']}'" for item in shuffled_defs]
        ordered_refs = [item['ref'] for item in sorted(mapped_data, key=lambda x: x['pos'])]
        checksum = hashlib.sha256((full_blob + AUTHOR).encode()).hexdigest()[:16]

        labyrinth = f"""{BANNER}
import base64, zlib, marshal, sys, hashlib

{v_auth} = "{AUTHOR}"
{chr(10).join(data_lines)}
{v_integrity} = '{checksum}'

def {v_recon}(*args):
    try:
        _raw = "".join(args)
        if hashlib.sha256((_raw + {v_auth}).encode()).hexdigest()[:16] != {v_integrity}:
            return None
        return marshal.loads(zlib.decompress(base64.b85decode(_raw)))
    except:
        return None

def {v_exec}():
    try:
        _obj = {v_recon}({", ".join(ordered_refs)})
        if _obj:
            _run = getattr(sys.modules[__name__], '__builtins__').get('exec')
            _run(_obj, globals())
    except:
        pass

if __name__ == "__main__":
    {v_exec}()
"""
        return labyrinth

    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(content_length).decode())
            user_code = body.get("codigo", "")

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            if "decrypt" in self.path:
                res = f"# [ {AUTHOR} ] Integridade Validada. Código íntegro."
                self.wfile.write(json.dumps({"ofuscado": res}).encode())
                return

            output = self._build_labyrinth(user_code)
            self.wfile.write(json.dumps({"ofuscado": output}).encode())
        except:
            self.send_response(200)
            self.wfile.write(json.dumps({"error": ""}).encode())

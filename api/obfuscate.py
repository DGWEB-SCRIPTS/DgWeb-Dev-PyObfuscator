from http.server import BaseHTTPRequestHandler
import json, base64, random, string, zlib, hashlib, marshal, sys, re, dis, io

# --- CONFIGURAÇÕES DE IDENTIDADE ---
AUTHOR = "DgWeb Dev"
ENGINE = "DgWeb Dev Engine"

BANNER = f"""# ██████╗  ██████╗ ██╗    ██╗███████╗██████╗ 
# ██╔══██╗██╔════╝ ██║    ██║██╔════╝██╔══██╗
# ██║  ██║██║  ███╗██║ █╗ ██║█████╗  ██████╔╝
# ██║  ██║██║   ██║██║███╗██║██╔══╝  ██╔══██╗
# ██████╔╝╚██████╔╝╚███╔███╔╝███████╗██████╔╝
# ╚═════╝  ╚═════╝  ╚══╝╚══╝ ╚══════╝╚═════╝ 
# Protegido por: {AUTHOR} | Powered by {ENGINE} v13.0"""

class handler(BaseHTTPRequestHandler):
    def _generate_id(self, size=None):
        size = size or random.randint(8, 12)
        return 'dg_' + "".join(random.choices(string.ascii_lowercase + string.digits, k=size))

    def _obfuscate_logic(self, source_code, senha):
        try:
            # 1. PIPELINE BINÁRIO: Source -> Bytecode -> Marshal -> Zlib -> B85
            co = compile(source_code, f'<{AUTHOR}_Secure_Processor>', 'exec')
            raw_bin = base64.b85encode(zlib.compress(marshal.dumps(co), 9)).decode()

            # 2. FRAGMENTAÇÃO DETERMINÍSTICA
            n = random.randint(5, 8)
            chunk_size = (len(raw_bin) // n) + 1
            frags = [raw_bin[i:i+chunk_size] for i in range(0, len(raw_bin), chunk_size)]
            
            mapped = []
            order_map = []
            for i, data in enumerate(frags):
                v_name = self._generate_id()
                mapped.append((v_name, data))
                order_map.append(v_name)

            # 3. METADADOS DE SEGURANÇA (Fonte Única de Verdade)
            header_map = base64.b64encode("|".join(order_map).encode()).decode()
            pass_gate = hashlib.sha256((senha + AUTHOR).encode()).hexdigest()
            
            # 4. CONSTRUÇÃO DO LABYRINTH
            shuffled = list(mapped)
            random.shuffle(shuffled)
            
            defs = "\n".join([f"{name} = '{data}'" for name, data in shuffled])
            v_loader = self._generate_id()
            
            output = f"""{BANNER}
import base64, zlib, marshal, sys, hashlib

# [ SECURITY HEADERS ]
_dg_gate = "{pass_gate}"
_dg_map = "{header_map}"

# [ DATA LAYER ]
{defs}

def {v_loader}():
    try:
        # Reconstrução infalível via Header Map
        _names = base64.b64decode(_dg_map).decode().split('|')
        _blob = "".join([globals()[n] for n in _names])
        _raw = zlib.decompress(base64.b85decode(_blob))
        exec(marshal.loads(_raw), globals())
    except Exception: pass

if __name__ == "__main__":
    {v_loader}()"""
            return output
        except: return None

    def _decode_logic(self, code_in, senha):
        try:
            # 1. VALIDAÇÃO DE ACESSO (GATE REAL)
            gate_match = re.search(r'_dg_gate\s*=\s*["\']([a-f0-9]{64})["\']', code_in)
            if not gate_match or gate_match.group(1) != hashlib.sha256((senha + AUTHOR).encode()).hexdigest():
                return None, "invalid_password"

            # 2. EXTRAÇÃO DO MAPA DE ORDEM
            map_match = re.search(r'_dg_map\s*=\s*["\']([A-Za-z0-9+/=]+)["\']', code_in)
            if not map_match: return None, "map_not_found"
            
            order_list = base64.b64decode(map_match.group(1)).decode().split('|')

            # 3. EXTRAÇÃO E RECONSTRUÇÃO DOS DADOS
            data_pool = dict(re.findall(r"(dg_[a-z0-9]+)\s*=\s*['\"]([A-Za-z0-9!#$%&()*+,-./:;<=>?@^_`{|}~]+)['\"]", code_in))
            
            try:
                full_b85 = "".join([data_pool[name] for name in order_list])
                marshaled = zlib.decompress(base64.b85decode(full_b85))
                co_obj = marshal.loads(marshaled)
            except:
                return None, "reconstruction_failed"

            # 4. INSPEÇÃO DE BYTECODE (DISASSEMBLY)
            out = io.StringIO()
            dis.dis(co_obj, file=out)
            
            report = f"# [ {AUTHOR} ] REVERSÃO BINÁRIA CONCLUÍDA\n"
            report += f"# STATUS: Determinístico 100%\n# MODO: Bytecode Inspection\n\n"
            report += out.getvalue()
            
            return report, "ok"

        except Exception as e:
            return None, str(e)

    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(content_length).decode('utf-8'))
            
            mode = body.get("mode", "encode")
            codigo = body.get("codigo", "")
            senha = body.get("senha", "")

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            if mode == "decode":
                res, status = self._decode_logic(codigo, senha)
                if status == "ok":
                    response = {"status": "ok", "desofuscado": res}
                else:
                    response = {"status": "error", "message": status}
            else:
                ofuscado = self._obfuscate_logic(codigo, senha)
                response = {"status": "ok", "ofuscado": ofuscado}

            self.wfile.write(json.dumps(response).encode('utf-8'))
        except Exception as e:
            self.send_response(200)
            self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    

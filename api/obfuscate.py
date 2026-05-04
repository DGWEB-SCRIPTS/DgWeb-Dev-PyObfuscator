import json
import base64
import zlib
import hashlib
import hmac
import random
import string
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn

# ==========================================================
# CONFIGURAÇÃO DE PRODUÇÃO - CRÉDITOS E IDENTIDADE
# ==========================================================
AUTHOR = "DgWeb Dev"
ENGINE = "DgWeb Dev Engine"
VERSION = "v24.3 (Stable Production - Network Fix)"

BANNER = f"""# ██████╗  ██████╗ ██╗    ██╗███████╗██████╗ 
# ██╔══██╗██╔════╝ ██║    ██║██╔════╝██╔══██╗
# ██║  ██║██║  ███╗██║ █╗ ██║█████╗  ██████╔╝
# ██║  ██║██║   ██║██║███╗██║██╔══╝  ██╔══██╗
# ██████╔╝╚██████╔╝╚███╔███╔╝███████╗██████╔╝
# ╚═════╝  ╚═════╝  ╚══╝╚══╝ ╚══════╝╚═════╝ 
# Protegido por: {AUTHOR} | Powered by {ENGINE} {VERSION}"""

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Permite conexões simultâneas sem travar o loop principal."""
    allow_reuse_address = True

class ProductionVMHandler(BaseHTTPRequestHandler):
    
    def _set_cors_headers(self):
        """Headers universais para impedir que o Vercel/Navegador corte a conexão."""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Access-Control-Max-Age', '86400')
    
    def _get_sha256(self, data):
        if isinstance(data, str):
            data = data.encode()
        return hashlib.sha256(data).hexdigest()

    def _obfuscate_logic(self, source_code, password):
        try:
            compile(source_code, '<obfuscation_check>', 'exec')
            z_data = zlib.compress(source_code.encode('utf-8'), 9)
            key = hashlib.sha256((password + AUTHOR).encode()).digest()
            enc_data = bytes(z_data[i] ^ key[i % len(key)] for i in range(len(z_data)))
            signature = hmac.new(key, enc_data, hashlib.sha256).hexdigest()
            b85_str = base64.b85encode(enc_data).decode()

            chunk_size = 64 
            chunks = [b85_str[i:i+chunk_size] for i in range(0, len(b85_str), chunk_size)]
            total_chunks = len(chunks)

            vmp = []
            for idx, chunk in enumerate(chunks):
                vmp.append([10, idx, chunk, self._get_sha256(chunk)])

            vmp.append([20, total_chunks]) 
            vmp.append([50, signature])
            vmp.append([55])
            vmp.append([60])
            vmp.append([70])

            vm_raw = json.dumps(vmp).encode()
            vm_payload = "DGS|" + base64.b85encode(zlib.compress(vm_raw)).decode() + "|DGE"
            return self._generate_runner(vm_payload, password)
        except Exception as e:
            return f"# BUILD_ERROR: {str(e)}"

    def _generate_runner(self, payload, psw):
        v_run = "vm_launch_" + "".join(random.choices(string.ascii_lowercase, k=5))
        return f"""{BANNER}
import sys, zlib, base64, hashlib, hmac, json

def {v_run}(key_input):
    v_data = "{payload}"
    try:
        raw_vmp = v_data.split("DGS|")[1].split("|DGE")[0]
        vmp = json.loads(zlib.decompress(base64.b85decode(raw_vmp)).decode())
    except Exception: return sys.stderr.write("VM_CORRUPTION_DETECTED\\n")

    max_idx = -1
    for i in vmp:
        if i[0] == 10 and i[1] > max_idx: max_idx = i[1]
    mem = [None] * (max_idx + 1) if max_idx >= 0 else []
    
    stack = []
    derived_key = hashlib.sha256((key_input + "{AUTHOR}").encode()).digest()

    for instr in vmp:
        op = instr[0]
        try:
            if op == 10: 
                idx, val, v_hash = instr[1], instr[2], instr[3]
                if hashlib.sha256(val.encode()).hexdigest() != v_hash:
                    raise ValueError("CHUNK_INTEGRITY_FAIL")
                mem[idx] = val
            elif op == 20: 
                raw_str = "".join([m for m in mem if m is not None])
                if not raw_str: raise ValueError("ASSEMBLE_EMPTY")
                stack.append(base64.b85decode(raw_str))
            elif op == 50: 
                if not stack: raise ValueError("STACK_EMPTY_ON_VERIFY")
                if hmac.new(derived_key, stack[-1], hashlib.sha256).hexdigest() != instr[1]:
                    return sys.stderr.write("INVALID_ACCESS_KEY\\n")
            elif op == 55: 
                if not stack: raise ValueError("STACK_EMPTY_ON_XOR")
                d = stack.pop()
                stack.append(bytes(d[i] ^ derived_key[i % len(derived_key)] for i in range(len(d))))
            elif op == 60: 
                if not stack: raise ValueError("STACK_EMPTY_ON_ZLIB")
                stack.append(zlib.decompress(stack.pop()).decode('utf-8'))
            elif op == 70: 
                if not stack: raise ValueError("STACK_EMPTY_ON_EXEC")
                exec(stack.pop(), {{"__name__": "__main__", "__builtins__": __builtins__}})
        except Exception as e:
            return sys.stderr.write(f"FATAL_VM_ERROR: {{type(e).__name__}} (OP: {{op}})\\n")

if __name__ == "__main__":
    {v_run}("{psw}")
"""

    def _decode_logic(self, payload, password):
        try:
            if "DGS|" not in payload: return None, "FORMATO_INVALIDO"
            raw_vmp = payload.split("DGS|")[1].split("|DGE")[0]
            vmp = json.loads(zlib.decompress(base64.b85decode(raw_vmp)).decode())

            max_idx = -1
            for i in vmp:
                if i[0] == 10 and i[1] > max_idx: max_idx = i[1]
            mem = [None] * (max_idx + 1) if max_idx >= 0 else []
            
            stack = []
            derived_key = hashlib.sha256((password + AUTHOR).encode()).digest()

            for instr in vmp:
                op = instr[0]
                if op == 10: mem[instr[1]] = instr[2]
                elif op == 20: 
                    raw_str = "".join([m for m in mem if m is not None])
                    if raw_str: stack.append(base64.b85decode(raw_str))
                elif op == 50:
                    if not stack: return None, "STACK_UNDERFLOW_HMAC"
                    if hmac.new(derived_key, stack[-1], hashlib.sha256).hexdigest() != instr[1]:
                        return None, "SENHA_INCORRETA_OU_INTEGRIDADE_VIOLADA"
                elif op == 55:
                    if not stack: return None, "STACK_UNDERFLOW_XOR"
                    d = stack.pop()
                    stack.append(bytes(d[i] ^ derived_key[i % len(derived_key)] for i in range(len(d))))
                elif op == 60:
                    if not stack: return None, "STACK_UNDERFLOW_ZLIB"
                    stack.append(zlib.decompress(stack.pop()).decode('utf-8'))
                elif op == 70:
                    if not stack: return None, "STACK_UNDERFLOW_EXEC"
                    return stack.pop(), "ok"
            return None, "VM_HALTED"
        except Exception as e:
            return None, f"ERRO_DECODE: {str(e)}"

    def do_OPTIONS(self):
        """Rota crucial para o Vercel: responde à checagem de segurança (Preflight)."""
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()

    def do_GET(self):
        """Rota de Health Check: responde se o Vercel ou o navegador apenas tentar acessar a raiz."""
        self.send_response(200)
        self._set_cors_headers()
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"status": "online", "engine": ENGINE}).encode())

    def do_POST(self):
        """Rota principal de processamento."""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                raise ValueError("Payload vazio")
                
            raw_data = self.rfile.read(content_length).decode('utf-8')
            post_data = json.loads(raw_data)
            
            mode = post_data.get("mode", "encode")
            code = post_data.get("codigo", "")
            psw = post_data.get("senha", "")

            self.send_response(200)
            self._set_cors_headers()
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            if mode == "encode":
                res = self._obfuscate_logic(code, psw)
                response = {"status": "ok", "ofuscado": res}
            elif mode == "decode":
                res, status = self._decode_logic(code, psw)
                response = {"status": "ok", "desofuscado": res} if status == "ok" else {"status": "error", "message": status}
            else:
                response = {"status": "error", "message": "MODO_INVALIDO"}

            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            # Tratamento seguro caso o Vercel feche a conexão antes de enviarmos o erro
            try:
                if not self.wfile.closed:
                    self.send_response(500)
                    self._set_cors_headers()
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode())
            except:
                pass # Socket já foi fechado pelo cliente, ignorar com segurança

def main():
    port = 8080
    print(f"--- {ENGINE} {VERSION} ---")
    print(f"STATUS: ONLINE EM PORTA {port}")
    server = ThreadedHTTPServer(('0.0.0.0', port), ProductionVMHandler)
    server.serve_forever()

if __name__ == "__main__":
    main()

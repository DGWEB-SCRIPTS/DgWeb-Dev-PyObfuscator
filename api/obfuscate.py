from http.server import BaseHTTPRequestHandler
import json, base64, random, string, zlib, hashlib, hmac, sys

AUTHOR = "DgWeb Dev"
ENGINE = "DgWeb Dev Engine"

BANNER = f"""# ██████╗  ██████╗ ██╗    ██╗███████╗██████╗ 
# ██╔══██╗██╔════╝ ██║    ██║██╔════╝██╔══██╗
# ██║  ██║██║  ███╗██║ █╗ ██║█████╗  ██████╔╝
# ██║  ██║██║   ██║██║███╗██║██╔══╝  ██╔══██╗
# ██████╔╝╚██████╔╝╚███╔███╔╝███████╗██████╔╝
# ╚═════╝  ╚═════╝  ╚══╝╚══╝ ╚══════╝╚═════╝ 
# Protegido por: {AUTHOR} | Powered by {ENGINE} v23.0 (Bulletproof VM)"""

class handler(BaseHTTPRequestHandler):
    def _gen_id(self, size=12):
        return random.choice(string.ascii_letters) + "".join(random.choices(string.ascii_letters + string.digits, k=size))

    def _generate_realistic_honeypots(self):
        c1, c2, c3 = self._gen_id(), self._gen_id(), self._gen_id()
        return f"""
class {c1}:
    def __init__(self, buffer_size=4096):
        self._b = bytearray(buffer_size)
        self._p = 0
    def flush(self):
        self._b = bytearray(len(self._b))
        self._p = 0
    def write(self, d):
        if self._p + len(d) > len(self._b): raise OverflowError()
        self._b[self._p:self._p+len(d)] = d
        self._p += len(d)

def {c2}(p, chunk=256):
    a = 0
    for i in range(0, len(p), chunk): a ^= len(p[i:i+chunk])
    return a

class {c3}:
    @staticmethod
    def derive(s, it=1000):
        k = hashlib.sha256(s.encode()).digest()
        for _ in range(it): k = hashlib.sha256(k).digest()
        return k
"""

    def _obfuscate_logic(self, source_code, senha):
        try:
            try: compile(source_code, '<validation>', 'exec')
            except SyntaxError as e: return f"# Falha de Sintaxe no original: {str(e)}"

            z_data = zlib.compress(source_code.encode('utf-8'), 9)
            key = hashlib.sha256((senha + AUTHOR).encode()).digest()
            k_len = len(key)
            
            # XOR Consertado: Indexação modular impede truncamento e perda de dados
            enc_data = bytes(z_data[i] ^ key[i % k_len] for i in range(len(z_data)))
            sig = hmac.new(key, enc_data, hashlib.sha256).hexdigest()

            blob = base64.b85encode(enc_data).decode()
            n_frags = random.randint(15, 25)
            c_size = (len(blob) // n_frags) + 1
            chunks = [blob[i:i+c_size] for i in range(0, len(blob), c_size)]

            vmp = []
            for i, chunk in enumerate(chunks):
                if random.random() > 0.5:
                    vmp.append([30, len(vmp) + 3]) 
                    vmp.append([40, "dead_branch", random.randint(0, 255)])
                    vmp.append([40, "fake_opcode"])
                
                vmp.append([10, chunk]) 
                if i > 0:
                    vmp.append([20])

            vmp.append([50, sig])
            vmp.append([55])
            vmp.append([60])
            vmp.append([70])

            # Assinatura blindada e serialização do programa da VM
            vm_payload = "DGS|" + base64.b85encode(zlib.compress(json.dumps(vmp).encode('utf-8'))).decode() + "|DGE"
            v_run = self._gen_id()
            v_data = self._gen_id()

            final_code = f"""{BANNER}
import sys, zlib, base64, hashlib, hmac, json
{self._generate_realistic_honeypots()}
{v_data} = "{vm_payload}"

def {v_run}(_k_in):
    try:
        _vmp_str = {v_data}.split("DGS|")[1].split("|DGE")[0]
        _VMP = json.loads(zlib.decompress(base64.b85decode(_vmp_str)).decode('utf-8'))
    except:
        sys.stderr.write("VME0\\n"); return
    
    s = []
    p = 0
    l = len(_VMP)
    cy = 0
    mx = l * 10
    
    try:
        while p < l:
            cy += 1
            if cy > mx: break # Anti Infinite Loop
            
            i = _VMP[p]
            o = i[0]
            
            if o == 10: 
                s.append(base64.b85decode(i[1]))
            elif o == 20:
                if len(s) < 2: break # Stack Underflow Protection
                a, b = s.pop(), s.pop()
                s.append(b + a)
            elif o == 30:
                nxt = i[1]
                if 0 <= nxt < l: # Out of Bounds Protection
                    p = nxt
                    continue
                break
            elif o == 50:
                if not s: break
                _k = hashlib.sha256((_k_in + "{AUTHOR}").encode()).digest()
                if hmac.new(_k, s[-1], hashlib.sha256).hexdigest() != i[1]:
                    sys.stderr.write("VME1\\n"); return
            elif o == 55:
                if not s: break
                _k = hashlib.sha256((_k_in + "{AUTHOR}").encode()).digest()
                d = s.pop()
                kl = len(_k)
                s.append(bytes(d[j] ^ _k[j % kl] for j in range(len(d))))
            elif o == 60:
                if not s: break
                try: 
                    s.append(zlib.decompress(s.pop()).decode('utf-8'))
                except: 
                    break # Safe Zlib Fail
            elif o == 70:
                if not s: break
                c = s.pop()
                try:
                    ns = {{"__builtins__": __builtins__, "__name__": "__main__"}}
                    exec(c, ns)
                except Exception as e:
                    # Captura erros do código do usuário sem crachar a VM
                    sys.stderr.write(f"Runtime Exception: {{e}}\\n")
                break
            p += 1
    except Exception:
        sys.stderr.write("VME2\\n")

if __name__ == "__main__":
    {v_run}("{senha}")
"""
            return final_code
        except Exception as e:
            return f"# Engine Build Fault: {str(e)}"

    def _decode_logic(self, code_in, senha):
        try:
            # 1. PARSING ESTRUTURAL IMUTÁVEL
            if "DGS|" not in code_in or "|DGE" not in code_in:
                return None, "Estrutura VM Ausente ou Marcadores Removidos."
            
            try:
                _vmp_str = code_in.split("DGS|")[1].split("|DGE")[0]
                _VMP = json.loads(zlib.decompress(base64.b85decode(_vmp_str)).decode('utf-8'))
            except:
                return None, "Falha na leitura do Payload (Corrompido)."

            # 2. SIMULAÇÃO DA VM COM PROTEÇÕES ATIVAS
            s = []
            p = 0
            l = len(_VMP)
            cy = 0
            mx = l * 10
            
            while p < l:
                cy += 1
                if cy > mx: return None, "Halt: Possível Loop Infinito detectado."
                
                i = _VMP[p]
                o = i[0]
                
                if o == 10:
                    s.append(base64.b85decode(i[1]))
                elif o == 20:
                    if len(s) < 2: return None, "Halt: Stack Underflow."
                    a, b = s.pop(), s.pop()
                    s.append(b + a)
                elif o == 30:
                    nxt = i[1]
                    if 0 <= nxt < l:
                        p = nxt
                        continue
                    return None, "Halt: JUMP Fora dos Limites."
                elif o == 40:
                    pass 
                elif o == 50:
                    if not s: return None, "Halt: Stack Vazia no VERIFY."
                    _k = hashlib.sha256((senha + AUTHOR).encode()).digest()
                    if hmac.new(_k, s[-1], hashlib.sha256).hexdigest() != i[1]:
                        return None, "Acesso Negado: Senha Inválida ou Modificação Detectada."
                elif o == 55:
                    if not s: return None, "Halt: Stack Vazia no DECRYPT."
                    _k = hashlib.sha256((senha + AUTHOR).encode()).digest()
                    d = s.pop()
                    kl = len(_k)
                    s.append(bytes(d[j] ^ _k[j % kl] for j in range(len(d))))
                elif o == 60:
                    if not s: return None, "Halt: Stack Vazia no DECOMPRESS."
                    try:
                        s.append(zlib.decompress(s.pop()).decode('utf-8'))
                    except:
                        return None, "Halt: Falha Crítica de Descompressão."
                elif o == 70:
                    if not s: return None, "Halt: Stack Vazia no EXEC."
                    original_code = s.pop()
                    return f"# [ {AUTHOR} ] FULL SOURCE RECOVERY SUCCESS\\n\\n{original_code}", "ok"
                p += 1

            return None, "Halt: Execução finalizada sem instrução de EXEC."

        except Exception as e:
            return None, f"Falha Estrutural no Decoder: {str(e)}"

    def do_POST(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length).decode('utf-8'))
            mode, code, psw = body.get("mode", "encode"), body.get("codigo", ""), body.get("senha", "")

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            if mode == "decode":
                res, status = self._decode_logic(code, psw)
                resp = {"status": "ok", "desofuscado": res} if status == "ok" else {"status": "error", "message": status}
            else:
                resp = {"status": "ok", "ofuscado": self._obfuscate_logic(code, psw)}

            self.wfile.write(json.dumps(resp).encode('utf-8'))
        except:
            self.send_response(200)
            self.wfile.write(json.dumps({"status": "error", "message": "API Handler Failure"}).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

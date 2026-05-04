import json
import base64
import zlib
import hashlib
import hmac
import random
import string
import sys
import traceback

AUTHOR = "DgWeb Dev"
ENGINE = "DgWeb Dev Engine"
VERSION = "v24.10"

BANNER = f"""# ██████╗  ██████╗ ██╗    ██╗███████╗██████╗ 
# ██╔══██╗██╔════╝ ██║    ██║██╔════╝██╔══██╗
# ██║  ██║██║  ███╗██║ █╗ ██║█████╗  ██████╔╝
# ██║  ██║██║   ██║██║███╗██║██╔══╝  ██╔══██╗
# ██████╔╝╚██████╔╝╚███╔███╔╝███████╗██████╔╝
# ╚═════╝  ╚═════╝  ╚══╝╚══╝ ╚══════╝╚═════╝ 
# Protegido por: {AUTHOR} | Powered by {ENGINE} {VERSION}"""

def debug_info(error):
    return {
        "status": "error",
        "error_type": type(error).__name__,
        "message": str(error),
        "trace": traceback.format_exc()
    }

def _get_sha256(data):
    if isinstance(data, str):
        data = data.encode()
    return hashlib.sha256(data).hexdigest()

def _generate_runner(payload, psw):
    v_run = "vm_launch_" + "".join(random.choices(string.ascii_lowercase, k=5))
    return f"""{BANNER}
import sys, zlib, base64, hashlib, hmac, json

def {v_run}(key_input):
    v_data = "{payload}"
    try:
        raw_vmp = v_data.split("DGS|")[1].split("|DGE")[0]
        vmp = json.loads(zlib.decompress(base64.b64decode(raw_vmp)).decode('utf-8'))
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
                stack.append(base64.b64decode(raw_str))
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

def obfuscate_logic(source_code, password):
    compile(source_code, '<obfuscation_check>', 'exec')
    z_data = zlib.compress(source_code.encode('utf-8'), 9)
    key = hashlib.sha256((password + AUTHOR).encode()).digest()
    enc_data = bytes(z_data[i] ^ key[i % len(key)] for i in range(len(z_data)))
    signature = hmac.new(key, enc_data, hashlib.sha256).hexdigest()
    
    b64_str = base64.b64encode(enc_data).decode('utf-8')

    chunk_size = 64 
    chunks = [b64_str[i:i+chunk_size] for i in range(0, len(b64_str), chunk_size)]
    total_chunks = len(chunks)

    vmp = []
    for idx, chunk in enumerate(chunks):
        vmp.append([10, idx, chunk, _get_sha256(chunk)])

    vmp.append([20, total_chunks]) 
    vmp.append([50, signature])
    vmp.append([55])
    vmp.append([60])
    vmp.append([70])

    vm_raw = json.dumps(vmp).encode('utf-8')
    vm_payload = "DGS|" + base64.b64encode(zlib.compress(vm_raw)).decode('utf-8') + "|DGE"
    return _generate_runner(vm_payload, password)

def decode_logic(payload, password):
    if "DGS|" not in payload: return None, "FORMATO_INVALIDO"
    raw_vmp = payload.split("DGS|")[1].split("|DGE")[0]
    vmp = json.loads(zlib.decompress(base64.b64decode(raw_vmp)).decode('utf-8'))

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
            if raw_str: stack.append(base64.b64decode(raw_str))
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

def handler(request):
    try:
        body = {}

        try:
            body = request.get_json() or {}
        except:
            raw = getattr(request, "body", None)

            if raw is None and hasattr(request, "get_data"):
                raw = request.get_data()

            if isinstance(raw, bytes):
                raw = raw.decode("utf-8")

            if raw:
                body = json.loads(raw)
            else:
                body = {}

        mode = body.get("mode", "encode")

        if mode == "debug":
            return {
                "status": "ok",
                "message": "DEBUG ATIVO",
                "server": "online"
            }

        code = body.get("codigo", "")
        psw = body.get("senha", "")

        if mode == "encode":
            return {
                "status": "ok",
                "ofuscado": obfuscate_logic(code, psw)
            }

        if mode == "decode":
            res, status = decode_logic(code, psw)
            return (
                {"status": "ok", "desofuscado": res}
                if status == "ok"
                else {"status": "error", "message": status}
            )

        return {"status": "error", "message": "MODO_INVALIDO"}

    except Exception as e:
        return debug_info(e)

app = handler

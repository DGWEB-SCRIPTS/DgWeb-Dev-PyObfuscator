from flask import Flask, request, jsonify
import base64, random, string, zlib, re, hashlib, sys, os

app = Flask(__name__)

ENGINE_NAME = "DgWeb Dev Engine"
VERSION = "v6.0-VM-Core"

BANNER = f"""# ██████╗  ██████╗ ██╗    ██╗███████╗██████╗ 
# ██╔══██╗██╔════╝ ██║    ██║██╔════╝██╔══██╗
# ██║  ██║██║  ███╗██║ █╗ ██║█████╗  ██████╔╝
# ██║  ██║██║   ██║██║███╗██║██╔══╝  ██╔══██╗
# ██████╔╝╚██████╔╝╚███╔███╔╝███████╗██████╔╝
# ╚═════╝  ╚═════╝  ╚══╝╚══╝ ╚══════╝╚═════╝ 
# {ENGINE_NAME} | VM Labyrinth Mode"""

ERR_AUTH = f"Erro: Senha incorreta. Acesso negado pela {ENGINE_NAME}."


class DgWebEngineCore:
    @staticmethod
    def _g_id(n=12):
        return 'dg_' + "".join(random.choices(string.ascii_lowercase + string.digits, k=n))

    @classmethod
    def _n_gen(cls, lines=10):  # ↓ reduzido pra não travar
        return "\n".join([
            f"{cls._g_id(10)} = lambda x: x[::-1] if isinstance(x, str) else x * {random.randint(2,8)}"
            for _ in range(lines)
        ])

    @classmethod
    def encode(cls, c_in, p_in):
        s_hash = hashlib.sha256(p_in.encode()).hexdigest()[:24]
        p_load = base64.b85encode(zlib.compress(c_in.encode())).decode()
        sz = max(1, len(p_load) // 4)
        pts = [p_load[i:i+sz] for i in range(0, len(p_load), sz)]

        v_pts = [cls._g_id() for _ in range(len(pts))]
        v_ldr, v_ex, v_pw = cls._g_id(), cls._g_id(), cls._g_id(16)

        out = [BANNER, "import base64, zlib, sys, hashlib", cls._n_gen(5)]

        defs = [f'{v_pts[i]} = "{pts[i]}"' for i in range(len(pts))]
        defs.extend([f'{v_pw} = "{s_hash}"'])
        random.shuffle(defs)
        out.extend(defs)

        vm_logic = f"""
def {v_ldr}(*c):
    return zlib.decompress(base64.b85decode("".join(c)))

def {v_ex}():
    try:
        exec({v_ldr}({", ".join(v_pts)}), globals())
    except:
        pass

if __name__ == "__main__":
    {v_ex}()
"""
        out.append(vm_logic)
        out.append(cls._n_gen(10))
        return "\n".join(out)

    @classmethod
    def decode(cls, c_in, p_in):
        s_hash = hashlib.sha256(p_in.encode()).hexdigest()[:24]
        frags = re.findall(r'dg_[a-z0-9]{12}\s*=\s*["\']([^"\']+)["\']', c_in)
        m_hash = re.search(r'dg_[a-z0-9]{16}\s*=\s*["\']([a-f0-9]{24})["\']', c_in)

        if frags and m_hash:
            if m_hash.group(1) == s_hash:
                full_p = "".join(frags)
                return zlib.decompress(base64.b85decode(full_p)).decode(), "ok"
            return ERR_AUTH, "error"

        return "# Erro: Padrao nao identificado.", "error"


@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "status": "active",
        "engine": ENGINE_NAME,
        "version": VERSION
    })


@app.route('/api', methods=['POST'])
def api():
    try:
        data = request.get_json()
        mode = data.get("mode")
        code = data.get("codigo")
        psw = data.get("senha")

        if mode == "encode":
            return jsonify({
                "status": "ok",
                "resultado": DgWebEngineCore.encode(code, psw)
            })

        elif mode == "decode":
            res, stat = DgWebEngineCore.decode(code, psw)
            return jsonify({
                "status": stat,
                "resultado": res
            })

        return jsonify({"status": "error", "message": "modo inválido"})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


# 🔥 ESSENCIAL PRA RENDER
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

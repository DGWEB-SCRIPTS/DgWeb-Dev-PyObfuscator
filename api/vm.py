import json
import traceback

# ==========================================================
# MODO DE SEGURANÇA - TESTE DE ROTA VERCEL
# ==========================================================
def debug_info(error):
    return {
        "status": "error",
        "error_type": type(error).__name__,
        "message": str(error),
        "trace": traceback.format_exc()
    }

def handler(request):
    try:
        body = {}

        # Parse seguro de body (Vercel)
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

        mode = body.get("mode", "Nenhum modo recebido")

        # Resposta forçada para testar a comunicação com o React
        return {
            "status": "ok",
            "message": "DEBUG ATIVO",
            "ofuscado": f"🔥 CONEXÃO ESTABELECIDA COM SUCESSO! A Vercel recebeu o modo: {mode}. O frontend e o backend estão se falando perfeitamente."
        }

    except Exception as e:
        return debug_info(e)

app = handler

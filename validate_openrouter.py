"""Teste de uma chamada gratuita e de tool calling no OpenRouter.

Lê OPENROUTER_API_KEY do ambiente ou do .env local sem exibir a chave.
Consome uma requisição da cota gratuita. Não entra no ZIP.
"""

import json
import os
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def obter_chave():
    chave = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if chave:
        return chave
    caminho = Path(__file__).parent / ".env"
    if caminho.exists():
        for linha in caminho.read_text(encoding="utf-8").splitlines():
            nome, separador, valor = linha.partition("=")
            if separador and nome.strip() == "OPENROUTER_API_KEY":
                return valor.strip().strip(chr(34) + chr(39))
    return ""


chave = obter_chave()
if not chave:
    raise SystemExit("Preencha OPENROUTER_API_KEY no .env local para iniciar o teste.")

consulta_chave = Request(
    "https://openrouter.ai/api/v1/key",
    headers={"Authorization": "Bearer " + chave},
)
try:
    with urlopen(consulta_chave, timeout=20) as resposta:
        dados_chave = json.load(resposta).get("data", {})
except HTTPError as erro:
    raise SystemExit(f"Não foi possível validar a credencial: HTTP {erro.code}.") from None
except URLError as erro:
    raise SystemExit(f"Não foi possível consultar a credencial: {type(erro.reason).__name__}.") from None
print("Credencial reconhecida pelo OpenRouter; plano gratuito:", bool(dados_chave.get("is_free_tier")))

modelo = os.environ.get("OPENROUTER_MODEL", "openrouter/free")
corpo = {
    "model": modelo,
    "messages": [{"role": "user", "content": "Consulte o estado do ponto P07 em 2026-11-11 usando a ferramenta."}],
    "tools": [{
        "type": "function",
        "function": {
            "name": "consultar_status_ponto",
            "description": "Consulta o estado de um ponto em uma data.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ponto_id": {"type": "string"},
                    "data_consulta": {"type": "string"},
                },
                "required": ["ponto_id", "data_consulta"],
            },
        },
    }],
    "tool_choice": "required",
    "max_tokens": 120,
}
requisicao = Request(
    "https://openrouter.ai/api/v1/chat/completions",
    data=json.dumps(corpo).encode("utf-8"),
    headers={"Authorization": "Bearer " + chave, "Content-Type": "application/json"},
    method="POST",
)
try:
    with urlopen(requisicao, timeout=45) as resposta:
        dados = json.load(resposta)
except HTTPError as erro:
    try:
        resposta_erro = json.loads(erro.read().decode("utf-8"))
        origem = resposta_erro.get("error", {}).get("metadata", {}).get("limit_source")
        mensagem = resposta_erro.get("error", {}).get("message", "")
    except (ValueError, UnicodeError, AttributeError):
        origem = None
        mensagem = ""
    origem_segura = origem if origem in {"openrouter_free_tier_per_minute", "openrouter_free_tier_per_day", "upstream_provider_shared_pool"} else "não informada"
    mensagem_segura = mensagem.replace(chave, "[credencial removida]")[:180]
    raise SystemExit(f"OpenRouter respondeu HTTP {erro.code}; origem do limite: {origem_segura}; detalhe: {mensagem_segura}.") from None
except URLError as erro:
    raise SystemExit(f"Não foi possível conectar ao OpenRouter: {type(erro.reason).__name__}.") from None

chamadas = dados.get("choices", [{}])[0].get("message", {}).get("tool_calls", [])
if not chamadas or chamadas[0].get("function", {}).get("name") != "consultar_status_ponto":
    raise SystemExit("A conexão funcionou, mas o modelo não retornou a chamada de ferramenta esperada.")
print("Conexão e chamada de ferramenta validadas para", modelo, ". Nenhuma credencial foi exibida.")

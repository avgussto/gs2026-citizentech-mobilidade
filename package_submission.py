"""Valida os itens finais e cria o ZIP da FIAP; execute apenas após a medição real."""

import json
import math
import re
from statistics import mean
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


root = Path(__file__).parent
itens = [
    "1_Notebook_GS2026_2.ipynb",
    "2_base_documental",
    "3_avaliacao_ragas.json",
    "4_README.md",
    "5_certificacao.txt",
    "6_Chat_Log.txt",
    "7_demo_video_url.txt",
]
for item in itens:
    if not (root / item).exists():
        raise SystemExit(f"Item ausente: {item}")

avaliacao = json.loads((root / "3_avaliacao_ragas.json").read_text(encoding="utf-8"))
if avaliacao.get("status") != "medido" or len(avaliacao.get("perguntas", [])) != 8:
    raise SystemExit("Execute o RAGAS com as 8 referências e copie o JSON medido antes de empacotar.")
metricas = {"faithfulness", "response_relevancy", "context_precision", "context_recall"}
for i, pergunta in enumerate(avaliacao["perguntas"], 1):
    if not pergunta.get("ground_truth", "").strip() or set(pergunta.get("metricas", {})) != metricas:
        raise SystemExit(f"Avaliação incompleta na pergunta {i}.")
    if any(not math.isfinite(valor) or not 0 <= valor <= 1 for valor in pergunta["metricas"].values()):
        raise SystemExit(f"Escore inválido na pergunta {i}.")
if set(avaliacao.get("medias", {})) != metricas:
    raise SystemExit("Médias RAGAS ausentes ou incompletas.")
for nome in metricas:
    calculada = mean(pergunta["metricas"][nome] for pergunta in avaliacao["perguntas"])
    if not math.isfinite(avaliacao["medias"][nome]) or not math.isclose(avaliacao["medias"][nome], calculada, abs_tol=1e-9):
        raise SystemExit(f"Média RAGAS inconsistente: {nome}.")

readme = (root / "4_README.md").read_text(encoding="utf-8")
if "Pendente de captura" in readme or "Pendente de execução real" in readme or "Pendente de análise" in readme:
    raise SystemExit("Atualize a tabela de evidências e análise do README.")
evidencias = list((root / "2_base_documental" / "evidencias").glob("*.png"))
if not evidencias or not all(f"2_base_documental/evidencias/{p.name}" in readme for p in evidencias):
    raise SystemExit("Inclua prints reais em evidencias/ e links relativos no README.")

certificacao = (root / "5_certificacao.txt").read_text(encoding="utf-8")
if "PENDENTE" in certificacao or "____________________" in certificacao:
    raise SystemExit("Preencha a certificação e seus links.")
video = (root / "7_demo_video_url.txt").read_text(encoding="utf-8")
if not re.search(r"https://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)", video):
    raise SystemExit("Insira o link do vídeo não listado do YouTube.")

notebook_text = (root / "1_Notebook_GS2026_2.ipynb").read_text(encoding="utf-8")
if "REFERENCIAS_MANUAIS = [\n    ''," in notebook_text:
    raise SystemExit("As referências ainda não foram preenchidas no notebook.")
if re.search(r"(?:OPENAI_API_KEY|OPENROUTER_API_KEY|HF_TOKEN|OLLAMA_API_KEY)\s*=\s*['\"][^'\"]+['\"]", notebook_text):
    raise SystemExit("Possível chave escrita no notebook; remova antes de empacotar.")

destino = root / "GS2026_2_1CCR_AuroraDoVale.zip"
with ZipFile(destino, "w", ZIP_DEFLATED) as pacote:
    for item in itens:
        caminho = root / item
        if caminho.is_file():
            pacote.write(caminho, item)
        else:
            for arquivo in sorted(caminho.rglob("*")):
                if arquivo.is_file():
                    pacote.write(arquivo, arquivo.relative_to(root).as_posix())
print(f"ZIP criado: {destino.name}")

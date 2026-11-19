"""Teste local do checkpoint RAGAS sem rede nem dependências externas."""

import json
import os
import tempfile
from pathlib import Path
from statistics import mean


root = Path(__file__).parent
notebook = json.loads((root / "1_Notebook_GS2026_2.ipynb").read_text(encoding="utf-8"))
source = "".join(notebook["cells"][16]["source"])
start = source.index("from math import isfinite")
evaluation_code = compile(source[start:], "notebook_ragas_checkpoint", "exec")


class Metric:
    name = ""

    def __init__(self, **kwargs):
        pass


class Faithfulness(Metric):
    name = "faithfulness"


class ResponseRelevancy(Metric):
    name = "response_relevancy"


class LLMContextPrecisionWithReference(Metric):
    name = "context_precision"


class LLMContextRecall(Metric):
    name = "context_recall"


class Result:
    def __init__(self, metric_name):
        self.metric_name = metric_name

    def to_pandas(self):
        column = "answer_relevancy" if self.metric_name == "response_relevancy" else self.metric_name
        return type("Table", (), {"columns": [column], "iloc": [{column: 0.5}]})()


class FakeChatOpenAI:
    def __init__(self, **kwargs):
        pass


calls = []
answers = []


def evaluate(dataset, metrics, **kwargs):
    calls.append(metrics[0].name)
    if len(calls) == 2:
        raise TimeoutError("falha simulada do provedor")
    return Result(metrics[0].name)


def responder_rag(question):
    answers.append(question)
    return {"resposta": "Resposta com fonte [AV-MOB-001]", "contextos": ["Trecho [AV-MOB-001]"]}


namespace = {
    "Path": Path, "json": json, "mean": mean,
    "MODEL_ID": "openrouter/free", "EMBEDDING_ID": "embedding-local",
    "escolha": {"tamanho": 850, "sobreposicao": 120},
    "PERGUNTAS_AVALIACAO": [("simples", f"Pergunta {i}") for i in range(8)],
    "REFERENCIAS_MANUAIS": [f"Referência {i}" for i in range(8)],
    "llm": object(), "EmbeddingsLocais": object,
    "ChatOpenAI": FakeChatOpenAI, "OPENROUTER_API_KEY": "test-only",
    "LangchainLLMWrapper": lambda llm: llm,
    "LangchainEmbeddingsWrapper": lambda embeddings: embeddings,
    "Faithfulness": Faithfulness, "ResponseRelevancy": ResponseRelevancy,
    "LLMContextPrecisionWithReference": LLMContextPrecisionWithReference,
    "LLMContextRecall": LLMContextRecall,
    "SingleTurnSample": lambda **kwargs: kwargs,
    "EvaluationDataset": lambda samples: samples,
    "RunConfig": lambda **kwargs: kwargs,
    "evaluate": evaluate, "responder_rag": responder_rag,
}

with tempfile.TemporaryDirectory(dir=root) as directory:
    previous = Path.cwd()
    try:
        os.chdir(directory)
        try:
            exec(evaluation_code, namespace)
        except RuntimeError as error:
            assert "O progresso anterior está salvo" in str(error)
        else:
            raise AssertionError("A falha simulada não interrompeu a avaliação.")
        partial = json.loads(Path("3_avaliacao_ragas.json").read_text(encoding="utf-8"))
        assert partial["status"] == "parcial"
        assert partial["perguntas"][0]["metricas"] == {"faithfulness": 0.5}
        assert len(answers) == 1

        exec(evaluation_code, namespace)
        complete = json.loads(Path("3_avaliacao_ragas.json").read_text(encoding="utf-8"))
        assert complete["status"] == "medido"
        assert len(calls) == 33  # 32 escores, incluindo uma tentativa que falhou.
        assert len(answers) == 8  # Cada resposta é gerada uma única vez.
        assert all(len(item["metricas"]) == 4 for item in complete["perguntas"])
        assert all(value == 0.5 for value in complete["medias"].values())
    finally:
        os.chdir(previous)

print("Checkpoint RAGAS: falha preserva progresso e retomada conclui sem repetir respostas/escores.")

# Vídeo de demonstração — CitizenTech Mobilidade

**Meta:** 2min45s a 2min55s. **Limite:** 3 minutos. Gravação de tela com voz de Sergio, Giovanni e Gabriel, nessa ordem, sem retorno a quem já falou. Use o [wizard de ensaio](.tmp/roteiro_video_wizard.sh) para passar pelas etapas antes de gravar.

## Preparar a tela

1. Abra o notebook final no Colab depois de executar `Runtime → Run all`. Confira que as seções 2, 4, 6, 7 e 8 mostram saídas reais. Se ainda não executou no Colab, use as capturas da execução local e diga isso na fala; não as apresente como execução no Colab.
2. Deixe abertas as capturas [chunking e busca](2_base_documental/evidencias/chunking_busca.png), [Gradio com histórico](2_base_documental/evidencias/interface_gradio.png), [trace do agente](2_base_documental/evidencias/agente_trace.png), [guardrails](2_base_documental/evidencias/guardrails.png) e [RAGAS](2_base_documental/evidencias/ragas_scores.png). Use a interface ao vivo se estiver funcionando; mantenha a captura como alternativa fiel à execução local.
3. Ajuste zoom para deixar respostas, fontes e números legíveis. Oculte `.env`, chave, painel Secrets, notificações e outras abas pessoais. Grave um teste de 15 segundos para conferir áudio dos três.

## Roteiro com falas

| Tempo | Tela e ação | Fala exata |
|---|---|---|
| **0:00–0:20** | Capa do notebook com nomes e RMs dos três. | **Sergio:** “Somos Sergio Augusto, RM 570184, Gabriel Freitas, RM 572943, e Giovanni Merlotti, RM 573721, da turma 1CCR. Este é o CitizenTech Mobilidade.” |
| **0:20–0:45** | Mostrar os três documentos; depois a comparação de chunking e busca. | **Sergio:** “Criamos três documentos simulados: itinerário, horários e uma portaria que interdita o P07. Comparamos dois tamanhos de trecho. O de 850 caracteres com sobreposição de 120 recuperou itinerário e portaria usando seis trechos.” |
| **0:45–1:15** | Mostrar pergunta composta e `agente_trace.png`. Aponte as duas ações e os resultados. | **Giovanni:** “A pergunta composta pede a próxima partida de domingo depois das nove e o estado do P07 em 11 de novembro. O agente chama duas ferramentas: calcula a saída das dez horas e confirma que o P07 está interditado. O trace registra argumentos, resultados e fontes.” |
| **1:15–1:37** | Mostrar as quatro linhas de `guardrails.png`. | **Giovanni:** “Testamos quatro limites: assunto fora de escopo, instrução maliciosa em documento, pedido de dados pessoais e pergunta sem informação na base. O assistente bloqueia ou admite quando não pode responder.” |
| **1:37–2:07** | Mostrar Gradio. Perguntar “O P07 está aberto em 11/11/2026?” e aproximar resposta e fontes. Se a resposta variar, mostrar a captura local identificada como tal. | **Gabriel:** “Em 11 de novembro, o P07 está interditado desde o dia 7. O assistente consulta os documentos, responde que não está aberto e mostra as fontes. A portaria posterior prevalece sobre o itinerário antigo.” |
| **2:07–2:40** | Mostrar `ragas_scores.png` e o JSON `medido`. Aponte oito perguntas, médias e pergunta 8. | **Gabriel:** “Avaliamos oito perguntas e medimos 32 scores reais com o modelo gpt-4o-mini. A fidelidade média foi 0,9571; a cobertura de contexto, 0,6667. Na pergunta oito, a resposta começou com ‘sim’, mas explicou que os horários não foram cancelados. Propomos checar a coerência da primeira frase em perguntas de sim ou não.” |
| **2:40–2:54** | Voltar à conclusão do notebook ou ao Gradio. | **Gabriel:** “Este é um protótipo acadêmico com dados simulados. Para uso público, precisaríamos de documentos oficiais atualizados, monitoramento e cuidados de privacidade.” |

**Duração prevista: 2min54s.** Reservem até 6 segundos para transições. Falem sem acelerar. Mostrem apenas resultados presentes na tela; se a demonstração ao vivo divergir, expliquem a divergência ou usem a captura real da execução local.

## Conferência antes de publicar

1. Assista ao vídeo inteiro. Confirme duração de até 3 minutos, áudio dos três e apresentação de nomes e RMs no início.
2. Confira se `P07 interditado`, `P09`, duas ações no trace, quatro guardrails, 32 scores e médias ficam legíveis. Não mostre chave de API.
3. Publique como **não listado** no YouTube. Abra o link em janela privada para conferir acesso. Registre a URL em `7_demo_video_url.txt`.
4. O trio deve revisar falas, autoria e arquivos finais antes da certificação e do ZIP.

Este roteiro é arquivo de apoio. `package_submission.py` não o inclui no ZIP de sete itens.

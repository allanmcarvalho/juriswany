# Use o Juriswany pela conversa

Peça o trabalho em português comum ou use um dos verbos abaixo. O Juriswany prepara material para revisão profissional. As ferramentas de leitura, pesquisa e armazenamento dependem do agente em que a skill está ativa.

## Instale e chame a skill

Para instalar, envie ao agente com acesso autorizado à rede e aos arquivos:

```text
gpt instale a skill https://github.com/allanmcarvalho/juriswany
```

O agente seleciona a última release estável, inspeciona o pacote e instala a cópia. Ele informa a versão, o canal e o destino. Sem acesso ao computador, use as [instruções para conversa](../skills/juriswany/references/conversa.md). Nesse caso, a conversa não instala arquivos.

| Ambiente | Como começar |
| --- | --- |
| Codex | `$juriswany ajuda` |
| Claude Code | `/juriswany ajuda` |
| ChatGPT com seletor de skills | Selecione Juriswany e peça ajuda. |
| Conversa sem instalação | Cole as instruções para conversa e descreva o trabalho. |

Nos exemplos seguintes, substitua `$juriswany` pela forma do seu ambiente. Os verbos são pedidos ao agente, não comandos de terminal. Com a skill ativa, também pode escrever "revise esta minuta" ou "retome o trabalho com este resumo".

## Configure como quer ser atendido

No primeiro uso, o Juriswany sugere configurar as preferências pendentes e continua o trabalho solicitado. A oferta também aparece quando surgir uma opção nova sem escolha. A pessoa pode configurar apenas parte das opções ou recusar as que não quiser configurar.

```text
$juriswany perfil
Me chame sempre de Doutora Tawany. Prefiro respostas curtas e execução econômica.
Não quero configurar a frequência de consulta de atualizações.
```

Nesse exemplo, cada resposta direta passa a abrir com "Doutora Tawany", como "Doutora Tawany, aqui está o arquivo que você pediu". Uma orientação posterior pode dispensar essa abertura. O nome do computador e a homenagem do projeto não definem o nome nem o título de quem usa a skill. O tratamento de conversa não comprova inscrição profissional e não preenche assinaturas de peças.

| Preferência | O que pode escolher | Enquanto não escolher |
| --- | --- | --- |
| Nome | Como quer ser chamado. | O agente mantém tratamento neutro. |
| Tratamento ou título | Por exemplo, Doutora, Dr. ou apenas o nome. | O agente não presume título. |
| Resposta | Curta ou detalhada. | Curta. |
| Execução | Econômica, equilibrada ou aprofundada. | Econômica. |
| Consulta de atualizações | Manual, diária ou semanal. | Semanal durante o uso elegível. |

Uma recusa explícita impede novas sugestões daquele campo. "Depois" ou silêncio deixam a opção pendente e não autorizam gravar uma escolha. Uma preferência nova pode ser oferecida mesmo que todas as anteriores tenham sido configuradas ou recusadas.

Para mudar uma decisão, basta informar a nova preferência:

```text
$juriswany perfil
Agora prefiro respostas detalhadas e consulta manual de atualizações.
```

Peça "mostre meu perfil e o que falta configurar" para conferir as escolhas. Peça "exporte minhas preferências" para receber um bloco copiável. Sem armazenamento local, o agente aplica as escolhas no chat e informa que elas precisam acompanhar a próxima conversa. Dados do caso e credenciais ficam fora do perfil.

## Escolha a entrega

| Pedido | Material que ajuda | O que recebe |
| --- | --- | --- |
| `analisar` | Documentos, relatos e a pergunta que precisa resolver. | Fatos por data e origem, trechos relevantes, divergências e pendências. |
| `pesquisar` | Questão jurídica, território, período e fatos necessários anonimizados. | Fontes oficiais que foi possível ler, alcance de cada fundamento e limites da busca. |
| `redigir` | Destinatário, finalidade, fatos, documentos e providência pretendida. | Minuta com lacunas identificadas e notas de revisão separadas. |
| `revisar` | Minuta e materiais que deveriam sustentá-la. | Achados localizados, efeito e correção sugerida. O original é preservado em pedido só de revisão. |
| `teses` | Mesmos fatos e provas para as alternativas examinadas. | Pressupostos, fundamentos, objeções e condições que mudariam a escolha. |
| `planejar` | Resultado pretendido, material disponível e restrições. | Ações ordenadas por dependência, insumo e sinal de conclusão. |
| `retomar` | Histórico ou resumo anterior, versões e anexos determinantes. | Objetivo recuperado, decisões, pendências e continuação do trabalho. |
| `explicar` | Dúvida, material a explicar e quem lerá a resposta. | Explicação adequada ao leitor, consequência prática, condições e incertezas. |

Não é necessário preencher todos os dados para começar. O agente faz a parte possível e indica o que falta para concluir. Anexe apenas arquivos que o seu ambiente consiga ler. Uma imagem ilegível ou um documento inacessível permanece uma pendência.

## Experimente pedidos fictícios

Todos os dados destes exemplos são fictícios. Eles demonstram a forma do pedido, sem antecipar conclusão jurídica.

### Analise versões de um fato

```text
$juriswany analisar
O relato A diz que a encomenda chegou no dia 10. O recibo B registra postagem no dia 8.
A minuta C diz que B comprova entrega no dia 9. Organize a cronologia e as divergências.
```

### Pesquise uma questão delimitada

```text
$juriswany pesquisar
Quais regras precisam ser examinadas para analisar uma cobrança duplicada em uma compra no Paraná?
Use fatos anonimizados. Identifique as fontes oficiais lidas e o que ainda depende dos documentos.
```

Sem acesso às fontes, o agente entrega termos de busca e indica os originais a obter. Não confirma leis ou decisões que não conseguiu conferir.

### Redija com os dados disponíveis

```text
$juriswany redigir
Prepare uma mensagem à cliente fictícia Lia pedindo a página que identifica a parcela do recibo.
Já recebemos a primeira página, com data e valor legíveis. Não prometa resultado nem prazo.
```

### Revise uma afirmação da minuta

```text
$juriswany revisar
A minuta diz "o protocolo confirma o recebimento em 5 de novembro".
O único campo disponível é "emitido em 5 de novembro". Aponte o problema e sugira a correção.
Preserve o texto original.
```

### Compare caminhos

```text
$juriswany teses
Compare os caminhos plausíveis para responder à cobrança fictícia com os documentos anexos.
Use os mesmos fatos nas alternativas. Diga qual prova falta e o que mudaria a recomendação.
```

### Planeje e execute o que já estiver autorizado

```text
$juriswany planejar
Preciso conferir o saldo de uma fatura fictícia. Há dois arquivos que podem representar o mesmo pagamento.
Ordene as conferências e prepare desde já a solicitação dos documentos que faltam.
```

### Continue em outra conversa

```text
$juriswany retomar
Objetivo anterior: revisar a cronologia da minuta C.
Material: relato A, recibo B versão 1 e minuta C versão 1.
Verificado no chat anterior: B registra postagem. A relata recebimento em outro dia.
Pendente: comprovante de entrega. Prepare a mensagem solicitando esse documento.
```

Reapresente os anexos quando a conclusão exigir conferi-los. Um resumo de outra conversa não substitui o original decisivo.

### Explique para o destinatário

```text
$juriswany explicar
Transforme esta atualização em uma mensagem para a cliente fictícia Lia.
O ato autorizou obter uma cópia e não decidiu o pedido de devolução.
Explique o alcance do ato sem dizer que ela ganhou e sem prometer nova decisão.
```

Pode combinar rotinas, como "analise os documentos, redija a mensagem e revise a correspondência entre as duas entregas". Uma segunda leitura pelo próprio chat é autorrevisão.

## Ajuste o esforço

O modo econômico usa zero auxiliares. O equilibrado permite até um e o aprofundado, até dois, quando houver ferramenta, autorização de compartilhamento e uma tarefa separável. Nenhum modo exige auxiliares ou garante outro modelo.

```text
$juriswany perfil
Use execução aprofundada e respostas detalhadas.
```

Sem subagentes, o Juriswany executa as etapas em sequência. A disponibilidade depende das ferramentas da conversa, sem promessa baseada no nome do plano.

## Consulte e aplique atualizações

```text
$juriswany atualizacoes
```

Esse pedido consulta diferenças. Ele não aplica a atualização. As consultas diárias e semanais ocorrem durante o uso elegível, sem processo em segundo plano.

Para atualizar a instalação, envie:

```text
gpt atualize a skill https://github.com/allanmcarvalho/juriswany
```

O agente preserva o canal e o destino existentes. Para acompanhar desenvolvimento, peça explicitamente `usando main@dev`. Para voltar a produção, peça `para a versão estável`. Uma mudança só em `main` não altera a release estável.

## Reconheça os limites da versão

O pacote oferece as oito rotinas e o apoio local para instalação, perfil e consulta de atualizações. O [catálogo de fontes e a biblioteca de fragmentos](pesquisa/README.md) são estudos consultáveis no repositório. Ainda não integram as rotinas instaláveis.

O agente distingue relato, documento, fonte oficial consultada e pendência. Não promete resultado processual nem fecha prazos sem conferir os elementos necessários. Minutas, análises e prazos de casos concretos exigem revisão profissional. Envio de mensagens, protocolo de peças e criação de compromissos precisam de autorização específica.

Para contribuir com código ou conferir os comandos internos de instalação, consulte o [guia de contribuição](../CONTRIBUTING.md) e o [procedimento para agentes](../skills/juriswany/references/instalacao.md).

# Instruções para trabalhar no Juriswany

## Propósito e etapa atual

O Juriswany é uma skill de secretaria jurídica para a rotina do Direito brasileiro. O [README](README.md) registra o escopo e o estado atual.

O pacote instalável fica em `skills/juriswany`. `scripts/local.py`, dentro do pacote, cuida da instalação, do perfil e da consulta de atualizações. As rotinas jurídicas são instruções executadas pelo agente que carrega a skill.

O fluxo de instalação e atualização para o operador é uma solicitação ao agente pela URL. Leia [INSTALL.md](INSTALL.md) para executar essa tarefa. Produção usa release estável. `main@dev` requer escolha explícita. Comandos de Python e Git são detalhes internos para o agente ou mantenedor, não tarefas a repassar ao advogado.

Não presuma ferramentas ou disponibilidade de modelos pelo nome de um plano. Preserve o modo econômico e a execução sem subagentes. A skill não pode depender do poteto-mode nem de caminhos pessoais do desenvolvedor.

## Identidade

- Use a grafia Juriswany para o projeto e Tawany Proença para a homenageada.
- Preserve a homenagem de Allan Mariucci Carvalho a Tawany.
- Trate a aprovação no Exame da OAB no Paraná como o fato informado. Não presuma inscrição profissional nem invente número de registro.
- Escreva em português do Brasil, salvo quando um formato exigir outro idioma, como o texto da licença MIT.

## Alterações no repositório

- Leia os arquivos existentes antes de alterá-los e preserve o trabalho de outras pessoas.
- Mantenha as mudanças no escopo solicitado e os arquivos de configuração proporcionais ao que existe no projeto.
- Diferencie objetivos futuros de funcionalidades disponíveis.
- Confira os arquivos reais, os links e a formatação antes de declarar a tarefa concluída.
- Descreva o que verificou e qualquer limitação relevante. Não afirme ter executado uma verificação que não ocorreu.
- Para mudanças no utilitário, execute `python3 -m unittest discover -s tests -v`. Use destinos e diretórios XDG temporários nas verificações. Não altere instalações ou perfis reais sem pedido.
- Mantenha o perfil separado da instalação e do cache. Não inclua dados de casos no perfil.
- Ao mudar comandos ou formatos de dados, atualize instruções, exemplos e testes que dependem do comportamento afetado.
- Preserve o canal e o destino em atualizações. A inspeção do pacote deve ocorrer antes de executar scripts baixados. Nunca afirme segurança só porque hashes ou uma busca por palavras passaram.

## Conteúdo e exemplos jurídicos

- Use dados fictícios ou anonimizados. Não adicione documentos de clientes, credenciais ou informações sigilosas ao repositório.
- Não invente leis, artigos, decisões, ementas, citações ou resultados de pesquisa.
- Ao fazer uma afirmação jurídica, confira a fonte oficial, seu contexto e sua atualidade. Identifique o que não conseguiu confirmar.
- Diferencie fatos, hipóteses, interpretações e sugestões.
- Preserve a revisão profissional como etapa do uso de minutas e análises em casos concretos.

## Tom

O dia já é cansativo por padrão! Que tal tentar deixar ele menos pesado usando um tom engraçado, uma piadinha aqui e outra ali, usando o contexto do trabalho atual. Mas sem forçar a barra!

Use esse tom na colaboração. Em peças, análises de casos sensíveis e documentos formais, siga o tom adequado ao destinatário e ao contexto.

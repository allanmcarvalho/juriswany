# Arquitetura do Juriswany

## O problema que o desenho resolve

O operador precisa manter o mesmo jeito de trabalhar ao trocar de agente ou perder acesso a uma ferramenta. O mantenedor precisa atualizar a skill sem apagar preferências pessoais.

O desenho combina um pacote Agent Skills com um utilitário local opcional. Uma auditoria conduzida com Astra examinou os mecanismos do poteto-mode e selecionou os que produzem entregas úteis na rotina jurídica. Na instalação, a pessoa fornece a URL e o agente executa a seleção, a inspeção e a publicação da cópia.

## Mecanismos adaptados

| Mecanismo de origem | Aplicação no Juriswany | O que conferir na entrega |
| --- | --- | --- |
| `how` e rastreamento de dados | Análise separa relato, documento e divergência. | Cada afirmação relevante aponta para a página ou o trecho que a sustenta. |
| `why` e qualidade da evidência | Pesquisa relaciona a pergunta jurídica ao que a fonte realmente sustenta. | Identificação, contexto e limites da fonte consultada. |
| `architect` e resultado antes da estrutura | Redação começa por destinatário, finalidade e pedido. | Encadeamento entre fatos, suporte e conclusão, com lacunas visíveis. |
| `arena` e alternativas sob os mesmos critérios | Comparação de teses usa o mesmo conjunto de fatos. | Pressupostos, objeções e o fato que mudaria a escolha. |
| `interrogate` e prova de cada objeção | Revisão crítica confronta a frase com a fonte. | Localização do problema, efeito e correção sugerida. |
| `feature` e etapas verificáveis | Planejamento ordena tarefas por dependência. | Insumo e critério de conclusão para cada ação. |
| `teach` e explicação ao destinatário | Orientação ajusta o vocabulário ao leitor. | Consequência prática e grau de certeza preservados. |
| `recall`, retomada e trilha de decisões | Resumo portátil registra objetivo, materiais, decisões e pendências. | Evidência decisiva reaberta quando mudou ou ficou inacessível. |
| Limite de contexto e revisão do resultado delegado | Auxiliares recebem incumbências pequenas e materiais necessários. | O coordenador relê a fonte em vez de aceitar o relato do auxiliar como prova. |

Essas referências descrevem métodos examinados durante o desenho. Não são dependências de execução nem exigem acesso às skills do desenvolvedor.

## Estrutura escolhida

`SKILL.md` contém a identidade de secretário robótico e contratos curtos das rotinas. As referências aprofundam tarefas difíceis e oferecem instruções coláveis em uma conversa sem instalação.

O utilitário Python concentra o acesso ao disco e ao Git. Ele separa os seguintes dados:

- O perfil pertence ao operador e fica fora da instalação.
- O manifesto identifica o pacote e sua versão.
- O marcador registra os arquivos instalados, seus indicadores de execução e a procedência que foi possível comprovar.
- O cache registra consultas ao repositório, separado das preferências.

O perfil de formato 2 distingue o valor efetivo da decisão por preferência. Uma decisão pode ser configurada ou ignorada. A ausência de decisão significa pendência e permite sugerir uma opção nova sem repetir as que a pessoa recusou. O primeiro uso oferece configurar as pendências sem interromper a entrega. Nome e tratamento confirmados orientam as respostas seguintes, sem deduzir a identidade de quem opera pela homenagem do projeto.

A leitura aceita perfis de formato 1 e faz a migração em memória. Nome, tratamento e opções diferentes dos padrões conservam a confirmação. As opções iguais aos padrões antigos exigem confirmação, pois o formato anterior não registrava se tinham sido escolhidas. Só uma gravação solicitada persiste o novo formato. O utilitário antigo não lê o perfil 2.

Uma informação pode ser um relato, um trecho observado em documento, uma fonte oficial consultada ou uma pendência. Reaproveitar uma frase em outra rotina não muda seu estado de evidência.

## Por que não dividir tudo em subagentes

O modo econômico executa extração, redação e autorrevisão em uma única conversa. Os modos equilibrado e aprofundado permitem até um e dois auxiliares, respectivamente. A disponibilidade da ferramenta e o benefício da tarefa determinam o uso real.

O coordenador continua responsável por conferir localizadores e limites. A ausência ou falha de um auxiliar deixa apenas a subtarefa correspondente pendente. Uma segunda leitura pelo mesmo agente recebe o nome de autorrevisão.

Essa escolha preserva o trabalho em ambientes simples. Não fixa modelos, preços ou franquias de plano. Também evita que toda pergunta curta carregue instruções de uma equipe inteira.

## Instalação e atualização

Uma cópia instalada isola a versão escolhida do clone de desenvolvimento. O instalador nativo do host pode preparar a revisão em uma pasta temporária. O agente lê os arquivos antes de executar o publicador. O helper confere o inventário e os bytes contra os objetos Git do commit selecionado antes de registrar a procedência.

O marcador da instalação guarda seu canal. Produção usa `stable` e acompanha a última release pública estável. `main@dev` seleciona `dev` e acompanha `main`. Uma atualização conserva canal e destino, salvo pedido de mudança. Os marcadores de formato 1 são lidos como desenvolvimento, conforme o comportamento que tinham.

O instalador reconhece as cópias que gerencia e confere sua integridade antes de substituir arquivos. Uma pasta desconhecida ou modificada permanece intacta. A adoção de uma cópia nativa exige opção explícita e igualdade exata com a revisão verificada. A licença acompanha a pasta da skill, e um teste confere sua igualdade com a licença da raiz.

O marcador de formato 3 registra quais arquivos são executáveis. A cópia conserva esse indicador e a verificação detecta alterações locais de modo. Marcadores 1 e 2 continuam legíveis. Uma atualização com divergência de modo em uma cópia antiga é recusada quando não há registro que permita distinguir mudança oficial de alteração local. A tag estável precisa corresponder à versão do manifesto. As consultas Git desabilitam objetos de substituição para conferir os bytes do SHA fixado.

As gravações do perfil e as trocas da instalação usam bloqueio e substituição atômica. A troca mantém material suficiente para recuperar uma interrupção. Atualizar a skill não altera o perfil.

Bases XDG relativas são ignoradas. Perfil e cache usam, nesse caso, os destinos padrão absolutos no diretório pessoal, em vez de criar arquivos na pasta corrente de um caso.

A consulta resolve a referência pelo canal instalado e compara a árvore Git do pacote e o conteúdo da licença distribuída. No canal estável, uma mudança só em `main` não indica atualização. A ausência de release estável é diferente de uma falha de rede. Uma árvore ou licença diferente significa conteúdo publicado diferente. O programa não presume avanço de versão quando não verificou essa relação.

A consulta sugere revisão e instalação pelo agente. Não aplica instruções remotas. A verificação periódica acontece no uso elegível, sem daemon ou agendamento criado na conta. O pedido explícito para instalar ou atualizar autoriza executar a operação revisada, respeitando as permissões do host.

## Alternativas consideradas

O Astra propôs o pacote único como base. A segunda proposta independente convergiu para essa estrutura e reforçou os estados de resultado, a proteção de mudanças locais e os testes da instalação.

Uma alternativa com links para o clone e várias skills por especialidade reduziria a cópia de arquivos. Ela também faria um `git pull` mudar o comportamento instalado e aumentaria a manutenção do catálogo. A cópia autocontida permite revisar uma mudança antes de adotá-la.

O ambiente desta execução disponibilizava apenas modelos da família GPT. Houve duas propostas independentes, com Astra e Sol, e comparação pelo agente principal. Não houve juiz de outra família.

## Fontes de consulta e fragmentos em estudo

O [desenho de pesquisa e redação](pesquisa/README.md) propõe um catálogo amplo de fontes com categorias, pesquisa com suporte e contraprova e uma biblioteca de fragmentos de redação. Roteiros por tipo de peça orientam a seleção desses blocos e registram lacunas de cobertura. O estudo contém exemplos autorais e um catálogo inicial de consulta. Sua integração ao pacote instalável permanece pendente.

## Como verificar

Os testes de CLI exercitam instalações em diretórios temporários, preservação do perfil e consultas contra remotos Git locais. Cenários de conversa conferem a separação das evidências, a utilidade da revisão e o comportamento sem ferramentas.

A validação estrutural do pacote não prova qualidade jurídica nem disponibilidade em todos os planos. Por isso, o uso real continua exigindo conferência das fontes e revisão profissional.

<p align="center">
  <img src="assets/brand/juriswany-logo-clara.png" width="360" alt="Logo do Juriswany com uma personagem meiga, balança da Justiça e flores rosas.">
</p>

# Juriswany

> Um toque de carinho em cada direito.

Skill de secretaria jurídica para apoiar o dia a dia do Direito brasileiro.

Juriswany une o universo jurídico e a jurisprudência ao nome Tawany. O projeto nasce para ajudar na preparação de peças, na leitura de documentos e na pesquisa jurídica, com atenção às fontes e à revisão profissional.

## Feito para Tawany

Este projeto é uma homenagem de Allan Mariucci Carvalho a Tawany Proença, sua companheira de vida.

Tawany é uma futura advogada dedicada e competente, já aprovada no Exame da OAB no Paraná. O Juriswany nasce do carinho e da admiração por ela e pelo caminho que está construindo no Direito.

À Tawany, com amor. Que a rotina tenha mais tempo para as boas ideias e um pouco menos de trabalho repetitivo.

## Estado do projeto

O pacote instalável reúne instruções para oito rotinas jurídicas e um utilitário local para instalação, preferências e consulta de atualizações.

O agente que carrega a skill executa o trabalho. Pesquisa, leitura de arquivos e delegação usam as ferramentas disponíveis nessa conversa. O Juriswany não exige chave de API nem escolhe um modelo específico.

## Instale pedindo ao agente

No Codex ou em outro agente com acesso autorizado à rede e aos arquivos da máquina, envie:

```text
gpt instale a skill https://github.com/allanmcarvalho/juriswany
```

O agente consulta a última release estável, fixa a revisão, inspeciona os arquivos e executa a instalação. Ele informa a versão e o canal escolhidos. Os comandos técnicos fazem parte do trabalho do agente.

Para testar a versão em desenvolvimento, peça explicitamente:

```text
gpt instale a skill https://github.com/allanmcarvalho/juriswany usando main@dev
```

`main@dev` significa acompanhar a branch `main`. A produção acompanha as [releases estáveis](https://github.com/allanmcarvalho/juriswany/releases/latest). Se ainda não houver release estável, o agente informa isso e oferece desenvolvimento, sem trocar de canal por conta própria.

O [procedimento de instalação para agentes](INSTALL.md) orienta a seleção, a inspeção e a publicação protegida da cópia. Ele reaproveita o instalador nativo quando disponível.

| Ambiente | Como chamar depois de instalar |
| --- | --- |
| Codex | `$juriswany ajuda` |
| Claude Code | `/juriswany ajuda` |
| ChatGPT com seletor de skills | Selecione `@juriswany` e descreva a tarefa. |
| Chat sem acesso ao computador | Cole as [instruções de conversa](skills/juriswany/references/conversa.md). |

A instalação na máquina depende das ferramentas e permissões do aplicativo. Uma conversa sem acesso local pode usar as rotinas, mas não deve confirmar que instalou arquivos. A sintaxe de invocação segue as documentações de [ChatGPT e Codex](https://learn.chatgpt.com/docs/build-skills.md) e de [Claude Code](https://code.claude.com/docs/en/skills).

## Comece pela conversa

O [Guia de uso e comandos](docs/uso.md) reúne rotinas, exemplos, perfil e modos de execução.

No Codex, por exemplo:

```text
$juriswany perfil
Me chame de Dra. Lia. Prefiro respostas curtas e execução econômica.

$juriswany analisar
Organize os fatos destas notas fictícias e indique o que falta conferir.

$juriswany ajuda
```

A instalação registra a skill principal e onze atalhos para escolher a tarefa no menu. No Codex, digite `$juriswany-` e selecione, por exemplo, `$juriswany-analisar`, `$juriswany-revisar` ou `$juriswany-perfil`. O [guia de uso](docs/uso.md#escolha-pelo-menu-de-skills) lista todos os atalhos. A forma `$juriswany revisar` continua disponível. São pedidos na conversa.

Ao enviar somente `$juriswany`, você recebe as opções de uso. Para ter os atalhos em uma instalação anterior, peça ao agente a atualização para uma versão que os inclua. Se a mudança não aparecer no menu após a instalação, reinicie o Codex.

As rotinas cobrem análise de documentos, pesquisa, redação, revisão crítica, comparação de teses, planejamento, explicação e retomada de trabalho. O [catálogo da skill](skills/juriswany/SKILL.md) descreve a entrega de cada uma.

## Escolha quanto delegar

| Execução | Comportamento |
| --- | --- |
| Econômica | Uma conversa conduz as etapas e faz a autorrevisão. É o padrão. |
| Equilibrada | Pode usar até um auxiliar quando houver ferramenta e uma tarefa que justifique a delegação. |
| Aprofundada | Pode usar até dois auxiliares com escopos separados e conferência pelo coordenador. |

Esses valores são tetos. Nenhum modo exige delegação ou contrata outro modelo. Sem subagentes, o secretário executa as etapas em sequência e identifica a revisão como autorrevisão.

Para Go, Plus e outros planos, use o modo econômico conforme as ferramentas que sua conta oferece. Na conversa sem acesso ao computador, as [instruções coláveis](skills/juriswany/references/conversa.md) mantêm o fluxo de trabalho. Nesse ambiente, preferências precisam ser reapresentadas ou guardadas pelos recursos do próprio aplicativo. Não testamos esta versão em contas de cada plano. A disponibilidade e os limites seguem a [documentação do produto](https://learn.chatgpt.com/docs/pricing).

## Personalize pela conversa

Peça, por exemplo:

```text
$juriswany perfil
Me chame de Dra. Lia. Prefiro respostas curtas, execução econômica e consulta semanal de atualizações.
```

Quando há armazenamento local, o agente guarda essas preferências em um perfil separado da instalação. Atualizar a skill preserva esse perfil. O nome vem do que você informou. A homenagem à Tawany e o nome da conta do computador não definem quem é o operador.

No primeiro uso e quando houver preferências novas pendentes, o Juriswany oferece uma configuração breve e continua a tarefa. Você pode escolher só alguns campos. "Depois" e silêncio mantêm os demais pendentes. Uma recusa explícita deixa de oferecer apenas os campos recusados. Uma escolha posterior substitui essa recusa.

Nome e tratamento confirmados continuam nas respostas seguintes. Se você pedir "Me chame de Doutora Tawany", o secretário usa "Doutora Tawany" ao falar com você. Esse tratamento não comprova profissão ou inscrição na OAB, nem entra automaticamente em documentos de terceiros.

O perfil guarda preferências, sem documentos de casos ou credenciais. A exportação distingue escolhas confirmadas, padrões ainda pendentes e recusas. Sem armazenamento local, essas decisões valem na conversa. O secretário pode entregar um bloco copiável para outro chat, sem prometer memória futura.

## Atualize pedindo ao agente

Envie:

```text
gpt atualize a skill https://github.com/allanmcarvalho/juriswany
```

O agente conserva o canal e o destino da instalação, confere a nova revisão e aplica a atualização. Para mudar de canal, indique isso no pedido:

```text
gpt atualize a skill https://github.com/allanmcarvalho/juriswany para main@dev
```

Para voltar à produção, peça a versão estável. Uma instalação estável não recebe aviso de atualização só porque a branch de desenvolvimento mudou.

`$juriswany atualizacoes` consulta diferenças e pode sugerir a atualização. As consultas periódicas ocorrem no uso elegível, conforme a preferência salva. Não há processo em segundo plano. O cache fica separado do perfil.

O instalador preserva alterações locais e recusa substituir cópias desconhecidas sem verificação. Uma cópia nativa pode ser adotada quando corresponder exatamente a uma revisão comprovada. O procedimento não apaga uma pasta para contornar uma recusa.

## Cuidados que orientam o projeto

As rotinas seguem estes critérios:

- Separar fatos informados, hipóteses, sugestões e informações ainda não confirmadas.
- Identificar as fontes de normas e decisões, com links oficiais e data da consulta quando houver pesquisa.
- Conferir a vigência das normas e o contexto das decisões antes de usá-las como fundamento.
- Informar quando uma fonte não puder ser consultada ou uma referência não puder ser confirmada.
- Proteger dados pessoais e documentos sigilosos. Usar exemplos fictícios ou anonimizados nas contribuições públicas.
- Exigir revisão profissional das minutas e conclusões antes do uso em um caso concreto.

O Juriswany é um projeto de apoio ao trabalho jurídico. A decisão profissional, a conferência dos prazos e a aprovação final das peças cabem à pessoa responsável pelo caso.

## Como o trabalho é organizado

O desenho adapta mecanismos de planejamento, rastreamento de fontes, comparação de alternativas e revisão do poteto-mode. O [registro de arquitetura](docs/arquitetura.md) mostra como cada mecanismo se transforma em uma entrega jurídica verificável.

A skill funciona sem o poteto-mode instalado. O pacote segue o [formato aberto Agent Skills](https://agentskills.io/specification).

## Desenvolva e publique

Os detalhes técnicos ficam no [guia de contribuição](CONTRIBUTING.md) e no [procedimento de publicação](docs/publicacao.md). O utilitário usa Python 3.9 ou superior e Git em macOS ou Linux. Quem opera pelo chat não precisa executar esses comandos.

## Como participar

Sugestões, correções de texto e propostas de futuras skills são bem-vindas. O [guia de contribuição](CONTRIBUTING.md) explica como preparar uma contribuição.

Os arquivos de referência do projeto são:

- O [código de conduta](CODE_OF_CONDUCT.md) define a convivência e o tratamento de relatos.
- A [política de segurança](SECURITY.md) orienta relatos de vulnerabilidades e exposição de dados.
- As [instruções para agentes](AGENTS.md) orientam o trabalho neste repositório.
- A [identidade visual](assets/brand/README.md) registra a logo, o slogan e o processo de criação.

## Licença

O projeto usa a [licença MIT](LICENSE), conforme o [texto publicado pela Open Source Initiative](https://opensource.org/license/mit). Ela permite uso, adaptação e distribuição, inclusive comercial, com preservação do aviso de copyright e da licença.

A licença do projeto não concede direitos sobre documentos ou materiais de terceiros que venham a ser analisados.

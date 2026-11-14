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

Esta é a primeira versão instalável. O pacote reúne instruções para oito rotinas jurídicas e um utilitário local para instalação, preferências e consulta de atualizações.

O agente que carrega a skill executa o trabalho. Pesquisa, leitura de arquivos e delegação usam as ferramentas disponíveis nessa conversa. O Juriswany não exige chave de API nem escolhe um modelo específico.

## Instale no seu agente

Para as funções locais, use macOS ou Linux com Python 3.9 ou superior. A consulta de atualizações também precisa de Git e rede.

Baixe o repositório e instale a skill no Codex:

```sh
git clone https://github.com/allanmcarvalho/juriswany.git
cd juriswany
python3 skills/juriswany/scripts/local.py instalar codex
```

Para o Claude Code, execute:

```sh
python3 skills/juriswany/scripts/local.py instalar claude
```

Cada comando instala uma cópia autocontida. O instalador preserva mudanças locais e recusa substituir pastas que não reconhece.

| Ambiente | Destino da instalação | Como chamar |
| --- | --- | --- |
| Codex | `~/.agents/skills/juriswany` | `$juriswany analisar` |
| Claude Code | `~/.claude/skills/juriswany` | `/juriswany analisar` |
| ChatGPT com seletor de skills | Conforme a interface disponível | Selecione `@juriswany` e descreva a tarefa. |
| Chat sem instalação | Cole as [instruções de conversa](skills/juriswany/references/conversa.md). | Faça o pedido em linguagem comum. |

A sintaxe pertence ao aplicativo. Consulte as documentações de [skills no ChatGPT e Codex](https://learn.chatgpt.com/docs/build-skills.md) e de [skills no Claude Code](https://code.claude.com/docs/en/skills). Se a nova skill não aparecer, reinicie a sessão do agente.

## Comece pela conversa

No Codex, por exemplo:

```text
$juriswany perfil
Me chame de Dra. Lia. Prefiro respostas curtas e execução econômica.

$juriswany analisar
Organize os fatos destas notas fictícias e indique o que falta conferir.

$juriswany ajuda
```

Só `juriswany` é o nome de skill registrado. As palavras seguintes escolhem a rotina. Não são comandos do terminal.

As rotinas cobrem análise de documentos, pesquisa, redação, revisão crítica, comparação de teses, planejamento, explicação e retomada de trabalho. O [catálogo da skill](skills/juriswany/SKILL.md) descreve a entrega de cada uma.

## Escolha quanto delegar

| Execução | Comportamento |
| --- | --- |
| Econômica | Uma conversa conduz as etapas e faz a autorrevisão. É o padrão. |
| Equilibrada | Pode usar até um auxiliar quando houver ferramenta e uma tarefa que justifique a delegação. |
| Aprofundada | Pode usar até dois auxiliares com escopos separados e conferência pelo coordenador. |

Esses valores são tetos. Nenhum modo exige delegação ou contrata outro modelo. Sem subagentes, o secretário executa as etapas em sequência e identifica a revisão como autorrevisão.

Para Go, Plus e outros planos, use o modo econômico conforme as ferramentas que sua conta oferece. Na conversa sem acesso ao computador, as [instruções coláveis](skills/juriswany/references/conversa.md) mantêm o fluxo de trabalho. Nesse ambiente, preferências precisam ser reapresentadas ou guardadas pelos recursos do próprio aplicativo. Não testamos esta versão em contas de cada plano. A disponibilidade e os limites seguem a [documentação do produto](https://learn.chatgpt.com/docs/pricing).

## Guarde suas preferências na máquina

Quando há acesso local, o secretário usa um perfil fora da instalação. Por padrão, ele fica em `~/.config/juriswany/perfil.json`. A variável `XDG_CONFIG_HOME` permite outro diretório.

O perfil guarda nome de preferência, tratamento, extensão das respostas, modo de execução e frequência de consulta ao repositório. Não guarda documentos de casos nem credenciais.

Você também pode configurá-lo pelo terminal, a partir do clone:

```sh
python3 skills/juriswany/scripts/local.py perfil definir --nome Lia --tratamento Dra. --resposta curta --execucao economica --consulta semanal
python3 skills/juriswany/scripts/local.py perfil mostrar
python3 skills/juriswany/scripts/local.py perfil exportar
```

O secretário usa o nome informado por você. A homenagem à Tawany e o nome da conta do computador não definem quem é o operador. Sem perfil, ele começa com tratamento neutro.

## Confira as atualizações

Peça `$juriswany atualizacoes` ou, a partir da instalação no Codex, execute:

```sh
python3 ~/.agents/skills/juriswany/scripts/local.py atualizacoes --forcar
```

A consulta compara o conteúdo instalado da skill e a licença que a acompanha com o publicado no repositório. Uma mudança apenas na apresentação do repositório não implica nova skill.

No próximo uso elegível, a skill consulta o repositório conforme a frequência do perfil. O cache fica separado, em `~/.cache/juriswany`, ou sob `XDG_CACHE_HOME`. Não há processo em segundo plano.

Uma diferença gera uma sugestão com as referências disponíveis. A consulta não substitui arquivos nem executa instruções remotas. Depois de revisar a mudança, atualize seu clone e repita o comando de instalação.

Instalações a partir de arquivos modificados ou sem histórico Git continuam utilizáveis, mas podem não ter procedência suficiente para comparar revisões.

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

## Verifique o utilitário local

Execute os testes sem instalar a skill no seu perfil real:

```sh
python3 -m unittest discover -s tests -v
```

Os testes usam diretórios temporários e repositórios Git locais. A validação dos scripts não garante o resultado de uma análise jurídica. As instruções também precisam de avaliação por cenários de uso.

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

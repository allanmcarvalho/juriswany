# Instalação e atualização pelo agente

Leia este procedimento quando a pessoa pedir para instalar ou atualizar a skill pela URL deste repositório. O pedido autoriza o trabalho necessário à instalação escolhida. Estas instruções não substituem as permissões e políticas do aplicativo.

## Entenda o pedido

A primeira instalação usa a última release estável publicada. Para desenvolvimento, a pessoa precisa pedir `main@dev`. Esse seletor significa canal `dev` e referência `refs/heads/main`. Não é uma referência Git literal.

Na atualização, preserve o destino e o canal registrados. Uma mudança de canal precisa constar no pedido. Se não houver release estável, informe isso e ofereça desenvolvimento. Aguarde essa escolha. Uma falha de rede não significa ausência de release.

Se o ambiente não puder trabalhar nos arquivos da máquina, explique a limitação e ofereça as [instruções para conversa](conversa.md). Não confirme uma instalação que não ocorreu.

## Localize a instalação

Consulte os diretórios que o host reconhece antes de criar outra cópia. No Codex, considere o diretório informado pelo instalador nativo, `CODEX_HOME/skills`, `~/.codex/skills` e `~/.agents/skills`. No Claude Code, considere `~/.claude/skills`.

Use a pasta existente do Juriswany quando houver uma única instalação reconhecida. Se houver mais de uma candidata, mostre as opções e peça qual deve ser atualizada. Não elimine nenhuma delas para resolver a ambiguidade.

Na primeira instalação, use um diretório de skills autorizado e reconhecido pelo host. Passe esse destino explicitamente ao publicador para evitar duplicatas.

## Resolva a versão e fixe a revisão

1. Para `stable`, consulte a última release em `https://api.github.com/repos/allanmcarvalho/juriswany/releases/latest`. Confira publicação, `draft: false`, `prerelease: false` e tag `vMAJOR.MINOR.PATCH`. A versão do manifesto precisa coincidir com a tag sem o prefixo `v`.
2. Para `dev`, selecione `refs/heads/main`.
3. Prepare um repositório Git temporário com os objetos da referência escolhida. Resolva tags anotadas até o commit. Guarde o SHA completo e a tag da release.
4. Baixe e inspecione somente esse SHA. Se a referência ou os arquivos mudarem durante a preparação, resolva a divergência antes de publicar outros bytes.

A API de releases distingue releases de tags avulsas. Consulte a [documentação oficial do GitHub](https://docs.github.com/en/rest/releases/releases#get-the-latest-release) se precisar conferir os campos.

## Prepare e inspecione o pacote

No Codex, use o script da skill nativa `skill-installer` com estes argumentos. Encontre o caminho do script no catálogo do host. Não suponha um caminho pessoal do desenvolvedor.

```text
--repo allanmcarvalho/juriswany
--path skills/juriswany
--ref SHA_COMPLETO
--dest DIRETORIO_TEMPORARIO
```

O download ficará em `DIRETORIO_TEMPORARIO/juriswany`. O instalador nativo prepara a cópia nessa pasta. O destino ativo só será alterado depois da inspeção. Em outro agente, use a ferramenta de aquisição disponível ou um checkout temporário do mesmo commit.

Leia `SKILL.md`, o manifesto, as referências e os scripts do pacote. Confira o inventário e os caminhos relativos. Examine as dependências, operações de rede, destinos de escrita, chamadas a processos e tratamento de credenciais. Considere também as mudanças desde a versão instalada.

Antes de executar scripts do pacote, registre um resumo curto do que examinou, do SHA e dos efeitos encontrados. Se houver comportamento fora do pedido ou outro achado material, pare e apresente o problema concreto. Um hash verifica integridade dos bytes. Ele não demonstra segurança do comportamento, e uma busca por palavras suspeitas não substitui a leitura.

Se não houver achado material e o host permitir a operação, prossiga com a instalação já solicitada. A pessoa não precisa copiar comandos de terminal nem responder outra confirmação genérica.

## Publique a cópia revisada

Execute o `scripts/local.py` que acabou de inspecionar. Os argumentos internos são para o agente, não para o advogado.

```text
instalar codex
--destino PASTA_REAL_DA_SKILL
--canal stable
--release vMAJOR.MINOR.PATCH
--origem-git REPOSITORIO_GIT_TEMPORARIO
--commit SHA_COMPLETO
```

Para Claude Code, use `instalar claude`. Para desenvolvimento, passe `--canal dev` e omita `--release`. O repositório temporário precisa conter os objetos e a referência selecionada. O helper confere os bytes e o inventário do pacote contra a árvore daquele commit antes de registrar a procedência.

A pasta de uma instalação gerenciada passa pelas proteções de integridade, modos executáveis, bloqueio, cópia de segurança e recuperação. O marcador novo usa formato 3 e aceita a leitura dos formatos 1 e 2. Se um marcador antigo não comprovar a origem de uma divergência de modo, preserve a cópia e registre a pendência. Não altere permissões nem apague a pasta para contornar a recusa. O perfil pessoal fica fora dessa troca.

Uma cópia nativa sem marcador só pode ser adotada com `--adotar-nativa` e igualdade exata com a revisão verificada. Não use a opção para ignorar diferenças. Se a cópia antiga não corresponder ao alvo novo, identifique e verifique primeiro a revisão própria da cópia antiga. Sem procedência suficiente ou com alterações locais, preserve a pasta e explique o impedimento.

## Confira e responda

Leia o marcador e confira o conteúdo instalado. Informe a versão, o canal, o commit e o destino. Identifique qualquer limitação que tenha impedido concluir o pedido.

No Codex, a skill fica disponível no próximo turno. Se o host não reconhecer a mudança, siga a orientação de recarregamento da interface. Explique como chamar `$juriswany ajuda` no Codex, `/juriswany ajuda` no Claude Code ou selecionar a skill na interface que a oferecer.

## Atualize com o mesmo procedimento

Um pedido como "gpt atualize a skill https://github.com/allanmcarvalho/juriswany" repete seleção, preparação, inspeção e publicação. Preserve o canal e o destino existentes. A consulta `$juriswany atualizacoes` apenas informa diferenças. Um pedido para aplicar a atualização autoriza a instalação da versão revisada.

Os marcadores antigos de formato 1 acompanhavam `main` e são tratados como `dev`. Migrar esse uso para produção exige um pedido explícito pelo canal estável.

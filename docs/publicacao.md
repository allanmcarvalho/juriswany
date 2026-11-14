# Publique uma versão estável

Este procedimento é para quem mantém o repositório. A pessoa que usa o Juriswany pede a instalação ou atualização pela conversa.

## Prepare a revisão

1. Atualize `versao` em `skills/juriswany/manifest.json` para a versão da publicação.
2. Confira que `skills/juriswany/LICENSE` contém os mesmos bytes de `LICENSE` na raiz.
3. Execute `python3 -m unittest discover -s tests -v`.
4. Valide o formato de `SKILL.md`, suas referências e os metadados da interface.
5. Faça a revisão dos arquivos e registre o commit que será publicado.

A tag deve usar `vMAJOR.MINOR.PATCH`, com a versão declarada no manifesto. Uma tag sem uma release publicada não passa a ser a versão de produção.

## Publique a release

Prepare notas curtas com o comportamento novo, a verificação realizada e limitações materiais. Crie a release no GitHub para o commit revisado. Marque-a como estável, sem os estados draft e prerelease. Não mova uma tag já publicada para substituir seu conteúdo. Publique outra versão quando houver correção.

O canal `stable` acompanha a última release estável. O canal `dev`, escolhido como `main@dev`, acompanha `refs/heads/main`. Um commit novo em `main` não atualiza a produção por si só.

## Confira a distribuição real

1. Consulte `releases/latest` e confira tag, estado de publicação e revisão.
2. Resolva a tag até o SHA do commit e prepare seus objetos Git em diretório temporário.
3. Use o instalador nativo para baixar `skills/juriswany` nesse SHA em outra pasta temporária.
4. Leia os arquivos baixados e confira seu inventário contra o commit.
5. Instale em um destino temporário com canal `stable`, release e procedência verificados.
6. Consulte atualizações pela cópia instalada e confira versão, canal e hashes.

Uma inspeção básica registra os arquivos e efeitos examinados. Não equivale a uma garantia de segurança nem substitui a revisão profissional dos conteúdos jurídicos.

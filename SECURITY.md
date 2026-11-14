# Política de segurança

Esta política cobre vulnerabilidades do projeto e exposição de credenciais, dados pessoais ou documentos sigilosos no repositório.

## Estado atual

A análise de relatos considera a última release estável e o conteúdo da branch principal. Não há compromisso de suporte a versões antigas ou prazo garantido de resposta nesta etapa.

## Relate de forma reservada

Se a opção de relato privado estiver habilitada na área de segurança do repositório no GitHub, use "Report a vulnerability".

Se a opção não estiver disponível, abra uma issue com o título "Solicitação de contato reservado", sem descrever a falha ou incluir dados sensíveis. Aguarde o mantenedor combinar um canal privado antes de enviar os detalhes.

A criação deste arquivo não habilita relatos privados no GitHub. O funcionamento desse recurso está na [documentação oficial de relatos privados](https://docs.github.com/en/code-security/how-tos/report-and-fix-vulnerabilities/report-privately).

## Prepare o relato

No canal privado, informe:

- O arquivo, a referência ou a versão afetada.
- O comportamento observado e o impacto possível.
- Os passos para reproduzir o problema com dados fictícios.
- Uma sugestão de correção, se houver.

Não envie credenciais ativas, documentos de clientes ou cópias de dados expostos como prova. Descreva onde ocorre a exposição e compartilhe apenas o necessário para localizá-la.

## Se houver exposição de um segredo

Avise o responsável pelo segredo por um canal reservado para que ele possa revogá-lo ou substituí-lo. Remover um arquivo do estado atual do repositório não remove cópias já publicadas ou presentes no histórico.

## Outros tipos de correção

Erros de documentação e problemas de conteúdo sem implicações de segurança podem seguir o [guia de contribuição](CONTRIBUTING.md).

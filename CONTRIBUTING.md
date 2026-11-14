# Como contribuir com o Juriswany

Você pode contribuir com melhorias da skill, correções de documentação, fluxos jurídicos e manutenção do utilitário local.

## Prepare a contribuição

1. Leia o [README](README.md) e o [código de conduta](CODE_OF_CONDUCT.md).
2. Consulte as issues e os pull requests existentes para evitar propostas duplicadas.
3. Para uma mudança de escopo, abra uma issue e descreva o problema da rotina jurídica que deseja resolver.
4. Faça uma alteração com objetivo definido. Correções pequenas de texto podem seguir direto para um pull request.
5. Explique o que mudou e como você conferiu o resultado.

Não é necessário ser pessoa desenvolvedora para sugerir melhorias de conteúdo ou de fluxo de trabalho.

## Proteja os dados dos exemplos

Use dados fictícios ou exemplos anonimizados. Não envie documentos de clientes, credenciais, números de processos sigilosos ou informações que permitam identificar pessoas em casos reais.

Antes de anexar arquivos ou imagens, confira também metadados, comentários, histórico de revisão e texto oculto. Uma tarja visual pode deixar o texto original recuperável.

Se encontrar uma exposição de dados ou uma vulnerabilidade, siga a [política de segurança](SECURITY.md).

## Confira o conteúdo jurídico

Ao propor conteúdo sobre legislação ou jurisprudência:

- Informe a jurisdição, o contexto e a data da consulta.
- Inclua o link da fonte oficial e a identificação necessária para localizar a norma ou a decisão.
- Confira se a fonte sustenta a afirmação apresentada e se há alterações posteriores relevantes.
- Diferencie transcrição, resumo, interpretação e sugestão.
- Marque referências não confirmadas e explique o que falta verificar.
- Identifique exemplos hipotéticos como fictícios. Não os apresente como decisões reais.

Ao usar assistência de IA, revise o resultado e descreva no pull request qualquer limitação que afete a conferência. Quem envia a contribuição responde pela revisão do material enviado.

## Revise antes de abrir o pull request

- Escreva em português do Brasil, com linguagem direta e termos consistentes.
- Confira links, nomes de arquivos e a apresentação do Markdown.
- Descreva funcionalidades planejadas como planejadas. Não anuncie instalação, integrações ou testes que ainda não existam.
- Preserve a dedicatória e a grafia de Tawany Proença.
- Remova dados pessoais, segredos e arquivos locais sem relação com a mudança.
- Informe como verificou a alteração. Para documentação, a leitura e a conferência dos links podem ser suficientes.

Para alterações no utilitário local, execute os testes com Python 3.9 ou superior:

```sh
python3 -m unittest discover -s tests -v
```

Use destinos de instalação temporários e configure `XDG_CONFIG_HOME` e `XDG_CACHE_HOME` para diretórios temporários. Preserve suas instalações e preferências reais.

Para alterações nas instruções, experimente um pedido fictício com os recursos que a mudança declara suportar. Confira a entrega real. Em modo econômico, verifique que o agente não inventa delegação, pesquisa ou persistência.

Para mudanças de distribuição, confira o pedido natural de instalação ou atualização por URL. Preserve o canal e o destino escolhidos e a inspeção anterior à execução. Os testes de releases usam servidor HTTP em loopback e remotos Git locais. O [procedimento de publicação](docs/publicacao.md) orienta a criação de versões estáveis.

## Licença das contribuições

Ao enviar uma contribuição, você concorda em disponibilizá-la sob a [licença MIT](LICENSE) do projeto. Envie apenas material que você tenha autorização para compartilhar e respeite os direitos sobre conteúdo de terceiros.

## Revisão

O mantenedor revisa as contribuições e pode pedir ajustes antes de incorporá-las. Mudanças maiores devem explicar o benefício para a rotina jurídica e o trabalho necessário para mantê-las.

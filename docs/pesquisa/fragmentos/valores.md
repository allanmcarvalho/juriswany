# Valores, cálculos e informações específicas

Expor o que compõe um valor ou uma lista e permitir que o leitor confira cada entrada. Rascunhos editoriais para adaptação ao caso.

## Como escolher e redigir

Escolha a unidade de leitura conforme a questão. Um total isolado pode caber numa frase. Uma série mensal pede período, unidade e referência à memória. Um rol de pessoas precisa vincular cada indicação à finalidade admitida e aos dados que o procedimento exige. Distingua montante pedido, estimativa, saldo e valor atribuído à causa quando essas categorias forem pertinentes.

Confira os critérios aplicáveis antes de definir base, índice, juros, data de corte ou valor da causa. Indique as premissas e onde começam as divergências. Nos exemplos aritméticos, os valores são fictícios. A operação ilustra a apresentação da conta. Nenhum índice de atualização está pressuposto.

## Erros de composição

“Saldo de R$ 450,00” omite a data e as parcelas consideradas. Identifique a fatura de origem e as deduções, como em F73. Se houver atualização, discrimine o critério e a data de corte.

## Exemplos por situação

### F73 Composição simples de saldo

Uma única fatura tem dois pagamentos de chaves distintas. O recibo A destina integralmente R$ 300,00 a F1 e o recibo B destina integralmente R$ 150,00 à mesma fatura. São os únicos lançamentos considerados na data de corte.

> Da fatura F1, de R$ 900,00, deduzem-se R$ 300,00 do recibo A e R$ 150,00 do recibo B. Ambos identificam F1 no campo “fatura”. Em 30 de junho, o saldo nominal desses lançamentos é de R$ 450,00.

Se faltar a identificação da fatura em B e não houver outro registro de sua destinação, siga [F99](#f99-saldo-com-destinação-de-pagamento-em-aberto).

### F74 Estimativa com premissa identificada

O preço unitário está documentado, mas a quantidade ainda depende de conferência. Identifique a variável que mudará o total.

> Ao preço unitário de R$ 40,00, a estimativa para 12 unidades é de R$ 480,00. A quantidade foi informada por [origem]. A conferência depende do relatório de medição de [período].

### F75 Divergência de período

Dois demonstrativos apresentam valores mensais da mesma rubrica. Refaça os totais na janela comum antes de procurar a linha divergente.

> De março a junho, A soma R$ 430,00. Descontados os R$ 100,00 de março, A soma R$ 330,00 no período de abril a junho. No mesmo intervalo, B soma R$ 320,00. Abril e junho coincidem nos dois demonstrativos. Em maio, A registra R$ 110,00 e B, R$ 100,00. A linha de maio explica os R$ 10,00 de diferença no período comum.

Se B trouxer só o total, mantenha a diferença de R$ 10,00 e indique que as parcelas mensais de B são necessárias para localizar sua origem.

### F76 Apresentação de atualização

O critério e o intervalo já foram juridicamente conferidos. A planilha separa quantia original e resultado da atualização.

> A coluna [nome] traz os valores de origem em [datas]. A coluna [nome] aplica [critério e fundamento] até [data de corte]. Os fatores utilizados e sua fonte constam das linhas [referência].

### F77 Valor atribuído à causa

A base jurídica aplicável àquele pedido foi conferida. Explique de que parcela se partiu e como se chegou ao número.

> Atribui-se à causa o valor de [quantia], calculado a partir de [base] segundo [fundamento e critério conferidos]. A memória [referência] discrimina [parcelas ou elementos considerados].

### F78 Rol de pessoas em minuta de trabalho

A fase e a forma de indicação foram conferidas. Se o local de contato exigir tratamento reservado, examine o modo de apresentação.

> [Nome e qualificação exigida], com os dados de localização em [campo ou documento adequado], acompanhou [evento delimitado] no período [intervalo].

### F91 Dois valores atribuídos ao mesmo bem

Em levantamento sucessório, um imóvel aparece em documentos com valores diferentes. Indique a origem de cada número antes de discutir qual critério cabe ao caso.

> A ficha [referência] atribui ao imóvel [identificação suficiente] o valor de [quantia] em [data]. A avaliação [referência] apresenta [outra quantia] em [data posterior]. O quadro anexo mantém data e origem ao lado de cada valor.

### F99 Saldo com destinação de pagamento em aberto

A fatura F1 é de R$ 900,00. O recibo A registra R$ 300,00 destinados integralmente a F1. B e sua segunda via registram a mesma operação concluída de R$ 150,00, com a mesma chave. Nenhuma das vias de B identifica a fatura. O exercício considera os documentos disponíveis em 30 de junho.

> O recibo A identifica um pagamento de R$ 300,00 para F1. Considerado esse abatimento, restam R$ 600,00 dos R$ 900,00 da fatura. B e sua segunda via documentam um único pagamento de R$ 150,00. Se esse pagamento se destinar integralmente a F1 e não houver outros lançamentos, o saldo nominal será de R$ 450,00. Se houver rateio, o abatimento depende da parcela destinada a F1.

Compare primeiro os arquivos para identificar cada operação. Depois verifique a qual fatura e em que valor cada pagamento foi destinado. Se o registro de alocação destinar B integralmente a F2, conserve R$ 600,00 para F1 sob as mesmas premissas. Se destinar B integralmente a F1, aplique [F73](#f73-composição-simples-de-saldo). Se distribuir R$ 50,00 para F1 e R$ 100,00 para F2, substitua a conclusão condicional por “Dos R$ 150,00 de B, o registro de alocação destina R$ 50,00 a F1. Com esse abatimento, o saldo nominal de F1 passa de R$ 600,00 para R$ 550,00.” A simples presença de F1 no registro não define o valor a abater.

[Índice de fragmentos](../fragmentos.md)

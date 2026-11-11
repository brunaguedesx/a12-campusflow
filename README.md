A12 - OPERAÇÃO CAMPUSFLOW

Atividade prática de MongoDB Aula 14: Consultas Avançadas no MongoDB, feita com Python, PyMongo e MongoDB Atlas.

PREPARAÇÃO DO BANCO (seed.py)

O seed.py conecta no MongoDB Atlas, usa o banco campusflow_a12 e a collection solicitacoes, apaga o que já existir com delete_many({}) e insere 12 documentos com insert_many. Apagar antes de inserir evita duplicar os dados se o script for rodado mais de uma vez. No final ele cria o índice composto da atividade. Cada documento tem o protocolo, os dados do estudante (id, nome e curso), a categoria, a situação, a prioridade (de 1 a 5), a data de criação, as tags e a lista de atendimentos (setor, tipo e duração em minutos).

Saída:

12 documentos inseridos.


MISSÃO 1 - A FILA CRÍTICA

O que era pedido: localizar as solicitações ainda em aberto (ABERTA ou EM_ANALISE) com prioridade igual ou maior que 4, mostrando só alguns campos e ordenando por prioridade e data.

Como eu montei a consulta com find():

Filtro: usei $in para a situação (ABERTA ou EM_ANALISE) e $gte: 4 para a prioridade. As duas condições juntas funcionam como um “E”, então o documento precisa atender às duas.

Projeção: pedi só protocolo, estudante.nome, categoria.nome, situacao e prioridade, e tirei o _id com “_id”: 0. Para campos dentro de um objeto, usei a notação com ponto.

Ordenação: prioridade em ordem decrescente (-1) e, em caso de empate, criadoEm em ordem crescente (1). Assim, entre casos com a mesma prioridade, o mais antigo aparece primeiro.

Limite: não usei limit(), porque o enunciado diz que não existe quantidade fixa de resultados.

Resultado:

{‘protocolo’: ‘SOL-1011’, ‘estudante’: {‘nome’: ‘Isabela Torres’}, ‘categoria’: {‘nome’: ‘Trancamento de Disciplina’}, ‘situacao’: ‘ABERTA’, ‘prioridade’: 5}
{‘protocolo’: ‘SOL-1006’, ‘estudante’: {‘nome’: ‘Eduarda Rocha’}, ‘categoria’: {‘nome’: ‘Trancamento de Disciplina’}, ‘situacao’: ’EM_ANALISE’, ‘prioridade’: 5}
{‘protocolo’: ‘SOL-1001’, ‘estudante’: {‘nome’: ‘Ana Ribeiro’}, ‘categoria’: {‘nome’: ‘Aproveitamento de Disciplina’}, ‘situacao’: ’EM_ANALISE’, ‘prioridade’: 5}
{‘protocolo’: ‘SOL-1009’, ‘estudante’: {‘nome’: ‘Gabriela Moraes’}, ‘categoria’: {‘nome’: ‘Aproveitamento de Disciplina’}, ‘situacao’: ’EM_ANALISE’, ‘prioridade’: 4}

Interpretação: apareceram 4 solicitações: SOL-1011, SOL-1006, SOL-1001 e SOL-1009. As três primeiras têm prioridade 5 e estão ordenadas da mais antiga (29/10) para a mais recente (02/11). A SOL-1009 tem prioridade 4 e por isso vem depois. A SOL-1005 também tem prioridade 4, mas não entrou porque está como AGUARDANDO_DOCUMENTACAO, que não é ABERTA nem EM_ANALISE. Isso mostra que são poucos os casos graves: 4 de 12 solicitações (cerca de 33%).

MISSÃO 2 - ONDE ESTÁ O BACKLOG?

O que era pedido: contar, por categoria, quantas solicitações ainda não foram concluídas.

Como eu montei o pipeline:

match com {"situacao": {" ne”: “CONCLUIDA”}}: deixa passar só as solicitações pendentes. Coloquei no começo para os estágios seguintes trabalharem com menos documentos.
$group agrupando por categoria.nome, com {" sum”: 1} para contar quantas solicitações tem em cada categoria.
$sort por quantidade em ordem decrescente (-1), da maior para a menor.

Resultado:

{‘_id’: ‘Aproveitamento de Disciplina’, ‘quantidade’: 3}
{‘_id’: ‘Trancamento de Disciplina’, ‘quantidade’: 2}
{‘_id’: ‘Emissão de Declaração’, ‘quantidade’: 2}
{‘_id’: ‘Segunda Via de Boleto’, ‘quantidade’: 1}

Qual categoria possui o maior backlog?

Aproveitamento de Disciplina, com 3 solicitações não concluídas. No total existem 8 solicitações pendentes, então ela representa 37,5% do backlog. Em seguida vêm Trancamento de Disciplina (2), Emissão de Declaração (2) e Segunda Via de Boleto (1).

A categoria lidera, mas a diferença é pequena. Dizer que “Aproveitamento de Disciplina está acumulando tudo” é exagero: ela tem o maior backlog, porém os outros 5 casos pendentes estão espalhados em outras três categorias.

MISSÃO 3 - QUEM REALMENTE RECEBE MAIS TRABALHO?

O que era pedido: mudar a unidade de análise. Em vez de olhar para a solicitação, olhar para cada item da lista atendimentos, calculando por setor a quantidade de interações, o tempo médio e a maior duração.

Como eu montei o pipeline:

$unwind: "$atendimentos”: desmonta o array. Uma solicitação com 3 atendimentos vira 3 documentos no pipeline, cada um com um atendimento.
$group por $atendimentos.setor, com três acumuladores: $sum: 1 (interações), $avg sobre duracaoMin (tempo médio) e $max sobre duracaoMin (maior duração).
$sort por interacoes em ordem decrescente.

Ponto importante: depois do unwind, o {" sum”: 1} passa a contar atendimentos e não mais solicitações. A unidade de contagem muda quando o array é expandido, e é por isso que o total de interações (18) é maior que o total de solicitações (12).

Resultado:

{‘_id’: ‘SECRETARIA’, ‘interacoes’: 10, ‘tempoMedio’: 9.7, ‘maiorDuracao’: 14}
{‘_id’: ‘COORDENACAO’, ‘interacoes’: 5, ‘tempoMedio’: 47.0, ‘maiorDuracao’: 55}
{‘_id’: ‘FINANCEIRO’, ‘interacoes’: 3, ‘tempoMedio’: 7.333333333333333, ‘maiorDuracao’: 9}

A afirmação de que “o problema é a Secretaria” é sustentada pelos dados?

Só em parte. Usando dois indicadores:

Interações (volume): a Secretaria tem 10 das 18 interações, mais que o dobro da Coordenação (5) e mais que o triplo do Financeiro (3). Nesse indicador a afirmação se sustenta.

Tempo médio e maior duração: a Secretaria tem tempo médio de 9,7 min e maior duração de 14 min. A Coordenação tem tempo médio de 47 min e maior duração de 55 min, ou seja, cada atendimento dela leva cerca de 5 vezes mais tempo.

Para ver o peso total de cada setor, multipliquei interações por tempo médio: a Secretaria soma cerca de 97 minutos e a Coordenação cerca de 235 minutos, mesmo com metade das interações. O Financeiro soma cerca de 22 minutos.

Conclusão: a Secretaria recebe mais interações, mas são atendimentos rápidos (triagem, pendência). O gargalo de tempo está na Coordenação, onde ficam as análises mais demoradas. Então a opinião de que “o problema é a Secretaria” olha só para o volume e ignora o tempo.

MISSÃO 4 - HÁ ESTUDANTES RECORRENTES?

O que era pedido: descobrir os estudantes que têm mais de uma solicitação e manter os protocolos de cada um.

Como eu montei o pipeline:

$group por $estudante.id. Agrupei pelo id e não pelo nome porque o id identifica o estudante de forma única (dois alunos podem ter o mesmo nome). Dentro do grupo usei $first para guardar o nome, $sum: 1 para contar as solicitações e $push para juntar os protocolos em uma lista.
match com {"quantidade": {" gt”: 1}}: ficou depois do $group de propósito, porque a quantidade só existe depois que os documentos são agrupados.
$sort por quantidade em ordem decrescente.

Resultado:

{‘_id’: 101, ‘nome’: ‘Ana Ribeiro’, ‘quantidade’: 3, ‘protocolos’: [‘SOL-1001’, ‘SOL-1004’, ‘SOL-1012’]}
{‘_id’: 102, ‘nome’: ‘Bruno Lima’, ‘quantidade’: 2, ‘protocolos’: [‘SOL-1002’, ‘SOL-1008’]}

Existem indícios de concentração de solicitações em poucos estudantes?

Existem alguns indícios, mas são fracos. Ana Ribeiro (3 solicitações) e Bruno Lima (2) somam 5 das 12 solicitações, cerca de 42%. Os outros 7 estudantes têm só uma solicitação cada. Por outro lado, são apenas 2 recorrentes entre 9 estudantes, e o máximo por estudante é 3. Dá para dizer que existe uma leve concentração, mas os dados não sustentam que “poucos alunos abrindo várias solicitações” seja a causa principal do aumento do volume.

MISSÃO 5 - INDICADOR FINAL DO CAMPUSFLOW

O relatorio.py importa as funções do consultas.py, executa as consultas e imprime o relatório executivo com quatro seções: backlog por categoria, carga por setor, estudantes recorrentes e casos críticos (SOL-1011, SOL-1006, SOL-1001 e SOL-1009).

As conclusões são montadas dentro do código a partir dos resultados dos pipelines, então todas estão ligadas a uma consulta que foi executada.

Saída do relatório:

CAMPUSFLOW — RELATÓRIO OPERACIONAL

BACKLOG POR CATEGORIA
Aproveitamento de Disciplina: 3
Emissão de Declaração: 2
Trancamento de Disciplina: 2
Segunda Via de Boleto: 1

CARGA POR SETOR
SECRETARIA
Interações: 10
Tempo médio: 9.7 min
COORDENACAO
Interações: 5
Tempo médio: 47.0 min
FINANCEIRO
Interações: 3
Tempo médio: 7.3 min

ESTUDANTES RECORRENTES
Ana Ribeiro: 3 solicitações
Bruno Lima: 2 solicitações

CASOS CRÍTICOS
SOL-1011
SOL-1006
SOL-1001
SOL-1009

CONCLUSÕES

A categoria Aproveitamento de Disciplina concentra o maior backlog, com 3 solicitações não concluídas.
O setor SECRETARIA tem mais interações (10), mas o setor COORDENACAO tem o maior tempo médio de atendimento (47.0 min).
O estudante Ana Ribeiro aparece em 3 solicitações (SOL-1001, SOL-1004, SOL-1012), sendo o mais recorrente.

Origem de cada conclusão: a 1 vem da Missão 2, a 2 vem da Missão 3 e a 3 vem da Missão 4.

Sobre as quatro opiniões da coordenação:

“O problema é a Secretaria”: parcialmente verdadeira. Tem mais interações, mas o tempo está na Coordenação.

“Aproveitamento de Disciplina acumula tudo”: exagero. Lidera com 3 de 8 pendentes, mas não concentra tudo.

“Poucos alunos abrem várias solicitações”: evidência fraca. Só 2 recorrentes, com 3 e 2 solicitações.

“Só há poucas de prioridade alta”: 4 de 12 solicitações são críticas (cerca de 33%).

REQUISITO ADICIONAL - ÍNDICE

O índice criado no seed.py é composto: situacao em ordem crescente e prioridade em ordem decrescente.

A consulta que mais se beneficia dele é a da Missão 1, porque o find() filtra exatamente por situacao e prioridade ao mesmo tempo, e o índice já está na mesma ordem da consulta. Sem o índice, o MongoDB precisa ler todos os documentos da collection para ver quais atendem ao filtro. Com ele, vai direto aos documentos certos, e isso faz bastante diferença quando a collection tem milhões de registros.
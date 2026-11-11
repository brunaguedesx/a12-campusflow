from pymongo import MongoClient

URI_ATLAS = "mongodb+srv://brunaguedesx02_db_user:n9EcJjPRCiZ1k12q@cluster0.qt05aqa.mongodb.net/"


client = MongoClient(URI_ATLAS)
solicitacoes = client["campusflow_a12"]["solicitacoes"]


# Missão 1: a fila crítica
def fila_critica():
    return list(
        solicitacoes.find(
            {
                "situacao": {"$in": ["ABERTA", "EM_ANALISE"]},
                "prioridade": {"$gte": 4}
            },
            {
                "_id": 0,
                "protocolo": 1,
                "estudante.nome": 1,
                "categoria.nome": 1,
                "situacao": 1,
                "prioridade": 1
            }
        ).sort([
            ("prioridade", -1),
            ("criadoEm", 1)
        ])
    )


# Missão 2: onde está o backlog
def backlog_por_categoria():
    pipeline = [
        {"$match": {"situacao": {"$ne": "CONCLUIDA"}}},
        {"$group": {
            "_id": "$categoria.nome",
            "quantidade": {"$sum": 1}
        }},
        {"$sort": {"quantidade": -1}}
    ]
    return list(solicitacoes.aggregate(pipeline))


# Missão 3: quem realmente recebe mais trabalho
def carga_por_setor():
    pipeline = [
        {"$unwind": "$atendimentos"},
        {"$group": {
            "_id": "$atendimentos.setor",
            "interacoes": {"$sum": 1},
            "tempoMedio": {"$avg": "$atendimentos.duracaoMin"},
            "maiorDuracao": {"$max": "$atendimentos.duracaoMin"}
        }},
        {"$sort": {"interacoes": -1}}
    ]
    return list(solicitacoes.aggregate(pipeline))


# Missão 4: estudantes recorrentes
def estudantes_recorrentes():
    pipeline = [
        {"$group": {
            "_id": "$estudante.id",
            "nome": {"$first": "$estudante.nome"},
            "quantidade": {"$sum": 1},
            "protocolos": {"$push": "$protocolo"}
        }},
        {"$match": {"quantidade": {"$gt": 1}}},
        {"$sort": {"quantidade": -1}}
    ]
    return list(solicitacoes.aggregate(pipeline))


if __name__ == "__main__":
    print("MISSÃO 1: FILA CRÍTICA")
    for doc in fila_critica():
        print(doc)

    print("\nMISSÃO 2: BACKLOG POR CATEGORIA")
    for doc in backlog_por_categoria():
        print(doc)

    print("\nMISSÃO 3: CARGA POR SETOR")
    for doc in carga_por_setor():
        print(doc)

    print("\nMISSÃO 4: ESTUDANTES RECORRENTES")
    for doc in estudantes_recorrentes():
        print(doc)
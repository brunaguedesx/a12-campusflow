from consultas import (
    fila_critica,
    backlog_por_categoria,
    carga_por_setor,
    estudantes_recorrentes
)

backlog = backlog_por_categoria()
setores = carga_por_setor()
recorrentes = estudantes_recorrentes()
criticos = fila_critica()

print("=" * 40)
print("CAMPUSFLOW — RELATÓRIO OPERACIONAL")
print("=" * 40)

print("\nBACKLOG POR CATEGORIA")
for item in backlog:
    print(f"{item['_id']}: {item['quantidade']}")

print("\nCARGA POR SETOR")
for item in setores:
    print(item["_id"])
    print(f"  Interações: {item['interacoes']}")
    print(f"  Tempo médio: {item['tempoMedio']:.1f} min")

print("\nESTUDANTES RECORRENTES")
for item in recorrentes:
    print(f"{item['nome']}: {item['quantidade']} solicitações")

print("\nCASOS CRÍTICOS")
for item in criticos:
    print(item["protocolo"])

print("\n" + "=" * 40)

# Conclusões calculadas a partir dos resultados acima
setor_mais_interacoes = setores[0]
setor_maior_tempo = max(setores, key=lambda s: s["tempoMedio"])

print("CONCLUSÕES")
print(
    f"1. A categoria {backlog[0]['_id']} concentra o maior backlog, "
    f"com {backlog[0]['quantidade']} solicitações não concluídas."
)
print(
    f"2. O setor {setor_mais_interacoes['_id']} tem mais interações "
    f"({setor_mais_interacoes['interacoes']}), mas o setor "
    f"{setor_maior_tempo['_id']} tem o maior tempo médio de atendimento "
    f"({setor_maior_tempo['tempoMedio']:.1f} min)."
)
print(
    f"3. O estudante {recorrentes[0]['nome']} aparece em "
    f"{recorrentes[0]['quantidade']} solicitações "
    f"({', '.join(recorrentes[0]['protocolos'])}), "
    f"sendo o mais recorrente."
)
print("=" * 40)
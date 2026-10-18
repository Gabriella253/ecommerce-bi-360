from pathlib import Path
import pandas as pd

# ==========================================
# 1. CARREGAMENTO DOS DADOS
# ==========================================

diretorio = Path(__file__).resolve().parent.parent

arquivo = diretorio / "data" / "processed" / "base_consolidada.csv"

dados = pd.read_csv(arquivo)

print("Base consolidada carregada!")
print(f"Quantidade de registros: {len(dados)}")


# ==========================================
# 2. INDICADORES POR ESTADO
# ==========================================

indicadores = (
    dados.groupby("customer_state", as_index=False)
    .agg(
        quantidade_pedidos=("order_id", "nunique"),
        pedidos_com_pagamento=("valor_total_pagamentos", "count"),
        total_pagamentos=("valor_total_pagamentos", "sum")
    )
)


# ==========================================
# 3. TICKET MÉDIO
# ==========================================

indicadores["ticket_medio"] = (
    indicadores["total_pagamentos"]
    / indicadores["pedidos_com_pagamento"]
)


# ==========================================
# 4. ORDENAÇÃO DOS RESULTADOS
# ==========================================

indicadores = indicadores.sort_values(
    "total_pagamentos",
    ascending=False
)

print("\nINDICADORES POR ESTADO:")

print(indicadores.round(2).to_string(index=False))


# ==========================================
# 5. VALIDAÇÃO DOS RESULTADOS
# ==========================================

total_original = dados["valor_total_pagamentos"].sum()

total_agrupado = indicadores["total_pagamentos"].sum()

print("\nVALIDAÇÃO FINANCEIRA:")

print(f"Total original: R$ {total_original:.2f}")
print(f"Total agrupado: R$ {total_agrupado:.2f}")

if abs(total_original - total_agrupado) < 0.01:
    print("Validação financeira concluída!")
else:
    raise ValueError("Divergência nos valores financeiros!")


# ==========================================
# 6. EXPORTAÇÃO
# ==========================================

saida = diretorio / "data" / "processed"

saida.mkdir(parents=True, exist_ok=True)

indicadores.to_csv(
    saida / "indicadores_por_estado.csv",
    index=False
)

print("\nIndicadores exportados com sucesso!")
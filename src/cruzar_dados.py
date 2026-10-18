from pathlib import Path
import pandas as pd

# Localizar a pasta principal do projeto
diretorio = Path(__file__).resolve().parent.parent

# Carregar a tabela de pedidos tratados
pedidos = pd.read_csv(
    diretorio / "data" / "processed" / "pedidos_tratados.csv"
)

# Carregar a tabela de clientes
clientes = pd.read_csv(
    diretorio / "data" / "raw" / "olist_customers_dataset.csv"
)

# Cruzar as duas tabelas
dados_completos = pedidos.merge(
    clientes,
    on="customer_id",
    how="left",
    validate="many_to_one",
    indicator=True
)

print(dados_completos["_merge"].value_counts())

dados_completos = pedidos.merge(
    clientes,
    on="customer_id",
    how="left",
    validate="many_to_one",
    indicator=True
)

print("\nResultado do cruzamento:")

print(
    dados_completos[
        ["order_id", "customer_id", "customer_city", "customer_state"]
    ].head()
)

print("\nValidação do cruzamento:")

print(dados_completos["_merge"].value_counts())

print("\nRegistros antes do cruzamento:", len(pedidos))

print("Registros depois do cruzamento:", len(dados_completos))

pedidos_por_estado = (
    dados_completos
    .groupby("customer_state")["order_id"]
    .nunique()
    .sort_values(ascending=False)
)

print("\nQuantidade de pedidos por estado:")
print(pedidos_por_estado)

print("\nTotal de pedidos contabilizados:")
print(pedidos_por_estado.sum())

# Carregando a base de pagamentos
pagamentos = pd.read_csv(
    diretorio / "data" / "raw" / "olist_order_payments_dataset.csv"
)

print("\nQuantidade de registros de pagamentos:")
print(len(pagamentos))

print("\nQuantidade de pedidos distintos com pagamento:")
print(pagamentos["order_id"].nunique())

print("\nPedidos com mais registros de pagamento:")
print(pagamentos["order_id"].value_counts().head())

print("\nQuantidade de pedidos com múltiplos pagamentos:")
print((pagamentos["order_id"].value_counts() > 1).sum())

pagamentos_agrupados = pagamentos.groupby(
    "order_id", as_index=False
).agg(
    valor_total_pagamentos=("payment_value", "sum"),
    quantidade_pagamentos=("payment_value", "size")
)

print("\nPagamentos agrupados por pedido:")
print(pagamentos_agrupados.head())

print("\nQuantidade de pedidos após agrupamento:")
print(len(pagamentos_agrupados))

base_financeira = dados_completos.merge(
    pagamentos_agrupados,
    on="order_id",
    how="left",
    validate="one_to_one",
    indicator="origem_pagamento"
)

print("\nResultado do cruzamento financeiro:")
print(base_financeira["origem_pagamento"].value_counts())

print("\nQuantidade de registros após cruzamento:")
print(len(base_financeira))

print("\nValor total antes do cruzamento:")
print(pagamentos["payment_value"].sum().round(2))

print("\nValor total depois do cruzamento:")
print(base_financeira["valor_total_pagamentos"].sum().round(2))

print("\nPedidos sem pagamento correspondente:")
print(
    base_financeira[
        base_financeira["origem_pagamento"] == "left_only"
    ][["order_id", "order_status"]]
)

# ==========================================
# ANÁLISE FINANCEIRA POR ESTADO
# ==========================================

pagamentos_por_estado = (
    base_financeira
    .groupby("customer_state", as_index=False)
    .agg(
        quantidade_pedidos=("order_id", "nunique"),
        pedidos_com_pagamento=("valor_total_pagamentos", "count"),
        total_pagamentos=("valor_total_pagamentos", "sum")
    )
    .sort_values("total_pagamentos", ascending=False)
)

print("\nTOP 10 ESTADOS POR VALOR DE PAGAMENTOS:")

print(
    pagamentos_por_estado.head(10).to_string(index=False)
)

# Validando o total financeiro
print("\nTotal de pagamentos por estado:")

print(
    round(pagamentos_por_estado["total_pagamentos"].sum(), 2)
)

# ==========================================
# CÁLCULO DO TICKET MÉDIO
# ==========================================

pagamentos_por_estado["ticket_medio"] = (
    pagamentos_por_estado["total_pagamentos"]
    / pagamentos_por_estado["pedidos_com_pagamento"]
)

print("\nTICKET MÉDIO POR ESTADO:")

print(
    pagamentos_por_estado[
        [
            "customer_state",
            "quantidade_pedidos",
            "total_pagamentos",
            "ticket_medio"
        ]
    ].round(2).to_string(index=False)
)

# Diretório de saída
saida = diretorio / "data" / "processed"

saida.mkdir(parents=True, exist_ok=True)

# Arquivo consolidado
arquivo_saida = saida / "base_consolidada.csv"

# Exportação
base_financeira.to_csv(
    arquivo_saida,
    index=False
)

print("\nBase consolidada exportada com sucesso!")
from pathlib import Path
import pandas as pd


# ==================================================
# 1. CARREGAMENTO DOS DADOS
# ==================================================

diretorio_projeto = Path(__file__).resolve().parent.parent

arquivo = (
    diretorio_projeto
    / "data"
    / "raw"
    / "olist_orders_dataset.csv"
)

pedidos = pd.read_csv(arquivo)

print("\nBase carregada com sucesso!")
print(f"Quantidade de registros: {len(pedidos)}")


# ==================================================
# 2. VERIFICAÇÃO DE VALORES AUSENTES
# ==================================================

print("\nValores ausentes antes do tratamento:")
print(pedidos.isna().sum())


# ==================================================
# 3. CONVERSÃO DAS DATAS
# ==================================================

colunas_datas = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date"
]

# Guardando a quantidade de valores ausentes
nulos_antes = pedidos[colunas_datas].isna().sum()

# Convertendo textos para datetime
for coluna in colunas_datas:
    pedidos[coluna] = pd.to_datetime(
        pedidos[coluna],
        format="%Y-%m-%d %H:%M:%S",
        errors="coerce"
    )

# Verificando possíveis falhas de conversão
nulos_depois = pedidos[colunas_datas].isna().sum()

print("\nNovos valores ausentes após conversão:")
print(nulos_depois - nulos_antes)


# ==================================================
# 4. VERIFICAÇÃO DE DUPLICAÇÕES
# ==================================================

linhas_duplicadas = pedidos.duplicated().sum()

ids_duplicados = pedidos["order_id"].duplicated().sum()

print("\nLinhas duplicadas:", linhas_duplicadas)
print("IDs duplicados:", ids_duplicados)


# ==================================================
# 5. IDENTIFICAÇÃO DE INCONSISTÊNCIAS
# ==================================================

# Pedido entregue sem data de entrega
pedidos["inconsistencia_entrega"] = (
    (pedidos["order_status"] == "delivered")
    &
    (pedidos["order_delivered_customer_date"].isna())
)

# Pedido com data de entrega, mas status diferente
pedidos["verificar_status_entrega"] = (
    (pedidos["order_status"] != "delivered")
    &
    (pedidos["order_delivered_customer_date"].notna())
)

print("\nPedidos entregues sem data:")
print(pedidos["inconsistencia_entrega"].value_counts())

print("\nPedidos com data de entrega e outro status:")
print(pedidos["verificar_status_entrega"].value_counts())


# ==================================================
# 6. CÁLCULO DO TEMPO DE ENTREGA
# ==================================================

pedidos["tempo_entrega_dias"] = (
    pedidos["order_delivered_customer_date"]
    -
    pedidos["order_purchase_timestamp"]
).dt.total_seconds() / 86400

print("\nPrimeiros tempos de entrega:")
print(
    pedidos[
        ["order_id", "tempo_entrega_dias"]
    ].head()
)


# ==================================================
# 7. VALIDAÇÃO DOS TEMPOS DE ENTREGA
# ==================================================

# Identificando tempos negativos
pedidos["tempo_entrega_negativo"] = (
    pedidos["tempo_entrega_dias"] < 0
)

print("\nTempos de entrega negativos:")
print(pedidos["tempo_entrega_negativo"].sum())


# ==================================================
# 8. SELEÇÃO DAS ENTREGAS VÁLIDAS
# ==================================================

# Apenas pedidos entregues com datas válidas
mascara_entregas_validas = (
    (pedidos["order_status"] == "delivered")
    &
    (pedidos["tempo_entrega_dias"].notna())
    &
    (pedidos["tempo_entrega_dias"] >= 0)
    &
    (pedidos["order_estimated_delivery_date"].notna())
)

entregas_validas = pedidos.loc[
    mascara_entregas_validas
].copy()

print("\nQuantidade de entregas válidas:")
print(len(entregas_validas))


# ==================================================
# 9. ESTATÍSTICAS DOS TEMPOS DE ENTREGA
# ==================================================

print("\nEstatísticas dos tempos de entrega:")

print(
    entregas_validas["tempo_entrega_dias"]
    .describe()
    .round(2)
)

print("\nCinco maiores tempos de entrega:")

print(
    entregas_validas.nlargest(
        5, "tempo_entrega_dias"
    )[["order_id", "tempo_entrega_dias"]]
)


# ==================================================
# 10. IDENTIFICAÇÃO DE ENTREGAS ATRASADAS
# ==================================================

# Inicialmente, não sabemos se houve atraso
pedidos["entrega_atrasada"] = pd.Series(
    pd.NA,
    index=pedidos.index,
    dtype="boolean"
)

# Comparando as datas, sem considerar as horas
data_real = pedidos.loc[
    mascara_entregas_validas,
    "order_delivered_customer_date"
].dt.normalize()

data_prevista = pedidos.loc[
    mascara_entregas_validas,
    "order_estimated_delivery_date"
].dt.normalize()

pedidos.loc[
    mascara_entregas_validas,
    "entrega_atrasada"
] = data_real > data_prevista


# ==================================================
# 11. INDICADORES GERENCIAIS
# ==================================================

entregas_analisadas = pedidos.loc[
    mascara_entregas_validas
]

tempo_medio = entregas_analisadas[
    "tempo_entrega_dias"
].mean()

tempo_mediano = entregas_analisadas[
    "tempo_entrega_dias"
].median()

percentual_atrasos = (
    entregas_analisadas["entrega_atrasada"].mean()
    * 100
)

print("\nINDICADORES OPERACIONAIS")

print(f"Tempo médio de entrega: {tempo_medio:.2f} dias")

print(f"Tempo mediano de entrega: {tempo_mediano:.2f} dias")

print(f"Percentual de entregas atrasadas: {percentual_atrasos:.2f}%")


# ==================================================
# 12. EXPORTAÇÃO DOS DADOS TRATADOS
# ==================================================

diretorio_saida = diretorio_projeto / "data" / "processed"

diretorio_saida.mkdir(
    parents=True,
    exist_ok=True
)

arquivo_saida = (
    diretorio_saida
    / "pedidos_tratados.csv"
)

pedidos.to_csv(
    arquivo_saida,
    index=False
)

print("\nArquivo tratado exportado com sucesso!")
print(arquivo_saida)
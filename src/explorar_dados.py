from pathlib import Path
import pandas as pd

#Caminho para nossa base
arquivo = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "raw"
    / "olist_orders_dataset.csv"
)

#Carregando os dados
pedidos = pd.read_csv(arquivo)

#Exibindo os primeiros registros
print(pedidos.head())

#Verificando o tamanho
print("\nQuantidade de linhas e colunas:")
print(pedidos.shape)

#Identificando colunas e tipos
print("\nInformações da base:")
print(pedidos.info())

#Identificando valores ausentes
print("\nValores ausentes por coluna:")
print(pedidos.isnull().sum())

#Identificando quantidade de linhas duplicadas
print("\nQuantidade de linhas duplicadas: ")
print(pedidos.duplicated().sum())

#Investigando status dos pedidos
print("\nStatus dos pedidos:")
print(pedidos["order_status"].value_counts())

#Pedidos sem data de entrega
sem_entrega = pedidos[
    pedidos["order_delivered_customer_date"].isna()
]

print("\nStatus dos pedidos sem data de entrega:")
print(sem_entrega["order_status"].value_counts())

#Identificadores duplicados
print("\nIdentificadores duplicados:")
print(pedidos["order_id"].duplicated().sum())

#Investigando os pedidos sem data de entrega que foram entregues:
#pedidos inconsistentes, não vão participar do cálculo de entrega
entregues_sem_data = pedidos[
    (pedidos["order_status"] == "delivered") &
    (pedidos["order_delivered_customer_date"].isna())
]

print("\nPedidos entregues sem data registrada:")
print(entregues_sem_data)

print("\nInvestigação dos 8 pedidos:")

colunas = [
    "order_id",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date"
]

print(entregues_sem_data[colunas].to_string(index=False))
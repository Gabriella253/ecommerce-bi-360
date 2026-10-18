from pathlib import Path
import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, Numeric
from sqlalchemy.engine import URL

# Localizar o projeto
diretorio = Path(__file__).resolve().parent.parent

# Carregar configurações
load_dotenv(diretorio / ".env")

# Configurar conexão
url = URL.create(
    drivername="postgresql+psycopg",
    username=os.getenv("PGUSER"),
    password=os.getenv("PGPASSWORD"),
    host=os.getenv("PGHOST"),
    port=int(os.getenv("PGPORT", "5432")),
    database=os.getenv("PGDATABASE")
)

engine = create_engine(url)

# Carregar arquivos CSV
base = pd.read_csv(
    diretorio / "data" / "processed" / "base_consolidada.csv",
    parse_dates=[
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date"
    ]
)

indicadores = pd.read_csv(
    diretorio / "data" / "processed" / "indicadores_por_estado.csv"
)

print("Arquivos carregados!")

# Validar dados
if base["order_id"].duplicated().any():
    raise ValueError("Existem pedidos duplicados!")

if base["customer_state"].isna().any():
    raise ValueError("Existem pedidos sem estado!")

# Enviar dados ao PostgreSQL
with engine.begin() as conexao:

    base.to_sql(
        "pedidos_consolidados",
        con=conexao,
        schema="analytics",
        if_exists="replace",
        index=False,
        chunksize=2000,
        dtype={
            "valor_total_pagamentos": Numeric(14, 2)
        }
    )

    print("Pedidos enviados ao PostgreSQL!")

    indicadores.to_sql(
        "indicadores_estado",
        con=conexao,
        schema="analytics",
        if_exists="replace",
        index=False,
        dtype={
            "total_pagamentos": Numeric(14, 2),
            "ticket_medio": Numeric(14, 2)
        }
    )

    print("Indicadores enviados ao PostgreSQL!")

engine.dispose()

print("Carregamento concluído com sucesso!")
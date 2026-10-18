from pathlib import Path
import os
import psycopg
from dotenv import load_dotenv

# Configurações do projeto
diretorio = Path(__file__).resolve().parent.parent
load_dotenv(diretorio / ".env")

# Conexão com PostgreSQL
with psycopg.connect(
    host=os.getenv("PGHOST"),
    port=os.getenv("PGPORT"),
    dbname=os.getenv("PGDATABASE"),
    user=os.getenv("PGUSER"),
    password=os.getenv("PGPASSWORD")
) as conexao:

    with conexao.cursor() as cursor:

        # Verificar quantidade de pedidos e pagamentos
        cursor.execute("""
            SELECT
                COUNT(*) AS quantidade_pedidos,
                SUM(valor_total_pagamentos) AS total_pagamentos
            FROM analytics.pedidos_consolidados;
        """)

        resultado = cursor.fetchone()

        print("\nVALIDAÇÃO DO POSTGRESQL")
        print("Pedidos:", resultado[0])
        print("Total de pagamentos: R$", resultado[1])

        # Verificar indicadores por estado
        cursor.execute("""
            SELECT
                COUNT(*)
            FROM analytics.indicadores_estado;
        """)

        estados = cursor.fetchone()[0]

        print("Estados cadastrados:", estados)
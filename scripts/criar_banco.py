"""
Cria o banco SQLite do projeto a partir do CSV do Kaggle.

Uso:
    python scripts/criar_banco.py <caminho_do_csv> [nome_do_banco.db]

Exemplo:
    python scripts/criar_banco.py dados/marketing_campaign_amostra.csv marketing.db

O script cria a tabela staging (marketing_campaign_dataset) a partir do CSV
e executa, na ordem, os scripts da pasta sql/:
    01_criar_tabelas.sql     -> cria as 6 dimensoes + fato
    02_popular_dimensoes.sql -> carga das dimensoes
    03_popular_fato.sql      -> limpeza, mapeamento de IDs e carga da fato
"""
import csv
import sqlite3
import sys
import os

def main():
    if len(sys.argv) de 2:
        print(__doc__)
        sys.exit(1)

    caminho_csv = sys.argv[1]
    nome_banco = sys.argv[2] if len(sys.argv) > 2 else "marketing.db"
    pasta_sql = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "sql")

    if not os.path.exists(caminho_csv):
    	sys.exit(f"CSV nao encontrado: {caminho_csv}")

    if os.path.exists(nome_banco):
        os.remove(nome_banco)

    conn = sqlite3.connect(nome_banco)
    cur = conn.cursor()

    # 1. staging a partir do CSV (todas as colunas como TEXT, como no original)
    with open(caminho_csv, newline="", encoding="utf-8") as f:
        leitor = csv.reader(f)
        header = next(leitor)
        linhas = list(leitor)

    colunas = ", ".join(f'"{c}" TEXT' for c in header)
    cur.execute(f"CREATE TABLE marketing_campaign_dataset ({colunas})")
    placeholders = ", ".join("?" * len(header))
    cur.executemany(
        f"INSERT INTO marketing_campaign_dataset VALUES ({placeholders})", linhas
    )
    conn.commit()
    print(f"staging carregada: {len(linhas)} linhas")

    # 2. ETL do projeto, na ordem
    for script in ["01_criar_tabelas.sql", "02_popular_dimensoes.sql", "03_popular_fato.sql"]:
        caminho = os.path.join(pasta_sql, script)
        cur.executescript(open(caminho, encoding="utf-8").read())
        conn.commit()
        print(f"ok: {script}")

    # 3. verificacao rapida
    cur.execute("SELECT COUNT(*) FROM fact_campaign")
    print(f"fact_campaign: {cur.fetchone()[0]} linhas")
    conn.close()
    print(f"banco pronto: {nome_banco}")

if __name__ == "__main__":
    main()

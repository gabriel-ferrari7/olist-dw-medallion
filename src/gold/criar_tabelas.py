import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()

conexao = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
)

cursor = conexao.cursor()

with open("sql/criar_tabelas.sql", encoding="utf-8") as arquivo:
    cursor.execute(arquivo.read())

conexao.commit()

cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name")
for linha in cursor.fetchall():
    print(linha[0])

cursor.close()
conexao.close()
import json
import psycopg2
from dotenv import load_dotenv
import os

# Carrega as variáveis de ambiente do .env (caso esteja usando)
load_dotenv()

# Conexão com o PostgreSQL
DB_URL = os.getenv("DB_URL")

def conectar_bd():
    """Conecta ao PostgreSQL"""
    try:
        conn = psycopg2.connect(DB_URL)
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao banco: {e}")
        return None

def importar_json_para_bd():
    """Importa os dados do solicitacoes.json para o PostgreSQL"""
    conn = conectar_bd()
    if conn:
        cursor = conn.cursor()

        # Abre o arquivo JSON
        with open("solicitacoes.json", "r", encoding="utf-8") as file:
            solicitacoes = json.load(file)

        # Insere os dados no banco
        for solic in solicitacoes:
            cursor.execute("""
                INSERT INTO solicitacoes (nome, equipe, funcao, frota, matricula, tipo, descricao, quantidade, codigo_sap)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (solic["Nome"], solic["Equipe (BTF)"], solic["Função"], solic["Frota"], solic["Matrícula"], solic["Tipo"], solic["Descrição"], solic["Quantidade"], solic["Código SAP"]))

        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Dados importados para o PostgreSQL!")

# Rodar essa função para importar os dados
importar_json_para_bd()


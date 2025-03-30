import json
import os
from supabase import create_client
from dotenv import load_dotenv
from datetime import datetime, timedelta
from random import choice

# === Setup Supabase
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# === Carregar JSON
with open("solicitacoes.json", encoding="utf-8") as f:
    solicitacoes = json.load(f)

# === Loop de envio
for s in solicitacoes:
    nome = s["Nome"].strip().title()
    matricula = str(int(float(s["Matrícula"])))
    funcao = s["Função"].strip().title()
    equipe = s["Equipe (BTF)"].strip().upper()
    frota = s["Frota"].strip().title()

    tipo = ", ".join([t.strip().title() for t in s["Tipo"].split(",")])
    descricao = ", ".join([d.strip().capitalize() for d in s["Descrição"].split(",")])
    quantidade = ", ".join([q.strip() for q in s["Quantidade"].split(",")])
    codigo_sap = ", ".join([c.strip() for c in s["Código SAP"].split(",")])

    # Simular datas aleatórias entre hoje e até 4 semanas atrás
    dias_atras = choice([0, 7, 14, 21, 28])
    data_fake = datetime.now() - timedelta(days=dias_atras)

    # Semana baseada na data falsa
    ano, semana_num, _ = data_fake.isocalendar()
    semana = f"{ano}-W{semana_num:02d}"

    # Buscar ID do motorista
    motorista_res = supabase.table("motoristas").select("id").eq("matricula", matricula).execute()
    motorista_data = motorista_res.data
    if not motorista_data:
        print(f"❌ Motorista não encontrado: {nome} - matrícula {matricula}")
        continue
    motorista_id = motorista_data[0]["id"]

    # Verificar se já existe solicitação do motorista nesta semana
    existing = supabase.table("solicitacoes").select("id").eq("matricula", matricula).eq("semana", semana).execute()
    if existing.data:
        print(f"🔁 Já existe solicitação para {matricula} na semana {semana}, pulando.")
        continue

    # Inserir nova solicitação
    data = {
        "nome": nome,
        "matricula": matricula,
        "funcao": funcao,
        "equipe": equipe,
        "frota": frota,
        "tipo": tipo,
        "descricao": descricao,
        "codigo_sap": codigo_sap,
        "quantidade": quantidade,
        "data_solicitacao": data_fake.isoformat(),
        "semana": semana,
        "motorista_id": motorista_id,
        "epi_id": None
    }

    supabase.table("solicitacoes").insert(data).execute()
    print(f"✅ Solicitação registrada para {nome} ({matricula}) - Semana {semana}")

print("🏁 Importação finalizada.")

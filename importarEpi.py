import json
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# === EPIs ===
with open("epis.json", encoding="utf-8") as f:
    epis = json.load(f)

for epi in epis:
    tipo = epi.get("TIPO", "").strip().title()
    descricao = epi.get("DESCRIÇÃO", "").strip().capitalize()
    quantidade = int(epi.get("quantidades permitidas", 0))

    cod_sap_raw = epi.get("COD SAP")
    if cod_sap_raw is None:
        print(f"⚠️ Pulando EPI sem COD SAP: {descricao}")
        continue  # ou defina um valor padrão: cod_sap = 0

    cod_sap = int(cod_sap_raw)

    supabase.table("epis").insert({
        "tipo": tipo,
        "descricao": descricao,
        "cod_sap": cod_sap,
        "quantidade_permitida": quantidade
    }).execute()


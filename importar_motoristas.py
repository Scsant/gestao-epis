import json
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# === MOTORISTAS ===
with open("motorista.json", encoding="utf-8") as f:
    motoristas = json.load(f)

# Inserir ou atualizar motoristas com frota, equipe e função
for m in motoristas:
    nome = m["Nome"].strip().title()
    matricula = str(int(float(m["Matrícula"])))
    frota = m.get("Frota", "").strip().title()
    equipe = m.get("Equipe", "").strip().upper()
    funcao = m.get("Função", "").strip().title()

    supabase.table("motoristas").upsert({
        "nome": nome,
        "matricula": matricula,
        "frota": frota,
        "equipe": equipe,
        "funcao": funcao
    }, on_conflict=["matricula"]).execute()

print("✅ Motoristas enviados (com upsert).")

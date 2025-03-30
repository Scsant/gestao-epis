from supabase import create_client
from dotenv import load_dotenv
import os
import pandas as pd
from datetime import datetime, timedelta

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def carregar_motoristas():
    res = supabase.table("motoristas").select("*").execute()
    return pd.DataFrame(res.data)

def carregar_epis():
    res = supabase.table("epis").select("*").execute()
    return pd.DataFrame(res.data)

def carregar_solicitacoes():
    res = supabase.table("solicitacoes").select("*").order("data_solicitacao", desc=True).execute()
    return pd.DataFrame(res.data)

def ja_solicitou_na_semana(matricula):
    hoje = datetime.now()

    # Calcular o último domingo 00:00
    dias_para_domingo = (hoje.weekday() + 1) % 7
    domingo = hoje - timedelta(days=dias_para_domingo)
    domingo = domingo.replace(hour=0, minute=0, second=0, microsecond=0)

    res = supabase.table("solicitacoes") \
        .select("id") \
        .eq("matricula", str(matricula)) \
        .gte("data_solicitacao", domingo.isoformat()) \
        .execute()

    return len(res.data) > 0

def inserir_historico_unico(supabase, registro: dict):
    """
    Insere no histórico apenas se não existir já um registro com os mesmos dados-chave.
    """
    existe = supabase.table("historico_solicitacoes") \
        .select("id") \
        .eq("matricula", registro["matricula"]) \
        .eq("tipo", registro["tipo"]) \
        .eq("descricao", registro["descricao"]) \
        .eq("quantidade", registro["quantidade"]) \
        .eq("semana", registro["semana"]) \
        .execute()

    if not existe.data:
        supabase.table("historico_solicitacoes").insert(registro).execute()
        return True
    else:
        return False


def inserir_solicitacao(matricula, epi_id, quantidade):
    motorista = (
        supabase.table("motoristas")
        .select("id, nome, matricula, funcao, equipe, frota")
        .eq("matricula", str(matricula))
        .single()
        .execute()
    )
    motorista_data = motorista.data

    epi = (
        supabase.table("epis")
        .select("descricao, tipo, cod_sap")
        .eq("id", str(epi_id))
        .single()
        .execute()
    )
    epi_data = epi.data

    supabase.table("solicitacoes").insert({
        "motorista_id": motorista_data["id"],
        "epi_id": epi_id,
        "quantidade": int(quantidade),
        "nome": motorista_data["nome"],
        "matricula": str(motorista_data["matricula"]),
        "funcao": motorista_data.get("funcao", ""),
        "equipe": motorista_data.get("equipe", ""),
        "frota": motorista_data.get("frota", ""),
        "tipo": epi_data.get("tipo", ""),
        "descricao": epi_data["descricao"],
        "codigo_sap": str(epi_data.get("cod_sap", "")),
        "data_solicitacao": datetime.now().isoformat()  # ✅ campo obrigatório
    }).execute()

def carregar_historico():
    res = supabase.table("historico_solicitacoes").select("*").execute()
    return pd.DataFrame(res.data)


import streamlit as st
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

SENHA_TECNICO = "T3CNIC0EPI"  # pode mover pro .env depois

def show():
    st.title("👷 Cadastro de Motoristas")
    st.caption("Página restrita para uso do técnico responsável")

    senha = st.text_input("🔐 Digite a senha de técnico:", type="password")

    if senha != SENHA_TECNICO:
        st.warning("🔒 Acesso negado. Insira a senha correta.")
        st.stop()

    st.success("🔓 Acesso autorizado!")

    nome = st.text_input("Nome completo")
    matricula = st.text_input("Matrícula")
    frota = st.text_input("Frota")
    equipe = st.text_input("Equipe")
    funcao = st.text_input("Função")

    if st.button("➕ Cadastrar Motorista"):
        if not nome or not matricula:
            st.error("⚠️ Nome e matrícula são obrigatórios.")
            return

        # Verifica se matrícula já existe
        exists = supabase.table("motoristas") \
            .select("id") \
            .eq("matricula", matricula.strip()) \
            .execute()

        if exists.data:
            st.warning("❗ Motorista com esta matrícula já está cadastrado.")
            return

        # Insere novo motorista
        supabase.table("motoristas").insert({
            "nome": nome.strip().title(),
            "matricula": matricula.strip(),
            "frota": frota.strip().title(),
            "equipe": equipe.strip().upper(),
            "funcao": funcao.strip().title()
        }).execute()

        st.success(f"✅ Motorista {nome.strip().title()} cadastrado com sucesso!")

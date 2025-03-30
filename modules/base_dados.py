import streamlit as st
import pandas as pd
from database import carregar_solicitacoes
from io import BytesIO
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

SENHA_CORRETA = "SAP123"

def gerar_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Solicitacoes")
    output.seek(0)
    return output

def show_base():
    st.title("📦 Base de Dados de EPIs")
    st.caption("Área restrita — uso exclusivo para integração com SAP/VBA")

    senha = st.text_input("🔐 Digite a senha de acesso:", type="password")

    if senha != SENHA_CORRETA:
        st.warning("🔒 Acesso restrito. Insira a senha para continuar.")
        st.stop()

    st.success("🔓 Acesso liberado!")

    df = carregar_solicitacoes()

    if df.empty:
        st.info("Nenhuma solicitação registrada ainda.")
        return

    colunas_exibir = [
        "nome", "matricula", "funcao", "equipe", "frota",
        "tipo", "descricao", "quantidade", "codigo_sap",
        "data_solicitacao", "semana"
    ]
    df = df[colunas_exibir]

    st.subheader("📊 Visualização da base")
    st.dataframe(df, use_container_width=True)

    excel_bytes = gerar_excel(df)

    if st.download_button(
        label="📥 Baixar base em Excel",
        data=excel_bytes,
        file_name="base_epis.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    ):
        from database import inserir_historico_unico  # ou local, se preferir

        for row in df.to_dict(orient="records"):
            historico = {
                "nome": row["nome"].strip().title(),
                "matricula": str(row["matricula"]).strip(),
                "funcao": row.get("funcao", "").strip().title(),
                "equipe": row.get("equipe", "").strip().upper(),
                "frota": row.get("frota", "").strip().title(),
                "tipo": ", ".join([t.strip().title() for t in row["tipo"].split(",")]),
                "descricao": ", ".join([d.strip().capitalize() for d in row["descricao"].split(",")]),
                "quantidade": ", ".join([q.strip() for q in row["quantidade"].split(",")]),
                "codigo_sap": row["codigo_sap"].strip(),
                "data_solicitacao": row["data_solicitacao"],
                "semana": row["semana"].strip(),
                "motorista_id": row.get("motorista_id"),
                "epi_id": row.get("epi_id")
            }

            inserido = inserir_historico_unico(supabase, historico)
            if not inserido:
                st.info(f"📌 Solicitação duplicada ignorada para: {historico['nome']}")




        # Limpeza da base atual
        supabase.rpc("limpar_solicitacoes").execute()

        st.success("✅ Backup feito e tabela de solicitações limpa com sucesso!")

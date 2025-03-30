import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client
from dotenv import load_dotenv
import os
from io import BytesIO

# === Setup Supabase ===
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

SENHA_TECNICO = "Tecnico"

def exportar_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Emergencial")
    output.seek(0)
    return output

def show():
    st.title("🚨 Pedido Emergencial de EPIs")
    st.caption("Área exclusiva para uso do técnico responsável")

    senha = st.text_input("🔐 Digite a senha de técnico:", type="password")
    if senha != SENHA_TECNICO:
        st.warning("🔒 Acesso negado. Insira a senha correta.")
        st.stop()
    st.success("🔓 Acesso autorizado!")

    if "epis_emergenciais" not in st.session_state:
        st.session_state.epis_emergenciais = []

    st.subheader("📋 Novo Pedido Emergencial")

    nome = st.text_input("Nome do técnico")
    funcao = st.text_input("Função")
    equipe = st.text_input("Equipe")
    frota = st.text_input("Frota")
    observacao = st.text_area("Observações adicionais (opcional)")

    epis_df = supabase.table("epis").select("*").execute()
    epis_df = pd.DataFrame(epis_df.data)
    epis_por_tipo = epis_df.groupby("tipo")

    col1, col2, col3 = st.columns([3, 4, 2])
    with col1:
        tipo_escolhido = st.selectbox("Tipo de EPI", sorted(epis_por_tipo.groups.keys()))
    with col2:
        opcoes = epis_df[epis_df["tipo"] == tipo_escolhido]
        descricao_escolhida = st.selectbox("Descrição", opcoes["descricao"].tolist())
    with col3:
        quantidade = st.number_input("Quantidade", min_value=1, step=1, value=1)

    if st.button("➕ Adicionar ao Pedido"):
        epi_info = opcoes[opcoes["descricao"] == descricao_escolhida].iloc[0]
        st.session_state.epis_emergenciais.append({
            "tipo": tipo_escolhido,
            "descricao": descricao_escolhida,
            "quantidade": quantidade,
            "codigo_sap": str(epi_info["cod_sap"]),
            "epi_id": epi_info["id"]
        })

    if st.session_state.epis_emergenciais:
        st.subheader("✅ EPIs Selecionados")
        for i, epi in enumerate(st.session_state.epis_emergenciais):
            col_a, col_b = st.columns([5, 1])
            with col_a:
                st.markdown(f"- **{epi['descricao']}** ({epi['quantidade']}x)")
            with col_b:
                if st.button("❌", key=f"del_emergencial_{i}"):
                    st.session_state.epis_emergenciais.pop(i)
                    st.rerun()

        if st.button("📦 Enviar Pedido Emergencial"):
            try:
                tipos = ", ".join([e["tipo"] for e in st.session_state.epis_emergenciais])
                descricoes = ", ".join([e["descricao"] for e in st.session_state.epis_emergenciais])
                quantidades = ", ".join([str(e["quantidade"]) for e in st.session_state.epis_emergenciais])
                codigos_sap = ", ".join([e["codigo_sap"] for e in st.session_state.epis_emergenciais])
                semana = datetime.now().strftime("%Y-W%U")

                supabase.table("pedido_emergencial").insert({
                    "nome": nome.strip().title(),
                    "matricula": "",
                    "funcao": funcao.strip().title(),
                    "equipe": equipe.strip().upper(),
                    "frota": frota.strip().title(),
                    "tipo": tipos,
                    "descricao": descricoes,
                    "quantidade": quantidades,
                    "codigo_sap": codigos_sap,
                    "data_solicitacao": datetime.now().isoformat(),
                    "semana": semana,
                    "motorista_id": None,
                    "epi_id": None
                }).execute()

                st.success("🚀 Pedido emergencial enviado com sucesso!")
                st.session_state.epis_emergenciais = []
            except Exception as e:
                st.error(f"Erro ao enviar: {e}")

    # === Visualizar pedidos existentes ===
    st.markdown("---")
    st.subheader("📋 Pedidos Emergenciais Registrados")

    pedidos = supabase.table("pedido_emergencial").select("*").order("data_solicitacao", desc=True).execute()
    df = pd.DataFrame(pedidos.data)

    if not df.empty:
        st.dataframe(df, use_container_width=True)

        st.download_button(
            label="📥 Baixar em Excel",
            data=exportar_excel(df),
            file_name="pedidos_emergenciais.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        if st.button("🧹 Limpar Pedidos e Enviar para Histórico"):
            for row in df.to_dict(orient="records"):
                supabase.table("pedido_emergencial_historico").insert(row).execute()
            supabase.table("pedido_emergencial").delete().neq("id", 0).execute()
            st.success("✅ Pedidos movidos para o histórico e tabela limpa.")
    else:
        st.info("Nenhum pedido registrado ainda.")

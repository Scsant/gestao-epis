import streamlit as st
from database import (
    carregar_motoristas,
    carregar_epis,
    inserir_solicitacao,
    ja_solicitou_na_semana
)
from datetime import datetime

def show():
    st.title("🧾 Solicitação de EPIs")

    if "epis_selecionados" not in st.session_state:
        st.session_state.epis_selecionados = []

    matricula_input = st.text_input("Digite sua matrícula:", max_chars=20)

    if not matricula_input:
        st.info("👈 Digite sua matrícula para continuar.")
        return

    motoristas = carregar_motoristas()
    motorista = motoristas[motoristas["matricula"].astype(str) == matricula_input.strip()]

    if motorista.empty:
        st.error("❌ Motorista não cadastrado. Solicite o cadastro ao time de troca de turno.")
        return

    if ja_solicitou_na_semana(matricula_input):
        st.warning("⚠️ Você já fez uma solicitação nesta semana. Tente novamente após domingo 00:00.")
        return

    motorista_info = motorista.iloc[0]
    st.success("✅ Motorista encontrado!")
    st.write(f"**Nome:** {motorista_info['nome']}")
    st.write(f"**Função:** {motorista_info.get('funcao', '—')}")
    st.write(f"**Equipe:** {motorista_info.get('equipe', '—')}")
    st.write(f"**Frota:** {motorista_info.get('frota', '—')}")

    epis_df = carregar_epis()
    epis_por_tipo = epis_df.groupby("tipo")

    st.subheader("📋 Selecione os EPIs desejados")

    col1, col2, col3 = st.columns([3, 4, 2])
    with col1:
        tipo_escolhido = st.selectbox("Tipo de EPI", sorted(epis_por_tipo.groups.keys()))
    with col2:
        opcoes = epis_df[epis_df["tipo"] == tipo_escolhido]
        descricao_escolhida = st.selectbox("Descrição", opcoes["descricao"].tolist())
    with col3:
        quantidade_permitida = int(opcoes[opcoes["descricao"] == descricao_escolhida]["quantidade_permitida"].values[0])
        quantidade = st.number_input(
            "Qtd",
            min_value=1,
            max_value=quantidade_permitida,
            step=1,
            value=1,
            help=f"Máximo permitido: {quantidade_permitida}"
        )

    if st.button("➕ Adicionar EPI"):
        if descricao_escolhida in [e["descricao"] for e in st.session_state.epis_selecionados]:
            st.warning("⚠️ Este EPI já foi adicionado.")
        else:
            epi_info = opcoes[opcoes["descricao"] == descricao_escolhida].iloc[0]
            st.session_state.epis_selecionados.append({
                "tipo": tipo_escolhido,
                "descricao": descricao_escolhida,
                "quantidade": quantidade,
                "codigo_sap": str(epi_info["cod_sap"]),
                "epi_id": epi_info["id"]
            })

    if st.session_state.epis_selecionados:
        st.subheader("✅ EPIs Selecionados")
        for i, epi in enumerate(st.session_state.epis_selecionados):
            col_a, col_b = st.columns([5, 1])
            with col_a:
                st.markdown(f"- **{epi['descricao']}** ({epi['quantidade']}x)")
            with col_b:
                if st.button("❌", key=f"del_{i}"):
                    st.session_state.epis_selecionados.pop(i)
                    st.rerun()


        if st.button("📦 Enviar Solicitação"):
            try:
                tipos = ", ".join([e["tipo"] for e in st.session_state.epis_selecionados])
                descricoes = ", ".join([e["descricao"] for e in st.session_state.epis_selecionados])
                quantidades = ", ".join([str(e["quantidade"]) for e in st.session_state.epis_selecionados])
                codigos_sap = ", ".join([e["codigo_sap"] for e in st.session_state.epis_selecionados])
                motorista_id = int(motorista_info["id"])

                from supabase import create_client
                import os
                from dotenv import load_dotenv
                load_dotenv()
                supabase_url = os.getenv("SUPABASE_URL")
                supabase_key = os.getenv("SUPABASE_KEY")
                supabase = create_client(supabase_url, supabase_key)

                supabase.table("solicitacoes").insert({
                    "nome": motorista_info["nome"],
                    "matricula": str(motorista_info["matricula"]),
                    "funcao": motorista_info.get("funcao", ""),
                    "equipe": motorista_info.get("equipe", ""),
                    "frota": motorista_info.get("frota", ""),
                    "tipo": tipos,
                    "descricao": descricoes,
                    "quantidade": quantidades,
                    "codigo_sap": codigos_sap,
                    "data_solicitacao": datetime.now().isoformat(),
                    "motorista_id": motorista_id,
                    "epi_id": None,
                    "semana": datetime.now().strftime("%Y-W%U")
                }).execute()

                st.success("🚀 Solicitação enviada com sucesso!")
                st.session_state.epis_selecionados = []
            except Exception as e:
                st.error(f"Erro ao enviar: {e}")

import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
from database import carregar_historico, carregar_motoristas

SENHA_SUPERVISOR = "SAP123"

def exportar_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Analise")
    output.seek(0)
    return output

def show():
    st.title("📊 Painel Analítico de EPIs")
    st.caption("Área restrita para supervisores")

    senha = st.text_input("🔐 Digite a senha de supervisor:", type="password")
    if senha != SENHA_SUPERVISOR:
        st.warning("🔒 Acesso restrito. Insira a senha correta.")
        st.stop()

    st.success("🔓 Acesso autorizado!")

    df = carregar_historico()
    df_motoristas = carregar_motoristas()

    if df.empty:
        st.info("Nenhuma solicitação registrada.")
        return

    # ==== Filtro por semana ====
    semanas_disponiveis = sorted(df["semana"].dropna().unique(), reverse=True)
    semanas_opcoes = ["Todos"] + list(semanas_disponiveis)

    semana_selecionada = st.selectbox("📆 Filtrar por semana:", semanas_opcoes)
    

    if semana_selecionada != "Todos":
        df = df[df["semana"] == semana_selecionada]


    # ==== Filtro por data (slider) ====
    st.markdown("---")
    st.subheader("🗓️ Filtro por intervalo de datas")

    datas = pd.to_datetime(df["data_solicitacao"], errors="coerce")
    data_min = datas.min().date()
    data_max = datas.max().date()

    if data_min == data_max:
        st.info(f"📅 Apenas uma data disponível: {data_min.strftime('%d/%m/%Y')}")
    else:
        data_inicial, data_final = st.slider(
            "📅 Selecione o intervalo de datas:",
            min_value=data_min,
            max_value=data_max,
            value=(data_min, data_max),
            format="DD/MM/YYYY"
        )

        # Aplicar filtro ao dataframe
        df = df[
            (pd.to_datetime(df["data_solicitacao"]).dt.date >= data_inicial) &
            (pd.to_datetime(df["data_solicitacao"]).dt.date <= data_final)
        ]



    # ==== Gráfico 1: Solicitações por Equipe ====
    st.subheader("📦 Solicitações por Equipe")

    equipe_agg = (
        df.groupby("equipe")["id"]
        .count()
        .reset_index()
        .sort_values(by="id", ascending=False)  # ordena do maior para menor
    )
    equipe_agg.columns = ["Equipe", "Solicitações"]

    fig1 = px.bar(
        equipe_agg,
        x="Equipe",
        y="Solicitações",
        color_discrete_sequence=["rgba(0, 123, 255, 0.6)"],
        title=f"Solicitações por Equipe — Semana {semana_selecionada}",
    )
    fig1.update_layout(
        transition_duration=800,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig1, use_container_width=True)


    # ==== Gráfico 2: Motoristas por Equipe ====
    st.subheader("👷 Motoristas por Equipe")

    equipe_motoristas = (
        df_motoristas.groupby("equipe")["id"]
        .count()
        .reset_index()
        .sort_values(by="id", ascending=False)  # ordena do maior para o menor
    )
    equipe_motoristas.columns = ["Equipe", "Motoristas"]

    fig2 = px.bar(
        equipe_motoristas,
        x="Equipe",
        y="Motoristas",
        color_discrete_sequence=["rgba(0, 123, 255, 0.5)"],
        title="Motoristas cadastrados por Equipe",
    )
    fig2.update_layout(
        transition_duration=800,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig2, use_container_width=True)


    # ==== Gráfico 3: EPIs mais solicitados ====
    st.subheader("🧤 EPIs mais solicitados")

    epi_agg = df["descricao"].str.split(", ").explode().value_counts().reset_index()
    epi_agg.columns = ["Descrição", "Quantidade"]
    epi_agg = epi_agg.sort_values(by="Quantidade", ascending=True)

    altura_grafico = 30 * len(epi_agg)

    fig3 = px.bar(
        epi_agg,
        x="Quantidade",
        y="Descrição",
        orientation="h",
        color_discrete_sequence=["rgba(0, 123, 255, 0.4)"],
    )

    fig3.update_traces(
        text=epi_agg["Quantidade"],
        textposition="outside",
        textfont_size=12,
        cliponaxis=False
    )

    fig3.update_layout(
        title="EPIs mais solicitados",
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False, title=None),
        yaxis=dict(showgrid=False, showticklabels=True, title=None),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        transition_duration=800,
        height=altura_grafico
    )

    st.plotly_chart(fig3, use_container_width=True)



    # ==== Exportação Excel ====
    st.subheader("📥 Exportar dados")

    excel_bytes = exportar_excel(df)
    st.download_button(
        label="📁 Baixar análise filtrada em Excel",
        data=excel_bytes,
        file_name=f"analise_{semana_selecionada}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

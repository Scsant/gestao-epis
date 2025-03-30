import streamlit as st
from database import carregar_solicitacoes

def show():
    st.title("Solicitações Recentes 📝")
    df_solicitacoes = carregar_solicitacoes()
    st.dataframe(df_solicitacoes)
 

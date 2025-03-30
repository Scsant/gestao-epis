import streamlit as st
from streamlit_option_menu import option_menu

# === CONFIGURAÇÃO DA PÁGINA ===
st.set_page_config(page_title="Gestão de EPIs", layout="wide")
# === GRADIENTE DE FUNDO COM CSS ===
st.markdown("""
    <style>
    body {
        background: linear-gradient(135deg, #4b367a, #2b3835);
        color: #d6e47d !important;
    }
    .stApp {
        background: linear-gradient(135deg, #4b367a, #2b3835);
    }
    </style>
""", unsafe_allow_html=True)


# === MENU LATERAL CUSTOM ===
with st.sidebar:
    page = option_menu(
        "Menu",
        [
            "Solicitar EPI",
            "Ver Solicitações",
            "Controle",
            "Dashboard",
            "Base de Dados",
            "Pedido Emergencial",
            "Cadastro de Motoristas"
        ],
        icons=[
            "clipboard-plus", "list-task", "shield-check", "bar-chart",
            "database", "alert-octagon", "person-plus"
        ],
        menu_icon="cast",
        default_index=0
    )

# === IMPORTS DOS MÓDULOS ===
from modules import solicitacao, controle, dashboard, base_dados
from modules import pedido_emergencial, cadastro_motorista, visualizar

# === ROTEAMENTO ===
if page == "Solicitar EPI":
    solicitacao.show()

elif page == "Ver Solicitações":
    visualizar.show()

elif page == "Controle":
    controle.show()

elif page == "Dashboard":
    dashboard.show()

elif page == "Base de Dados":
    base_dados.show_base()

elif page == "Pedido Emergencial":
    pedido_emergencial.show()

elif page == "Cadastro de Motoristas":
    cadastro_motorista.show()

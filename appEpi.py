import streamlit as st
import pandas as pd
import json
from io import BytesIO
from datetime import datetime
from openpyxl import Workbook
import os
import streamlit as st
from github import Github
from dotenv import load_dotenv

# Adiciona uma imagem no header usando HTML
st.markdown(
    """
    <style>
        .header-container {
            display: flex;
            justify-content: center;
            align-items: center;
            border-radius: 100px;
            background: linear-gradient(135deg, #00009a, #b4df37);
           
        }
        .header-container img {
            max-width: 2000px; /* Tamanho da imagem */
            margin-right: 10px; /* Espaçamento ao lado da imagem */
            opacity: 0.6;
        }
        .header-container h1 {
            color: white; /* Cor do texto */
            font-size: 30px;
        }
    </style>
    <div class="header-container">
        <img src="https://raw.githubusercontent.com/Scsant/bracc2/3361f72d7f1b83260bd325f41387d614f7b49ffd/bracell.jpg" alt="Logo">
        
    </div>
    """,
    unsafe_allow_html=True
)


# CSS para alterar a cor do st.success
st.markdown(
    """
    <style>
    .stAlert {
        background: linear-gradient(135deg, #00009a, #b4df37);
        color: white; /* Cor do texto */
        border: 1px solid #f0f0d8; /* Cor da borda */
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Estilo para aplicar o gradiente
page_style = """
<style>
    /* Gradiente para o fundo */
    .stApp {
        background: linear-gradient(185deg, #00009a, #b4df37);
        color: white;
    }

</style>
"""

st.markdown(page_style, unsafe_allow_html=True)




# Carrega as variáveis do .env
load_dotenv()


# Caminho dos arquivos JSON


EPIS_FILE = "epis.json"



# Configurações do GitHub
GITHUB_TOKEN2 = os.getenv("GITHUB_TOKEN2")  # Configure como variável de ambiente para segurança
REPO_NAME = "Scsant/epiPython"
USUARIOS_FILE = "motorista.json"

def salvar_motoristas_no_github(conteudo_json):
    """Salva o arquivo motorista.json no GitHub."""
    g = Github(GITHUB_TOKEN2)  # Autentica usando o segundo token
    try:
        repo = g.get_repo(REPO_NAME)  # Obtém o repositório
        try:
            # Verifica se o arquivo já existe no repositório
            arquivo = repo.get_contents(USUARIOS_FILE)
            # Atualiza o arquivo existente
            repo.update_file(
                path=USUARIOS_FILE,
                message="Atualizando motorista.json",
                content=conteudo_json,
                sha=arquivo.sha,
            )
            print("motorista.json atualizado no GitHub com sucesso!")
        except Exception:
            # Se o arquivo não existir, cria um novo
            repo.create_file(
                path=USUARIOS_FILE,
                message="Criando motorista.json",
                content=conteudo_json,
            )
            print("motorista.json criado no GitHub com sucesso!")
    except Exception as e:
        print(f"Erro ao salvar motorista.json no GitHub: {e}")



# Configurações do GitHub
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # Configure como variável de ambiente para segurança
REPO_NAME = "Scsant/epiPython"
SOLICITACOES_FILE = "solicitacoes.json"

def salvar_no_github(conteudo_json):
    """Salva o arquivo no GitHub."""
    g = Github(GITHUB_TOKEN)
    try:
        repo = g.get_repo(REPO_NAME)
        try:
            # Verifica se o arquivo já existe no repositório
            arquivo = repo.get_contents(SOLICITACOES_FILE)
            # Atualiza o arquivo existente
            repo.update_file(
                path=SOLICITACOES_FILE,
                message="Atualizando solicitacoes.json",
                content=conteudo_json,
                sha=arquivo.sha,
            )
            st.success("Arquivo atualizado no GitHub com sucesso!")
        except Exception:
            # Se o arquivo não existir, cria um novo
            repo.create_file(
                path=SOLICITACOES_FILE,
                message="Criando solicitacoes.json",
                content=conteudo_json,
            )
            st.success("Arquivo criado no GitHub com sucesso!")
    except Exception as e:
        st.error(f"Erro ao salvar no GitHub: {e}")
        
def deletar_solicitacoes_do_github():
    """Deleta o arquivo solicitacoes.json do GitHub."""
    g = Github(GITHUB_TOKEN)
    try:
        repo = g.get_repo(REPO_NAME)
        arquivo = repo.get_contents(SOLICITACOES_FILE)
        repo.delete_file(
            path=SOLICITACOES_FILE,
            message="Deletando solicitacoes.json da base",
            sha=arquivo.sha,
        )
        st.success("Arquivo solicitacoes.json deletado do GitHub com sucesso!")
    except Exception as e:
        st.error(f"Erro ao deletar solicitacoes.json no GitHub: {e}")        


def carregar_json(filepath):
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as file:
            return json.load(file)
    return []

def salvar_json(filepath, data):
    """Salva o arquivo localmente e no GitHub."""
    # Salva localmente
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    # Salva no GitHub
    salvar_no_github(json.dumps(data, ensure_ascii=False, indent=4))


# Carregar usuários, solicitações e EPIs
usuarios = carregar_json(USUARIOS_FILE)
solicitacoes = carregar_json(SOLICITACOES_FILE)
epis = carregar_json(EPIS_FILE)

# Tokens para usuários e EPIs
st.session_state.setdefault("solicitacoes_temp", [])

# Função para buscar motoristas e técnicos por matrícula
def buscar_usuario_por_matricula(matricula):
    try:
        matricula = float(matricula)  # Converte a entrada para float
        for usuario in usuarios:
            if usuario["Matrícula"] == matricula:
                return usuario
    except ValueError:
        st.warning("Matrícula inválida. Por favor, insira apenas números.")
    return None

def verificar_duplicidade(lista, novo_item):
    """Verifica duplicidade de item em uma lista."""
    for item in lista:
        if (
            item["Matrícula"] == novo_item["Matrícula"] and
            item["Descrição"] == novo_item["Descrição"] and
            item["Tipo"] == novo_item["Tipo"]
        ):
            return item
    return None



# Função para obter tipos de EPIs

def obter_tipos_epis():
    return list(set([epi["TIPO"] for epi in epis]))

def obter_epis_por_tipo(tipo):
    return [epi for epi in epis if epi["TIPO"] == tipo]

# Área de solicitação de EPIs
menu = st.sidebar.selectbox("Selecione a área", ["Solicitação de EPIs", "Área Restrita - Supervisor"])

if menu == "Solicitação de EPIs":
    st.title("Solicitação de EPIs/Logística Florestal")

    matricula = st.text_input("Digite sua matrícula")
    usuario = buscar_usuario_por_matricula(matricula) if matricula else None

    if usuario:
        st.success(f"Bem-vindo, {usuario['Nome']} ({usuario['Função']})")

        # Solicitação de EPIs
        st.header("Selecione os EPIs necessários")

        tipo_epi = st.selectbox("Tipo de EPI", ["Selecione"] + obter_tipos_epis())
        if tipo_epi != "Selecione":
            epis_disponiveis = obter_epis_por_tipo(tipo_epi)
            descricao_epi = st.selectbox("Descrição do EPI", ["Selecione"] + [epi["DESCRIÇÃO"] for epi in epis_disponiveis])

            if descricao_epi != "Selecione":
                epi_selecionado = next(epi for epi in epis_disponiveis if epi["DESCRIÇÃO"] == descricao_epi)
                quantidade_permitida = epi_selecionado["quantidades permitidas"]

                if usuario["Função"] == "Técnico":
                    quantidade = st.number_input("Quantidade", min_value=1, step=1)
                else:
                    quantidade = st.number_input(
                        "Quantidade",
                        min_value=1,
                        max_value=quantidade_permitida,
                        step=1,
                    )

                if st.button("Adicionar ao Resumo"):
                    encontrado = False
                    for solicitacao in st.session_state["solicitacoes_temp"]:
                        if solicitacao["Matrícula"] == matricula:
                            # Verificar se o item exato já foi adicionado
                            descricoes_existentes = solicitacao["Descrição"].split(", ")
                            quantidades_existentes = solicitacao["Quantidade"].split(", ")
                            if descricao_epi in descricoes_existentes and str(quantidade) in quantidades_existentes:
                                st.warning("Este item já foi adicionado exatamente. Solicitação recusada!")
                                encontrado = True
                                break

                            # Atualizar a linha existente (concatenar)
                            solicitacao["Descrição"] += f", {descricao_epi}"
                            solicitacao["Tipo"] += f", {tipo_epi}"
                            solicitacao["Quantidade"] += f", {quantidade}"
                            solicitacao["Código SAP"] += f", {epi_selecionado['COD SAP']}"
                            encontrado = True
                            break

                    if not encontrado:
                        # Adicionar nova linha se não encontrado
                        st.session_state["solicitacoes_temp"].append(
                            {
                                "Nome": usuario["Nome"],
                                "Equipe (BTF)": usuario.get("Equipe", "N/A"),
                                "Função": usuario["Função"],
                                "Frota": usuario.get("Frota", "N/A"),
                                "Matrícula": matricula,
                                "Tipo": tipo_epi,
                                "Descrição": descricao_epi,
                                "Quantidade": str(quantidade),
                                "Código SAP": str(epi_selecionado["COD SAP"]),
                            }
                        )
                    st.success(f"{descricao_epi} adicionado com sucesso!")

        # Resumo de solicitações temporárias
        if st.session_state["solicitacoes_temp"]:
            st.subheader("Resumo das Solicitações")
            df_temp = pd.DataFrame(st.session_state["solicitacoes_temp"])
            st.dataframe(df_temp)

        if st.button("Enviar Solicitações"):
            solicitacoes.extend(st.session_state["solicitacoes_temp"])
            salvar_json(SOLICITACOES_FILE, solicitacoes)  # Agora salva localmente e no GitHub
            st.session_state["solicitacoes_temp"] = []
            st.success("Solicitações enviadas para análise do supervisor!")
# Área Restrita para Supervisores
elif menu == "Área Restrita - Supervisor":
    st.title("Área Restrita - Supervisor")
    senha = st.text_input("Digite a senha", type="password")

    if senha == "admin123":
        st.success("Acesso autorizado")

        # Carregar solicitações do JSON
        solicitacoes = carregar_json(SOLICITACOES_FILE)

        if solicitacoes:
            st.subheader("Solicitações Pendentes para Aprovação")
            df_pendentes = pd.DataFrame(solicitacoes)

            # Exibição padrão da tabela com redimensionamento
            st.dataframe(df_pendentes, use_container_width=True)

            # Botão para exportar para Excel
            def exportar_para_excel(dataframe):
                output = BytesIO()
                with pd.ExcelWriter(output, engine="openpyxl") as writer:
                    dataframe.to_excel(writer, index=False, sheet_name="SolicitacoesPendentes")
                return output.getvalue()

            if st.button("Exportar para Excel"):
                excel_data = exportar_para_excel(df_pendentes)
                st.download_button(
                    label="Baixar Excel",
                    data=excel_data,
                    file_name="solicitacoes_pendentes.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )

        # Área de cadastro de motoristas
        st.title("Área Restrita - Cadastro de Motoristas")

        # Formulário para cadastrar motoristas
        nome = st.text_input("Nome do Motorista")
        matricula = st.text_input("Matrícula")

        # Listas suspensas para Frota, Equipe e Função
        frota = st.selectbox("Frota", ["Selecione", "Frota Leste", "Frota Oeste", "Troca de Turno"])
        equipe = st.selectbox("Equipe", ["Selecione", "BTF1", "BTF2", "BTF3", "BTF4", "BTF5", "BTF6", "BTF7", "BTF8", "Troca de Turno"])
        funcao = st.selectbox("Função", ["Selecione", "Técnico", "Motorista"])

        if st.button("Cadastrar Motorista"):
            # Validações básicas
            if not nome or not matricula or frota == "Selecione" or equipe == "Selecione" or funcao == "Selecione":
                st.error("Todos os campos são obrigatórios!")
            else:
                try:
                    # Criar dicionário no padrão JSON
                    novo_motorista = {
                        "Frota": frota,
                        "Equipe": equipe,
                        "Matrícula": float(matricula),  # Converte matrícula para float
                        "Função": funcao,
                        "Nome": nome,
                    }

                    # Carregar dados existentes e adicionar o novo motorista
                    motoristas = carregar_json(USUARIOS_FILE)
                    motoristas.append(novo_motorista)
                    salvar_json(USUARIOS_FILE, motoristas)

                    # Salvar motoristas no GitHub
                    salvar_motoristas_no_github(json.dumps(motoristas, ensure_ascii=False, indent=4))

                    st.success(f"Motorista {nome} cadastrado com sucesso!")
                except Exception as e:
                    st.error(f"Erro ao cadastrar motorista: {e}")

        # Botão para deletar o arquivo de solicitações no GitHub
        st.subheader("Limpar Base de Solicitações")
        if st.button("Deletar Solicitações da Base"):
            deletar_solicitacoes_do_github()

                            

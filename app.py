import streamlit as st
import pandas as pd
import datetime
import numpy as np
import io
from fpdf import FPDF
import os

st.set_page_config(page_title="Plano Preventivas Novavia Mineração", layout="wide", page_icon="🏗️")

# IDENTIDADE VISUAL E LOGO REAL (CONFIGURAÇÃO DO TOPO)
col_logo, col_titulo = st.columns([1, 4]) # Ajusta a proporção para o logo não ficar gigante
with col_logo:
    # Verifica se o arquivo logo.png foi enviado para a pasta
    if os.path.exists("logo.png"):
        st.image("logo.png", width=150)
    else:
        # Mostra um ícone temporário caso você ainda não tenha subido a imagem
        st.markdown("<h1 style='text-align: center; margin:0; padding:0;'>🏗️</h1>", unsafe_allow_html=True)
with col_titulo:
    st.markdown("<h2 style='margin:0; padding:0; color: #1E3A8A;'>Plano Preventivas Novavia Mineração</h2>", unsafe_allow_html=True)
    st.markdown("<p style='font-style: italic; color: #555; margin:0;'>Gestão de Ativos e Confiabilidade</p>", unsafe_allow_html=True)

st.markdown("---")

# BANCO DE DADOS FOCADO APENAS NO CAMINHÃO CA0024
if 'frota' not in st.session_state:
    st.session_state.frota = [
        {
            "id": "CA0024", 
            "nome": "Volvo VM 360 - 01", 
            "tipo": "Horas", 
            "atual": 3443, 
            "ult_rev_horas": 3009, 
            "ult_rev_data": "15/02/2026", 
            "media": 10,
            "pecas_600": "Filtro Oleo Motor, Oleo 15W40, Filtros Combustivel"
        }
    ]

# PLANO MESTRE REPLICADO DO PROTHEUS DO CA0024
planos_mestre_dados = [
    {"Bem": "CA0024", "Nome Bem": "CAMINHAO VOLVO VM 360 6X4", "Serviço": "MPREV", "Sequência": "001", "Nome Manut.": "VOLVO VM 360 6X4 600H/15.000KM/ 1A"},
    {"Bem": "CA0024", "Nome Bem": "CAMINHAO VOLVO VM 360 6X4", "Serviço": "MPREV", "Sequência": "002", "Nome Manut.": "VOLVO VM 360 6X4 1200H/ 1A"},
    {"Bem": "CA0024", "Nome Bem": "CAMINHAO VOLVO VM 360 6X4", "Serviço": "MPREV", "Sequência": "003", "Nome Manut.": "VOLVO VM 360 6X4 3600H/ 65.000KM"},
    {"Bem": "CA0024", "Nome Bem": "CAMINHAO VOLVO VM 360 6X4", "Serviço": "MPREV", "Sequência": "004", "Nome Manut.": "VOLVO VM 360 6X4 4800H/ 150.000KM"},
    {"Bem": "CA0024", "Nome Bem": "CAMINHAO VOLVO VM 360 6X4", "Serviço": "MPREV", "Sequência": "005", "Nome Manut.": "VOLVO VM 360 6X4 1S"},
    {"Bem": "CA0024", "Nome Bem": "CAMINHAO VOLVO VM 360 6X4", "Serviço": "MPREV", "Sequência": "006", "Nome Manut.": "VOLVO VM 360 6X4 3M"},
    {"Bem": "CA0024", "Nome Bem": "CAMINHAO VOLVO VM 360 6X4", "Serviço": "MPREV", "Sequência": "007", "Nome Manut.": "VOLVO VM 360 6X4 4000H/ 2A / 200.000KM"},
    {"Bem": "CA0024", "Nome Bem": "CAMINHAO VOLVO VM 360 6X4", "Serviço": "MPREV", "Sequência": "008", "Nome Manut.": "VOLVO VM 360 6X4 180.000KM"},
    {"Bem": "CA0024", "Nome Bem": "CAMINHAO VOLVO VM 360 6X4", "Serviço": "MPREV", "Sequência": "009", "Nome Manut.": "VOLVO VM 360 6X4 4A/ 500.000KM"}
]

if 'historico' not in st.session_state:
    st.session_state.historico = []
def calcular_previsao_dias(horas_restantes, media_diaria):
    if media_diaria <= 0: return None
    dias_uteis = int(np.ceil(horas_restantes / media_diaria))
    hoje = datetime.date.today()
    data_futura = np.busday_offset(hoje, dias_uteis, roll='forward')
    return pd.to_datetime(data_futura).date()

aba1, aba2, aba3 = st.tabs(["📊 Painel Multigatilhos", "📋 Planos Cadastrados (Mestre)", "👨‍🔧 Oficina / Lançamentos"])

# ABA 1: PAINEL DE CONTROLE
with aba1:
    st.subheader("Situação dos Ciclos de Manutenção Preventiva")
    dados_painel = []
    for ativo in st.session_state.frota:
        horas_alvo = ativo['ult_rev_horas'] + 600
        horas_restantes = horas_alvo - ativo['atual']
        data_final = calcular_previsao_dias(horas_restantes, ativo['media'])
        status_geral = "🟢 OK"
        if ativo['atual'] >= horas_alvo: status_geral = "🔴 VENCIDA"
        dados_painel.append({
            "ID / TAG": ativo['id'], "Equipamento": ativo['nome'], "Horímetro Atual": f"{ativo['atual']} hrs",
            "Última Revisão": f"{ativo['ult_rev_horas']} hrs ({ativo['ult_rev_data']})", "Próxima Meta": f"{horas_alvo} hrs",
            "Data Alvo": data_final.strftime('%d/%m/%Y') if data_final else "IMEDIATO", "Status": status_geral
        })
    st.dataframe(pd.DataFrame(dados_painel), use_container_width=True, hide_index=True)

    st.markdown("---")
    with st.expander("📋 Ver Escopo Técnico da Preventiva (Tarefas e Materiais)"):
        st.markdown("### 🛠️ Sequência 001 - Escopo Técnico Preventiva 600 Horas")
        col_esq, col_dir = st.columns(2)
        with col_esq:
            st.markdown("**📋 Lista de Tarefas (O que executar):**")
            st.write("1. Efetuar a troca do óleo lubrificante do motor.")
            st.write("2. Substituir os filtros de óleo e combustível.")
            st.write("3. Substituir o elemento do filtro separador de água.")
            st.write("4. Reapertar os coxins do motor e da transmissão.")
            st.write("5. Lubrificar totalmente o chassi, quinta roda e articulações com graxa.")
            st.write("6. Inspecionar lonas de freio, vazamentos em cubos e folgas de direção.")
        with col_dir:
            st.markdown("**📦 Materiais e Insumos:**")
            materiais = {
                "Item / Componente": ["Óleo Lubrificante Motor 15W40 CI-4", "Filtro de Óleo Lubrificante (Motor)", "Filtro de Combustível Principal", "Elemento do Filtro Separador de Água", "Graxa Extrema Pressão EP2 (Chassis)"],
                "Quantidade": ["32 Litros", "2 Unidades", "1 Unidade", "1 Unidade", "2 Quilos"]
            }
            st.table(pd.DataFrame(materiais))

# ABA 2: CONSULTA DE PLANOS MESTRE
with aba2:
    st.subheader("📋 Planos Cadastrados no Protheus para o Ativo")
    st.dataframe(pd.DataFrame(planos_mestre_dados), use_container_width=True, hide_index=True)

# ABA 3: ENTRADA DE DADOS DA OFICINA
with aba3:
    st.subheader("Registrar Medição Diária")
    with st.form("form_ca0024"):
        novo_horimetro = st.number_input("Digite o Horímetro Atual do CA0024:", min_value=0, value=ativo['atual'])
        revisao_executada = st.selectbox("Preventiva executada?", ["Nenhuma", "Concluída Sequência 001 (600h)"])
        enviar = st.form_submit_button("Salvar Registro")
        if enviar:
            for a in st.session_state.frota:
                a['atual'] = novo_horimetro
                if "001" in revisao_executada:
                    a['ult_rev_horas'] = novo_horimetro
                    a['ult_rev_data'] = datetime.date.today().strftime('%d/%m/%Y')
            st.success("✔️ Registro salvo com sucesso!")
            st.rerun()

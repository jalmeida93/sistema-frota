import streamlit as st
import pandas as pd
import datetime
import numpy as np
import io
from fpdf import FPDF

st.set_page_config(page_title="Plano Preventivas Novavia Mineração", layout="wide", page_icon="🏗️")

# 1. IDENTIDADE VISUAL OFICIAL NOVAVIA MINERAÇÃO
col_logo, col_titulo = st.columns([1, 4])
with col_logo:
    st.markdown("<h1 style='text-align: center; margin:0; padding:0;'>🏗️</h1>", unsafe_allow_html=True)
with col_titulo:
    st.markdown("<h2 style='margin:0; padding:0; color: #1E3A8A;'>Plano Preventivas Novavia Mineração</h2>", unsafe_allow_html=True)
    st.markdown("<p style='font-style: italic; color: #555; margin:0;'>Gestão de Ativos e Engenharia de Confiabilidade</p>", unsafe_allow_html=True)

st.markdown("---")

# BANCO DE DADOS REGULADO CONFORME O CONTADOR DO PROTHEUS (3443 HORAS)
if 'frota' not in st.session_state:
    st.session_state.frota = [
        {
            "id": "CA0024", 
            "nome": "Volvo VM 360 - 01", 
            "tipo": "Horas", 
            "atual": 3443, 
            "ult_rev_horas": 3009, 
            "ult_rev_data": "13/06/2026", # Conforme Dt.Ult.Manut da folha 1
            "media": 10
        }
    ]

# DICIONÁRIO DE TAREFAS E MATERIAIS EXTRAÍDOS DO PDF DO PROTHEUS
escopos_preventivas = {
    "Sequência 001 (600h)": {
        "tarefas": [
            "LU0389 - Substituir óleo do motor (SAE 10W30 VDS-4.5)",
            "LU0329 - Substituir filtro de óleo do motor",
            "LU0322 - Substituir filtro de combustível",
            "LU0348 - Substituir filtro separador de água",
            "LU0319 - Substituir filtro de ar primário",
            "LU0153 / LU0416 - Lubrificação geral do chassi e suspensão dianteira (Graxa NLGI 2 EP)",
            "LU0495 / LU0499 - Engraxar alavanca de ajuste do eixo came e pino mestre",
            "LU0474 - Substituir o filtro antipólen do ar condicionado (Intervalo reduzido para 600h)"
        ],
        "materiais": {
            "Código": ["27241", "27179", "27180", "27181", "27182", "27893", "16657"],
            "Descrição do Insumo": [
                "ÓLEO LUBRIFICANTE SAE 10W30 VDS-4.5",
                "FILTRO ÓLEO VO24063074 CAMINHÃO VOLVO",
                "FILTRO COMBUSTÍVEL VO24275477 CAMINHÃO",
                "FILTRO VO24275463 CAMINHÃO VOLVO VM 36",
                "FILTRO AR VO21436535 CAMINHÃO VOLVO V",
                "FILTRO AR CONDICIONADO VO85134455 CAMI",
                "GRAXA MINERAL SABÃO DE LÍTIO NLGI 2 EP"
            ],
            "Qtd": ["24,00 L", "1,00 PC", "1,00 PC", "1,00 PC", "1,00 PC", "1,00 PC", "1,70 KG"]
        }
    },
    "Sequência 002 (1200h)": {
        "tarefas": [
            "LU0303 - Substituir óleo do câmbio e realizar limpeza do respiro de vapores",
            "LU0341 - Substituir filtro do óleo de transmissão e diferencial",
            "LU0386 - Substituir óleo do eixo dianteiro",
            "LU0387 - Substituir óleo do eixo traseiro",
            "LU0562 / LU0563 - Substituir óleo do cubo dianteiro (Direito e Esquerdo)",
            "LU0564 / LU0565 - Substituir óleo do cubo traseiro (Direito e Esquerdo)"
        ],
        "materiais": {
            "Código": ["27348", "27839", "27239"],
            "Descrição do Insumo": [
                "ÓLEO SAE 50 TO-4 / ALLISON C-4 (Câmbio)",
                "FILTRO CAIXA DE MUDANÇA VO24283117 CAM",
                "ÓLEO DIFERENCIAL 85W140 VO85131721 CAM (Eixos/Cubos)"
            ],
            "Qtd": ["18,00 L", "1,00 PC", "43,50 L"]
        }
    },
    "Sequência 003 (3600h)": {
        "tarefas": [
            "LU0501 - Substituir elemento do filtro de particulados (DPF)",
            "LU0567 - Substituir filtro do tanque do ARLA",
            "LU0568 - Substituir filtro da boia do tanque do ARLA"
        ],
        "materiais": {
            "Código": ["28798", "28799", "F-DPF"],
            "Descrição do Insumo": [
                "KIT FILTRO AR ARLA VO24147170 CAMINHÃO",
                "FILTRO BOIA TANQUE ARLA VO24111100 CAM",
                "ELEMENTO DO FILTRO DE PARTICULADOS (DPF)"
            ],
            "Qtd": ["1,00 KIT", "1,00 PC", "1,00 PC"]
        }
    }
}
def calcular_previsao_dias(horas_restantes, media_diaria):
    if media_diaria <= 0: return None
    dias_uteis = int(np.ceil(horas_restantes / media_diaria))
    hoje = datetime.date.today()
    data_futura = np.busday_offset(hoje, dias_uteis, roll='forward')
    return pd.to_datetime(data_futura).date()

aba1, aba2, aba3 = st.tabs(["📊 Painel Multigatilhos", "👨‍🔧 Oficina / Lançamentos", "📋 Histórico de Lançamentos"])

# ABA 1: PAINEL DE CONTROLE RECALIBRADO
with aba1:
    st.subheader("Situação dos Ciclos de Manutenção Preventiva")
    dados_painel = []
    for ativo in st.session_state.frota:
        frequencia_intervalo = 600
        horas_rodadas_desde_revisao = ativo['atual'] - ativo['ult_rev_horas']
        multiplicador_proximo_ciclo = int(np.floor(horas_rodadas_desde_revisao / frequencia_intervalo)) + 1
        horas_alvo = ativo['ult_rev_horas'] + (frequencia_intervalo * multiplicador_proximo_ciclo)
        
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

    # DINÂMICA COMPLETA DE SELEÇÃO DE ESCOPO COM MATERIAIS DO PROTHEUS
    st.markdown("---")
    st.subheader("🔍 Consulta Detalhada de Escopo de Tarefas e Insumos")
    sequencia_selecionada = st.selectbox("Selecione a Sequência de Preventiva para Visualizar o Escopo:", list(escopos_preventivas.keys()))
    
    with st.expander(f"📋 Visualizar Detalhes Operacionais - {sequencia_selecionada}", expanded=True):
        escopo = escopos_preventivas[sequencia_selecionada]
        col_esq, col_dir = st.columns(2)
        with col_esq:
            st.markdown("**📋 Lista de Tarefas do Protheus:**")
            for tarefa in escopo["tarefas"]:
                st.write(tarefa)
        with col_dir:
            st.markdown("**📦 Insumos e Quantidades Homologadas (Espelho RM):**")
            st.table(pd.DataFrame(escopo["materiais"]))

# ABA 2: ENTRADA DE DADOS DA OFICINA
with aba3:
    st.subheader("Registrar Medição Diária")
    with st.form("form_ca0024"):
        novo_horimetro = st.number_input("Digite o Horímetro Atual do CA0024:", min_value=0, value=ativo['atual'])
        revisao_executada = st.selectbox("Preventiva executada?", ["Nenhuma", "Concluída Sequência 001 (600h)", "Concluída Sequência 002 (1200h)", "Concluída Sequência 003 (3600h)"])
        enviar = st.form_submit_button("Salvar Registro")
        if enviar:
            for a in st.session_state.frota:
                a['atual'] = novo_horimetro
                if "001" in revisao_executada:
                    a['ult_rev_horas'] = novo_horimetro
                    a['ult_rev_data'] = datetime.date.today().strftime('%d/%m/%Y')
            st.success("✔️ Registro salvo com sucesso!")
            st.rerun()

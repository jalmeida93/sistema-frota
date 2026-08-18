import streamlit as st
import pandas as pd
import datetime
import numpy as np
import io
from fpdf import FPDF

st.set_page_config(page_title="Plano Preventivas Novavia Mineração", layout="wide", page_icon="🏗️")

# 1. IDENTIDADE VISUAL OFICIAL NOVAVIA MINERAÇÃO
col_logo, col_titulo = st.columns(2)
with col_logo:
    st.markdown("<h1 style='text-align: center; margin:0; padding:0;'>🏗️</h1>", unsafe_allow_html=True)
with col_titulo:
    st.markdown("<h2 style='margin:0; padding:0; color: #1E3A8A;'>Plano Preventivas Novavia Mineração</h2>", unsafe_allow_html=True)
    st.markdown("<p style='font-style: italic; color: #555; margin:0;'>Gestão de Ativos e Engenharia de Confiabilidade</p>", unsafe_allow_html=True)

st.markdown("---")

# BANCO DE DADOS DETALHADO DO CA0024 CONFORME O RELATÓRIO DO PROTHEUS
if 'frota_ca0024' not in st.session_state:
    st.session_state.frota_ca0024 = {
        "id": "CA0024",
        "nome": "Volvo VM 360 - 01",
        "atual": 3443,
        "media_diaria": 10,
        "sequencias": {
            "001": {"nome": "600H/15.000KM/1A", "tipo": "Misto", "intervalo_h": 600, "ult_h": 3009, "ult_data": "13/06/2026"},
            "002": {"nome": "1200H/1A", "tipo": "Misto", "intervalo_h": 1200, "ult_h": 2456, "ult_data": "03/03/2026"},
            "003": {"nome": "3600H/65.000KM", "tipo": "Horas", "intervalo_h": 3600, "ult_h": 1, "ult_data": "10/08/2024"},
            "004": {"nome": "4800H/150.000KM", "tipo": "Horas", "intervalo_h": 4800, "ult_h": 1, "ult_data": "10/08/2024"},
            "005": {"nome": "1S (Semanal)", "tipo": "Tempo", "intervalo_dias": 7, "ult_h": 3443, "ult_data": "11/08/2026"},
            "006": {"nome": "3M (Trimestral)", "tipo": "Tempo", "intervalo_dias": 90, "ult_h": 3443, "ult_data": "18/05/2026"},
            "007": {"nome": "4000H/2A/200.000KM", "tipo": "Misto", "intervalo_h": 4000, "ult_h": 1, "ult_data": "10/08/2024"},
            "008": {"nome": "180.000KM", "tipo": "Horas", "intervalo_h": 4500, "ult_h": 1, "ult_data": "10/08/2024"},
            "009": {"nome": "4A/500.000KM", "tipo": "Tempo", "intervalo_dias": 1460, "ult_h": 1, "ult_data": "10/08/2024"}
        }
    }

# DICIONÁRIO DE TAREFAS E MATERIAIS PARA CONSULTA DETALHADA
escopos_preventivas = {
    "001": {
        "tarefas": ["LU0389-Substituir óleo motor", "LU0329-Substituir filtro óleo", "LU0322-Filtro combustível", "LU0348-Filtro separador", "LU0319-Filtro ar primário", "LU0474-Filtro ar condicionado", "LU0153/LU0416/LU0495/LU0499-Lubrificação geral e eixos"],
        "materiais": {"Código": ["27241", "27179", "27180", "27181", "27182", "27893", "16657"], "Descrição": ["ÓLEO LUBRIFICANTE SAE 10W30 VDS-4.5", "FILTRO ÓLEO VO24063074", "FILTRO COMBUSTÍVEL VO24275477", "FILTRO SEPARADOR VO24275463", "FILTRO AR VO21436535", "FILTRO AR CONDICIONADO VO85134455", "GRAXA MINERAL NLGI 2 EP"], "Qtd": ["24 L", "1 PC", "1 PC", "1 PC", "1 PC", "1 PC", "1,7 KG"]}
    },
    "002": {
        "tarefas": ["LU0303-Substituir óleo câmbio", "LU0341-Filtro óleo transmissão/dif", "LU0386-Óleo eixo dianteiro", "LU0387-Óleo eixo traseiro", "LU0562/0563-Óleo cubos diant", "LU0564/0565-Óleo cubos tras"],
        "materiais": {"Código": ["27348", "27839", "27239"], "Descrição": ["ÓLEO SAE 50 TO-4 (Câmbio)", "FILTRO CAIXA DE MUDANÇA VO24283117", "ÓLEO DIFERENCIAL 85W140 VO85131721"], "Qtd": ["18 L", "1 PC", "43,5 L"]}
    },
    "003": {
        "tarefas": ["LU0501-Substituir filtro DPF", "LU0567-Filtro tanque ARLA", "LU0568-Filtro boia tanque ARLA"],
        "materiais": {"Código": ["28798", "28799", "F-DPF"], "Descrição": ["KIT FILTRO AR ARLA VO24147170", "FILTRO BOIA TANQUE VO24111100", "ELEMENTO FILTRO PARTICULADOS DPF"], "Qtd": ["1 KIT", "1 PC", "1 PC"]}
    }
}

if 'historico' not in st.session_state:
    st.session_state.historico = []
def calcular_previsao_dias(horas_restantes, media_diaria):
    if horas_restantes <= 0: return None
    if media_diaria <= 0: return None
    dias_uteis = int(np.ceil(horas_restantes / media_diaria))
    hoje = datetime.date.today()
    data_futura = np.busday_offset(hoje, dias_uteis, roll='forward')
    return pd.to_datetime(data_futura).date()

aba1, aba2, aba3 = st.tabs(["📊 Painel Multigatilhos (Todas Sequências)", "👨‍🔧 Oficina / Lançamentos", "📋 Histórico de Crise"])

with aba1:
    st.subheader(f"Situação dos Ciclos de Manutenção Preventiva - Ativo: {st.session_state.frota_ca0024['id']}")
    st.markdown(f"**Contador Atual:** `{st.session_state.frota_ca0024['atual']} hrs` | **Ritmo:** `10 horas/dia útil` (Sáb/Dom desconsiderados)")
    
    dados_painel = []
    hoje = datetime.date.today()
    
    for seq_id, seq in st.session_state.frota_ca0024["sequencias"].items():
        dt_ult_manut = datetime.datetime.strptime(seq["ult_data"], "%d/%m/%Y").date()
        
        meta_exibicao = "-"
        data_alvo_final = None
        status = "🟢 OK"
        
        # 1. CÁLCULO PELO GATILHO DE HORAS
        if seq["tipo"] == "Horas" or seq["tipo"] == "Misto":
            horas_desde_ult = st.session_state.frota_ca0024['atual'] - seq["ult_h"]
            multiplicador = int(np.floor(horas_desde_ult / seq["intervalo_h"])) + 1
            horas_alvo = seq["ult_h"] + (seq["intervalo_h"] * multiplicador)
            meta_exibicao = f"{horas_alvo} hrs"
            
            horas_restantes = horas_alvo - st.session_state.frota_ca0024['atual']
            data_alvo_final = calcular_previsao_dias(horas_restantes, st.session_state.frota_ca0024['media_diaria'])
            
            if st.session_state.frota_ca0024['atual'] >= horas_alvo: 
                status = "🔴 VENCIDA (Horas)"
                data_alvo_final = "IMEDIATO"
                
        # 2. CÁLCULO PELO GATILHO DE TEMPO (CORREÇÃO DO CALENDÁRIO 2026/2027)
        if seq["tipo"] == "Tempo" or seq["tipo"] == "Misto":
            intervalo_dias = seq["intervalo_dias"] if "intervalo_dias" in seq else 365
            data_limite_tempo = dt_ult_manut + datetime.timedelta(days=intervalo_dias)
            
            if seq["tipo"] == "Tempo":
                meta_exibicao = data_limite_tempo.strftime('%d/%m/%Y')
                if hoje >= data_limite_tempo:
                    status = "🔴 VENCIDA (Tempo)"
                    data_alvo_final = "IMEDIATO"
                else:
                    data_util = np.busday_offset(data_limite_tempo, 0, roll='forward')
                    data_alvo_final = pd.to_datetime(data_util).date()
            else:
                # Regra Avançada Mista: "O que ocorrer primeiro"
                if hoje >= data_limite_tempo:
                    status = "🔴 VENCIDA (Tempo)"
                    data_alvo_final = "IMEDIATO"
                elif data_alvo_final and isinstance(data_alvo_final, datetime.date):
                    if data_alvo_final > data_limite_tempo:
                        # Vence por tempo antes das horas estourarem
                        data_util = np.busday_offset(data_limite_tempo, 0, roll='forward')
                        data_alvo_final = pd.to_datetime(data_util).date()

        # Formata o texto final da Data Alvo na tabela
        texto_data_alvo = "IMEDIATO"
        if data_alvo_final != "IMEDIATO" and data_alvo_final is not None:
            texto_data_alvo = data_alvo_final.strftime('%d/%m/%Y') if isinstance(data_alvo_final, datetime.date) else str(data_alvo_final)
        elif data_alvo_final is None:
            texto_data_alvo = "-"

        dados_painel.append({
            "Seq": seq_id,
            "Descrição da Frequência Mestre": seq["nome"],
            "Última Execução": f"{seq['ult_h']} hrs ({seq['ult_data']})",
            "Próxima Meta": meta_exibicao,
            "Data Alvo": texto_data_alvo,
            "Status": status
        })
        
    st.dataframe(pd.DataFrame(dados_painel), use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("🔍 Consulta Detalhada de Escopo de Tarefas e Insumos Faturados")
    seq_sel = st.selectbox("Selecione uma sequência para abrir o espelho de requisição do Protheus/RM:", ["001", "002", "003"])
    if seq_sel in escopos_preventivas:
        escopo = escopos_preventivas[seq_sel]
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**📋 Lista de Tarefas Mecânicas:**")
            for t in escopo["tarefas"]: st.write(t)
        with col2:
            st.markdown("**📦 Código de Produtos e Consumo Real:**")
            st.table(pd.DataFrame(escopo["materiais"]))

# ABA 2: ENTRADA DE DADOS DA OFICINA
with aba2:
    st.subheader("Registrar Apontamento de Campo")
    with st.form("form_oficina"):
        novo_h = st.number_input("Digite o Horímetro Atualizado do CA0024:", min_value=0, value=st.session_state.frota_ca0024["atual"])
        seq_executada = st.selectbox("Alguma sequência foi executada por completo?", ["Nenhuma"] + [f"{k} - {v['nome']}" for k, v in st.session_state.frota_ca0024["sequencias"].items()])
        enviar = st.form_submit_button("Lançar na Oficina")
        if enviar:
            st.session_state.frota_ca0024["atual"] = novo_h
            if "Nenhuma" not in seq_executada:
                cod_seq = seq_executada.split(" - ")[0]
                st.session_state.frota_ca0024["sequencias"][cod_seq]["ult_h"] = novo_h
                st.session_state.frota_ca0024["sequencias"][cod_seq]["ult_data"] = datetime.date.today().strftime('%d/%m/%Y')
                st.session_state.historico.append({"Data Lançamento": datetime.date.today().strftime('%d/%m/%Y'), "Sequência Baixada": seq_executada, "Horímetro no Fechamento": novo_h})
            st.success("✔️ Registro gravado com sucesso! Prazos recalculados.")
            st.rerun()

# ABA 3: HISTÓRICO DE CRISE
with aba3:
    st.subheader("Histórico de Ordens de Serviço Executadas Manualmente")
    if len(st.session_state.historico) == 0:
        st.info("Nenhuma preventiva baixada durante o período de contingência.")
    else:
        st.dataframe(pd.DataFrame(st.session_state.historico), use_container_width=True, hide_index=True)

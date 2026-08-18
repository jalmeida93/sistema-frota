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

# BANCO DE DADOS DETALHADO DA FROTA (CA0024 E CA0025 REGULADOS COM HISTÓRICO REAL DO PROTHEUS)
if 'banco_frota' not in st.session_state:
    st.session_state.banco_frota = {
        "CA0024": {
            "id": "CA0024", "nome": "Volvo VM 360 - 01", "atual": 3443, "media_diaria": 10,
            "sequencias": {
                "001": {"nome": "600H/15.000KM/1A", "tipo": "Misto", "intervalo_h": 600, "ult_h": 3009, "ult_data": "13/06/2026"},
                "002": {"nome": "1200H/1A", "tipo": "Misto", "intervalo_h": 1200, "ult_h": 2456, "ult_data": "03/03/2026"},
                "003": {"nome": "3600H/65.000KM", "tipo": "Horas", "intervalo_h": 3600, "ult_h": 1, "ult_data": "10/08/2024"},
                "004": {"nome": "4800H/150.000KM", "tipo": "Horas", "intervalo_h": 4800, "ult_h": 1, "ult_data": "10/08/2024"},
                "005": {"nome": "1S (Semanal)", "tipo": "Tempo", "intervalo_dias": 7, "ult_h": 3443, "ult_data": "11/08/2026"},
                "007": {"nome": "4000H/2A/200.000KM", "tipo": "Misto", "intervalo_h": 4000, "ult_h": 1, "ult_data": "10/08/2024"},
                "008": {"nome": "180.000KM", "tipo": "Horas", "intervalo_h": 4500, "ult_h": 1, "ult_data": "10/08/2024"},
                "009": {"nome": "4A/500.000KM", "tipo": "Tempo", "intervalo_dias": 1460, "ult_h": 1, "ult_data": "10/08/2024"}
            }
        },
        "CA0025": {
            "id": "CA0025", "nome": "Volvo VM 360 - 02", "atual": 3823, "media_diaria": 10,
            "sequencias": {
                "001": {"nome": "600H/15.000KM/1A", "tipo": "Misto", "intervalo_h": 600, "ult_h": 3655, "ult_data": "25/07/2026"},
                "002": {"nome": "1200H/1A", "tipo": "Misto", "intervalo_h": 1200, "ult_h": 3655, "ult_data": "25/07/2026"},
                "003": {"nome": "3600H/65.000KM", "tipo": "Horas", "intervalo_h": 3600, "ult_h": 3655, "ult_data": "25/07/2026"},
                "004": {"nome": "4800H/150.000KM", "tipo": "Horas", "intervalo_h": 4800, "ult_h": 1, "ult_data": "10/08/2024"},
                "005": {"nome": "1S (Semanal)", "tipo": "Tempo", "intervalo_dias": 7, "ult_h": 3823, "ult_data": "11/08/2026"},
                "007": {"nome": "4000H/2A/200.000KM", "tipo": "Misto", "intervalo_h": 4000, "ult_h": 1, "ult_data": "10/08/2024"},
                "008": {"nome": "180.000KM", "tipo": "Horas", "intervalo_h": 4500, "ult_h": 1, "ult_data": "10/08/2024"},
                "009": {"nome": "4A/500.000KM", "tipo": "Tempo", "intervalo_dias": 1460, "ult_h": 1, "ult_data": "10/08/2024"}
            }
        }
    }

# DICIONÁRIO MASTRUZ COMPLETO COM TODAS AS 8 SEQUÊNCIAS DO PROTHEUS DA NOVAVIA
escopos_preventivas = {
    "001": {
        "tarefas": ["LU0389-Substituir óleo motor", "LU0329-Substituir filtro óleo do motor", "LU0322-Substituir filtro combustível", "LU0348-Substituir filtro separador de água", "LU0319-Substituir filtro de ar primário", "LU0153 / LU0416-Lubrificação geral do chassi e suspensão dianteira", "LU0495 / LU0499-Engraxar alavanca de ajuste do eixo came e pino mestre", "LU0474-Substituir o filtro antipólen do ar condicionado"],
        "materiais": {"Código": ["27241", "27179", "27179", "27180", "27181", "27182", "27893", "16657"], "Descrição": ["ÓLEO LUBRIFICANTE SAE 10W30 VDS-4.5", "TRAPO PARA LIMPEZA", "FILTRO ÓLEO VO24063074 CAMINHÃO VOLVO", "FILTRO COMBUSTÍVEL VO24275477 CAMINHÃO", "FILTRO VO24275463 CAMINHÃO VOLVO VM 36", "FILTRO AR VO21436535 CAMINHÃO VOLVO V", "FILTRO AR CONDICIONADO VO85134455 CAMI", "GRAXA MINERAL SABÃO DE LÍTIO NLGI 2 EP"], "Qtd": ["24,00 L", "3,00 KG", "1,00 PC", "1,00 PC", "1,00 PC", "1,00 PC", "1,00 PC", "1,70 KG"]}
    },
    "002": {
        "tarefas": ["LU0303-Substituir óleo do câmbio e limpeza do respiro", "LU0341-Substituir filtro do óleo de transmissão e diferencial", "LU0386-Substituir óleo do eixo dianteiro", "LU0387-Substituir óleo do eixo traseiro", "LU0562 / LU0563-Substituir óleo do cubo dianteiro (Dir/Esq)", "LU0564 / LU0565-Substituir óleo do cubo traseiro (Dir/Esq)"],
        "materiais": {"Código": ["27348", "27839", "27239"], "Descrição": ["ÓLEO SAE 50 TO-4 / ALLISON C-4", "FILTRO CAIXA DE MUDANÇA VO24283117 CAM", "ÓLEO DIFERENCIAL 85W140 VO85131721 CAM"], "Qtd": ["18,00 L", "1,00 PC", "43,50 L"]}
    },
    "003": {
        "tarefas": ["LU0501-Substituir elemento do filtro de particulados (DPF)", "LU0567-Substituir filtro do tanque do ARLA", "LU0568-Filtro boia tanque ARLA"],
        "materiais": {"Código": ["28798", "28799", "F-DPF"], "Descrição": ["KIT FILTRO AR ARLA VO24147170 CAMINHÃO", "FILTRO BOIA TANQUE ARLA VO24111100 CAM", "ELEMENTO DO FILTRO DE PARTICULADOS (DPF)"], "Qtd": ["1,00 KIT", "1,00 PC", "1,00 PC"]}
    },
    "004": {
        "tarefas": ["ME0994-Ajuste regulagem nas unidades / válvulas injetoras do motor"],
        "materiais": {"Código": ["ESPECIALIDADE MEF"], "Descrição": ["MÃO DE OBRA ESPECIALIZADA MECÂNICO - FROTA"], "Qtd": ["0,50 H"]}
    },
    "005": {
        "tarefas": ["ME1027-Limpeza evaporador do ar", "ME0724-Inspecionar luz freio/sirene ré", "ME1020-Verificar buzina", "ME0370-Inspecionar freios", "LU0069/LU0077-Nível óleo motor e arrefecimento", "LU0070-Nível óleo direção hidráulica", "ME0887-Verificar separador água", "LU0050/LU0052-Filtros ar/cabine", "EL0007-Faróis e alarmes", "ME0026-Pressão e desgaste pneus"],
        "materiais": {"Código": ["SUP-01"], "Descrição": ["MATERIAIS DE APOIO / INSPEÇÃO VISUAL SEMANAL"], "Qtd": ["1,00 AP"]}
    },
    "007": {
        "tarefas": ["ME0991-Substituir correia transmissão motriz", "LU0357-Substituir fluido direção hidráulica", "LU0324-Substituir filtro direção hidráulica"],
        "materiais": {"Código": ["27184", "09814", "28850"], "Descrição": ["CORREIA TRANSMISSÃO VO22707521 CAMINHA", "ÓLEO HIDRÁULICO DIREÇÃO/TRANSMISSÃO TE", "FILTRO DIREÇÃO HIDRÁULICA VO21519716 C"], "Qtd": ["1,00 PC", "4,00 L", "1,00 PC"]}
    },
    "008": {
        "tarefas": ["LU0503-Substituir sensor de oxigênio (Sonda Lambda original)"],
        "materiais": {"Código": ["S-OXIG"], "Descrição": ["SENSOR DE OXIGÊNIO ORIGINAL VOLVO VM"], "Qtd": ["1,00 PC"]}
    },
    "009": {
        "tarefas": ["LU0358-Substituir líquido de arrefecimento (Aditivo VCS2 Laranja)", "LU0342-Substituir filtro secador APU", "ME0992-Substituir esticador correia motriz", "ME0993-Substituir polia intermediária correia"],
        "materiais": {"Código": ["27285", "27183", "27185", "27186"], "Descrição": ["ADITIVO VOLVO VCS2 (40% A 60%) LARANJA", "FILTRO SECADOR VO21620181 CAMINHAO VOL", "ESTICADOR CORREIA VO22307253 CAMINHÃO", "POLIA INTERMEDIARIA VO22307251 CAMINHA"], "Qtd": ["32,00 L", "1,00 PC", "1,00 PC", "1,00 PC"]}
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

# SELEÇÃO INDIVIDUAL DO VEÍCULO NO TOPO DA PÁGINA
tag_selecionado = st.selectbox(" 🚛 Selecione o Veículo para Gerenciamento:", list(st.session_state.banco_frota.keys()))
ativo_atual = st.session_state.banco_frota[tag_selecionado]

aba1, aba2, aba3 = st.tabs(["📊 Painel Multigatilhos", "👨‍🔧 Oficina / Lançamentos", "📋 Histórico de Crise"])

with aba1:
    st.subheader(f"Situação dos Ciclos de Manutenção Preventiva - Ativo: {ativo_atual['id']}")
    st.markdown(f"**Contador Atual:** `{ativo_atual['atual']} hrs` | **Ritmo:** `{ativo_atual['media_diaria']} horas/dia útil` (Sáb/Dom desconsiderados)")
    
    dados_painel = []
    hoje = datetime.date.today()
    
    for seq_id, seq in ativo_atual["sequencias"].items():
        dt_ult_manut = datetime.datetime.strptime(seq["ult_data"], "%d/%m/%Y").date()
        meta_exibicao = "-"
        data_alvo_final = None
        status = "🟢 OK"
        
        if seq["tipo"] == "Horas" or seq["tipo"] == "Misto":
            horas_desde_ult = ativo_atual['atual'] - seq["ult_h"]
            multiplicador = int(np.floor(horas_desde_ult / seq["intervalo_h"])) + 1
            horas_alvo = seq["ult_h"] + (seq["intervalo_h"] * multiplicador)
            meta_exibicao = f"{horas_alvo} hrs"
            horas_restantes = horas_alvo - ativo_atual['atual']
            data_alvo_final = calcular_previsao_dias(horas_restantes, ativo_atual['media_diaria'])
            if ativo_atual['atual'] >= horas_alvo: 
                status = "🔴 VENCIDA (Horas)"
                data_alvo_final = "IMEDIATO"
                
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
                if hoje >= data_limite_tempo:
                    status = "🔴 VENCIDA (Tempo)"
                    data_alvo_final = "IMEDIATO"
                elif data_alvo_final and isinstance(data_alvo_final, datetime.date):
                    if data_alvo_final > data_limite_tempo:
                        data_util = np.busday_offset(data_limite_tempo, 0, roll='forward')
                        data_alvo_final = pd.to_datetime(data_util).date()

        texto_data_alvo = "IMEDIATO"
        if data_alvo_final != "IMEDIATO" and data_alvo_final is not None:
            texto_data_alvo = data_alvo_final.strftime('%d/%m/%Y') if isinstance(data_alvo_final, datetime.date) else str(data_alvo_final)
        elif data_alvo_final is None:
            texto_data_alvo = "-"

        dados_painel.append({
            "Seq": seq_id, "Descrição da Frequência Mestre": seq["nome"], "Última Execução": f"{seq['ult_h']} hrs ({seq['ult_data']})",
            "Próxima Meta": meta_exibicao, "Data Alvo": texto_data_alvo, "Status": status
        })
    st.dataframe(pd.DataFrame(dados_painel), use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("🔍 Consulta Detalhada de Escopo de Tarefas e Insumos Faturados")
    seq_sel = st.selectbox("Selecione uma sequência ativa para abrir o espelho de requisição do Protheus/RM:", list(escopos_preventivas.keys()))
    if seq_sel in escopos_preventivas:
        escopo = escopos_preventivas[seq_sel]
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**📋 Lista de Tarefas Mecânicas (Sequência {seq_sel}):**")
            for t in escopo["tarefas"]: st.write(t)
        with col2:
            st.markdown(f"**📦 Código de Produtos e Consumo Real (Espelho RM):**")
            dados_tabela = escopo["materials"] if "materials" in escopo else escopo["materiais"]
            st.table(pd.DataFrame(dados_tabela))

# ABA 2: ENTRADA DE DADOS DA OFICINA COMPLETA COM CAMPOS DE DATA
with aba2:
    st.subheader("Registrar Apontamento de Campo")
    with st.form("form_oficina_melhorado", clear_on_submit=True):
        col_form1, col_form2 = st.columns(2)
        with col_form1:
            novo_h = st.number_input(f"Digite o Horímetro Lido no Painel do {ativo_atual['id']}:", min_value=0, value=ativo_atual["atual"])
            data_leitura = st.date_input("📅 Data da Leitura do Horímetro:", datetime.date.today())
        with col_form2:
            seq_executada = st.selectbox("Alguma sequência foi executada por completo?", ["Nenhuma"] + [f"{k} - {v['nome']}" for k, v in ativo_atual["sequencias"].items()])
            data_execucao_preventiva = st.date_input("🛠️ Data Real da Execução da Sequência:", datetime.date.today())

        num_os_manual = st.text_input("Nº da OS em Papel (Manual):", placeholder="Opcional")
        num_rm = st.text_input("Nº da Requisição gerada no RM:", placeholder="Opcional")
        foto_os = st.file_uploader("📷 Anexe a foto da OS física:", type=["jpg", "jpeg", "png", "pdf"])
        
        enviar = st.form_submit_button("Lançar Informações de Campo")
        
        if enviar:
            st.session_state.banco_frota[tag_selecionado]["atual"] = novo_h
            texto_acao = "Apenas Atualização de Horímetro"
            dt_registro_final = data_leitura.strftime('%d/%m/%Y')
            
            if "Nenhuma" not in seq_executada:
                cod_seq = seq_executada.split(" - ")[0]
                dt_registro_final = data_execucao_preventiva.strftime('%d/%m/%Y')
                st.session_state.banco_frota[tag_selecionado]["sequencias"][cod_seq]["ult_h"] = novo_h
                st.session_state.banco_frota[tag_selecionado]["sequencias"][cod_seq]["ult_data"] = dt_registro_final
                texto_acao = f"Fechamento Completo da Sequência {cod_seq}"
                
            nome_foto = foto_os.name if foto_os is not None else "Nao anexada"
            st.session_state.historico.append({
                "Data Lançamento": datetime.date.today().strftime('%d/%m/%Y'),
                "Ativo / TAG": tag_selecionado,
                "Data Ocorrência (Campo)": dt_registro_final,
                "Horímetro Informado": f"{novo_h} hrs",
                "Ação Executada": texto_acao,
                "OS Papel": num_os_manual if num_os_manual else "-",
                "REQ RM": num_rm if num_rm else "-",
                "Evidência": nome_foto
            })
            st.success("✔️ Informações de campo processadas com sucesso! Calendário de preventivas atualizado.")
            st.rerun()

# ABA 3: HISTÓRICO DE CRISE
with aba3:
    st.subheader("Histórico de Ordens de Serviço Executadas Manualmente")
    if len(st.session_state.historico) == 0:
        st.info("Nenhuma preventiva baixada durante o período de contingência.")
    else:
        st.dataframe(pd.DataFrame(st.session_state.historico), use_container_width=True, hide_index=True)

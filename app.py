import streamlit as st
import pandas as pd
import datetime
import numpy as np
import io
from fpdf import FPDF

st.set_page_config(page_title="Plano Preventivas Novavia Mineração", layout="wide", page_icon="🏗️")

# 1. IDENTIDADE VISUAL OFICIAL NOVAVIA MINERAÇÃO
col_logo, col_titulo = st.columns()
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
            "ult_rev_data": "13/06/2026", 
            "media": 10
        }
    ]

# DICIONÁRIO COMPLETO COM AS 9 SEQUÊNCIAS DO PROTHEUS DO GRUPO NOVA VIA
escopos_preventivas = {
    "Sequência 001 (600h)": {
        "tarefas": [
            "LU0389 - Substituir óleo do motor", "LU0329 - Substituir filtro de óleo do motor",
            "LU0322 - Substituir filtro de combustível", "LU0348 - Substituir filtro separador de água",
            "LU0319 - Substituir filtro de ar primário", "LU0153 / LU0416 - Lubrificação geral do chassi e suspensão dianteira",
            "LU0495 / LU0499 - Engraxar alavanca de ajuste do eixo came e pino mestre",
            "LU0474 - Substituir o filtro antipólen do ar condicionado (Reduzido para 600h devido às condições de trabalho)"
        ],
        "materiais": {
            "Código": ["27241", "27179", "27179", "27180", "27181", "27182", "27893", "16657"],
            "Descrição do Insumo": ["ÓLEO LUBRIFICANTE SAE 10W30 VDS-4.5", "TRAPO PARA LIMPEZA", "FILTRO ÓLEO VO24063074 CAMINHÃO VOLVO", "FILTRO COMBUSTÍVEL VO24275477 CAMINHÃO", "FILTRO VO24275463 CAMINHÃO VOLVO VM 36", "FILTRO AR VO21436535 CAMINHÃO VOLVO V", "FILTRO AR CONDICIONADO VO85134455 CAMI", "GRAXA MINERAL SABÃO DE LÍTIO NLGI 2 EP"],
            "Qtd": ["24,00 L", "3,00 KG", "1,00 PC", "1,00 PC", "1,00 PC", "1,00 PC", "1,00 PC", "1,70 KG"]
        }
    },
    "Sequência 002 (1200h)": {
        "tarefas": [
            "LU0303 - Substituir óleo do câmbio e limpeza do respiro (Permitido adicionar 2L acima do nível para mineração)",
            "LU0341 - Substituir filtro do óleo de transmissão e diferencial", "LU0386 - Substituir óleo do eixo dianteiro",
            "LU0387 - Substituir óleo do eixo traseiro", "LU0562 / LU0563 - Substituir óleo do cubo dianteiro (Dir/Esq)",
            "LU0564 / LU0565 - Substituir óleo do cubo traseiro (Dir/Esq)"
        ],
        "materiais": {
            "Código": ["27348", "27839", "27239"],
            "Descrição do Insumo": ["ÓLEO SAE 50 TO-4 / ALLISON C-4", "FILTRO CAIXA DE MUDANÇA VO24283117 CAM", "ÓLEO DIFERENCIAL 85W140 VO85131721 CAM"],
            "Qtd": ["18,00 L", "1,00 PC", "43,50 L"]
        }
    },
    "Sequência 003 (3600h)": {
        "tarefas": [
            "LU0501 - Substituir elemento do filtro de particulados (DPF)",
            "LU0567 - Substituir filtro do tanque do ARLA", "LU0568 - Substituir filtro da boia do tanque do ARLA"
        ],
        "materiais": {
            "Código": ["28798", "28799", "F-DPF"],
            "Descrição do Insumo": ["KIT FILTRO AR ARLA VO24147170 CAMINHÃO", "FILTRO BOIA TANQUE ARLA VO24111100 CAM", "ELEMENTO DO FILTRO DE PARTICULADOS (DPF)"],
            "Qtd": ["1,00 KIT", "1,00 PC", "1,00 PC"]
        }
    },
    "Sequência 004 (4800h)": {
        "tarefas": ["ME0994 - Ajuste nas unidades / válvulas injetoras do motor (Regulagem mecânica de fábrica)"],
        "materiais": {
            "Código": ["MEC-01"],
            "Descrição do Insumo": ["MÃO DE OBRA ESPECIALIZADA MECÂNICO - FROTA"],
            "Qtd": ["0,50 H"]
        }
    },
    "Sequência 005 (Semanal)": {
        "tarefas": [
            "ME1027 - Realizar limpeza do evaporador do ar condicionado", "ME0724 - Inspecionar luz de freio e sirene de ré",
            "ME1020 - Verificar funcionamento da buzina (substituir se necessário)", "ME0370 - Inspecionar sistema de freio",
            "LU0069 / LU0077 - Inspecionar nível de óleo do motor e líquido de arrefecimento (completar se necessário)",
            "LU0070 - Inspecionar nível de óleo do reservatório da direção hidráulica", "ME0887 - Verificar nível do separador de água e drenar",
            "LU0050 / LU0052 - Inspecionar e limpar filtro de ar e filtro do ar condicionado",
            "EL0007 - Inspecionar faróis, iluminação de trabalho e alarme de marcha ré", "ME0026 - Conferir pressão, desgaste e danos nos pneus (fazer rodízio)"
        ],
        "materiais": {
            "Código": ["SUP-01"],
            "Descrição do Insumo": ["MATERIAIS DE APOIO / INSPECÇÃO VISUAL DIÁRIA/SEMANAL"],
            "Qtd": ["1,00 AP"]
        }
    },
    "Sequência 006 (Trimestral)": {
        "tarefas": ["LU0502 - Substituir tampa do reservatório de fluido de embreagem (Manutenção preventiva do sistema hidráulico)"],
        "materiais": {
            "Código": ["T-EMB"],
            "Descrição do Insumo": ["TAMPA DO RESERVATÓRIO FLUIDO DE EMBREAGEM"],
            "Qtd": ["1,00 PC"]
        }
    },
    "Sequência 007 (4000h / 2A)": {
        "tarefas": [
            "ME0991 - Substituir correia de transmissão motriz",
            "LU0357 - Substituir fluido do sistema da direção hidráulica",
            "LU0324 - Substituir filtro de direção hidráulica"
        ],
        "materiais": {
            "Código": ["27184", "09814", "28850"],
            "Descrição do Insumo": ["CORREIA TRANSMISSÃO VO22707521 CAMINHA", "ÓLEO HIDRÁULICO DIREÇÃO/TRANSMISSÃO TE", "FILTRO DIREÇÃO HIDRÁULICA VO21519716 C"],
            "Qtd": ["1,00 PC", "4,00 L", "1,00 PC"]
        }
    },
    "Sequência 008 (180.000KM)": {
        "tarefas": ["LU0503 - Substituir sensor de oxigênio (Garantia de controle de emissões e injeção eletrônica do veículo)"],
        "materiais": {
            "Código": ["S-OXIG"],
            "Descrição do Insumo": ["SENSOR DE OXIGÊNIO ORIGINAL VOLVO VM"],
            "Qtd": ["1,00 PC"]
        }
    },
    "Sequência 009 (4A / 500.000KM)": {
        "tarefas": [
            "LU0358 - Substituir líquido de arrefecimento completo (Aditivo VCS2 Laranja)",
            "LU0342 - Substituir filtro secador de ar do sistema pneumático (APU)",
            "ME0992 - Substituir esticador da correia motriz do motor",
            "ME0993 - Substituir polia intermediária da correia"
        ],
        "materiais": {
            "Código": ["27285", "27183", "27185", "27186"],
            "Descrição do Insumo": ["ADITIVO VOLVO VCS2 (40% A 60%) LARANJA", "FILTRO SECADOR VO21620181 CAMINHAO VOL", "ESTICADOR CORREIA VO22307253 CAMINHÃO", "POLIA INTERMEDIARIA VO22307251 CAMINHA"],
            "Qtd": ["32,00 L", "1,00 PC", "1,00 PC", "1,00 PC"]
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

    # DINÂMICA COMPLETA DE SELEÇÃO DE ESCOPO COM AS 9 SEQUÊNCIAS DO PROTHEUS
    st.markdown("---")
    st.subheader("🔍 Consulta Detalhada de Escopo de Tarefas e Insumos")
    sequencia_selecionada = st.selectbox("Selecione a Sequência de Preventiva para Visualizar o Escopo:", list(escopos_preventivas.keys()))
    
    with st.expander(f"📋 Visualizar Detalhes Operacionais - {sequencia_selecionada}", expanded=True):
        escopo = escopos_preventivas[sequencia_selecionada]
        col_esq, col_dir = st.columns(2)
        with col_esq:
            st.markdown("**📋 Lista de Tarefas do Protheus (O que executar):**")
            for tarefa in escopo["tarefas"]:
                st.write(tarefa)
        with col_dir:
            st.markdown("**📦 Insumos e Quantidades Homologadas (Espelho RM):**")
            st.table(pd.DataFrame(escopo["materiais"]))

# ABA 2: ENTRADA DE DADOS DA OFICINA
with aba2:
    st.subheader("Registrar Medição Diária")
    with st.form("form_ca0024"):
        novo_horimetro = st.number_input("Digite o Horímetro Atual do CA0024:", min_value=0, value=ativo['atual'])
        revisao_executada = st.selectbox("Preventiva executada?", ["Nenhuma"] + list(escopos_preventivas.keys()))
        enviar = st.form_submit_button("Salvar Registro")
        if enviar:
            for a in st.session_state.frota:
                a['atual'] = novo_horimetro
                if "Nenhuma" not in revisao_executada:
                    a['ult_rev_horas'] = novo_horimetro
                    a['ult_rev_data'] = datetime.date.today().strftime('%d/%m/%Y')
            st.success("✔️ Registro salvo com sucesso!")
            st.rerun()


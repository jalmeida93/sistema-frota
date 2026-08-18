import streamlit as st
import pandas as pd
import datetime
import numpy as np
import io
from fpdf import FPDF

# Configuração da página
st.set_page_config(page_title="Gestão Avançada de Frotas", layout="wide", page_icon="🚜")

# 1. BANCO DE DADOS AVANÇADO (Múltiplas Preventivas e Data Limite)
# "ult_rev_horas" e "ult_rev_data" marcam quando foi feita a última revisão geral (ponto zero)
if 'frota' not in st.session_state:
    st.session_state.frota = [
        {
            "id": "CA0024", 
            "nome": "Volvo VM 360 - 01", 
            "tipo": "Horas", 
            "atual": 4200, 
            "ult_rev_horas": 4000, 
            "ult_rev_data": "15/02/2026", 
            "media": 8,
            "pecas_250": "Filtro Óleo Motor, Óleo 15W40",
            "pecas_500": "Filtros de Combustível, Filtro Separador, Óleo Motor",
            "pecas_1000": "Filtros de Ar (Primário/Secundário), Óleo da Transmissão",
            "pecas_2000": "Óleo Hidráulico completo, Filtros Hidráulicos, Regulagem de Válvulas"
        },
        {
            "id": "L90-01", 
            "nome": "Carregadeira Volvo L90 - 01", 
            "tipo": "Horas", 
            "atual": 2420, 
            "ult_rev_horas": 2250, 
            "ult_rev_data": "20/08/2025", # Exemplo de máquina que vai vencer por tempo (1 ano)
            "media": 7,
            "pecas_250": "Filtro Motor, Óleo Lubrificante, Graxa EP2",
            "pecas_500": "Filtros de Combustível, Filtro Transmissão",
            "pecas_1000": "Óleo dos Eixos, Filtro de Ar",
            "pecas_2000": "Óleo Hidráulico, Filtros Hidráulicos"
        }
    ]

if 'historico' not in st.session_state:
    st.session_state.historico = []

# LÓGICA DE PROJEÇÃO PULANDO FINS DE SEMANA
def calcular_previsao_dias(horas_restantes, media_diaria):
    if media_diaria <= 0:
        return None
    dias_uteis = int(np.ceil(horas_restantes / media_diaria))
    hoje = datetime.date.today()
    data_futura = np.busday_offset(hoje, dias_uteis, roll='forward')
    return pd.to_datetime(data_futura).date()

# FUNÇÃO RESTRUTURADA DE GERAÇÃO DE PDF PARA O RM
def gerar_pdf_rm_avancado(ativo, plano_vencido, pecas):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="REQUISICAO DE MANUTENCAO - MODO CONTINGENCIA", ln=1, align="C")
    pdf.cell(200, 10, txt=f"Data: {datetime.date.today().strftime('%d/%m/%Y')}", ln=2, align="C")
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Equipamento: {ativo['nome']} ({ativo['id']})", ln=1)
    pdf.cell(200, 10, txt=f"Plano Disparado: {plano_vencido}", ln=1)
    pdf.cell(200, 10, txt=f"Horimetro Atual: {ativo['atual']} hrs", ln=1)
    pdf.ln(10)
    pdf.set_font("Arial", style="B", size=11)
    pdf.cell(140, 10, "Insumos Necessarios para Lancamento no RM", border=1)
    pdf.cell(40, 10, "Qtd", border=1, ln=1)
    pdf.set_font("Arial", size=10)
    for p in pecas.split(", "):
        pdf.cell(140, 10, p, border=1)
        pdf.cell(40, 10, "1", border=1, ln=1)
    return pdf.output(dest="S").encode("latin-1")

st.title("🛞 Painel de Manutenção Frota Pesada - Níveis Avançados")
st.warning("⚠️ Modo Contingência: Controle de múltiplos horizontes (250h a 2000h) ou 1 Ano.")

# BARRA LATERAL PARA EXPORTAR REQUISIÇÃO DO RM
st.sidebar.header("📄 Exportar Requisição RM")
lista_ids = [a['id'] for a in st.session_state.frota]
id_selecionado_rm = st.sidebar.selectbox("Selecione o ID para o PDF:", lista_ids)
plano_selecionado_rm = st.sidebar.selectbox("Selecione o Nível da OS:", ["PM 250h", "PM 500h", "PM 1000h", "PM 2000h", "Anual (Tempo)"])

ativo_ref = next(item for item in st.session_state.frota if item["id"] == id_selecionado_rm)
pecas_mapeadas = ativo_ref["pecas_250"]
if "500" in plano_selecionado_rm: pecas_mapeadas = ativo_ref["pecas_500"]
elif "1000" in plano_selecionado_rm: pecas_mapeadas = ativo_ref["pecas_1000"]
elif "2000" in plano_selecionado_rm: pecas_mapeadas = ativo_ref["pecas_2000"]

pdf_bytes = gerar_pdf_rm_avancado(ativo_ref, plano_selecionado_rm, pecas_mapeadas)
st.sidebar.download_button(
    label=f"📥 Baixar PDF {id_selecionado_rm} ({plano_selecionado_rm})",
    data=pdf_bytes,
    file_name=f"RM_{id_selecionado_rm}_{plano_selecionado_rm}.pdf",
    mime="application/pdf"
)

# ABAS DO SISTEMA
aba1, aba2, aba3 = st.tabs(["📊 Painel Multigatilhos", "👨‍🔧 Fechamento de OS (Oficina)", "📁 Histórico Geral"])

# ABA 1: PAINEL MULTIGATILHOS (Cálculo de Horas e 1 Ano)
with aba1:
    st.subheader("Situação dos Ciclos de Manutenção Preventiva")
    
    dados_painel = []
    hoje = datetime.date.today()
    
    for ativo in st.session_state.frota:
        horas_desde_ultima = ativo['atual'] - ativo['ult_rev_horas']
        
        # 1. Cálculo dos Gatilhos de Horas
        prox_250 = ativo['ult_rev_horas'] + 250
        prox_500 = ativo['ult_rev_horas'] + 500
        prox_1000 = ativo['ult_rev_horas'] + 1000
        prox_2000 = ativo['ult_rev_horas'] + 2000
        
        # 2. Cálculo do Gatilho de Tempo (1 Ano = 365 dias)
        data_ult = datetime.datetime.strptime(ativo['ult_rev_data'], "%d/%m/%Y").date()
        data_limite_tempo = data_ult + datetime.timedelta(days=365)
        
        # Identificar qual o próximo ciclo de horas que ainda não venceu
        if horas_desde_ultima < 250:
            proximo_ciclo_horas = "250h"
            horas_alvo = prox_250
        elif horas_desde_ultima < 500:
            proximo_ciclo_horas = "500h"
            horas_alvo = prox_500
        elif horas_desde_ultima < 1000:
            proximo_ciclo_horas = "1000h"
            horas_alvo = prox_1000
        else:
            proximo_ciclo_horas = "2000h"
            horas_alvo = prox_2000
            
        horas_restantes = horas_alvo - ativo['atual']
        data_prevista_horas = calcular_previsao_dias(horas_restantes, ativo['media'])
        
        # LÓGICA DO "O QUE OCORRER PRIMEIRO"
        status_geral = "🟢 OK"
        motivo_parada = f"Aguardando {proximo_ciclo_horas}"
        data_final_parada = data_prevista_horas if data_prevista_horas else data_limite_tempo
        
        # Verificação se estourou horas ou data limite
        if ativo['atual'] >= horas_alvo:
            status_geral = "🔴 VENCIDA (Horas)"
            motivo_parada = f"Estourou ciclo de {proximo_ciclo_horas}"
            data_final_parada = "IMEDIATO"
        elif hoje >= data_limite_tempo:
            status_geral = "🔴 VENCIDA (Tempo - 1 Ano)"
            motivo_parada = "Atingiu limite de 1 ano parado/rodando"
            data_final_parada = "IMEDIATO"
        elif data_prevista_horas and data_prevista_horas > data_limite_tempo:
            # Se a máquina roda pouco, ela vai vencer por tempo antes de bater as horas!
            motivo_parada = f"Vai vencer por Tempo (1 Ano) antes das horas"
            data_final_parada = data_limite_tempo
            if (data_limite_tempo - hoje).days <= 10:
                status_geral = "🟡 PRÓXIMA (Tempo)"
        elif horas_restantes <= (ativo['media'] * 3):
            status_geral = "🟡 PRÓXIMA (Horas)"
            motivo_parada = f"Próxima de bater {proximo_ciclo_horas}"

        dados_painel.append({
            "ID / TAG": ativo['id'],
            "Equipamento": ativo['nome'],
            "Horímetro Atual": f"{ativo['atual']} hrs",
            "Última Revisão Geral": f"{ativo['ult_rev_horas']} hrs ({ativo['ult_rev_data']})",
            "Próxima Meta (Horas)": f"{horas_alvo} hrs ({proximo_ciclo_horas})",
            "Prazo Limite (Tempo)": data_limite_tempo.strftime('%d/%m/%Y'),
            "Data Alvo Prevista": data_final_parada.strftime('%d/%m/%Y') if isinstance(data_final_parada, datetime.date) else data_final_parada,
            "Diagnóstico / Ação": motivo_parada,
            "Status Geral": status_geral
        })
        
    st.dataframe(pd.DataFrame(dados_painel), use_container_width=True, hide_index=True)

# ABA 2: FECHAMENTO DE OS (OFICINA)
with aba2:
    st.subheader("Registrar Medição Diária e Execução de Revisões")
    
    with st.form("form_mecanico_avancado", clear_on_submit=True):
        lista_nomes = [f"{a['id']} - {a['nome']}" for a in st.session_state.frota]
        selecionado = st.selectbox("Escolha o Equipamento:", lista_nomes)
        id_sel = selecionado.split(" - ")[0]
        
        num_os_manual = st.text_input("Nº da OS em Papel (Manual):", placeholder="Ex: OS-MNT-2026")
        num_rm = st.text_input("Nº da Requisição gerada no RM:", placeholder="Ex: REQ-10452")
        novo_horimetro = st.number_input("Digite o Horímetro Atual da Máquina:", min_value=0, step=1)
        
        st.markdown("---")
        st.markdown("**Se alguma revisão foi executada por completo, selecione abaixo para resetar os ciclos:**")
        revisao_executada = st.selectbox("Alguma preventiva foi realizada?", ["Nenhuma - Apenas atualizar horímetro", "Concluída PM 250h", "Concluída PM 500h", "Concluída PM 1000h", "Concluída PM 2000h", "Concluída Revisão Anual por Tempo"])
        
        foto_os = st.file_uploader("📷 Anexe a foto da OS física preenchida/assinada:", type=["jpg", "jpeg", "png", "pdf"])
        enviar = st.form_submit_button("Salvar Registro de Oficina")
        
        if enviar:
            for a in st.session_state.frota:
                if a['id'] == id_sel:
                    a['atual'] = novo_horimetro
                    
                    # Se fez qualquer revisão, atualiza o ponto zero de contagem de horas ou data
                    if "Concluída PM" in revisao_executada:
                        a['ult_rev_horas'] = novo_horimetro
                        a['ult_rev_data'] = datetime.date.today().strftime('%d/%m/%Y')
                    elif "Anual" in revisao_executada:
                        a['ult_rev_data'] = datetime.date.today().strftime('%d/%m/%Y')
                        
                    nome_foto = foto_os.name if foto_os is not None else "Não anexada"
                    st.session_state.historico.append({

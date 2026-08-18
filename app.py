import streamlit as st
import pandas as pd
import datetime
import numpy as np
import io
from fpdf import FPDF

st.set_page_config(page_title="Gestao Avançada de Frotas", layout="wide", page_icon="🚜")

if 'frota' not in st.session_state:
    st.session_state.frota = [
        {"id": "CA0024", "nome": "Volvo VM 360 - 01", "tipo": "Horas", "atual": 3443, "ult_rev_horas": 3009, "ult_rev_data": "13/06/2026", "media": 8, "pecas_250": "Filtro Oleo Motor, Oleo 15W40", "pecas_500": "Filtros Combustivel, Filtro Separador", "pecas_1000": "Filtros de Ar, Oleo Transmissao", "pecas_2000": "Oleo Hidraulico, Filtros Hidraulicos"},
        {"id": "VM360-02", "nome": "Volvo VM 360 - 02", "tipo": "Horas", "atual": 0, "ult_rev_horas": 0, "ult_rev_data": "18/08/2026", "media": 8, "pecas_250": "Filtro Oleo Motor, Oleo 15W40", "pecas_500": "Filtros Combustivel", "pecas_1000": "Filtros Ar", "pecas_2000": "Oleo Transmissao e Diferencial"},
        {"id": "VM360-03", "nome": "Volvo VM 360 - 03", "tipo": "Horas", "atual": 0, "ult_rev_horas": 0, "ult_rev_data": "18/08/2026", "media": 8, "pecas_250": "Filtro Oleo Motor, Oleo 15W40", "pecas_500": "Filtros Combustivel", "pecas_1000": "Filtros Ar", "pecas_2000": "Oleo Transmissao e Diferencial"},
        {"id": "IV260-01", "nome": "Iveco 260E25", "tipo": "Horas", "atual": 0, "ult_rev_horas": 0, "ult_rev_data": "18/08/2026", "media": 6, "pecas_250": "Filtro Oleo Lubrificante, Oleo Motor", "pecas_500": "Filtros Combustivel", "pecas_1000": "Filtros de Ar", "pecas_2000": "Kit de Freios e Ajustes"},
        {"id": "IVDY-01", "nome": "Iveco Daily 170-43", "tipo": "Horas", "atual": 0, "ult_rev_horas": 0, "ult_rev_data": "18/08/2026", "media": 4, "pecas_250": "Filtro Oleo, Oleo Sintetico", "pecas_500": "Filtro de Combustivel", "pecas_1000": "Filtro de Ar", "pecas_2000": "Revisao Geral de Suspensao"},
        {"id": "L90-01", "nome": "Carregadeira Volvo L90 - 01", "tipo": "Horas", "atual": 2420, "ult_rev_horas": 2250, "ult_rev_data": "20/08/2025", "media": 7, "pecas_250": "Filtro Motor, Oleo, Graxa EP2", "pecas_500": "Filtros Combustivel, Filtro Transmissao", "pecas_1000": "Oleo dos Eixos, Filtro de Ar", "pecas_2000": "Oleo Hidraulico, Filtros Hidraulicos"},
        {"id": "L90-02", "nome": "Carregadeira Volvo L90 - 02", "tipo": "Horas", "atual": 0, "ult_rev_horas": 0, "ult_rev_data": "18/08/2026", "media": 7, "pecas_250": "Filtro Motor, Graxa EP2", "pecas_500": "Filtros Combustivel", "pecas_1000": "Oleo dos Eixos", "pecas_2000": "Oleo Hidraulico completo"},
        {"id": "L90-03", "nome": "Carregadeira Volvo L90 - 03", "tipo": "Horas", "atual": 0, "ult_rev_horas": 0, "ult_rev_data": "18/08/2026", "media": 7, "pecas_250": "Filtro Motor, Graxa EP2", "pecas_500": "Filtros Combustivel", "pecas_1000": "Oleo dos Eixos", "pecas_2000": "Oleo Hidraulico completo"},
        {"id": "JH120-EL", "nome": "Carregadeira Eletr JH120", "tipo": "Horas", "atual": 0, "ult_rev_horas": 0, "ult_rev_data": "18/08/2026", "media": 5, "pecas_250": "Graxa Articulacoes, Inspecao Cabos", "pecas_500": "Filtro de Cabine", "pecas_1000": "Fluido Arrefecimento Bateria", "pecas_2000": "Inspecao Motor Eletrico e Torque"},
        {"id": "SAV-01", "nome": "Caminhonete Saveiro", "tipo": "Horas", "atual": 0, "ult_rev_horas": 0, "ult_rev_data": "18/08/2026", "media": 2, "pecas_250": "Filtro Oleo, Oleo Sintetico", "pecas_500": "Filtro de Ar e Combustivel", "pecas_1000": "Velas de Ignicao", "pecas_2000": "Correia Dentada e Tensores"},
        {"id": "EC350-01", "nome": "Escavadeira Volvo EC350", "tipo": "Horas", "atual": 0, "ult_rev_horas": 0, "ult_rev_data": "18/08/2026", "media": 8, "pecas_250": "Filtro Oleo Motor, Graxa EP2", "pecas_500": "Filtros Combustivel Separador", "pecas_1000": "Oleo Comando Final", "pecas_2000": "Oleo Hidraulico e Elementos"},
        {"id": "EC380-01", "nome": "Escavadeira Volvo EC380", "tipo": "Horas", "atual": 0, "ult_rev_horas": 0, "ult_rev_data": "18/08/2026", "media": 9, "pecas_250": "Filtro Oleo Motor, Graxa EP2", "pecas_500": "Filtros Combustivel Separador", "pecas_1000": "Oleo Comando Final", "pecas_2000": "Oleo Hidraulico e Elementos"},
        {"id": "EC240-01", "nome": "Escavadeira Volvo EC240", "tipo": "Horas", "atual": 0, "ult_rev_horas": 0, "ult_rev_data": "18/08/2026", "media": 8, "pecas_250": "Filtro Oleo Motor, Graxa EP2", "pecas_500": "Filtros Combustivel Separador", "pecas_1000": "Oleo Comando Final", "pecas_2000": "Oleo Hidraulico e Elementos"},
        {"id": "PC350-01", "nome": "Escavadeira Komatsu PC350", "tipo": "Horas", "atual": 0, "ult_rev_horas": 0, "ult_rev_data": "18/08/2026", "media": 8, "pecas_250": "Filtro Oleo Lubrificante, Graxa", "pecas_500": "Filtros de Combustivel", "pecas_1000": "Elemento Filtro de Ar", "pecas_2000": "Oleo Hidraulico e Filtro de Linha"}
    ]
if 'historico' not in st.session_state:
    st.session_state.historico = []

def calcular_previsao_dias(horas_restantes, media_diaria):
    if media_diaria <= 0: return None
    dias_uteis = int(np.ceil(horas_restantes / media_diaria))
    hoje = datetime.date.today()
    data_futura = np.busday_offset(hoje, dias_uteis, roll='forward')
    return pd.to_datetime(data_futura).date()

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
    label=f"📥 Baixar PDF {id_selecionado_rm}",
    data=pdf_bytes,
    file_name=f"RM_{id_selecionado_rm}_{plano_selecionado_rm}.pdf",
    mime="application/pdf"
)

aba1, aba2, aba3 = st.tabs(["📊 Painel Multigatilhos", "👨‍🔧 Fechamento de OS (Oficina)", "📁 Histórico Geral"])

with aba1:
    st.subheader("Situação dos Ciclos de Manutenção Preventiva")
    dados_painel = []
    hoje = datetime.date.today()
    for ativo in st.session_state.frota:
        horas_desde_ultima = ativo['atual'] - ativo['ult_rev_horas']
        prox_250 = ativo['ult_rev_horas'] + 250
        prox_500 = ativo['ult_rev_horas'] + 500
        prox_1000 = ativo['ult_rev_horas'] + 1000
        prox_2000 = ativo['ult_rev_horas'] + 2000
        data_ult = datetime.datetime.strptime(ativo['ult_rev_data'], "%d/%m/%Y").date()
        data_limite_tempo = data_ult + datetime.timedelta(days=365)
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
        status_geral = "🟢 OK"
        motivo_parada = f"Aguardando {proximo_ciclo_horas}"
        data_final_parada = data_prevista_horas if data_prevista_horas else data_limite_tempo
        if ativo['atual'] >= horas_alvo:
            status_geral = "🔴 VENCIDA (Horas)"
            motivo_parada = f"Estourou ciclo de {proximo_ciclo_horas}"
            data_final_parada = "IMEDIATO"
        elif hoje >= data_limite_tempo:
            status_geral = "🔴 VENCIDA (Tempo - 1 Ano)"
            motivo_parada = "Atingiu limite de 1 ano"
            data_final_parada = "IMEDIATO"
        elif data_prevista_horas and data_prevista_horas > data_limite_tempo:
            motivo_parada = "Vai vencer por Tempo antes das horas"
            data_final_parada = data_limite_tempo
            if (data_limite_tempo - hoje).days <= 10: status_geral = "🟡 PROXIMA (Tempo)"
        elif horas_restantes <= (ativo['media'] * 3):
            status_geral = "🟡 PROXIMA (Horas)"
            motivo_parada = f"Proxima de bater {proximo_ciclo_horas}"
        dados_painel.append({
            "ID / TAG": ativo['id'], "Equipamento": ativo['nome'], "Horimetro Atual": f"{ativo['atual']} hrs",
            "Ultima Revisao": f"{ativo['ult_rev_horas']} hrs ({ativo['ult_rev_data']})", "Proxima Meta": f"{horas_alvo} hrs",
            "Prazo Limite": data_limite_tempo.strftime('%d/%m/%Y'), "Data Alvo": data_final_parada.strftime('%d/%m/%Y') if isinstance(data_final_parada, datetime.date) else data_final_parada,
            "Diagnostico": motivo_parada, "Status": status_geral
        })
    st.dataframe(pd.DataFrame(dados_painel), use_container_width=True, hide_index=True)

with aba2:
    st.subheader("Registrar Medição Diária e Execução de Revisões")
    with st.form("form_mecanico_avancado", clear_on_submit=True):
        lista_nomes = [f"{a['id']} - {a['nome']}" for a in st.session_state.frota]
        selecionado = st.selectbox("Escolha o Equipamento:", lista_nomes)
        id_sel = selecionado.split(" - ")[0]
        num_os_manual = st.text_input("Nº da OS em Papel (Manual):")
        num_rm = st.text_input("Nº da Requisição gerada no RM:")
        novo_horimetro = st.number_input("Digite o Horímetro Atual da Máquina:", min_value=0, step=1)
        revisao_executada = st.selectbox("Alguma preventiva foi realizada?", ["Nenhuma", "Concluída PM 250h", "Concluída PM 500h", "Concluída PM 1000h", "Concluída PM 2000h", "Concluída Revisão Anual por Tempo"])
        foto_os = st.file_uploader("📷 Anexe a foto da OS física:", type=["jpg", "jpeg", "png", "pdf"])
        enviar = st.form_submit_button("Salvar Registro de Oficina")
        if enviar:
            for a in st.session_state.frota:
                if a['id'] == id_sel:
                    a['atual'] = novo_horimetro
                    if "PM" in revisao_executada:
                        a['ult_rev_horas'] = novo_horimetro
                        a['ult_rev_data'] = datetime.date.today().strftime('%d/%m/%Y')
                    elif "Anual" in revisao_executada:
                        a['ult_rev_data'] = datetime.date.today().strftime('%d/%m/%Y')
                    nome_foto = foto_os.name if foto_os is not None else "Nao anexada"
                    st.session_state.historico.append({
                        "Data": datetime.date.today().strftime('%d/%m/%Y'), "ID": a['id'], "Equipamento": a['nome'],
                        "Horimetro": novo_horimetro, "OS": num_os_manual, "RM": num_rm, "Acao": revisao_executada, "Foto": nome_foto
                    })
            st.success("✔️ Registro processado! Confira os prazos na aba 'Painel Multigatilhos'.")

with aba3:
    st.subheader("Histórico de Lançamentos para Conciliação no Protheus")
    if len(st.session_state.historico) == 0:
        st.info("Nenhum lançamento registrado ainda.")
    else:
        df_hist = pd.DataFrame(st.session_state.historico)
        st.dataframe(df_hist, use_container_width=True, hide_index=True)
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df_hist.to_excel(writer, index=False, sheet_name='Modo_Crise_MNT')
        st.markdown("---")
        st.download_button(label="🟢 Baixar Histórico em Excel (.xlsx)", data=buffer.getvalue(), file_name="Contingencia_MNT.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

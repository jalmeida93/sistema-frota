import streamlit as st
import pandas as pd
import datetime
import numpy as np
import io
from fpdf import FPDF

# Configuração da página do site
st.set_page_config(page_title="Contingência - Gestão de Frotas", layout="wide", page_icon="🚛")

# 1. BANCO DE DADOS DE CONTINGÊNCIA (Simulação dos seus ativos)
if 'frota' not in st.session_state:
    st.session_state.frota = [
        {"id": "CA0024", "nome": "Volvo VM 360 - 01", "tipo": "Horas", "atual": , "gatilho": 135000, "media": 150, "pecas": "Filtro de Óleo, Filtro de Combustível, Óleo Motor 15W40"},
        {"id": "VM-02", "nome": "Volvo VM 360 - 02", "tipo": "KM", "atual": 98000, "gatilho": 100000, "media": 200, "pecas": "Filtro de Óleo, Filtro de Combustível, Óleo Motor 15W40"},
        {"id": "VM-03", "nome": "Volvo VM 360 - 03", "tipo": "KM", "atual": 45000, "gatilho": 50000, "media": 120, "pecas": "Filtro de Óleo, Filtro de Combustível, Óleo Motor 15W40"},
        {"id": "IV-01", "nome": "Iveco 260E25", "tipo": "KM", "atual": 241000, "gatilho": 240000, "media": 100, "pecas": "Filtro de Óleo, Filtro de Combustível, Kit de Freios"},
        {"id": "ID-01", "nome": "Iveco Daily 170-43", "tipo": "KM", "atual": 85000, "gatilho": 90000, "media": 80, "pecas": "Filtro de Óleo, Filtro de Ar, Óleo Sintético"},
        {"id": "L90-01", "nome": "Carregadeira Volvo L90 - 01", "tipo": "Horas", "atual": 2420, "gatilho": 2500, "media": 8, "pecas": "Filtro Motor, Filtro Transmissão, Graxa EP2"},
        {"id": "L90-02", "nome": "Carregadeira Volvo L90 - 02", "tipo": "Horas", "atual": 1890, "gatilho": 2000, "media": 7, "pecas": "Filtro Motor, Filtro Transmissão, Graxa EP2"},
        {"id": "L90-03", "nome": "Carregadeira Volvo L90 - 03", "tipo": "Horas", "atual": 3110, "gatilho": 3250, "media": 9, "pecas": "Filtro Motor, Filtro Transmissão, Graxa EP2"},
        {"id": "JH-01", "nome": "Carregadeira Elétrica JH120", "tipo": "Horas", "atual": 420, "gatilho": 500, "media": 6, "pecas": "Fluido Arrefecimento Bateria, Filtro de Cabine"},
        {"id": "SAV-01", "nome": "Caminhonete Saveiro", "tipo": "KM", "atual": 62000, "gatilho": 70000, "media": 50, "pecas": "Filtro Óleo, Óleo Sintético, Correia Dentada"},
        {"id": "EC350", "nome": "Escavadeira Volvo EC350", "tipo": "Horas", "atual": 4310, "gatilho": 4450, "media": 8, "pecas": "Filtro Óleo Motor, Filtro Combustível Separador, Graxa EP2"},
        {"id": "EC380", "nome": "Escavadeira Volvo EC380", "tipo": "Horas", "atual": 2100, "gatilho": 2250, "media": 10, "pecas": "Filtro Óleo Motor, Filtro Combustível Separador, Graxa EP2"},
        {"id": "EC240", "nome": "Escavadeira Volvo EC240", "tipo": "Horas", "atual": 5890, "gatilho": 6000, "media": 8, "pecas": "Filtro Óleo Motor, Filtro Combustível Separador, Graxa EP2"},
        {"id": "PC350", "nome": "Escavadeira Komatsu PC350", "tipo": "Horas", "atual": 1240, "gatilho": 1250, "media": 8, "pecas": "Filtro de Óleo, Filtros de Combustível, Elemento Filtro Ar"}
    ]

if 'historico' not in st.session_state:
    st.session_state.historico = []

# LÓGICA DE PROJEÇÃO PULANDO FINS DE SEMANA
def calcular_data_revisao(atual, gatilho, media):
    if media <= 0:
        return "Sem média"
    restante = gatilho - atual
    if restante <= 0:
        return "VENCIDA"
    dias_uteis = int(np.ceil(restante / media))
    hoje = datetime.date.today()
    data_futura = np.busday_offset(hoje, dias_uteis, roll='forward')
    return pd.to_datetime(data_futura).strftime('%d/%m/%Y')

# FUNÇÃO PARA GERAR PDF DA REQUISIÇÃO DO RM
def gerar_pdf_rm(ativo, pecas):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="REQUISICAO DE MANUTENCAO EMERGENCIAL (CONTINGENCIA)", ln=1, align="C")
    pdf.cell(200, 10, txt=f"Data: {datetime.date.today().strftime('%d/%m/%Y')}", ln=2, align="C")
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Equipamento: {ativo['nome']} ({ativo['id']})", ln=1)
    pdf.cell(200, 10, txt=f"Medicao: {ativo['atual']} de {ativo['gatilho']} {ativo['tipo']}", ln=1)
    pdf.ln(10)
    pdf.set_font("Arial", style="B", size=11)
    pdf.cell(140, 10, "Insumos para lancar no RM", border=1)
    pdf.cell(40, 10, "Qtd", border=1, ln=1)
    pdf.set_font("Arial", size=10)
    for p in pecas.split(", "):
        pdf.cell(140, 10, p, border=1)
        pdf.cell(40, 10, "1", border=1, ln=1)
    return pdf.output(dest="S").encode("latin-1")

# INTERFACE WEB
st.title("🛞 Painel de Manutenção e Frota - Modo Contingência")
st.warning("⚠️ Atenção: Sistema operando de forma isolada devido à falha de integração do Protheus SIGAMNT.")

# GERADOR DE REQUISIÇÃO RM (NA BARRA LATERAL PARA EVITAR BUG DE TELA)
st.sidebar.header("📄 Exportar Requisição RM")
lista_ids = [a['id'] for a in st.session_state.frota]
id_selecionado_rm = st.sidebar.selectbox("Selecione o ID para gerar PDF:", lista_ids)

ativo_ref = next(item for item in st.session_state.frota if item["id"] == id_selecionado_rm)
pdf_bytes = gerar_pdf_rm(ativo_ref, ativo_ref['pecas'])

st.sidebar.download_button(
    label=f"📥 Baixar PDF do {id_selecionado_rm}",
    data=pdf_bytes,
    file_name=f"Requisicao_RM_{id_selecionado_rm}.pdf",
    mime="application/pdf"
)

# ABAS DO SISTEMA
aba1, aba2, aba3 = st.tabs(["📊 Painel de Controle", "👨‍🔧 Lançamento do Mecânico", "📁 Histórico e Exportação Excel"])

# ABA 1: PAINEL DE CONTROLE (Renderização limpa e segura)
with aba1:
    st.subheader("Status Atual da Frota e Linha Amarela")
    
    tabela_visual = []
    for ativo in st.session_state.frota:
        status = "🟢 OK"
        if ativo['atual'] >= ativo['gatilho']:
            status = "🔴 VENCIDA"
        elif (ativo['gatilho'] - ativo['atual']) <= (ativo['media'] * 3):
            status = "🟡 PRÓXIMA"
            
        data_prevista = calcular_data_revisao(ativo['atual'], ativo['gatilho'], ativo['media'])
        
        tabela_visual.append({
            "ID": ativo['id'],
            "Equipamento": ativo['nome'],
            "Tipo": ativo['tipo'],
            "Uso Atual": ativo['atual'],
            "Meta Próxima Preventiva": ativo['gatilho'],
            "Previsão de Parada": data_prevista,
            "Status": status
        })
        
    df_visual = pd.DataFrame(tabela_visual)
    st.dataframe(df_visual, use_container_width=True, hide_index=True)

# ABA 2: LANÇAMENTO DO MECÂNICO
with aba2:
    st.subheader("Registrar Medição Diária e Conclusão de OS")
    
    with st.form("form_mecanico", clear_on_submit=True):
        lista_nomes = [f"{a['id']} - {a['nome']}" for a in st.session_state.frota]
        selecionado = st.selectbox("Escolha o Equipamento:", lista_nomes)
        id_sel = selecionado.split(" - ")[0]
        
        num_os_manual = st.text_input("Nº da OS em Papel (Manual):", placeholder="Ex: OS-2026-001")
        num_rm = st.text_input("Nº da Requisição gerada no RM:", placeholder="Ex: REQ-10452")
        novo_valor = st.number_input("Digite o Horímetro ou KM Atual da Máquina:", min_value=0, step=1)
        
        st.markdown("---")
        foto_os = st.file_uploader("📷 Anexe a foto da OS física preenchida/assinada:", type=["jpg", "jpeg", "png", "pdf"])
        marcar_feita = st.checkbox("Esta OS foi executada por completo? (Zera o gatilho da preventiva)")
        
        enviar = st.form_submit_button("Salvar Registro de Campo")
        
        if enviar:
            for a in st.session_state.frota:
                if a['id'] == id_sel:
                    a['atual'] = novo_valor
                    if marcar_feita:
                        incremento = 250 if a['tipo'] == "Horas" else 15000
                        a['gatilho'] = novo_valor + incremento
                    
                    nome_foto = foto_os.name if foto_os is not None else "Não anexada"
                    st.session_state.historico.append({
                        "Data Registro": datetime.date.today().strftime('%d/%m/%Y'),
                        "ID / Prefixo": a['id'],
                        "Equipamento": a['nome'],
                        "Medição Informada": f"{novo_valor} {a['tipo']}",
                        "Nº OS Papel": num_os_manual,
                        "Nº Doc RM": num_rm,
                        "Evidência Anexada": nome_foto,
                        "Preventiva Concluída": "Sim" if marcar_feita else "Apenas Medição"
                    })
            st.success("✔️ Registro salvo com sucesso! Clique na aba 'Painel de Controle' para ver o status atualizado.")

# ABA 3: HISTÓRICO E EXPORTAÇÃO
with aba3:
    st.subheader("Histórico de Manutenções Realizadas na Crise")
    
    if len(st.session_state.historico) == 0:
        st.info("Nenhum fechamento ou medição foi registrado por esta interface ainda.")
    else:
        df_hist = pd.DataFrame(st.session_state.historico)
        st.dataframe(df_hist, use_container_width=True, hide_index=True)
        
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df_hist.to_excel(writer, index=False, sheet_name='Lançamentos')
            
        st.markdown("---")
        st.download_button(
            label="🟢 Baixar Histórico de OS em Excel (.xlsx)",
            data=buffer.getvalue(),
            file_name=f"Conciliacao_Para_Protheus_{datetime.date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

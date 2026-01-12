import streamlit as st
import os
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
from pypdf import PdfReader

# ==========================================
# 1. CONFIGURAÇÃO DA PÁGINA E ESTILO
# ==========================================
st.set_page_config(
    page_title="JurisMatch | Auditoria Imobiliária AI",
    page_icon="⚖️",
    layout="wide"
)

# CSS Customizado para deixar com cara de SaaS profissional
st.markdown("""
<style>
    .reportview-container {
        background: #f0f2f6
    }
    .metric-card {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .stAlert {
        padding: 10px;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. MODELOS DE DADOS (Igual ao Backend)
# ==========================================
class NivelRisco(str, Enum):
    CRITICO = "CRITICO"
    ATENCAO = "ATENCAO"
    CONFORME = "CONFORME"

class ItemAnalise(BaseModel):
    topico: str = Field(description="O tópico analisado (ex: Garantia, Multa)")
    status: NivelRisco
    descricao_problema: Optional[str] = Field(None)
    sugestao_correcao: Optional[str] = Field(None)

class ResumoContrato(BaseModel):
    locador: str
    locatario: str
    valor_aluguel: float
    indice_reajuste: str
    garantias_encontradas: List[str]

class RelatorioAuditoria(BaseModel):
    resumo: ResumoContrato
    analise_riscos: List[ItemAnalise]
    parecer_final: str

# ==========================================
# 3. FUNÇÕES UTILITÁRIAS
# ==========================================
def extract_text_from_pdf(uploaded_file):
    reader = PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

def analisar_contrato(texto, api_key):
    client = OpenAI(api_key=api_key)
    
    system_prompt = """
    Você é o JurisMatch Senior Auditor, especialista na Lei do Inquilinato Brasileira (Lei 8.245/91).
    Analise o contrato buscando nulidades (dupla garantia, multas abusivas) e riscos comerciais (IGP-M).
    Seja rigoroso.
    """
    
    try:
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Analise este contrato:\n\n{texto}"},
            ],
            response_format=RelatorioAuditoria,
        )
        return completion.choices[0].message.parsed
    except Exception as e:
        st.error(f"Erro na análise: {e}")
        return None

# ==========================================
# 4. INTERFACE DO USUÁRIO (FRONTEND)
# ==========================================

# Sidebar
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2237/2237699.png", width=80)
    st.title("JurisMatch")
    st.markdown("---")
    api_key = st.text_input("OpenAI API Key", type="password", help="Insira sua chave para processar")
    st.markdown("### Sobre")
    st.info("Este agente utiliza IA para identificar riscos na Lei do Inquilinato (8.245/91).")

# Cabeçalho Principal
st.title("Auditoria de Contratos de Locação 🇧🇷")
st.markdown("Carregue seu contrato (PDF) ou cole o texto para uma análise de compliance imediata.")

# Tabs para Upload ou Texto
tab1, tab2 = st.tabs(["📂 Upload de PDF", "📝 Colar Texto"])

texto_para_analise = ""

with tab1:
    uploaded_file = st.file_uploader("Arraste seu contrato aqui", type="pdf")
    if uploaded_file:
        texto_para_analise = extract_text_from_pdf(uploaded_file)
        st.success("PDF lido com sucesso! Clique em analisar.")

with tab2:
    texto_input = st.text_area("Cole o texto do contrato aqui", height=300)
    if texto_input:
        texto_para_analise = texto_input

# Botão de Ação
if st.button("🔍 Iniciar Auditoria Jurídica", type="primary"):
    if not api_key:
        st.warning("Por favor, insira sua OpenAI API Key na barra lateral.")
    elif not texto_para_analise:
        st.warning("Por favor, forneça um contrato para análise.")
    else:
        with st.spinner("O JurisMatch está lendo as cláusulas e consultando a Lei 8.245/91..."):
            resultado = analisar_contrato(texto_para_analise, api_key)

        if resultado:
            st.divider()
            
            # --- SEÇÃO 1: RESUMO ---
            st.subheader("📋 Resumo do Contrato")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Valor", f"R$ {resultado.resumo.valor_aluguel:,.2f}")
            col2.metric("Índice", resultado.resumo.indice_reajuste)
            col3.metric("Garantias", ", ".join(resultado.resumo.garantias_encontradas))
            
            # Lógica visual para garantias (Alerta de dupla garantia)
            if len(resultado.resumo.garantias_encontradas) > 1:
                col3.markdown("🔴 **ILEGAL**")
            
            col4.metric("Locatário", resultado.resumo.locatario.split()[0]) # Apenas primeiro nome para caber

            # --- SEÇÃO 2: SEMÁFORO DE RISCOS ---
            st.subheader("🚨 Análise de Risco & Compliance")
            
            criticos = [i for i in resultado.analise_riscos if i.status == NivelRisco.CRITICO]
            atencao = [i for i in resultado.analise_riscos if i.status == NivelRisco.ATENCAO]
            conforme = [i for i in resultado.analise_riscos if i.status == NivelRisco.CONFORME]

            # Exibir CRÍTICOS primeiro (Vermelho)
            if criticos:
                st.error(f"⚠️ {len(criticos)} PONTOS CRÍTICOS ENCONTRADOS (RISCO DE NULIDADE)")
                for item in criticos:
                    with st.expander(f"🔴 {item.topico}: {item.descricao_problema}", expanded=True):
                        st.markdown(f"**Análise:** {item.descricao_problema}")
                        if item.sugestao_correcao:
                            st.code(item.sugestao_correcao, language="markdown")
            else:
                st.success("Nenhum risco crítico de nulidade encontrado.")

            # Exibir ATENÇÃO (Amarelo)
            if atencao:
                st.warning(f"⚠️ {len(atencao)} Pontos de Atenção Comercial")
                for item in atencao:
                    with st.expander(f"🟡 {item.topico}"):
                        st.write(item.descricao_problema)
                        if item.sugestao_correcao:
                             st.info(f"Sugestão: {item.sugestao_correcao}")

            # --- SEÇÃO 3: PARECER FINAL ---
            st.markdown("### ⚖️ Parecer Final do Auditor IA")
            st.info(resultado.parecer_final)

# ⚖️ JurisMatch MVP - Auditoria Imobiliária com IA

> Um Agente de Inteligência Artificial especializado na **Lei do Inquilinato (Lei nº 8.245/91)** para análise automática de riscos em contratos de locação.

![Status](https://img.shields.io/badge/Status-MVP-green) ![Python](https://img.shields.io/badge/Python-3.10%2B-blue) ![Stack](https://img.shields.io/badge/AI-OpenAI%20%2B%20Pydantic-orange)

## 🎯 O Problema
Pequenas imobiliárias e corretores autônomos no Brasil perdem horas revisando contratos manualmente ou dependem de departamentos jurídicos caros, atrasando fechamentos.

## 🚀 A Solução
O **JurisMatch** atua como um "Auditor Sênior Digital". Ele lê arquivos PDF ou texto e utiliza LLMs com saídas estruturadas (Structured Outputs) para verificar:
- **Nulidades:** Dupla garantia (Art. 37), Multas abusivas.
- **Riscos Comerciais:** Uso de IGP-M vs IPCA.
- **Conformidade:** Prazos legais e renovações automáticas.

## 🛠️ Tecnologias Utilizadas
- **Frontend:** Streamlit (Interface Web)
- **IA/LLM:** OpenAI GPT-4o-mini (Custo-benefício)
- **Validação:** PydanticAI (Garante que a IA não "alucine" dados)
- **Processamento:** PyPDF (Leitura de documentos)

## ⚙️ Instalação e Uso

1. **Clone o repositório:**
   ```bash
   git clone [https://github.com/SEU-USUARIO/jurismatch-mvp.git](https://github.com/SEU-USUARIO/jurismatch-mvp.git)
   cd jurismatch-mvp

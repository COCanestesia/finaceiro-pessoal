import streamlit as st
from app_financeiro import sistema_financeiro
from dashboard_app import dashboard_financeiro

# 🔥 CONFIG
st.set_page_config(
    page_title="Portal Financeiro",
    page_icon="💰",
    layout="wide"
)

# 🔥 SIDEBAR
with st.sidebar:
    st.title("💰 Portal Financeiro")
    st.markdown("---")

    menu = st.radio(
        "Navegação",
        ["💳 Sistema Financeiro", "📊 Dashboard"]
    )

    st.markdown("---")
    st.caption("Versão 1.0")

# 🔥 CONTEÚDO
if menu == "💳 Sistema Financeiro":
    sistema_financeiro()

elif menu == "📊 Dashboard":
    dashboard_financeiro()
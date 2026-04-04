# portal.py
import streamlit as st
from app_financeiro import sistema_financeiro
from dashboard_app import dashboard_financeiro

# 🔥 CONFIG SÓ AQUI
st.set_page_config(page_title="Portal Financeiro", layout="wide")

# 🔥 TÍTULO NA SIDEBAR (não no topo)
st.sidebar.title("💰 Portal Financeiro")
st.sidebar.markdown("---")

menu = st.sidebar.selectbox(
    "Navegação",
    ["Sistema Financeiro", "Dashboard"]
)

if menu == "Sistema Financeiro":
    sistema_financeiro()

elif menu == "Dashboard":
    dashboard_financeiro()
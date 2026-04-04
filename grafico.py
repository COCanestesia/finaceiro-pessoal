import streamlit as st
import pandas as pd


# ================================
# 📈 LINHA - RECEITA VS DESPESA
# ================================
def grafico_linha(df):
    st.subheader("📈 Receita vs Despesa ao longo do tempo")

    # Agrupar por data e classificação
    resumo = (
        df.groupby(["DATA", "CLASSIFICAÇÃO"])["VALOR"]
        .sum()
        .unstack()
        .fillna(0)
    )

    # Garantir colunas
    if "RECEITA" not in resumo:
        resumo["RECEITA"] = 0
    if "DESPESA" not in resumo:
        resumo["DESPESA"] = 0

    resumo = resumo.sort_index()

    st.line_chart(resumo[["RECEITA", "DESPESA"]])


# ================================
# 💰 RESUMO (KPIs SIMPLES)
# ================================
def grafico_resumo(resumo):
    st.subheader("💰 Resumo Financeiro")

    def br(valor):
        return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    col1, col2, col3 = st.columns(3)

    col1.metric("Receita", f"R$ {br(resumo['receita'])}")
    col2.metric("Despesa", f"R$ {br(resumo['despesa'])}")
    col3.metric("Saldo", f"R$ {br(resumo['saldo'])}")
# data.py
import gspread
import pandas as pd
import streamlit as st
from google.oauth2.service_account import Credentials

# -------------------------
# 🔐 CONEXÃO GOOGLE SHEETS
# -------------------------
def conectar_google():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scope
    )

    client = gspread.authorize(creds)

    planilha = client.open_by_url(
        "https://docs.google.com/spreadsheets/d/1OvodwLlhguQmbKQPXbQiP9DkZ5IDrq6WESNFEBT_TTo/edit?usp=sharing"
    )

    return planilha

def carregar_dados():
    planilha = conectar_google()

    # -------------------------
    # 📥 ABA DADOS
    # -------------------------
    aba_dados = planilha.worksheet("Dados")
    dados = aba_dados.get_all_records()
    df_dados = pd.DataFrame(dados)

    if not df_dados.empty:
        # 🔹 Padroniza colunas
        df_dados.columns = df_dados.columns.str.strip().str.upper()

        # 🔹 Controle de linha
        df_dados["LINHA_SHEET"] = df_dados.index + 2

        # 🔹 DATA
        df_dados["DATA"] = pd.to_datetime(df_dados["DATA"], errors="coerce")

        # 🔹 VALOR (🔥 principal correção)
        df_dados["VALOR"] = (
            df_dados["VALOR"]
            .astype(str)
            .str.replace("R$", "", regex=False)
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False)
            .str.strip()
        )

        df_dados["VALOR"] = pd.to_numeric(df_dados["VALOR"], errors="coerce").fillna(0)

        # 🔹 TEXTO PADRONIZADO
        df_dados["CLASSIFICAÇÃO"] = (
            df_dados["CLASSIFICAÇÃO"]
            .astype(str)
            .str.upper()
            .str.strip()
        )

        df_dados["CATEGORIA"] = (
            df_dados["CATEGORIA"]
            .astype(str)
            .str.strip()
        )

        # 🔹 LIMPEZA FINAL
        df_dados = df_dados.dropna(subset=["DATA"])
        df_dados = df_dados[df_dados["VALOR"] > 0]
        df_dados = df_dados.drop_duplicates()

    # -------------------------
    # 📥 ABA META
    # -------------------------
    aba_meta = planilha.worksheet("Meta")
    metas = aba_meta.get_all_records()
    df_meta = pd.DataFrame(metas)

    return df_dados, df_meta

# -------------------------
# 💾 SALVAR DADOS
# -------------------------
def salvar_dados(linha):
    planilha = conectar_google()
    aba = planilha.worksheet("Dados")
    aba.append_row(linha)

# -------------------------
# ✏️ ATUALIZAR DADOS
# -------------------------
def atualizar_dados(linha_num, novos_dados):
    planilha = conectar_google()
    aba = planilha.worksheet("Dados")
    aba.update(f"A{linha_num}:I{linha_num}", [novos_dados])

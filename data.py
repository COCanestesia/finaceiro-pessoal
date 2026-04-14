import pandas as pd
from database import (
    buscar_transacoes,
    buscar_metas,
    inserir_transacao,
    atualizar_transacao
)

def carregar_dados():

    df_dados = buscar_transacoes()
    df_meta = buscar_metas()

    if not df_dados.empty:

        # 🔹 REMOVE ACENTOS + PADRONIZA
        df_dados.columns = df_dados.columns.str.normalize('NFKD')\
            .str.encode('ascii', errors='ignore')\
            .str.decode('utf-8')\
            .str.upper()\
            .str.strip()

        # 🔹 CONTROLE
        if "ID" in df_dados.columns:
            df_dados["LINHA_SHEET"] = df_dados["ID"]

        # 🔹 DATA
        if "DATA" in df_dados.columns:
            df_dados["DATA"] = pd.to_datetime(df_dados["DATA"], errors="coerce")

        # 🔹 VALOR
        if "VALOR" in df_dados.columns:
            df_dados["VALOR"] = pd.to_numeric(df_dados["VALOR"], errors="coerce").fillna(0)

        # 🔹 TEXTO
        if "CLASSIFICACAO" in df_dados.columns:
            df_dados["CLASSIFICACAO"] = (
                df_dados["CLASSIFICACAO"]
                .astype(str)
                .str.upper()
                .str.strip()
            )

        if "CATEGORIA" in df_dados.columns:
            df_dados["CATEGORIA"] = df_dados["CATEGORIA"].astype(str).str.strip()

        # 🔹 LIMPEZA
        df_dados = df_dados.dropna(subset=["DATA"])
        df_dados = df_dados[df_dados["VALOR"] > 0]
        df_dados = df_dados.drop_duplicates()

    return df_dados, df_meta


# -------------------------
# 💾 SALVAR DADOS
# -------------------------
def salvar_dados(linha):
    try:
        inserir_transacao(linha)
    except Exception as e:
        import streamlit as st
        st.error(f"Erro ao salvar: {e}")


# -------------------------
# ✏️ ATUALIZAR DADOS
# -------------------------
def atualizar_dados(id_linha, novos_dados):
    try:
        atualizar_transacao(id_linha, novos_dados)
    except Exception as e:
        import streamlit as st
        st.error(f"Erro ao atualizar: {e}")
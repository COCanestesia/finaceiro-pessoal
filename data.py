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

    if df_dados.empty:
        return df_dados, df_meta

    # =========================
    # 🧾 LIMPEZA DE COLUNAS
    # =========================
    df_dados.columns = df_dados.columns.str.strip()

    # =========================
    # 🔥 PADRONIZAÇÃO
    # =========================

    # ID
    if "id" in df_dados.columns:
        df_dados["id"] = df_dados["id"]

    # DATA
    if "data" in df_dados.columns:
        df_dados["Data"] = pd.to_datetime(df_dados["data"], errors="coerce")

    # VALOR
    if "valor" in df_dados.columns:
        df_dados["Valor"] = pd.to_numeric(df_dados["valor"], errors="coerce").fillna(0)
    else:
        df_dados["Valor"] = 0

    # CLASSIFICAÇÃO
    if "classificacao" in df_dados.columns:
        df_dados["Classificação"] = df_dados["classificacao"].fillna("Despesa")
    else:
        df_dados["Classificação"] = "Despesa"

    # CONTA
    if "conta" in df_dados.columns:
        df_dados["Conta"] = df_dados["conta"].fillna("ESPÉCIE")
    else:
        df_dados["Conta"] = "ESPÉCIE"

    # CATEGORIA
    if "categoria" in df_dados.columns:
        df_dados["Categoria"] = df_dados["categoria"]

    # =========================
    # ❌ REMOVIDO ERRO CRÍTICO
    # NÃO FILTRAR VALOR > 0
    # =========================

    return df_dados, df_meta
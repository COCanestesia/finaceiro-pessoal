import pandas as pd
from database import buscar_transacoes, buscar_metas, inserir_transacao, atualizar_transacao


# =========================
# 📥 CARREGAR DADOS (DASHBOARD)
# =========================
def carregar_dados():

    df_dados = buscar_transacoes()
    df_meta = buscar_metas()

    if df_dados.empty:
        return df_dados, df_meta

    # =========================
    # 🧹 LIMPEZA
    # =========================
    df_dados.columns = df_dados.columns.str.strip()

    # =========================
    # 🔥 PADRONIZAÇÃO PRINCIPAL
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

    # SUBCATEGORIA
    if "subcategoria" in df_dados.columns:
        df_dados["Subcategoria"] = df_dados["subcategoria"]

    # TIPO DESPESA
    if "tipo_despesa" in df_dados.columns:
        df_dados["Tipo de despesa"] = df_dados["tipo_despesa"]

    # DATA VENCIMENTO
    if "data_vencimento" in df_dados.columns:
        df_dados["Data Vencimento"] = pd.to_datetime(df_dados["data_vencimento"], errors="coerce")
    else:
        df_dados["Data Vencimento"] = pd.NaT

    # STATUS
    if "status" in df_dados.columns:
        df_dados["Status"] = df_dados["status"].fillna("Pendente")
    else:
        df_dados["Status"] = "Pendente"

    # =========================
    # 🔑 ID PARA EDIÇÃO
    # =========================
    if "id" not in df_dados.columns:
        df_dados["id"] = df_dados.index

    # =========================
    # 🧼 LIMPEZA FINAL
    # =========================
    df_dados = df_dados.dropna(subset=["Data"])
    df_dados = df_dados.drop_duplicates()

    return df_dados, df_meta


# =========================
# 💾 SALVAR (ATALHO OPCIONAL)
# =========================
def salvar_dados(linha):
    inserir_transacao(linha)


# =========================
# ✏️ ATUALIZAR (ATALHO OPCIONAL)
# =========================
def atualizar_dados(id_linha, novos_dados):
    atualizar_transacao(id_linha, novos_dados)
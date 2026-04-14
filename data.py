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
    # 🧹 PADRONIZAÇÃO FORTE
    # =========================
    df_dados.columns = [
        str(c).strip().lower()
        for c in df_dados.columns
    ]

    # =========================
    # 🔥 VALOR
    # =========================
    if "valor" in df_dados.columns:
        df_dados["valor"] = pd.to_numeric(df_dados["valor"], errors="coerce").fillna(0)

    # =========================
    # 🔥 CLASSIFICAÇÃO
    # =========================
    if "classificacao" in df_dados.columns:
        df_dados["classificacao"] = df_dados["classificacao"].astype(str).str.upper().str.strip()
    else:
        df_dados["classificacao"] = "DESPESA"

    # =========================
    # 🔥 CONTA
    # =========================
    if "conta" in df_dados.columns:
        df_dados["conta"] = df_dados["conta"].astype(str).fillna("ESPÉCIE")

    # =========================
    # 🔥 DATA
    # =========================
    if "data" in df_dados.columns:
        df_dados["data"] = pd.to_datetime(df_dados["data"], errors="coerce")

    # =========================
    # 🔥 DATA VENCIMENTO
    # =========================
    if "data_vencimento" in df_dados.columns:
        df_dados["data_vencimento"] = pd.to_datetime(df_dados["data_vencimento"], errors="coerce")

    # =========================
    # 🔥 OUTROS CAMPOS
    # =========================
    for col in ["titular", "mes", "descricao", "categoria", "subcategoria", "tipo_despesa", "status"]:
        if col in df_dados.columns:
            df_dados[col] = df_dados[col].astype(str)

    # =========================
    # 🔥 LIMPEZA FINAL
    # =========================
    df_dados = df_dados.dropna(subset=["data"])
    df_dados = df_dados.drop_duplicates()

    return df_dados, df_meta


# =========================
# 💾 SALVAR
# =========================
def salvar_dados(linha):
    inserir_transacao(linha)


# =========================
# ✏️ ATUALIZAR
# =========================
def atualizar_dados(id_linha, novos_dados):
    atualizar_transacao(id_linha, novos_dados)
import pandas as pd
from database import buscar_transacoes, buscar_metas, inserir_transacao, atualizar_transacao


# =========================
# 📥 CARREGAR DADOS (ROBUSTO)
# =========================
def carregar_dados():

    df = buscar_transacoes()
    df_meta = buscar_metas()

    if df is None or df.empty:
        return pd.DataFrame(), df_meta

    df = df.copy()

    # =========================
    # 🧹 PADRONIZA COLUNAS
    # =========================
    df.columns = [str(c).strip().lower() for c in df.columns]

    # =========================
    # 💰 VALOR (FORÇADO SEGURO)
    # =========================
    if "valor" not in df.columns:
        df["valor"] = 0

    df["valor"] = (
        df["valor"]
        .astype(str)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
    )

    df["valor"] = pd.to_numeric(df["valor"], errors="coerce").fillna(0)

    # =========================
    # 📌 CLASSIFICAÇÃO
    # =========================
    if "classificacao" not in df.columns:
        df["classificacao"] = "DESPESA"

    df["classificacao"] = (
        df["classificacao"]
        .fillna("DESPESA")
        .astype(str)
        .str.upper()
        .str.strip()
    )

    # =========================
    # 🏦 CONTA
    # =========================
    if "conta" not in df.columns:
        df["conta"] = "ESPÉCIE"

    df["conta"] = df["conta"].fillna("ESPÉCIE").astype(str)

    # =========================
    # 📅 DATAS SEGURAS
    # =========================
    if "data" not in df.columns:
        df["data"] = pd.NaT
    else:
        df["data"] = pd.to_datetime(df["data"], errors="coerce")

    if "data_vencimento" not in df.columns:
        df["data_vencimento"] = pd.NaT
    else:
        df["data_vencimento"] = pd.to_datetime(df["data_vencimento"], errors="coerce")

    # =========================
    # 📌 STATUS
    # =========================
    if "status" not in df.columns:
        df["status"] = "PENDENTE"

    df["status"] = df["status"].fillna("PENDENTE").astype(str)

    return df, df_meta


# =========================
# 💰 SALDO (ESTILO BANCO)
# =========================
def calcular_saldos(df):

    if df is None or df.empty:
        return {}

    df = df.copy()

    if "valor" not in df.columns:
        return {}

    if "classificacao" not in df.columns:
        df["classificacao"] = "DESPESA"

    if "conta" not in df.columns:
        df["conta"] = "ESPÉCIE"

    bancos = ["Itaú", "Bradesco", "Banco do Brasil", "Nubank"]

    saldos = {b: 0 for b in bancos}
    saldos["Dinheiro (Caixa físico)"] = 0

    for _, row in df.iterrows():

        try:
            valor = float(row["valor"])
        except:
            valor = 0

        if str(row["classificacao"]).upper() == "DESPESA":
            valor = -abs(valor)

        conta = str(row["conta"])

        if "TRANSFERÊNCIA BANCÁRIA" in conta and "(" in conta:
            try:
                banco = conta.split("(")[1].replace(")", "").strip()
                if banco in saldos:
                    saldos[banco] += valor
                else:
                    saldos["Dinheiro (Caixa físico)"] += valor
            except:
                saldos["Dinheiro (Caixa físico)"] += valor
        else:
            saldos["Dinheiro (Caixa físico)"] += valor

    return saldos


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
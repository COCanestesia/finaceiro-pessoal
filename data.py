import pandas as pd
from database import buscar_transacoes, buscar_metas

# =========================
# 🧠 CÉREBRO DO SISTEMA
# =========================
def carregar_dados():

    df = buscar_transacoes()
    df_meta = buscar_metas()

    if df is None or df.empty:
        return pd.DataFrame(), df_meta

    df = df.copy()

    # =========================
    # 🧼 PADRONIZA COLUNAS
    # =========================
    df.columns = [str(c).strip().lower() for c in df.columns]

    # =========================
    # 💰 VALOR
    # =========================
    df["valor"] = (
        df.get("valor", 0)
        .astype(str)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
    )
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce").fillna(0)

    # =========================
    # 📌 CLASSIFICAÇÃO
    # =========================
    df["classificacao"] = df.get("classificacao", "DESPESA")
    df["classificacao"] = df["classificacao"].fillna("DESPESA").astype(str).str.upper()

    # =========================
    # 🏦 CONTA
    # =========================
    df["conta"] = df.get("conta", "ESPÉCIE").fillna("ESPÉCIE").astype(str)

    # =========================
    # 📅 DATAS
    # =========================
    df["data"] = pd.to_datetime(df.get("data"), errors="coerce")
    df["data_vencimento"] = pd.to_datetime(df.get("data_vencimento"), errors="coerce")

    return df, df_meta


# =========================
# 💰 SALDO (CÉREBRO)
# =========================
def calcular_saldos(df):

    if df is None or df.empty:
        return {}

    bancos = ["Itaú", "Bradesco", "Banco do Brasil", "Nubank"]

    saldos = {b: 0 for b in bancos}
    saldos["Dinheiro (Caixa físico)"] = 0

    for _, row in df.iterrows():

        valor = row["valor"]

        if row["classificacao"] == "DESPESA":
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
from database import inserir_transacao, atualizar_transacao

def salvar_dados(linha):
    inserir_transacao(linha)

def atualizar_dados(id_linha, novos_dados):
    atualizar_transacao(id_linha, novos_dados)
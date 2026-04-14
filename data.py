import pandas as pd
from database import buscar_transacoes, buscar_metas


# =========================
# 🧠 CÉREBRO
# =========================
def carregar_dados():

    df = buscar_transacoes()
    df_meta = buscar_metas()

    if df is None or df.empty:
        return pd.DataFrame(), df_meta

    df = df.copy()

    # padroniza colunas
    df.columns = [str(c).strip().lower() for c in df.columns]

    # valor seguro
    df["valor"] = (
        df.get("valor", 0)
        .astype(str)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
    )
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce").fillna(0)

    # classificação
    df["classificacao"] = (
        df.get("classificacao", "DESPESA")
        .fillna("DESPESA")
        .astype(str)
        .str.upper()
        .str.strip()
    )

    # conta
    df["conta"] = df.get("conta", "ESPÉCIE").fillna("ESPÉCIE").astype(str)

    # datas
    df["data"] = pd.to_datetime(df.get("data"), errors="coerce")
    df["data_vencimento"] = pd.to_datetime(df.get("data_vencimento"), errors="coerce")

    return df, df_meta


# =========================
# 💰 SALDO (TEMPO REAL)
# =========================
def calcular_saldos(df):

    if df is None or df.empty:
        return {}

    bancos = ["Itaú", "Bradesco", "Banco do Brasil", "Nubank"]

    saldos = {b: 0.0 for b in bancos}
    saldos["Dinheiro (Caixa físico)"] = 0.0

    for _, row in df.iterrows():

        valor = float(row["valor"])

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
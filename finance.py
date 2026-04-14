import pandas as pd


def calcular_saldos(df):

    if df.empty:
        return {}

    df = df.copy()
    df.columns = [c.lower() for c in df.columns]

    df["valor"] = pd.to_numeric(df["valor"], errors="coerce").fillna(0)
    df["classificacao"] = df["classificacao"].str.upper()
    df["conta"] = df["conta"].astype(str)

    bancos = ["Itaú", "Bradesco", "Banco do Brasil", "Nubank"]

    saldos = {b: 0 for b in bancos}
    saldos["Dinheiro (Caixa físico)"] = 0

    for _, row in df.iterrows():

        valor = row["valor"]

        if row["classificacao"] == "DESPESA":
            valor = -valor

        conta = row["conta"]

        if "TRANSFERÊNCIA BANCÁRIA" in conta and "(" in conta:
            banco = conta.split("(")[1].replace(")", "").strip()

            if banco in saldos:
                saldos[banco] += valor
            else:
                saldos["Dinheiro (Caixa físico)"] += valor
        else:
            saldos["Dinheiro (Caixa físico)"] += valor

    return saldos
import pandas as pd
from database import buscar_transacoes, buscar_metas
from database import atualizar_transacao


# =========================
# 🧠 CÉREBRO
# =========================
def carregar_dados():

    df = buscar_transacoes()
    df_meta = buscar_metas()

    if df is None or df.empty:
        return pd.DataFrame(), df_meta

    df = df.copy()
    df.columns = [str(c).strip().lower() for c in df.columns]

    # valor seguro
    df["valor"] = pd.to_numeric(df.get("valor", 0), errors="coerce").fillna(0)

    # classificação segura
    df["classificacao"] = (
        df.get("classificacao")
        .fillna("")
        .astype(str)
        .str.upper()
        .str.strip()
    )
    df["status"] = (
        df.get("status", "")
        .fillna("")
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

    saldos = {}

    for _, row in df.iterrows():

        status = str(row.get("status", "")).upper()
        if status != "PAGO":
            continue

        valor = abs(float(row.get("valor", 0)))

        tipo = str(row.get("tipo", "")).upper()
        origem = row.get("conta_origem")
        destino = row.get("conta_destino")

        # inicializa contas
        if origem and origem not in saldos:
            saldos[origem] = 0
        if destino and destino not in saldos:
            saldos[destino] = 0

        # 💰 RECEITA
        if tipo == "RECEITA":
            if destino:
                saldos[destino] += valor

        # 💸 DESPESA
        elif tipo == "DESPESA":
            if origem:
                saldos[origem] -= valor

        # 🔁 TRANSFERÊNCIA
        elif tipo == "TRANSFERENCIA":
            if origem:
                saldos[origem] -= valor
            if destino:
                saldos[destino] += valor

    return saldos

def gerar_alertas_inteligentes(df):

    hoje = pd.Timestamp.today().normalize()
    avisos = []

    if df is None or df.empty:
        return avisos

    for _, row in df.iterrows():

        if str(row.get("classificacao", "")).upper().strip() != "DESPESA":
            continue

        if str(row.get("status", "")).upper().strip() == "PAGO":
            continue

        vencimento = row.get("data_vencimento")

        if pd.isna(vencimento):
            continue

        try:
            vencimento = pd.to_datetime(vencimento).normalize()
        except:
            continue

        dias = (vencimento - hoje).days
        descricao = row.get("descricao", "Sem descrição")

        if dias < 0:
            nivel = "error"
            risco = 100
            msg = f"🔴 {descricao} vencido há {abs(dias)} dia(s)"

        elif dias == 0:
            nivel = "warning"
            risco = 90
            msg = f"🟠 {descricao} vence HOJE"

        elif dias <= 3:
            nivel = "warning"
            risco = 70
            msg = f"🟡 {descricao} vence em {dias} dia(s)"

        elif dias <= 7:
            nivel = "info"
            risco = 40
            msg = f"🔵 {descricao} vence em {dias} dia(s)"

        else:
            continue

        avisos.append({
            "nivel": nivel,
            "msg": msg,
            "dias": dias,
            "descricao": descricao,
            "risco": risco
        })

    avisos.sort(key=lambda x: x["risco"], reverse=True)

    return avisos

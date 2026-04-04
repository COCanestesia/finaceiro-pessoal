import streamlit as st


# ================================
# 💰 FORMATAÇÃO BR
# ================================
def br(valor):
    try:
        return f"{float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "0,00"


# ================================
# 📊 KPIs PRINCIPAIS
# ================================
def mostrar_kpis(df):

    # 🛡 segurança (evita erro se vier dataframe quebrado)
    if df.empty:
        st.warning("Sem dados disponíveis")
        return 0, 0, 0

    # 🔥 GARANTE PADRÃO DO data.py
    if "VALOR_AJUSTADO" not in df.columns:
        df["VALOR_AJUSTADO"] = df["VALOR"]
        df.loc[df["CLASSIFICAÇÃO"] == "DESPESA", "VALOR_AJUSTADO"] *= -1

    # ================================
    # 📊 CÁLCULOS (OTIMIZADOS)
    # ================================
    receita = df.loc[df["CLASSIFICAÇÃO"] == "RECEITA", "VALOR"].sum()
    despesa = df.loc[df["CLASSIFICAÇÃO"] == "DESPESA", "VALOR"].sum()
    resultado = df["VALOR_AJUSTADO"].sum()

    percentual = (despesa / receita * 100) if receita > 0 else 0

    col1, col2, col3 = st.columns(3)

    # ================================
    # 💰 RECEITA
    # ================================
    col1.metric(
        "💰 Receita",
        f"R$ {br(receita)}"
    )

    # ================================
    # 💸 DESPESA
    # ================================
    col2.metric(
        "💸 Despesa",
        f"R$ {br(despesa)}",
        f"{percentual:.1f}% da receita"
    )

    # ================================
    # 📊 RESULTADO
    # ================================
    if resultado >= 0:
        cor = "#00C853"
        status = "Lucro"
        emoji = "📈"
    else:
        cor = "#FF4B4B"
        status = "Prejuízo"
        emoji = "📉"

    col3.markdown(
        f"""
        <div style="
            background:#1E1E1E;
            padding:15px;
            border-radius:10px;
            text-align:center;
        ">
            <div style="font-size:14px; color:#AAA;">{emoji} Resultado</div>
            <div style="font-size:22px; font-weight:700; color:{cor};">
                R$ {br(resultado)}
            </div>
            <div style="font-size:12px; color:#AAA;">
                {status}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    return receita, despesa, resultado
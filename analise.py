import streamlit as st


# ================================
# 💰 FORMATAÇÃO BR
# ================================
def br(valor):
    try:
        return f"{float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "0,00"


# ================================
# 📊 KPIs PRINCIPAIS (CORRIGIDO)
# ================================
def mostrar_kpis(df):

    if df.empty:
        st.warning("Sem dados disponíveis")
        return 0, 0, 0

    # ================================
    # 🔥 GARANTIR PADRÃO
    # ================================
    df["Classificação"] = df["Classificação"].astype(str).str.upper().str.strip()
    df["Valor"] = df["Valor"].fillna(0)

    # ================================
    # 🔥 VALOR AJUSTADO (CORRETO)
    # ================================
    df["Valor_Ajustado"] = df["Valor"]

    df.loc[df["Classificação"] == "DESPESA", "Valor_Ajustado"] *= -1

    # ================================
    # 📊 CÁLCULOS CORRETOS
    # ================================
    receita = df.loc[df["Classificação"] == "RECEITA", "Valor"].sum()
    despesa = df.loc[df["Classificação"] == "DESPESA", "Valor"].sum()
    resultado = df["Valor_Ajustado"].sum()

    percentual = (despesa / receita * 100) if receita > 0 else 0

    col1, col2, col3 = st.columns(3)

    # 💰 RECEITA
    col1.metric("💰 Receita", f"R$ {br(receita)}")

    # 💸 DESPESA
    col2.metric(
        "💸 Despesa",
        f"R$ {br(despesa)}",
        f"{percentual:.1f}% da receita"
    )

    # 📊 RESULTADO
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
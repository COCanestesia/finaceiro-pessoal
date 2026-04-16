import streamlit as st
import pandas as pd


# ================================
# 💰 FORMATAÇÃO BR
# ================================
def br(valor):
    try:
        return f"{float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "0,00"


# ================================
# 📊 KPIs PRINCIPAIS (PADRÃO CORRETO)
# ================================
def mostrar_kpis(df):

    if df.empty:
        st.warning("Sem dados disponíveis")
        return 0, 0, 0

    # 🔥 GARANTE PADRÃO (MINÚSCULO)
    df = df.copy()

    df["classificacao"] = (
        df.get("classificacao", "")
        .astype(str)
        .str.upper()
        .str.strip()
    )

    df["valor"] = pd.to_numeric(
        df.get("valor", 0),
        errors="coerce"
    ).fillna(0)

    # 🔥 VALOR AJUSTADO
    df["valor_ajustado"] = df["valor"]
    df.loc[df["classificacao"] == "DESPESA", "valor_ajustado"] *= -1

    # 📊 CÁLCULOS
    receita = df.loc[df["classificacao"] == "RECEITA", "valor"].sum()
    despesa = df.loc[df["classificacao"] == "DESPESA", "valor"].sum()
    resultado = df["valor_ajustado"].sum()

    percentual = (despesa / receita * 100) if receita > 0 else 0

    col1, col2, col3 = st.columns(3)

    col1.metric("💰 Receita", f"R$ {br(receita)}")

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
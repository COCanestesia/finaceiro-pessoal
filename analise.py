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

    FUNDO = "#1E1E1E"
    VERDE = "#00C853"
    VERMELHO = "#FF4B4B"
    CINZA = "#AAAAAA"

    # 💰 RECEITA
    col1.markdown(f"""
    <div style="
        background:{FUNDO};
        padding:20px;
        border-radius:12px;
        border-left:5px solid {VERDE};
    ">
        <div style="color:{CINZA}; font-size:13px;">💰 Receita</div>
        <div style="font-size:26px; font-weight:700; color:{VERDE};">
            R$ {br(receita)}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 💸 DESPESA
    col2.markdown(f"""
    <div style="
        background:{FUNDO};
        padding:20px;
        border-radius:12px;
        border-left:5px solid {VERMELHO};
    ">
        <div style="color:{CINZA}; font-size:13px;">💸 Despesa</div>
        <div style="font-size:26px; font-weight:700; color:{VERMELHO};">
            R$ {br(despesa)}
        </div>
        <div style="font-size:12px; color:{CINZA}; margin-top:5px;">
            {percentual:.1f}% da receita
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 📊 RESULTADO
    if resultado >= 0:
        cor = VERDE
        status = "Lucro"
        emoji = "📈"
    else:
        cor = VERMELHO
        status = "Prejuízo"
        emoji = "📉"

    col3.markdown(f"""
    <div style="
        background:{FUNDO};
        padding:20px;
        border-radius:12px;
        border-left:5px solid {cor};
    ">
        <div style="color:{CINZA}; font-size:13px;">{emoji} Resultado</div>
        <div style="font-size:26px; font-weight:700; color:{cor};">
            R$ {br(resultado)}
        </div>
        <div style="font-size:12px; color:{CINZA}; margin-top:5px;">
            {status}
        </div>
    </div>
    """, unsafe_allow_html=True)

    return receita, despesa, resultado
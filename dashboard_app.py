import streamlit as st
import pandas as pd
from datetime import datetime
import calendar

from data import carregar_dados
from database import atualizar_transacao

from analise import mostrar_kpis

import plotly.express as px
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events

def br(valor):
    """Formata número em padrão brasileiro"""
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
# ==========================
# 🚀 FUNÇÃO PRINCIPAL
# ==========================
def dashboard_financeiro():
    st.title("💰 Dashboard Financeiro Pessoal")

    # 🔥 CARREGAR DUAS ABAS
    df_total, df_meta = carregar_dados()

    mes = st.sidebar.selectbox("Mês", list(range(1, 13)), index=datetime.now().month - 1)
    ano = st.sidebar.number_input("Ano", 2000, 2100, datetime.now().year)
    
    if df_total.empty:
        st.warning("Sem dados ainda")
        st.stop()

    # Filtrar mês e ano
    df = df_total[
        (df_total["DATA"].dt.month == mes) &
        (df_total["DATA"].dt.year == ano)
    ].copy()  # 🔹 usar .copy() evita warning do pandas

    # 🔹 Corrigir a coluna VALOR para float
    # Remove "R$", espaços e troca vírgula por ponto
    df["VALOR"] = df["VALOR"].astype(str) \
        .str.replace("R$", "") \
            .str.replace(".", "") \
                .str.replace(",", ".") \
                    .str.strip()

    df["VALOR"] = pd.to_numeric(df["VALOR"], errors="coerce").fillna(0)
    
    # 🔹 Remove duplicatas e linhas inválidas
    df = df.drop_duplicates()
    df = df[df["VALOR"] > 0]  # ignora valores zerados ou inválidos
    
    # Separar receita e despesa
    df_receita = df[df["CLASSIFICAÇÃO"] == "RECEITA"].copy()
    df_despesa = df[df["CLASSIFICAÇÃO"] == "DESPESA"].copy()

    # Calcular KPIs
    receita = df_receita["VALOR"].sum()
    despesa = df_despesa["VALOR"].sum()
    resultado = receita - despesa


    # ==========================
    # 📊 Categorias de despesa
    # ==========================
    df_cat = df_despesa.groupby("CATEGORIA")["VALOR"].sum().reset_index()
    df_cat = df_cat.sort_values(by="VALOR", ascending=False)

    with st.sidebar.expander("🎯 Metas", expanded=False):
        meta = st.number_input("Meta de economia (R$)", value=500)
        st.markdown("---")
        st.markdown("**Por categoria**")

        metas = {}
        for categoria in df_cat["CATEGORIA"]:
            metas[categoria] = st.number_input(
                f"{categoria}",
                min_value=0.0,
                value=500.0,
                step=50.0,
                key=f"meta_{categoria}"
            )

    # ==========================
    # METAS ABA META
    # ==========================
    if not df_meta.empty:
        st.subheader("🎯 Metas financeiras")
        st.dataframe(df_meta, use_container_width=True)
        
        
    # ==========================
    # ABAS
    # ==========================
    aba1, aba2, aba3 = st.tabs([
        "Resumo",
        "Gráficos",
        "Interativo"
        ])

    with aba1:

        # ==========================
        # 📊 KPIs
        # ==========================
        receita, despesa, resultado = mostrar_kpis(df)

        st.markdown("---")
 
        # ==========================
        # 📊 RECEITA VS DESPESA
        # ==========================
        st.subheader("📊 Receita vs Despesa")
 
        df_resumo = pd.DataFrame({
            "Tipo": ["Receita", "Despesa"],
            "Valor": [receita, despesa],
            "Altura": [1, 1]  # 🔥 força mesma altura
        })

        fig_resumo = px.bar(
            df_resumo,
            x="Tipo",
            y="Altura",   # 🔥 não usa mais o valor real aqui
            text="Valor"
        )

        fig_resumo.update_traces(
            marker_color=["#00C853", "#FF4B4B"],
            texttemplate="R$ %{text:,.0f}",
            textposition="outside"
        )

        fig_resumo.update_layout(
            yaxis=dict(visible=False),  # 🔥 remove eixo
            xaxis_title="",
            yaxis_title=""
        )

        st.plotly_chart(fig_resumo, use_container_width=True)
    
        # ==========================
        # 📊 PARA ONDE VAI O DINHEIRO
        # ==========================
        df_cat = df[df["CLASSIFICAÇÃO"] == "DESPESA"].groupby("CATEGORIA")["VALOR"].sum().reset_index()
        df_cat = df_cat.sort_values(by="VALOR", ascending=False)

        total_despesa = df_cat["VALOR"].sum()

        if total_despesa > 0:
            df_cat["Porcentagem"] = (df_cat["VALOR"] / total_despesa * 100).round(1)
        else:
            df_cat["Porcentagem"] = 0

        # ==========================
        # 🚨 MAIOR GASTO (COM ALERTA VISUAL)
        # ==========================
        if not df_cat.empty:
            top = df_cat.iloc[0]

            if top["Porcentagem"] > 30:
                cor_fundo = "#FF4B4B"
                cor_texto = "white"
            else:
                cor_fundo = "#F0F2F6"
                cor_texto = "black"

            st.markdown(f"""
            <div style="
                background-color: {cor_fundo};
                color: {cor_texto};
                padding: 15px 25px;
                border-radius: 12px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 15px;
                font-size: 16px;
            ">
                <div><b>🚨 Maior gasto:</b> {top['CATEGORIA']}</div>
                <div><b>💰 R$ {top['VALOR']:,.2f}</b></div>
                <div><b>📊 {top['Porcentagem']:.1f}%</b></div>
            </div>
            """, unsafe_allow_html=True)

        # ==========================
        # 📊 GRÁFICOS LADO A LADO
        # ==========================
        col1, col2 = st.columns(2)

        # 🥧 Pizza
        with col1:
            fig_pie = px.pie(
                df_cat,
                names="CATEGORIA",
                values="VALOR"
            )

            fig_pie.update_traces(
                textinfo="percent+label",
                hovertemplate="<b>%{label}</b><br>R$ %{value:,.2f}<br>%{percent}<extra></extra>"
            )

            st.plotly_chart(fig_pie, use_container_width=True)

        # 📊 Barra com vermelho + destaque
        with col2:
            max_valor = df_cat["VALOR"].max()
            cores = ["#8B0000" if v == max_valor else "#FF4B4B" for v in df_cat["VALOR"]]

            fig_bar = px.bar(
                df_cat,
                x="CATEGORIA",
                y="VALOR",
                text="VALOR"
            )

            fig_bar.update_traces(
                marker_color=cores,
                texttemplate="R$ %{text:,.0f}",
                textposition="outside",
                hovertemplate="<b>%{x}</b><br>R$ %{y:,.2f}<extra></extra>"
            )

            fig_bar.update_layout(
                yaxis_tickprefix="R$ ",
                xaxis_title="",
                yaxis_title=""
            )

            st.plotly_chart(fig_bar, use_container_width=True)

        # ==========================
        # 📋 TABELA DETALHADA
        # ==========================
        st.markdown("### 📋 Detalhamento dos gastos")

        st.dataframe(
            df_cat.rename(columns={
                "CATEGORIA": "Categoria",
                "VALOR": "Valor (R$)",
                "Porcentagem": "% do total"
            }).style.format({
                "Valor (R$)": "R$ {:,.2f}",
                "% do total": "{:.1f}%"
            }),
            use_container_width=True
        )

        # ==========================
        # 📊 KPIs
        # ==========================
        receita, despesa, resultado = mostrar_kpis(df)

        # 🔥 GARANTE QUE EXISTE
        comprometimento = (despesa / receita * 100) if receita > 0 else 0

        st.markdown("---")

        # ==========================
        # 🧠 DIAGNÓSTICO
        # ==========================
        st.subheader("🧠 Diagnóstico")

        if resultado < 0:
            st.error("🚨 Você está no prejuízo")
        elif comprometimento > 80:
            st.warning("⚠️ Alto risco financeiro")
        elif comprometimento > 60:
            st.info("ℹ️ Atenção nos gastos")
        else:
            st.success("✅ Tudo sob controle")

        # ==========================
        # 🎯 METAS
        # ==========================
        st.subheader("🎯 Metas financeiras")

        percentual_meta = (resultado / meta * 100) if meta > 0 else 0

        # 🎨 cor + alerta
        if percentual_meta >= 100:
            cor = "#00C853"
            status = "✅ Meta atingida"
        elif percentual_meta >= 70:
            cor = "#FFA500"
            status = "⚠️ Quase lá"
        else:
            cor = "#FF4B4B"
            status = "🚨 Abaixo da meta"
        
        # 📦 LINHA ÚNICA
        col1, col2, col3 = st.columns([2, 2, 2])

        with col1:
            st.markdown(f"**🎯 Meta:** R$ {br(meta)}")
        
        with col2:
            st.markdown(f"**💰 Resultado:** R$ {br(resultado)}")

        with col3:
            st.markdown(
                f"<div style='color:{cor}; font-weight:700; text-align:right;'>"
                f"{percentual_meta:.0f}% • {status}</div>",
                unsafe_allow_html=True
            )
        
        st.markdown("---")

        # ==========================
        # 📊 COMPARAÇÃO
        # ==========================
        df_cat["Meta"] = df_cat["CATEGORIA"].map(metas)

        df_cat["% Meta"] = df_cat.apply(
            lambda x: (x["VALOR"] / x["Meta"]* 100)
            if x["Meta"] > 0 else 0,
            axis=1
         ).round(1)

        # ==========================
        # 📊 PROGRESSO
        # ==========================
        st.subheader("📊 Acompanhamento das metas")

        for _, row in df_cat.iterrows():
        
            categoria = row["CATEGORIA"]
            valor = row["VALOR"]
            meta_cat = row["Meta"]

            percentual = (valor / meta_cat * 100) if meta_cat > 0 else 0
            progresso = min(percentual / 100, 1.0)

            # 🎨 cor da %
            if percentual > 100:
                cor = "#FF4B4B"
                status = "🚨"
            elif percentual > 80:
                cor = "#FFA500"
                status = "⚠️"
            else:
                cor = "#00C853"
                status = "✅"

            # ==========================
            # 📦 LINHA COMPACTA
            # ==========================
            col1, col2, col3 = st.columns([2, 2, 1])

            with col1:
                st.markdown(f"**{categoria}**")

            with col2:
                st.markdown(
                    f"<div style='color:#FFFFFF; font-weight:500;'>"
                    f"R$ {br(valor)} / R$ {br(meta_cat)}"
                    f"</div>",
                    unsafe_allow_html=True
                )

            with col3:
                st.markdown(
                    f"<div style='text-align:right; color:{cor}; font-weight:600;'>"
                    f"{percentual:.0f}% {status}</div>",
                    unsafe_allow_html=True
                )

            cor_barra = cor

            st.markdown(f"""
            <div style="
                background-color:#2A2A2A;
                border-radius:8px;
                height:8px;
                overflow:hidden;
                margin-top:4px;
            ">
                <div style="
                    width:{progresso*100}%;
                    background:{cor_barra};
                    height:100%;
                "></div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<div style='margin-bottom:8px'></div>", unsafe_allow_html=True)

        # ==========================
        # 📋 EXPLORAR DADOS
        # ==========================
        st.markdown("---")
        st.subheader("📋 Explorar seus dados")

        colunas = st.multiselect(
            "Escolha as colunas",
            df.columns.tolist(),
            default=[
                "DATA",
                "CATEGORIA",
                "VALOR"
            ]
        )

        df_view = df[colunas]

        if "CATEGORIA" in df.columns:
            categorias = st.multiselect(
                "Filtrar Categoria",
                df["CATEGORIA"].dropna().unique()
            )

            if categorias:
                df_view = df_view[df_view["CATEGORIA"].isin(categorias)]

        ordenar = st.selectbox("Ordenar por", df_view.columns)
        ordem = st.radio("Ordem", ["Decrescente", "Crescente"])

        df_view = df_view.sort_values(
            by=ordenar,
            ascending=(ordem == "Crescente")
        )

        modo = st.radio("Visualização", ["Tabela", "Gráfico"])

        if modo == "Tabela":
            st.dataframe(
                df_view.style.format({
                    "VALOR": "R$ {:,.2f}"
                }),
            use_container_width=True
            )
        else:
            st.subheader("📊 Criar gráfico")

            eixo_x = st.selectbox("Eixo X", df_view.columns)
            eixo_y = st.selectbox("Eixo Y", ["VALOR"])
            tipo = st.selectbox("Tipo de gráfico", ["Barra", "Linha"])

            df_group = df_view.groupby(eixo_x)[eixo_y].sum().reset_index()

            if tipo == "Barra":
                fig = px.bar(df_group, x=eixo_x, y=eixo_y)
            else:
                fig = px.line(df_group, x=eixo_x, y=eixo_y)

            fig.update_traces(
                texttemplate="R$ %{y:,.0f}",
                textposition="outside",
                hovertemplate="<b>%{x}</b><br>Valor: R$ %{y:,.2f}<extra></extra>"
            )

            fig.update_layout(yaxis_tickprefix="R$ ")

            st.plotly_chart(fig, use_container_width=True)
    # ==========================
    # 📈 ABA 2 - GRÁFICOS
    # ==========================
    with aba2:

        st.subheader("📅 Comparação ao longo do tempo")

        df_total["Mes"] = df_total["DATA"].dt.to_period("M").dt.to_timestamp()

        # 🔥 separa corretamente
        df_receita = (
            df_total[df_total["CLASSIFICAÇÃO"] == "RECEITA"]
            .groupby("Mes")["VALOR"]
            .sum()
            .reset_index(name="Receita")
        )

        df_despesa = (
            df_total[df_total["CLASSIFICAÇÃO"] == "DESPESA"]
            .groupby("Mes")["VALOR"]
            .sum()
            .reset_index(name="Despesa")
        )

        # 🔥 merge correto
        df_mes = pd.merge(df_receita, df_despesa, on="Mes", how="outer").fillna(0)

        # 🔥 resultado correto
        df_mes["Resultado"] = df_mes["Receita"] - df_mes["Despesa"]

        # ==========================
        # 📈 Receita vs Despesa
        # ==========================
        fig = px.line(
            df_mes,
            x="Mes",
            y=["Receita", "Despesa"]
        )

        fig.update_layout(
            yaxis_tickprefix="R$ ",
            xaxis_title="Mês",
            yaxis_title="Valor"
        )

        st.plotly_chart(fig, use_container_width=True)

        # ==========================
        # 📊 Resultado
        # ==========================
        fig2 = px.bar(
            df_mes,
            x="Mes",
            y="Resultado",
            text="Resultado"
        )

        fig2.update_traces(
            texttemplate="R$ %{text:,.0f}",
            textposition="outside"
        )

        fig2.update_layout(
            yaxis_tickprefix="R$ ",
            xaxis_title="Mês",
            yaxis_title="Resultado"
            )

        st.plotly_chart(fig2, use_container_width=True)
    # ==========================
    # 🧠 ABA 3 - INTERATIVO (FINAL)
    # ==========================
    with aba3:

        st.subheader("📊 Análise Interativa")

        # ==========================
        # 🔥 BASE LIMPA
        # ==========================
        df_interativo = df_total.copy()

        # 🔥 GARANTE COLUNA SUBCATEGORIA
        if "SUBCATEGORIA" not in df_interativo.columns:
            df_interativo["SUBCATEGORIA"] = "Outros"

        df_interativo["SUBCATEGORIA"] = (
            df_interativo["SUBCATEGORIA"]
            .fillna("Outros")
            .astype(str)
            .str.upper()
            .str.strip()
        )

        # 🔥 GARANTE VALOR NUMÉRICO
        df_interativo["VALOR"] = pd.to_numeric(
            df_interativo["VALOR"], errors="coerce"
        ).fillna(0)

        df_interativo["CATEGORIA"] = (
            df_interativo["CATEGORIA"]
            .astype(str)
            .str.upper()
            .str.strip()
        )

        # ==========================
        # 📅 FILTRO DE MÊS
        # ==========================
        meses = st.multiselect(
            "Selecione os meses",
            options=sorted(df_interativo["MÊS"].dropna().unique()),
            default=sorted(df_interativo["MÊS"].dropna().unique())
        )

        df_filtrado = df_interativo[
            df_interativo["MÊS"].isin(meses)
        ].copy()

        df_filtrado = df_filtrado.drop_duplicates()

        # ==========================
        # 🧠 ESTADOS
        # ==========================
        if "filtro_categoria" not in st.session_state:
            st.session_state.filtro_categoria = None

        if "filtro_subcategoria" not in st.session_state:
            st.session_state.filtro_subcategoria = None

        # ==========================
        # 📊 GRÁFICO CATEGORIA
        # ==========================
        df_cat = (
            df_filtrado
            .groupby("CATEGORIA", as_index=False)["VALOR"]
            .sum()
            .sort_values(by="VALOR", ascending=False)
        )

        df_cat = df_cat[df_cat["VALOR"] > 0]

        fig_cat = go.Figure()

        fig_cat.add_trace(go.Bar(
            x=df_cat["VALOR"],
            y=df_cat["CATEGORIA"],
            orientation='h',
            text=[f"R$ {v:,.2f}" for v in df_cat["VALOR"]],
            textposition='outside'
        ))

        fig_cat.update_layout(
            title="💸 Gasto por Categoria",
            xaxis=dict(tickprefix="R$ "),
    
            # 🔥 melhora alinhamento das categorias
            yaxis=dict(
                categoryorder="total ascending",
                automargin=True
            ),

            # 🔥 evita cortar ou desalinhamento
            margin=dict(l=180),

            # 🔥 altura dinâmica (opcional mas recomendado)
            height=40 * len(df_cat)
        )

        selected = st.plotly_chart(
            fig_cat,
            use_container_width=True,
            on_select="rerun"
        )

        # ==========================
        # 🎯 CLIQUE CATEGORIA
        # ==========================
        if selected and "selection" in selected:
            pontos = selected["selection"]["points"]
            if pontos:
                st.session_state.filtro_categoria = pontos[0]["y"]
                st.session_state.filtro_subcategoria = None  # reset sub

            # ==========================
            # 📊 FILTRO CATEGORIA
            # ==========================
            if st.session_state.filtro_categoria:
                df_filtrado = df_filtrado[
                    df_filtrado["CATEGORIA"] == st.session_state.filtro_categoria
                ]
                st.info(f"Categoria: {st.session_state.filtro_categoria}")

            # ==========================
            # 📊 SUBCATEGORIA
            # ==========================
            df_sub = (
                df_filtrado
                .groupby("SUBCATEGORIA", as_index=False)["VALOR"]
                .sum()
                .sort_values(by="VALOR", ascending=False)
            )

            fig_sub = go.Figure()

            fig_sub.add_trace(go.Bar(
                x=df_sub["VALOR"],
                y=df_sub["SUBCATEGORIA"],
                orientation='h',
                text=[f"R$ {v:,.2f}" for v in df_sub["VALOR"]],
                textposition='outside'
            ))

            fig_sub.update_layout(
                title="📂 Subcategorias",
                xaxis=dict(tickprefix="R$ "),
                height=400
            )

            selected_sub = st.plotly_chart(
                fig_sub,
                use_container_width=True,
                on_select="rerun"
            )

            # ==========================
            # 🎯 CLIQUE SUBCATEGORIA
            # ==========================
            if selected_sub and "selection" in selected_sub:
                pontos = selected_sub["selection"]["points"]
                if pontos:
                    st.session_state.filtro_subcategoria = pontos[0]["y"]

        # ==========================
        # 📊 FILTRO FINAL
        # ==========================
        if st.session_state.filtro_subcategoria:
            df_filtrado = df_filtrado[
                df_filtrado["SUBCATEGORIA"] == st.session_state.filtro_subcategoria
            ]
            st.success(f"Subcategoria: {st.session_state.filtro_subcategoria}")

        # ==========================
        # 💰 KPI
        # ==========================
        total = df_filtrado["VALOR"].sum()
        st.markdown(f"## 💰 R$ {total:,.2f}")

        # ==========================
        # 📈 EVOLUÇÃO
        # ==========================
        df_evo = (
            df_filtrado
            .groupby("DATA", as_index=False)["VALOR"]
            .sum()
        )

        fig_evo = px.line(df_evo, x="DATA", y="VALOR", markers=True)
        fig_evo.update_layout(yaxis_tickprefix="R$ ")

        st.plotly_chart(fig_evo, use_container_width=True)

        # ==========================
        # 📋 TABELA
        # ==========================
        st.markdown("### 📋 Detalhamento")

        df_tabela = df_filtrado.copy()
        df_tabela["DATA"] = df_tabela["DATA"].dt.strftime("%d")

        colunas = ["MÊS", "DATA", "CATEGORIA", "SUBCATEGORIA", "VALOR", "DESCRIÇÃO"]

        st.dataframe(
            df_tabela[colunas]
            .sort_values(by="VALOR", ascending=False)
            .style.format({"VALOR": "R$ {:,.2f}"}),
            use_container_width=True,
            height=400
        )
        
        # ==========================
        # 🧠 INTELIGÊNCIA FINANCEIRA
        # ==========================

        st.markdown("---")
        st.subheader("🧠 Inteligência Financeira")

        # ==========================
        # 🔮 PREVISÃO DO MÊS
        # ==========================


        hoje = datetime.now()
        dia_atual = hoje.day
        dias_mes = calendar.monthrange(hoje.year, hoje.month)[1]

        df_mes_atual = df_total[
            (df_total["DATA"].dt.month == hoje.month) &
            (df_total["DATA"].dt.year == hoje.year) &
            (df_total["CLASSIFICAÇÃO"] == "DESPESA")
        ].copy()

        df_mes_atual["VALOR"] = pd.to_numeric(df_mes_atual["VALOR"], errors="coerce").fillna(0)

        gasto_atual = df_mes_atual["VALOR"].sum()

        previsao = (gasto_atual / dia_atual) * dias_mes if dia_atual > 0 else 0

        col1, col2 = st.columns(2)

        with col1:
            st.metric("💰 Gasto atual", f"R$ {gasto_atual:,.2f}")

        with col2:
            st.metric("🔮 Previsão do mês", f"R$ {previsao:,.2f}")

        if previsao > gasto_atual * 1.5:
            st.warning("⚠️ Ritmo de gasto alto — tendência de estourar o orçamento")

        # ==========================
        # 🚨 GASTOS ANORMAIS
        # ==========================
        st.markdown("---")
        st.subheader("🚨 Gastos Anormais")

        df_outlier = df_total[df_total["CLASSIFICAÇÃO"] == "DESPESA"].copy()

        df_outlier["VALOR"] = pd.to_numeric(df_outlier["VALOR"], errors="coerce").fillna(0)

        # média e desvio padrão (mais profissional)
        stats = df_outlier.groupby("SUBCATEGORIA")["VALOR"].agg(["mean", "std"]).reset_index()

        df_outlier = df_outlier.merge(stats, on="SUBCATEGORIA", how="left")

        df_outlier["anomalia"] = df_outlier["VALOR"] > (df_outlier["mean"] + 2 * df_outlier["std"])

        anomalias = df_outlier[df_outlier["anomalia"]]

        if not anomalias.empty:
            for _, row in anomalias.iterrows():
                st.error(
                    f"🚨 {row['SUBCATEGORIA']} → R$ {row['VALOR']:,.2f} "
                    f"(normal ~ R$ {row['mean']:,.2f})"
                )
        else:
            st.success("✅ Nenhum gasto anormal detectado")

        # ==========================
        # 📈 ANÁLISE DE SUBIDA / QUEDA
        # ==========================
        st.markdown("---")
        st.subheader("📈 Análise de Variação")
 
        df_total["Mes"] = df_total["DATA"].dt.to_period("M").dt.to_timestamp()

        df_mensal = (
            df_total[df_total["CLASSIFICAÇÃO"] == "DESPESA"]
            .groupby(["Mes", "CATEGORIA", "SUBCATEGORIA"])["VALOR"]
            .sum()
            .reset_index()
        )

        meses = sorted(df_mensal["Mes"].unique())

        if len(meses) >= 2:

            mes_atual = meses[-1]
            mes_anterior = meses[-2]

            df_atual = df_mensal[df_mensal["Mes"] == mes_atual]
            df_anterior = df_mensal[df_mensal["Mes"] == mes_anterior]

            df_comp = pd.merge(
                df_atual,
                df_anterior,
                on=["CATEGORIA", "SUBCATEGORIA"],
                how="outer",
                suffixes=("_atual", "_anterior")
            ).fillna(0)

            df_comp["dif"] = df_comp["VALOR_atual"] - df_comp["VALOR_anterior"]

            df_comp["pct"] = df_comp.apply(
                lambda x: (x["dif"] / x["VALOR_anterior"] * 100)
                if x["VALOR_anterior"] > 0 else 0,
                axis=1
            )

            for _, row in df_comp.iterrows():

                cat = row["CATEGORIA"]
                sub = row["SUBCATEGORIA"]
                dif = row["dif"]
                pct = row["pct"]
 
                if dif > 0 and pct > 30:
                    st.error(f"🚨 {cat} → {sub} aumentou {pct:.0f}% (+R$ {dif:,.2f})")

                elif dif > 0 and pct > 10:
                    st.warning(f"⚠️ {cat} → {sub} subiu {pct:.0f}%")

                elif dif < 0:
                    st.success(f"✅ {cat} → {sub} reduziu {abs(pct):.0f}%")

            # 🔥 TOP AUMENTOS
            st.markdown("### 🔥 Maiores aumentos")

            top = df_comp.sort_values(by="dif", ascending=False).head(5)

            st.dataframe(
                top[["CATEGORIA", "SUBCATEGORIA", "dif", "pct"]]
                .rename(columns={
                    "dif": "Aumento (R$)",
                    "pct": "% aumento"
                })
                .style.format({
                    "Aumento (R$)": "R$ {:,.2f}",
                    "% aumento": "{:.1f}%"
                }),
                use_container_width=True
            )

        else:
            st.info("📊 Ainda não há dados suficientes para comparação mensal")

        # ==========================
        # 🔄 RESET
        # ==========================
        if st.button("🔄 Limpar tudo"):
            st.session_state.filtro_categoria = None
            st.session_state.filtro_subcategoria = None
            st.rerun()
# ==========================
# EXECUÇÃO
# ==========================
if __name__ == "__main__":
    dashboard_financeiro()
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
        (df_total["data"].dt.month == mes) &
        (df_total["data"].dt.year == ano)
    ].copy()  # 🔹 usar .copy() evita warning do pandas

    # 🔹 Corrigir a coluna VALOR para float
    # Remove "R$", espaços e troca vírgula por ponto
    df["valor"] = df["valor"].astype(str) \
        .str.replace("R$", "") \
            .str.replace(".", "") \
                .str.replace(",", ".") \
                    .str.strip()

    df["valor"] = pd.to_numeric(df["valor"], errors="coerce").fillna(0)
    
    # 🔹 Remove duplicatas e linhas inválidas
    df = df.drop_duplicates()
    df = df[df["valor"] > 0]  # ignora valores zerados ou inválidos
    
    # Separar receita e despesa
    df_receita = df[df["classificacao"] == "RECEITA"].copy()
    df_despesa = df[df["classificacao"] == "DESPESA"].copy()

    # Calcular KPIs
    receita = df_receita["valor"].sum()
    despesa = df_despesa["valor"].sum()
    resultado = receita - despesa


    # ==========================
    # 📊 Categorias de despesa
    # ==========================
    df_cat = df_despesa.groupby("categoria")["valor"].sum().reset_index()
    df_cat = df_cat.sort_values(by="valor", ascending=False)

    with st.sidebar.expander("🎯 Metas", expanded=False):
        meta = st.number_input("Meta de economia (R$)", value=500)
        st.markdown("---")
        st.markdown("**Por categoria**")

        metas = {}
        for categoria in df_cat["categoria"]:
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
    aba1, aba2 = st.tabs([
        "Resumo",
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
        df_cat = df[df[""] == "DESPESA"].groupby("categoria")["valor"].sum().reset_index()
        df_cat = df_cat.sort_values(by="valor", ascending=False)

        total_despesa = df_cat["valor"].sum()

        if total_despesa > 0:
            df_cat["Porcentagem"] = (df_cat["valor"] / total_despesa * 100).round(1)
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
                <div><b>🚨 Maior gasto:</b> {top['categoria']}</div>
                <div><b>💰 R$ {top['valor']:,.2f}</b></div>
                <div><b>📊 {top['Porcentagem']:.1f}%</b></div>
            </div>
            """, unsafe_allow_html=True)

        # ==========================
        # 📊 GRÁFICOS LADO A LADO
        # ==========================
        col1, col2 = st.columns(2)

        # 📊 Barra (substitui a pizza)
        with col1:
            fig_bar_cat = px.bar(
                df_cat,
                x="valor",
                y="categoria",
                orientation="h",
                text="valor"
            )

            fig_bar_cat.update_traces(
                texttemplate="R$ %{text:,.0f}",
                textposition="outside",
                hovertemplate="<b>%{y}</b><br>R$ %{x:,.2f}<extra></extra>"
            )

            fig_bar_cat.update_layout(
                xaxis_tickprefix="R$ ",
                yaxis_title="",
                xaxis_title=""
            )

        st.plotly_chart(fig_bar_cat, use_container_width=True)

        # 📊 Barra com vermelho + destaque
        with col2:
            max_valor = df_cat["valor"].max()
            cores = ["#8B0000" if v == max_valor else "#FF4B4B" for v in df_cat["valor"]]

            fig_bar = px.bar(
                df_cat,
                x="categoria",
                y="valor",
                text="valor"
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
                "categoria": "Categoria",
                "valor": "Valor (R$)",
                "Porcentagem": "% do total"
            }).style.format({
                "valor (R$)": "R$ {:,.2f}",
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
        df_cat["meta"] = df_cat["categoria"].map(metas)

        df_cat["% meta"] = df_cat.apply(
            lambda x: (x["valor"] / x["meta"]* 100)
            if x["meta"] > 0 else 0,
            axis=1
         ).round(1)

        # ==========================
        # 📊 PROGRESSO
        # ==========================
        st.subheader("📊 Acompanhamento das metas")

        for _, row in df_cat.iterrows():
        
            categoria = row["categoria"]
            valor = row["valor"]
            meta_cat = row["meta"]

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
                "data",
                "categoria",
                "valor"
            ]
        )

        df_view = df[colunas]

        if "categoria" in df.columns:
            categorias = st.multiselect(
                "Filtrar Categoria",
                df["categoria"].dropna().unique()
            )

            if categorias:
                df_view = df_view[df_view["categoria"].isin(categorias)]

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
                    "valor": "R$ {:,.2f}"
                }),
            use_container_width=True
            )
        else:
            st.subheader("📊 Criar gráfico")

            eixo_x = st.selectbox("Eixo X", df_view.columns)
            eixo_y = st.selectbox("Eixo Y", ["valor"])
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
    # 🧠 ABA 2 - INTERATIVO (FINAL)
    # ==========================
    with aba2:

        st.subheader("📊 Análise Interativa")

        # ==========================
        # 🔥 BASE LIMPA
        # ==========================
        df_interativo = df_total.copy()

        # 🔥 GARANTE COLUNA SUBCATEGORIA
        if "subcategoria" not in df_interativo.columns:
            df_interativo["subcategoria"] = "Outros"

        df_interativo["subcategoria"] = (
            df_interativo["subcategoria"]
            .fillna("Outros")
            .astype(str)
            .str.upper()
            .str.strip()
        )

        # 🔥 GARANTE VALOR NUMÉRICO
        df_interativo["valor"] = pd.to_numeric(
            df_interativo["valor"], errors="coerce"
        ).fillna(0)

        df_interativo["categoria"] = (
            df_interativo["categoria"]
            .astype(str)
            .str.upper()
            .str.strip()
        )

        # ==========================
        # 📅 FILTRO DE MÊS
        # ==========================
        meses = st.multiselect(
            "Selecione os meses",
            options=sorted(df_interativo["mes"].dropna().unique()),
            default=sorted(df_interativo["mes"].dropna().unique())
        )

        df_filtrado = df_interativo[
            df_interativo["mes"].isin(meses)
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
            .groupby("categoria", as_index=False)["valor"]
            .sum()
            .sort_values(by="valor", ascending=False)
        )

        df_cat = df_cat[df_cat["valor"] > 0]

        fig_cat = go.Figure()

        fig_cat.add_trace(go.Bar(
            x=df_cat["valor"],
            y=df_cat["categoria"],
            orientation='h',
            text=[f"R$ {v:,.2f}" for v in df_cat["valor"]],
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
                    df_filtrado["categoria"] == st.session_state.filtro_categoria
                ]
                st.info(f"Categoria: {st.session_state.filtro_categoria}")

            # ==========================
            # 📊 SUBCATEGORIA
            # ==========================
            df_sub = (
                df_filtrado
                .groupby("subcategoria", as_index=False)["valor"]
                .sum()
                .sort_values(by="valor", ascending=False)
            )

            fig_sub = go.Figure()

            fig_sub.add_trace(go.Bar(
                x=df_sub["valor"],
                y=df_sub["subcategoria"],
                orientation='h',
                text=[f"R$ {v:,.2f}" for v in df_sub["valor"]],
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
                df_filtrado["subcategoria"] == st.session_state.filtro_subcategoria
            ]
            st.success(f"Subcategoria: {st.session_state.filtro_subcategoria}")

        # ==========================
        # 💰 KPI
        # ==========================
        total = df_filtrado["valor"].sum()
        st.markdown(f"## 💰 R$ {total:,.2f}")

        # ==========================
        # 📈 EVOLUÇÃO
        # ==========================
        df_evo = (
            df_filtrado
            .groupby("data", as_index=False)["valor"]
            .sum()
        )

        fig_evo = px.line(df_evo, x="data", y="valor", markers=True)
        fig_evo.update_layout(yaxis_tickprefix="R$ ")

        st.plotly_chart(fig_evo, use_container_width=True)

        # ==========================
        # 📋 TABELA
        # ==========================
        st.markdown("### 📋 Detalhamento")

        df_tabela = df_filtrado.copy()
        df_tabela["data"] = df_tabela["data"].dt.strftime("%d")

        colunas = ["mes", "data", "categoria", "subcategoria", "valor", "descricao"]

        st.dataframe(
            df_tabela[colunas]
            .sort_values(by="valor", ascending=False)
            .style.format({"valor": "R$ {:,.2f}"}),
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
            (df_total["data"].dt.month == hoje.month) &
            (df_total["data"].dt.year == hoje.year) &
            (df_total["classificacao"] == "DESPESA")
        ].copy()

        df_mes_atual["valor"] = pd.to_numeric(df_mes_atual["valor"], errors="coerce").fillna(0)

        gasto_atual = df_mes_atual["valor"].sum()

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

        df_outlier = df_total[df_total["classificacao"] == "DESPESA"].copy()

        df_outlier["valor"] = pd.to_numeric(df_outlier["valor"], errors="coerce").fillna(0)

        # média e desvio padrão (mais profissional)
        stats = df_outlier.groupby("subcategoria")["valor"].agg(["mean", "std"]).reset_index()

        df_outlier = df_outlier.merge(stats, on="subcategoria", how="left")

        df_outlier["anomalia"] = df_outlier["valor"] > (df_outlier["mean"] + 2 * df_outlier["std"])

        anomalias = df_outlier[df_outlier["anomalia"]]

        if not anomalias.empty:
            for _, row in anomalias.iterrows():
                st.error(
                    f"🚨 {row['subcategoria']} → R$ {row['valor']:,.2f} "
                    f"(normal ~ R$ {row['mean']:,.2f})"
                )
        else:
            st.success("✅ Nenhum gasto anormal detectado")

        # ==========================
        # 📈 ANÁLISE DE SUBIDA / QUEDA
        # ==========================
        st.markdown("---")
        st.subheader("📈 Análise de Variação")
 
        df_total["mes"] = df_total["data"].dt.to_period("M").dt.to_timestamp()

        df_mensal = (
            df_total[df_total["classificacao"] == "DESPESA"]
            .groupby(["mes", "categoria", "subcategoria"])["valor"]
            .sum()
            .reset_index()
        )

        meses = sorted(df_mensal["mes"].unique())

        if len(meses) >= 2:

            mes_atual = meses[-1]
            mes_anterior = meses[-2]

            df_atual = df_mensal[df_mensal["mes"] == mes_atual]
            df_anterior = df_mensal[df_mensal["mes"] == mes_anterior]

            df_comp = pd.merge(
                df_atual,
                df_anterior,
                on=["categoria", "subcategoria"],
                how="outer",
                suffixes=("_atual", "_anterior")
            ).fillna(0)

            df_comp["dif"] = df_comp["valor_atual"] - df_comp["valor_anterior"]

            df_comp["pct"] = df_comp.apply(
                lambda x: (x["dif"] / x["valor_anterior"] * 100)
                if x["valor_anterior"] > 0 else 0,
                axis=1
            )

            for _, row in df_comp.iterrows():

                cat = row["categoria"]
                sub = row["subcategoria"]
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
                top[["categoria", "subcategoria", "dif", "pct"]]
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
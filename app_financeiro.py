import pandas as pd
import streamlit as st
from datetime import datetime
from data import carregar_dados, calcular_saldos

from database import (
    inserir_transacao,
    atualizar_transacao,
    buscar_transacoes,
    buscar_metas
)

# =========================
# 🚀 FUNÇÃO PRINCIPAL
# =========================
def sistema_financeiro():

    st.title("💰 Sistema Financeiro")

    df_topo = carregar_dados()


    # =========================
    # 🚨 ALERTAS DE VENCIMENTO
    # =========================
    def verificar_alertas(df):

        hoje = datetime.today().date()
        avisos = []

        if df.empty:
            return avisos

        for _, row in df.iterrows():

            # ✔ usa coluna padronizada
            if str(row.get("classificacao", "")).upper() != "DESPESA":
                continue

            if str(row.get("status", "")).upper() == "PAGO":
                continue

            vencimento = row.get("data_vencimento")

            if pd.isna(vencimento):
                continue

            try:
                vencimento = pd.to_datetime(vencimento).date()
            except:
                continue

            dias = (vencimento - hoje).days

            descricao = row.get("descricao", "Sem descrição")

            if dias < 0:
                avisos.append(f"❌ {descricao} está vencido há {abs(dias)} dia(s)")
            elif dias <= 3:
                avisos.append(f"⚠️ {descricao} vence em {dias} dia(s)")

        return avisos

    # =========================
    # 💰 SALDO (TEMPO REAL)
    # =========================
    saldos = calcular_saldos(df)

    colunas = st.columns(len(saldos))

    for i, (nome, saldo) in enumerate(saldos.items()):

        icone = "💵" if "Dinheiro" in nome else "🏦"
        cor = "🔴" if saldo < 0 else "🟢"

        colunas[i].markdown(
            f"### {icone} {nome}\n{cor} R$ {saldo:,.2f}"
        )
    
            
    # -------------------------
    # 📌 CATEGORIAS
    # -------------------------
    if "categorias" not in st.session_state:
        st.session_state.categorias = [
            "COMPRAS PESSOAIS", "CIGARROS", "TAXA DE IMÓVEL", "EQUIPAMENTOS",
            "TAXA", "ASSINATURAS", "ALIMENTAÇÃO", "TRANSPORTE",
            "REMUNERAÇÃO", "MANUTENÇÃO", "MORADIA", "CARTÃO DE CRÉDITO",
            "PLANTÕES", "SAÚDE", "TERCEIRIZADOS", "EDUCAÇÃO",
            "ACORDO JUDICIAL", "APORTE HCT", "HONORÁRIOS"
        ]

    # -------------------------
    # 📑 ABAS
    # -------------------------
    tab1, tab2, tab3 = st.tabs([
        "💾 Lançamentos",
        "📋 Consulta",
        "💰 RESUMO DE SALDOS"
    ])

    # -------------------------
    # 📝 ABA 1 - INSERIR
    # -------------------------
    with tab1:
        st.subheader("Adicionar lançamento")

        # Inicializar categorias
        if "categorias" not in st.session_state:
            st.session_state.categorias = ["Alimentação", "Transporte", "Lazer"]

        with st.form("form_dados", clear_on_submit=True):

            titular = st.text_input("titular")
            data = st.date_input("data")

            mes = st.selectbox("mês", [
                "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
            ])

            descricao = st.text_input("descrição")
    
            # Lista de bancos
            bancos = ["Itaú", "Bradesco", "Banco do Brasil", "Nubank"]

            # Contas possíveis
            contas = ["ESPÉCIE"] + [f"TRANSFERÊNCIA BANCÁRIA ({banco})" for banco in bancos]

            conta = st.selectbox("Conta", contas)
            valor = st.number_input("valor", min_value=0.0)
            # NOVOS CAMPOS
            data_vencimento = st.date_input("data de vencimento", value=datetime.today().date())

            status = st.selectbox("status", ["Pendente", "Pago"])

            # -----------------------
            # ✅ CATEGORIA DINÂMICA (DENTRO DO SELECT)
            # -----------------------
            opcoes = st.session_state.categorias + ["➕ nova categoria"]

            categoria = st.selectbox("Categoria", opcoes)

            # Campo só aparece se escolher nova categoria
            nova_categoria = None
            if categoria == "➕ nova categoria":
                nova_categoria = st.text_input("Digite a nova categoria")

            subcategoria = st.text_input("subcategoria")
            tipo_despesa = st.text_input("tipo de despesa")

            classificacao = st.selectbox("classificação", ["Receita", "Despesa"])

            submit = st.form_submit_button("Salvar")

            # -----------------------
            # 💾 SALVAR
            # -----------------------
            if submit:

                # 🔥 Trata nova categoria
                if categoria == "➕ nova categoria":
                    if nova_categoria:
                        if nova_categoria not in st.session_state.categorias:
                            st.session_state.categorias.append(nova_categoria)
                            categoria = nova_categoria
                        else:
                            categoria = nova_categoria
                    else:
                        st.warning("Digite o nome da nova categoria!")
                        st.stop()

                linha = [
                    titular,
                    str(data),
                    mes,
                    descricao,
                    conta,
                    valor,
                    categoria,
                    subcategoria,
                    tipo_despesa,
                    classificacao,
                    str(data_vencimento),  # NOVO
                    status                 # NOVO 
                ]

                inserir_transacao(linha)
                st.success("Salvo no banco de dados!")
                st.rerun()

    # -------------------------
    # 📊 ABA 2 - CONSULTA
    # -------------------------
    with tab2:
        st.subheader("📋 Consulta de dados")

        df = carregar_dados()

        if df.empty:
            st.info("Sem dados ainda")
        else:
            df.columns = df.columns.str.strip()
            df["Data"] = pd.to_datetime(df["Data"], errors="coerce")

            # -------------------------
            # FILTROS
            # -------------------------
            df["Ano"] = df["Data"].dt.year
            df["Mes_num"] = df["Data"].dt.month

            col1, col2 = st.columns(2)
            ano = col1.selectbox("Ano", sorted(df["Ano"].dropna().unique()))
            mes = col2.selectbox("Mês", ["Todos"] + list(range(1, 13)))

            if mes == "Todos":
                df_filtrado = df[df["Ano"] == ano]
            else:
                df_filtrado = df[(df["Ano"] == ano) & (df["Mes_num"] == mes)]

            # -------------------------
            # 🎯 SELETOR DE MODO
            # -------------------------
            modo = st.radio(
                "Visualização",
                ["📋 Tabela normal", "📅 Acompanhamento diário"],
                horizontal=True
            )

            # =========================
            # 📋 TABELA NORMAL
            # =========================
            if modo == "📋 Tabela normal":

                if df_filtrado.empty:
                    st.warning("Sem dados")
                else:
                    df_final = df_filtrado[[
                        "Titular", "Data", "Mês", "Descrição", "Conta",
                        "Valor", "Categoria", "Tipo de despesa", "Classificação"
                    ]]

                    # Renomear colunas
                    df_final.columns = [
                        "TITULAR", "DATA", "MÊS", "DESCRIÇÃO", "CONTA",
                        "VALOR", "CATEGORIA", "TIPO DE DESPESA", "CLASSIFICAÇÃO"
                    ]

                    # Função para formatar valores em Real
                    def format_real(x):
                        return f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

                    # Aplicar apenas na coluna VALOR
                    df_final["VALOR"] = df_final["VALOR"].apply(format_real)

                    st.dataframe(df_final, use_container_width=True)

            if modo == "📅 Acompanhamento diário":

                st.markdown("## 📅 Acompanhamento Diário")

                df_filtrado = df_filtrado.sort_values("Data")

                for data, grupo in df_filtrado.groupby("Data"):

                    # =========================
                    # 📅 VENCIMENTO (TÍTULO DO DIA)
                    # =========================
                    st.markdown(
                        f"""
                        <div style='background-color:#d9e1f2;padding:10px;border-radius:8px'>
                            <b>📅 Vencimento: {data.strftime('%d/%m/%Y')}</b>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    col1, col2 = st.columns([4, 1])

                    # =========================
                    # 📋 TABELA DO DIA
                    # =========================
                    with col1:

                        tabela = pd.DataFrame({
                            "TITULAR": grupo.get("Titular", ""),
                            "CATEGORIA": grupo.get("Categoria", ""),
                            "DESCRIÇÃO": grupo.get("Descrição", ""),
                            "TIPO": grupo.get("Tipo de despesa", ""),
                            "FORMA DE PAGAMENTO": grupo.get("Conta", ""),
                            "PLANEJADO": 0,  # Substitua pelo valor real se tiver
                            "EXECUTADO": grupo.get("Valor", 0)
                        })

                        # Totais do dia
                        total_planejado = tabela["PLANEJADO"].sum()
                        total_executado = tabela["EXECUTADO"].sum()

                        # Função para formatar valores em Real
                        def format_real(x):
                            return f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

                        tabela["PLANEJADO"] = tabela["PLANEJADO"].apply(format_real)
                        tabela["EXECUTADO"] = tabela["EXECUTADO"].apply(format_real)

                        st.dataframe(tabela, use_container_width=True)

                    # =========================
                    # 💰 RESUMO LATERAL
                    # =========================
                    with col2:

                        diferenca = total_planejado - total_executado

                        st.markdown("### 💰 Totais do dia")

                        st.metric("Planejado", format_real(total_planejado))
                        st.metric("Executado", format_real(total_executado))
                        st.metric("Diferença", format_real(diferenca))

                    st.markdown("---")

    # -------------------------
    # 💰 ABA 3 - RESUMO DE SALDOS
    # -------------------------
    with tab3:
        st.subheader("💰 Saldos por Conta/Banco")

        df_topo = carregar_dados()

        if df_topo.empty:
            st.info("Sem dados ainda")
        else:

            df_topo.columns = [str(c).strip().lower() for c in df_topo.columns]

            df_topo["valor"] = pd.to_numeric(df_topo["valor"], errors="coerce").fillna(0)
            df_topo["classificacao"] = df_topo["classificacao"].astype(str).str.upper().str.strip()
            df_topo["conta"] = df_topo["conta"].astype(str)

            bancos = ["Itaú", "Bradesco", "Banco do Brasil", "Nubank"]
            saldos = {banco: 0 for banco in bancos}
            saldos["Dinheiro (Caixa físico)"] = 0

            for _, row in df_topo.iterrows():

                valor = float(row["valor"])
                tipo = row["classificacao"]
                conta = row["conta"]

                if tipo == "DESPESA":
                    valor = -valor

                if "TRANSFERÊNCIA BANCÁRIA" in conta and "(" in conta:
                    banco = conta.split("(")[1].replace(")", "").strip()

                    if banco in saldos:
                        saldos[banco] += valor
                    else:
                        saldos["Dinheiro (Caixa físico)"] += valor
                else:
                    saldos["Dinheiro (Caixa físico)"] += valor

        # 🔥 EXIBIR
        colunas = st.columns(len(saldos))

        for i, (nome, saldo) in enumerate(saldos.items()):
            icone = "💵" if nome == "Dinheiro (Caixa físico)" else "🏦"

            if saldo < 0:
                colunas[i].metric(f"{icone} {nome}", f"🔴 R$ {saldo:,.2f}")
            else:
                colunas[i].metric(f"{icone} {nome}", f"🟢 R$ {saldo:,.2f}")

        st.metric("💼 Total Geral", f"R$ {sum(saldos.values()):,.2f}")
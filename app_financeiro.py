import pandas as pd
import streamlit as st
from datetime import datetime

# 🧠 cérebro (somente leitura + regras)
from data import carregar_dados, calcular_saldos,gerar_alertas_inteligentes

# 💾 banco (CRUD real)
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

    df_topo, _ = carregar_dados()

    saldos = calcular_saldos(df_topo)



    # =========================
    # 💰 SALDO (SEGURO)
    # =========================
    df, meta = carregar_dados()

    if df is None:
        df = pd.DataFrame()

    saldos = calcular_saldos(df)

    qtd = len(saldos)

    if qtd < 1:
        st.warning("Nenhum saldo disponível para exibir.")
        st.stop()

    cols = st.columns(qtd)

    for i, (nome, saldo) in enumerate(saldos.items()):

        icone = "💵" if "Dinheiro" in nome else "🏦"
        cor = "🔴" if saldo < 0 else "🟢"

        cols[i].metric(
            label=f"{icone} {nome}",
            value=f"R$ {saldo:,.2f}"
        )
    # =========================
    # 🚨 ALERTAS DE VENCIMENTO
    # =========================
    avisos = gerar_alertas_inteligentes(df)

    if avisos:
        st.subheader("🚨 Alertas Inteligentes")

        for a in avisos:
            if a["nivel"] == "error":
                st.error(a["msg"])
            elif a["nivel"] == "warning":
                st.warning(a["msg"])
            else:
                st.info(a["msg"])
            
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
        "📊 Resumo Financeiro"
    ])

    # -------------------------
    # 📝 ABA 1 - INSERIR
    # -------------------------
    with tab1:
        st.subheader("Adicionar lançamento")

        # -------------------------
        # 📌 CATEGORIAS INICIAIS
        # -------------------------
        if "categorias" not in st.session_state:
            st.session_state.categorias = [
                "Alimentação", "Transporte", "Lazer"
            ]

        with st.form("form_dados", clear_on_submit=True):

            # -------------------------
            # 📥 CAMPOS
            # -------------------------
            titular = st.text_input("Titular")
            data = st.date_input("Data")

            mes = st.selectbox("Mês", [
                "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
            ])

            descricao = st.text_input("Descrição")

            # -------------------------
            # 🏦 CONTAS
            # -------------------------
            bancos = ["Itaú", "Bradesco", "Banco do Brasil", "Nubank"]
            contas = ["ESPÉCIE"] + [f"TRANSFERÊNCIA BANCÁRIA ({b})" for b in bancos]

            conta = st.selectbox("Conta", contas)

            # -------------------------
            # 💰 VALOR (CRÍTICO)
            # -------------------------
            valor = st.number_input("Valor", min_value=0.0, format="%.2f")

            # -------------------------
            # 📅 VENCIMENTO + STATUS
            # -------------------------
            data_vencimento = st.date_input(
                "Data de vencimento",
                value=datetime.today().date()
            )

            status = st.selectbox("Status", ["Pendente", "Pago"])

            # -------------------------
            # 📌 CATEGORIA DINÂMICA
            # -------------------------
            opcoes = st.session_state.categorias + ["➕ Nova categoria"]

            categoria = st.selectbox("Categoria", opcoes)

            nova_categoria = None
            if categoria == "➕ Nova categoria":
                nova_categoria = st.text_input("Digite a nova categoria")

            subcategoria = st.text_input("Subcategoria")
            tipo_despesa = st.text_input("Tipo de despesa")

            classificacao = st.selectbox(
                "Classificação",
                ["Receita", "Despesa"]
                )

            submit = st.form_submit_button("Salvar")

            # -------------------------
            # 💾 SALVAR
            # -------------------------
            if submit:

                # 🔥 VALIDAÇÕES
                if not descricao:
                    st.warning("Digite uma descrição")
                    st.stop()

                if not titular:
                    st.warning("Digite o titular")
                    st.stop()

                # 🔥 TRATA NOVA CATEGORIA
                if categoria == "➕ Nova categoria":
                    if nova_categoria:
                        if nova_categoria not in st.session_state.categorias:
                            st.session_state.categorias.append(nova_categoria)
                        categoria = nova_categoria
                    else:
                        st.warning("Digite o nome da nova categoria!")
                        st.stop()

                # 🔥 GARANTE VALOR LIMPO (ESSENCIAL)
                try:
                    valor_limpo = float(valor)
                except:
                    valor_limpo = 0.0

                # 🔥 PADRONIZA CLASSIFICAÇÃO
                classificacao = classificacao.upper()

                # -------------------------
                # 📦 LINHA FINAL
                # -------------------------
                linha = [
                    titular,
                    str(data),
                    mes,
                    descricao,
                    conta,
                    valor_limpo,
                    categoria,
                    subcategoria,
                    tipo_despesa,
                    classificacao,
                    str(data_vencimento),
                    status
                ]

                # -------------------------
                # 💾 SALVAR NO BANCO
                # -------------------------
                inserir_transacao(linha)

                st.success("✅ Lançamento salvo com sucesso!")
                st.rerun()

    # -------------------------
    # 📊 ABA 2 - CONSULTA
    # -------------------------
    with tab2:
        st.subheader("📋 Consulta de dados")

        df, _ = carregar_dados()

        if df.empty:
            st.info("Sem dados ainda")

        else:
            # =========================
            # 🧠 GARANTIA DE COLUNAS (CÉREBRO SAFE)
            # =========================
            df = df.copy()

            df["Data"] = pd.to_datetime(df["data"], errors="coerce")
            df["Titular"] = df.get("titular", "")
            df["Mês"] = df.get("mes", "")
            df["Descrição"] = df.get("descricao", "")
            df["Conta"] = df.get("conta", "")
            df["Valor"] = df.get("valor", 0)
            df["Categoria"] = df.get("categoria", "")
            df["Tipo de despesa"] = df.get("tipo_despesa", "")
            df["Classificação"] = df.get("classificacao", "")

            # remove datas inválidas
            df = df.dropna(subset=["Data"])

            # =========================
            # 📊 FILTROS
            # =========================
            df["Ano"] = df["Data"].dt.year
            df["Mes_num"] = df["Data"].dt.month
 
            col1, col2 = st.columns(2)

            anos_validos = sorted(df["Ano"].dropna().unique())
            ano = col1.selectbox("Ano", anos_validos)

            mes = col2.selectbox("Mês", ["Todos"] + list(range(1, 13)))

            if mes == "Todos":
                df_filtrado = df[df["Ano"] == ano]
            else:
                df_filtrado = df[(df["Ano"] == ano) & (df["Mes_num"] == mes)]

            # =========================
            # 🎯 MODO VISUALIZAÇÃO
            # =========================
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
                    ]].copy()

                    df_final.columns = [
                        "TITULAR", "DATA", "MÊS", "DESCRIÇÃO", "CONTA",
                        "VALOR", "CATEGORIA", "TIPO DE DESPESA", "CLASSIFICAÇÃO"
                    ]

                    def format_real(x):
                        try:
                            return f"R$ {float(x):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                        except:
                            return "R$ 0,00"

                    df_final["VALOR"] = df_final["VALOR"].apply(format_real)

                    st.dataframe(df_final, use_container_width=True)

            # =========================
            # 📅 DIÁRIO
            # =========================
            else:

                st.markdown("## 📅 Acompanhamento Diário")

                df_filtrado = df_filtrado.sort_values("Data")

                for data, grupo in df_filtrado.groupby("Data"):

                    st.markdown(
                        f"""
                        <div style='background-color:#d9e1f2;padding:10px;border-radius:8px'>
                            <b>📅 Data: {data.strftime('%d/%m/%Y')}</b>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    col1, col2 = st.columns([4, 1])

                    with col1:

                        tabela = pd.DataFrame({
                            "TITULAR": grupo["Titular"],
                            "CATEGORIA": grupo["Categoria"],
                            "DESCRIÇÃO": grupo["Descrição"],
                            "TIPO": grupo["Tipo de despesa"],
                            "FORMA DE PAGAMENTO": grupo["Conta"],
                            "PLANEJADO": 0,
                            "EXECUTADO": grupo["Valor"]
                        })

                        total_planejado = tabela["PLANEJADO"].sum()
                        total_executado = tabela["EXECUTADO"].sum()

                        def format_real(x):
                            return f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

                        tabela["PLANEJADO"] = tabela["PLANEJADO"].apply(format_real)
                        tabela["EXECUTADO"] = tabela["EXECUTADO"].apply(format_real)

                        st.dataframe(tabela, use_container_width=True)

                    with col2:

                        st.markdown("### 💰 Totais do dia")

                        st.metric("Planejado", format_real(total_planejado))
                        st.metric("Executado", format_real(total_executado))
                        st.metric("Diferença", format_real(total_planejado - total_executado))

                    st.markdown("---")
    # -------------------------
    # 📊 ABA 3 - Resumo Financeiro
    # -------------------------
    with tab3:

        st.subheader("📊 Resumo Financeiro")

        df, _ = carregar_dados()
        saldos = calcular_saldos(df)

        if not saldos:
            st.warning("Sem dados financeiros")
            st.stop()
        total = sum(saldos.values())

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 🏦 Bancos e Caixa")

            for nome, valor in saldos.items():
                cor = "🟢" if valor >= 0 else "🔴"
                st.metric(label=f"{cor} {nome}", value=f"R$ {valor:,.2f}")

        with col2:
            st.markdown("### 💰 Total Geral")

            cor_total = "🟢" if total >= 0 else "🔴"

            st.metric(
                label=f"{cor_total} Patrimônio Total",
                value=f"R$ {total:,.2f}"
            )
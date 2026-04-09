# app_financeiro.py
import gspread
import pandas as pd
import streamlit as st
from google.oauth2.service_account import Credentials


# -------------------------
# 🔐 CONEXÃO GOOGLE SHEETS
# -------------------------
def conectar_google():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scope
    )

    client = gspread.authorize(creds)

    planilha = client.open_by_url(
        "https://docs.google.com/spreadsheets/d/1OvodwLlhguQmbKQPXbQiP9DkZ5IDrq6WESNFEBT_TTo/edit?usp=sharing"
    )

    aba = planilha.worksheet("Dados")

    return aba

# -------------------------
# 📥 CARREGAR DADOS
# -------------------------
def carregar_dados():
    aba = conectar_google()
    dados = aba.get_all_records()
    df = pd.DataFrame(dados)

    df["linha_sheet"] = df.index + 2

    # ✅ CORREÇÃO DO VALOR
    df["Valor"] = (
        df["Valor"]
        .astype(str)
        .str.replace("R$", "", regex=False)
        .str.replace(" ", "", regex=False)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
    )

    df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce").fillna(0)

    return df

# -------------------------
# 💾 SALVAR DADOS
# -------------------------
def salvar_dados(linha):
    aba = conectar_google()
    aba.append_row(linha)

# =========================
# 🚀 FUNÇÃO PRINCIPAL
# =========================
def sistema_financeiro():

    st.title("💰 Sistema Financeiro")

    df_topo = carregar_dados()

    # =========================
    # 💰 SALDOS NO TOPO
    # =========================
    bancos = ["Itaú", "Bradesco", "Banco do Brasil", "Nubank"]
    saldos = {banco: 0 for banco in bancos}
    saldos["Dinheiro (Caixa físico)"] = 0

    if not df_topo.empty:
        df_topo.columns = df_topo.columns.str.strip()
        df_topo["Data"] = pd.to_datetime(df_topo["Data"], errors="coerce")
        df_topo = df_topo.sort_values("Data")

        for _, row in df_topo.iterrows():
            valor = row["Valor"]
            tipo = row["Classificação"]
            conta = row["Conta"]

            if tipo == "Despesa":
                valor = -valor

            if "TRANSFERÊNCIA BANCÁRIA" in conta and "(" in conta:
                banco = conta.split("(")[1].replace(")", "")
                if banco in bancos:
                    saldos[banco] += valor
                else:
                    saldos["Dinheiro (Caixa físico)"] += valor
            else:
                saldos["Dinheiro (Caixa físico)"] += valor

    # MOSTRAR
    colunas = st.columns(len(saldos))
    for i, (nome, saldo) in enumerate(saldos.items()):
        icone = "💵" if nome == "Dinheiro (Caixa físico)" else "🏦"
        colunas[i].metric(f"{icone} {nome}", f"R$ {saldo:,.2f}")
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
    tab1, tab2, tab3, tab4 = st.tabs([
        "💾 Lançamentos",
        "📋 Consulta",
        "✏️ Editar",
        "💰 RESUMO DE SALDOS"
    ])

    # -------------------------
    # 📝 ABA 1 - INSERIR
    # -------------------------
    with tab1:
        st.subheader("Adicionar lançamento")

        with st.form("form_dados", clear_on_submit=True):
            titular = st.text_input("Titular")
            data = st.date_input("Data")

            mes = st.selectbox("Mês", [
                "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
            ])

            descricao = st.text_input("Descrição")
        
            # Lista de bancos
            bancos = ["Itaú", "Bradesco", "Banco do Brasil", "Nubank"]

            # Contas possíveis
            contas = ["ESPÉCIE"] + [f"TRANSFERÊNCIA BANCÁRIA ({banco})" for banco in bancos]

            # Selectbox
            conta = st.selectbox("Conta", contas)
            valor = st.number_input("Valor", min_value=0.0)

            # Inicializar categorias no session_state
            if "categorias" not in st.session_state:
                st.session_state.categorias = ["Alimentação", "Transporte", "Lazer"]  # exemplo inicial

            # -----------------------
            # Categoria dinâmica
            # -----------------------
            opcoes = st.session_state.categorias + ["➕ Nova categoria"]
            categoria = st.selectbox("Categoria", opcoes)

            if categoria == "➕ Nova categoria":
                nova = st.text_input("Nova categoria")
    
                # Só adiciona se o usuário digitar algo
                if nova:
                    if nova not in st.session_state.categorias:
                        st.session_state.categorias.append(nova)
                        st.success(f"Categoria '{nova}' adicionada!")
        
                    # Atualiza o selectbox para mostrar a nova categoria
                    categoria = nova
            subcategoria = st.text_input("Subcategoria")  # Nova coluna
            tipo_despesa = st.text_input("Tipo de despesa")
            classificacao = st.selectbox("Classificação", ["Receita", "Despesa"])

            submit = st.form_submit_button("Salvar")

            if submit:
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
                    classificacao
                ]

                salvar_dados(linha)
                st.success("Salvo no Google Sheets!")

                st.rerun()  # 🔥 ESSA LINHA FAZ ATUALIZAR NA HORA

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
            
    # ----------------------
    # ✏️ ABA 3 EDITAR
    # ----------------------            
    with tab3:
        st.subheader("✏️ Editar lançamento")

        df = carregar_dados()

        if df.empty:
            st.info("Sem dados ainda")
        else:
            # 🔥 garantir coluna limpa
            df.columns = df.columns.str.strip()
            
        # 🔥 criar índice da linha no Sheets
        df["linha_sheet"] = df.index + 2

        # Seleção do registro
        linha_sel = st.selectbox(
            "Selecione o lançamento",
            df.index,
            format_func=lambda x: f"{df.loc[x, 'Titular']} | {df.loc[x, 'Descrição']} | R$ {df.loc[x, 'Valor']}"
        )
        df.columns = df.columns.str.strip()
        if "Subdescrição" not in df.columns:
            df["Subdescrição"] = ""  # cria a coluna vazia se não existir

        linha = df.loc[linha_sel]

        # Campos editáveis
        titular = st.text_input("Titular", linha["Titular"])
        data = st.date_input("Data", pd.to_datetime(linha["Data"]))
        mes = st.text_input("Mês", linha["Mês"])
        descricao = st.text_input("Descrição", linha["Descrição"])
        conta = st.selectbox("Conta", ["ESPÉCIE", "TRANSFERÊNCIA BANCÁRIA"])
        valor = st.number_input("Valor", value=float(linha["Valor"]))
        categoria = st.text_input("Categoria", linha["Categoria"])
        subcategoria = st.text_input("Subcategoria", linha.get("Subcategoria", ""))
        tipo = st.text_input("Tipo de despesa", linha["Tipo de despesa"])
        classificacao = st.selectbox("Classificação", ["Receita", "Despesa"])

        # Botão salvar
        if st.button("💾 Salvar alteração"):
            aba = conectar_google()

            numero_linha = int(linha["linha_sheet"])

            novos_dados = [
                titular,
                str(data),
                mes,
                descricao,
                conta,
                valor,
                categoria,
                subcategoria,
                tipo,
                classificacao
            ]

            aba.update(f"A{numero_linha}:I{numero_linha}", [novos_dados])

            st.success("Alteração salva com sucesso!")

    # -------------------------
    # 💰 ABA 4 - RESUMO DE SALDOS
    # -------------------------
    with tab4:
        st.subheader("💰 Saldos por Conta/Banco")

        df_topo = carregar_dados()

        if df_topo.empty:
            st.info("Sem dados ainda")
        else:
            df_topo.columns = df_topo.columns.str.strip()
            df_topo["Data"] = pd.to_datetime(df_topo["Data"], errors="coerce")
            
            bancos = ["Itaú", "Bradesco", "Banco do Brasil", "Nubank"]
            saldos = {banco: 0 for banco in bancos}
            saldos["Dinheiro (Caixa físico)"] = 0

            for _, row in df_topo.iterrows():
                valor = row["Valor"]
                tipo = row["Classificação"]
                conta = row["Conta"]

                if tipo == "Despesa":
                    valor = -valor

                if "TRANSFERÊNCIA BANCÁRIA" in conta and "(" in conta and ")" in conta:
                    banco = conta.split("(")[1].replace(")", "")
                    if banco in bancos:
                        saldos[banco] += valor
                    else:
                        saldos["Dinheiro (Caixa físico)"] += valor
                else:
                    saldos["Dinheiro (Caixa físico)"] += valor

            # Exibir colunas
            colunas = st.columns(len(saldos))
            for i, (nome, saldo) in enumerate(saldos.items()):
                icone = "💵" if nome == "Dinheiro (Caixa físico)" else "🏦"
                colunas[i].metric(f"{icone} {nome}", f"R$ {saldo:,.2f}")

            # Total geral
            st.metric("💼 Total Geral", f"R$ {sum(saldos.values()):,.2f}")

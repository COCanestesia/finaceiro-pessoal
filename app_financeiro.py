# app_financeiro.py
import pandas as pd
import streamlit as st
from database import inserir_transacao, buscar_transacoes
from datetime import datetime
from database import atualizar_transacao

# -------------------------
# 📥 CARREGAR DADOS
# -------------------------
def carregar_dados():
    from database import buscar_transacoes
    import pandas as pd

    df = buscar_transacoes()

    # 🔥 MANTER COMPATIBILIDADE COM SEU SISTEMA
    if df.empty:
        return df

    # =========================
    # 🧾 PADRONIZAR COLUNAS
    # =========================
    df.columns = df.columns.str.strip()

    # Simular linha do Sheets (pra não quebrar seu editar)
    df["linha_sheet"] = df.index + 2

    # =========================
    # 💰 VALOR
    # =========================
    if "valor" in df.columns:
        df["Valor"] = pd.to_numeric(df["valor"], errors="coerce").fillna(0)
    elif "Valor" in df.columns:
        df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce").fillna(0)

    # =========================
    # 📅 DATA
    # =========================
    if "data" in df.columns:
        df["Data"] = pd.to_datetime(df["data"], errors="coerce")

    # =========================
    # 📅 DATA VENCIMENTO
    # =========================
    if "data_vencimento" in df.columns:
        df["Data Vencimento"] = pd.to_datetime(df["data_vencimento"], errors="coerce")
    else:
        df["Data Vencimento"] = pd.NaT

    # =========================
    # 📌 STATUS
    # =========================
    if "status" not in df.columns:
        df["Status"] = "Pendente"
    else:
        df["Status"] = df["status"]

    # =========================
    # 🧠 MAPEAR NOMES (CRÍTICO)
    # =========================
    mapa = {
        "titular": "Titular",
        "mes": "Mês",
        "descricao": "Descrição",
        "conta": "Conta",
        "categoria": "Categoria",
        "subcategoria": "Subcategoria",
        "tipo_despesa": "Tipo de despesa",
        "classificacao": "Classificação"
    }

    for col_banco, col_app in mapa.items():
        if col_banco in df.columns:
            df[col_app] = df[col_banco]

    return df

# -------------------------
# 💾 SALVAR DADOS
# -------------------------
def salvar_dados(linha):
    from database import inserir_transacao

    try:
        inserir_transacao(linha)
    except Exception as e:
        import streamlit as st
        st.error(f"Erro ao salvar no banco: {e}")

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

            # Só despesas
            if row.get("Classificação") != "Despesa":
                continue

            # Ignora pagos
            if row.get("Status") == "Pago":
                continue

            vencimento = row.get("Data Vencimento")

            # 🔥 TRAVA DE SEGURANÇA (ESSENCIAL)
            if pd.isna(vencimento):
                continue

            try:
                vencimento = pd.to_datetime(vencimento).date()
            except:
                continue

            dias = (vencimento - hoje).days

            if dias < 0:
                avisos.append(f"❌ {row['Descrição']} está vencido há {abs(dias)} dia(s)")
            elif dias <= 3:
                avisos.append(f"⚠️ {row['Descrição']} vence em {dias} dia(s)")

        return avisos


    avisos = verificar_alertas(df_topo)

    # 🔥 CAIXA DE ALERTA BONITA
    if avisos:
        st.markdown("### 🚨 Contas para atenção")

        for aviso in avisos:
            if "❌" in aviso:
                st.error(aviso)
            else:
                st.warning(aviso)
    else:
        st.success("✅ Nenhuma conta pendente ou próxima do vencimento")


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

    # 🔥 EXIBIR SALDOS
    colunas = st.columns(len(saldos))

    for i, (nome, saldo) in enumerate(saldos.items()):
        icone = "💵" if nome == "Dinheiro (Caixa físico)" else "🏦"

        # Cor dinâmica (verde positivo / vermelho negativo)
        if saldo < 0:
            colunas[i].markdown(f"### {icone} {nome}\n🔴 R$ {saldo:,.2f}")
        else:
            colunas[i].markdown(f"### {icone} {nome}\n🟢 R$ {saldo:,.2f}")
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

        # Inicializar categorias
        if "categorias" not in st.session_state:
            st.session_state.categorias = ["Alimentação", "Transporte", "Lazer"]

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

            conta = st.selectbox("Conta", contas)
            valor = st.number_input("Valor", min_value=0.0)
            # NOVOS CAMPOS
            data_vencimento = st.date_input("Data de vencimento", value=datetime.today().date())

            status = st.selectbox("Status", ["Pendente", "Pago"])

            # -----------------------
            # ✅ CATEGORIA DINÂMICA (DENTRO DO SELECT)
            # -----------------------
            opcoes = st.session_state.categorias + ["➕ Nova categoria"]

            categoria = st.selectbox("Categoria", opcoes)

            # Campo só aparece se escolher nova categoria
            nova_categoria = None
            if categoria == "➕ Nova categoria":
                nova_categoria = st.text_input("Digite a nova categoria")

            subcategoria = st.text_input("Subcategoria")
            tipo_despesa = st.text_input("Tipo de despesa")

            classificacao = st.selectbox("Classificação", ["Receita", "Despesa"])

            submit = st.form_submit_button("Salvar")

            # -----------------------
            # 💾 SALVAR
            # -----------------------
            if submit:

                # 🔥 Trata nova categoria
                if categoria == "➕ Nova categoria":
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

                salvar_dados(linha)
                st.success("Salvo no Google Sheets!")

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

        # 🔥 TRATAR VALORES (evita erro com NaN)
        titular_val = linha.get("Titular", "")
        data_val = pd.to_datetime(linha.get("Data"), errors="coerce")
        mes_val = linha.get("Mês", "")
        descricao_val = linha.get("Descrição", "")
        conta_val = linha.get("Conta", "ESPÉCIE")
        valor_val = float(linha.get("Valor", 0))
        categoria_val = linha.get("Categoria", "")
        subcategoria_val = linha.get("Subcategoria", "")
        tipo_val = linha.get("Tipo de despesa", "")
        classificacao_val = linha.get("Classificação", "Despesa")
        status_val = linha.get("Status", "Pendente")
        data_venc_val = pd.to_datetime(linha.get("Data Vencimento"), errors="coerce")

        # -------------------------
        # CAMPOS EDITÁVEIS
        # -------------------------
        titular = st.text_input("Titular", titular_val)

        data = st.date_input(
            "Data",
            data_val if pd.notnull(data_val) else pd.Timestamp.today()
        )

        mes = st.text_input("Mês", mes_val)

        descricao = st.text_input("Descrição", descricao_val)

        conta = st.selectbox(
            "Conta",
            ["ESPÉCIE", "TRANSFERÊNCIA BANCÁRIA (Itaú)", "TRANSFERÊNCIA BANCÁRIA (Nubank)"],
            index=0 if conta_val not in ["ESPÉCIE", "TRANSFERÊNCIA BANCÁRIA (Itaú)", "TRANSFERÊNCIA BANCÁRIA (Nubank)"] 
            else ["ESPÉCIE", "TRANSFERÊNCIA BANCÁRIA (Itaú)", "TRANSFERÊNCIA BANCÁRIA (Nubank)"].index(conta_val)
        )

        valor = st.number_input("Valor", value=valor_val)

        categoria = st.text_input("Categoria", categoria_val)

        subcategoria = st.text_input("Subcategoria", subcategoria_val)

        tipo = st.text_input("Tipo de despesa", tipo_val)

        classificacao = st.selectbox(
            "Classificação",
            ["Receita", "Despesa"],
            index=0 if classificacao_val == "Receita" else 1
        )

        # 🔥 CAMPOS NOVOS (IMPORTANTES)
        data_vencimento = st.date_input(
            "Data de vencimento",
            data_venc_val if pd.notnull(data_venc_val) else pd.Timestamp.today()
        )

        status = st.selectbox(
            "Status",
            ["Pendente", "Pago"],
            index=0 if status_val == "Pendente" else 1
        )


        if st.button("💾 Salvar alteração"):

            id_linha = int(linha["id"])  # 🔥 agora é ID do banco

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
            classificacao,
            str(data_vencimento),  # se tiver no seu form
            status                 # se tiver no seu form
        ]

    atualizar_transacao(id_linha, novos_dados)

    st.success("Alteração salva no banco!")
    st.rerun()

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

import psycopg2
import pandas as pd
import streamlit as st


def conectar_banco():
    return psycopg2.connect(
        host=st.secrets["DB_HOST"],
        database=st.secrets["DB_NAME"],
        user=st.secrets["DB_USER"],
        password=st.secrets["DB_PASS"],
        port="5432",
        sslmode="require"
    )

# 📥 BUSCAR TRANSAÇÕES
def buscar_transacoes():
    conn = conectar_banco()
    df = pd.read_sql("SELECT * FROM transacoes ORDER BY data DESC", conn)
    conn.close()
    return df

# 💾 INSERIR
def inserir_transacao(linha):
    conn = conectar_banco()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO transacoes (
            titular, data, mes, descricao, conta, valor,
            categoria, subcategoria, tipo_despesa,
            classificacao, data_vencimento, status
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, linha)

    conn.commit()
    conn.close()

# ✏️ ATUALIZAR
def atualizar_transacao(id_linha, novos_dados):
    conn = conectar_banco()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE transacoes SET
            titular=%s, data=%s, mes=%s, descricao=%s,
            conta=%s, valor=%s, categoria=%s,
            subcategoria=%s, tipo_despesa=%s,
            classificacao=%s, data_vencimento=%s, status=%s
        WHERE id=%s
    """, (*novos_dados, id_linha))

    conn.commit()
    conn.close()

# ❌ DELETAR
def deletar_transacao(id_linha):
    conn = conectar_banco()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM transacoes WHERE id=%s", (id_linha,))

    conn.commit()
    conn.close()

# 📊 METAS
def buscar_metas():
    conn = conectar_banco()
    df = pd.read_sql("SELECT * FROM metas", conn)
    conn.close()
    return df

def inserir_meta(categoria, valor, mes, ano):
    conn = conectar_banco()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO metas (categoria, valor, mes, ano)
        VALUES (%s, %s, %s, %s)
    """, (categoria, valor, mes, ano))

    conn.commit()
    conn.close()
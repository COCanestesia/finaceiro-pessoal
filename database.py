import pandas as pd
from supabase_client import conectar_supabase

# =========================
# 📥 BUSCAR TRANSAÇÕES
# =========================
def buscar_transacoes():
    supabase = conectar_supabase()

    response = (
        supabase
        .table("transacoes")
        .select("*")
        .order("data", desc=True)
        .execute()
    )

    return pd.DataFrame(response.data or [])


# =========================
# 💾 INSERIR TRANSAÇÃO
# =========================
def inserir_transacao(linha):
    supabase = conectar_supabase()

    dados = {
        "titular": linha[0],
        "data": str(linha[1]) if linha[1] else None,
        "mes": linha[2],
        "descricao": linha[3],
        "conta": linha[4],
        "valor": float(linha[5]) if linha[5] else 0,
        "categoria": linha[6],
        "subcategoria": linha[7],
        "tipo_despesa": linha[8],
        "classificacao": linha[9],
        "data_vencimento": str(linha[10]) if linha[10] else None,
        "status": linha[11]
    }

    supabase.table("transacoes").insert(dados).execute()


# =========================
# ✏️ ATUALIZAR TRANSAÇÃO
# =========================
def atualizar_transacao(id_linha, novos_dados):
    supabase = conectar_supabase()

    if not id_linha:
        return

    dados = {
        "titular": novos_dados[0],
        "data": str(novos_dados[1]) if novos_dados[1] else None,
        "mes": novos_dados[2],
        "descricao": novos_dados[3],
        "conta": novos_dados[4],
        "valor": float(novos_dados[5]) if novos_dados[5] else 0,
        "categoria": novos_dados[6],
        "subcategoria": novos_dados[7],
        "tipo_despesa": novos_dados[8],
        "classificacao": novos_dados[9],
        "data_vencimento": str(novos_dados[10]) if novos_dados[10] else None,
        "status": novos_dados[11]
    }

    supabase.table("transacoes").update(dados).eq("id", id_linha).execute()


# =========================
# ❌ DELETAR TRANSAÇÃO
# =========================
def deletar_transacao(id_linha):
    supabase = conectar_supabase()

    if not id_linha:
        return

    supabase.table("transacoes").delete().eq("id", id_linha).execute()


# =========================
# 📊 BUSCAR METAS
# =========================
def buscar_metas():
    supabase = conectar_supabase()

    response = supabase.table("metas").select("*").execute()

    return pd.DataFrame(response.data or [])


# =========================
# 📥 INSERIR META
# =========================
def inserir_meta(categoria, valor, mes, ano):
    supabase = conectar_supabase()

    dados = {
        "categoria": categoria,
        "valor": float(valor) if valor else 0,
        "mes": mes,
        "ano": ano
    }

    supabase.table("metas").insert(dados).execute()
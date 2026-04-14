import pandas as pd
from supabase_client import conectar_supabase


# =========================
# 🔧 LIMPAR VALOR BR → FLOAT
# =========================
def limpar_valor(valor):
    try:
        return float(
            str(valor)
            .replace("R$", "")
            .replace(".", "")
            .replace(",", ".")
            .strip()
        )
    except:
        return 0.0


# =========================
# 📥 TRANSAÇÕES
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
# 💾 INSERIR
# =========================
def inserir_transacao(linha):
    supabase = conectar_supabase()

    dados = {
        "titular": linha[0],
        "data": linha[1],
        "mes": linha[2],
        "descricao": linha[3],
        "conta": linha[4],
        "valor": limpar_valor(linha[5]),
        "categoria": linha[6],
        "subcategoria": linha[7],
        "tipo_despesa": linha[8],
        "classificacao": linha[9],
        "data_vencimento": linha[10],
        "status": linha[11]
    }

    supabase.table("transacoes").insert(dados).execute()


# =========================
# ✏️ ATUALIZAR
# =========================
def atualizar_transacao(id_linha, novos_dados):
    supabase = conectar_supabase()

    if not id_linha:
        return

    dados = {
        "titular": novos_dados[0],
        "data": novos_dados[1],
        "mes": novos_dados[2],
        "descricao": novos_dados[3],
        "conta": novos_dados[4],
        "valor": limpar_valor(novos_dados[5]),
        "categoria": novos_dados[6],
        "subcategoria": novos_dados[7],
        "tipo_despesa": novos_dados[8],
        "classificacao": novos_dados[9],
        "data_vencimento": novos_dados[10],
        "status": novos_dados[11]
    }

    supabase.table("transacoes").update(dados).eq("id", id_linha).execute()


# =========================
# ❌ DELETAR
# =========================
def deletar_transacao(id_linha):
    supabase = conectar_supabase()

    if not id_linha:
        return

    supabase.table("transacoes").delete().eq("id", id_linha).execute()


# =========================
# 📊 METAS
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
        "valor": limpar_valor(valor),
        "mes": mes,
        "ano": ano
    }

    supabase.table("metas").insert(dados).execute()
import pandas as pd
import numpy as np
import re

# =========================
# 1. CARREGAR DADOS
# =========================
# Substitua pelo caminho do seu arquivo local
dados = pd.read_excel("Formulário de Pedido - Atlética Frenética (respostas).xlsx")

# =========================
# 2. PADRONIZAR TELEFONES
# =========================
col_tel_original = 'Telefone para Contato (WhatsApp)'


def formatar_tel(t):
    t = str(t).replace('.0', '')
    t = "".join(filter(str.isdigit, t))
    if not t or t == "nan":
        return None
    if len(t) == 11:
        return f'({t[:2]}) {t[2:7]}-{t[7:]}'
    if len(t) == 10:
        return f'({t[:2]}) {t[2:6]}-{t[6:]}'
    return t


# Tenta encontrar a coluna de telefone ignorando maiúsculas/minúsculas
col_tel_real = next((c for c in dados.columns if c.lower() == col_tel_original.lower()), col_tel_original)
dados[col_tel_real] = dados[col_tel_real].apply(formatar_tel)

# =========================
# 3. NORMALIZAR NOMES DE COLUNAS
# =========================
dados.columns = (
    dados.columns
    .str.strip()
    .str.lower()
    .str.replace(r'\s+', ' ', regex=True)
)


def deixar_colunas_unicas(cols):
    seen = {}
    out = []
    for c in cols:
        if c in seen:
            seen[c] += 1
            out.append(f"{c}_{seen[c]}")
        else:
            seen[c] = 0
            out.append(c)
    return out


dados.columns = deixar_colunas_unicas(dados.columns)
colunas_originais = list(dados.columns)

# =========================
# 4. FUNÇÃO DE LIMPEZA COM REMOÇÃO DE "1 UNIDADE"
# =========================


def limpar_lista_v2(valores):
    """Limpa nulos, strings vazias e remove o termo '1 unidade'."""
    if isinstance(valores, pd.Series):
        valores = valores.tolist()
    
    if not isinstance(valores, (list, np.ndarray)):
        valores = [valores]
    
    resultado = []
    for v in valores:
        if pd.isna(v) if np.isscalar(v) else False:
            continue
            
        v_str = str(v).strip()
        
        # REMOÇÃO DE "1 UNIDADE" (case insensitive)
        # Remove o termo e limpa espaços ou vírgulas que sobrarem
        v_str = re.sub(r'1\s*unidade', '', v_str, flags=re.IGNORECASE).strip()
        v_str = v_str.strip(',').strip()

        # Só adiciona à lista se sobrou algum conteúdo útil
        if v_str != "" and v_str.lower() != "nan":
            resultado.append(v_str)
            
    return resultado


# =========================
# 5. PROCESSAR NOMES E NÚMEROS
# =========================
col_nome_ref = [c for c in colunas_originais if "nome referente" in c]
col_num_ref = [c for c in colunas_originais if "numero referente" in c]

dados["lista_nomes"] = dados[col_nome_ref].apply(limpar_lista_v2, axis=1)
dados["lista_numeros"] = dados[col_num_ref].apply(limpar_lista_v2, axis=1)

# =========================
# 6. PROCESSAR PRODUTOS (TAMANHOS)
# =========================
col_camisa = [c for c in colunas_originais if "camisa" in c and "referente" not in c]
col_calca = [c for c in colunas_originais if "calça" in c and "referente" not in c]
col_kit = [c for c in colunas_originais if "kit" in c and "referente" not in c]
col_top = [c for c in colunas_originais if "top" in c and "referente" not in c]

dados["camisas_avulsas"] = dados[col_camisa].apply(limpar_lista_v2, axis=1)
dados["calcas"] = dados[col_calca].apply(limpar_lista_v2, axis=1)
dados["kits"] = dados[col_kit].apply(limpar_lista_v2, axis=1)
dados["tops"] = dados[col_top].apply(limpar_lista_v2, axis=1)

# =========================
# 7. CONSOLIDAR PEDIDOS E TAMANHOS
# =========================


def extrair_pedidos(row):
    p = []
    # Usamos o len() original antes da limpeza radical ou checamos se havia algo
    if row["kits"] or any(pd.notna(row[col_kit])): p.append("Kit")
    if row["camisas_avulsas"] or any(pd.notna(row[col_camisa])): p.append("Camisa")
    if row["calcas"] or any(pd.notna(row[col_calca])): p.append("Calça")
    if row["tops"] or any(pd.notna(row[col_top])): p.append("Top")
    return ", ".join(list(set(p))) if p else "Nenhum"


dados["pedidos_resumo"] = dados.apply(extrair_pedidos, axis=1)

# =========================
# 8. CRIAR DATAFRAME FINAL
# =========================
df_final = pd.DataFrame()
df_final["Cliente"] = dados["nome completo"]
df_final["Telefone"] = dados[col_tel_real.lower()]
df_final["Pedidos"] = dados["pedidos_resumo"]
df_final["Tamanhos"] = dados.apply(lambda r: {
    "camisa": r["camisas_avulsas"], 
    "calça": r["calcas"], 
    "top": r["tops"]
}, axis=1)
df_final["Nomes na Camisa"] = dados["lista_nomes"]
df_final["Números na Camisa"] = dados["lista_numeros"]
df_final["Forma de Pagamento"] = dados["forma de pagamento preferida:"]
df_final["Gestao"] = dados["gestao"]

# Quantidades (ajustadas para não zerar se houver apenas "1 unidade" no campo original)
df_final["Qtd Camisas"] = dados[col_camisa].notna().sum(axis=1)
df_final["Qtd Kits"] = dados[col_kit].notna().sum(axis=1)

# salvar resultado final
df_final.to_excel("pedidos_frenetica_final.xlsx", index=False)


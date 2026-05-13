# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from database import get_session, Estoque, Vendas

@st.cache_data(ttl=600)
def get_vendas_df():
    """Recupera todas as vendas do banco e retorna um DataFrame para o Dashboard."""
    session = get_session()
    try:
        vendas = session.query(Vendas).all()
        if not vendas:
            return pd.DataFrame()
        
        
        df = pd.DataFrame([{
            "id": v.id,
            "nome_prod": v.nome_prod,
            "qtd_vendida": v.qtd_vendida,
            "lucro": v.lucro,
            "status_pagamento": v.status_pagamento,
            "data": v.data,
            "nome_cliente": v.nome_cliente,
            "telefone": v.telefone,
            "metodo_pagamento": v.metodo_pagamento,
            "preco_venda_total": v.preco_venda_total
        } for v in vendas])
        
        df['lucro'] = pd.to_numeric(df['lucro'], errors='coerce').fillna(0)
        df['qtd_vendida'] = pd.to_numeric(df['qtd_vendida'], errors='coerce').fillna(0)
        return df
    finally:
        session.close()

@st.cache_data(ttl=300)
def get_estoque_df():
    """Recupera o estoque e retorna um DataFrame formatado."""
    session = get_session()
    try:
        dados = session.query(Estoque).order_by(Estoque.id.desc()).all()
        if not dados:
            return pd.DataFrame()
            
        return pd.DataFrame([{
            "id": i.id,
            "nome_produto": i.nome_produto,
            "quantidade": i.quantidade,
            "preco_venda_un": i.preco_venda_un,
            "preco_custo": i.preco_custo,
            "personalizavel": i.personalizavel
        } for i in dados])
    finally:
        session.close()

def clear_cache():
    """Limpa o cache de dados do portal."""
    st.cache_data.clear()
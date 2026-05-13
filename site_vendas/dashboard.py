# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px
from data_manager import get_vendas_df, get_estoque_df
from utils import format_currency
import strings_config as s
from strings_config import DASH as d 

def render_dashboard():
    
    st.header(s.DASH["TITULO"]) 
    session = get_session()

    # --- MÉTRICAS PRINCIPAIS ---
    col1, col2, col3 = st.columns(3)
    
    if not df_v.empty:
        # Lógica de lucro mantendo os status originais
        lucro_total_pago = df_v[df_v['status_pagamento'] == "Pago"]['lucro'].sum()
        lucro_meio_pago = df_v[df_v['status_pagamento'] == "Pago 50%"]['lucro'].sum() * 0.5
        total_lucro_realizado = float(lucro_total_pago + lucro_meio_pago)
        
        # Ranking processado a partir do DataFrame do cache
        ranking_vendas = df_v.groupby('nome_prod')['qtd_vendida'].sum().sort_values(ascending=False)
        mais_vendido_nome = ranking_vendas.idxmax()
        mais_vendido_qtd = ranking_vendas.max()
        
        col1.metric(d["METRICA_VENDAS"], len(df_v))
        col2.metric(label=d["METRICA_PROD_MAIS_VENDIDO"], value=f"{mais_vendido_nome} ({int(mais_vendido_qtd)})")
        col3.metric(d["METRICA_LUCRO"], format_currency(total_lucro_realizado))
        
        # Alerta de valores pendentes
        lucro_pendente = float(df_v[df_v['status_pagamento'] != "Pago"]['lucro'].sum())
        if lucro_pendente > 0:
            st.caption(f"⚠️ Há {format_currency(lucro_pendente)} em lucro pendente de pagamento.")
    else:
        col1.metric(d["METRICA_VENDAS"], 0)
        col2.metric(d["METRICA_PROD_MAIS_VENDIDO"], "N/A")
        col3.metric(d["METRICA_LUCRO"], format_currency(0))

    st.divider()

    # --- GRÁFICOS ---
    g1, g2 = st.columns(2)

    with g1:
        st.subheader(s.DASH["GRAFICO_ESTOQUE"]) 
        if not vendas_por_dia.empty:
            fig_vendas = px.line(vendas_por_dia, x='Data', y='preco_venda_total', 
                                 title="Faturamento Diário", markers=True)
            fig_vendas.update_traces(line_color=s.COR_AZUL_MARCA) # Identidade visual
            st.plotly_chart(fig_vendas, use_container_width=True)

    with g2:
        st.subheader(s.DASH["GRAFICO_RANKING"])
        if not df_vendas.empty:
            top_prods = df_vendas.groupby('Produto')['qtd_vendida'].sum().nlargest(5).reset_index()
            fig_bar = px.bar(top_prods, x='Produto', y='qtd_vendida', 
                             title="Qtd Vendida por Produto", color_discrete_sequence=[s.COR_AMARELO_MARCA])
            st.plotly_chart(fig_bar, use_container_width=True)

    # --- TABELA DE ESTOQUE CRÍTICO ---
    st.divider()

    # --- GRÁFICO 2: RANKING DE VENDAS ---
    st.subheader(d["GRAFICO_RANKING"])
    if not df_v.empty:
        df_plot = ranking_vendas.reset_index()
        df_plot.columns = ['Produto', 'Quantidade']

        fig_vendas = px.bar(
            df_plot, x='Produto', y='Quantidade',
            text_auto='.0f', color='Quantidade',
            color_continuous_scale="Viridis"
        )
        fig_vendas.update_layout(height=500, coloraxis_showscale=False, margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig_vendas, use_container_width=True)
    else:
        st.info(d["MSG_SEM_VENDAS"])

    
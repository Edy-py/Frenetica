# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px
from data_manager import get_vendas_df, get_estoque_df
from utils import format_currency
import strings_config as s
from strings_config import DASH as d 

def render_dashboard():
    st.header(d["TITULO"])
    
    # Busca de dados via Cache
    df_v = get_vendas_df()
    df_e = get_estoque_df()

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

    # --- GRÁFICO 1: NÍVEIS DE ESTOQUE ---
    st.subheader(d["GRAFICO_ESTOQUE"])
    if not df_e.empty:
        df_e['Status_Estoque'] = df_e['quantidade'].apply(
            lambda q: d["LABEL_STATUS_CRITICO"] if q < 1 else (d["LABEL_STATUS_ALERTA"] if q <= 5 else d["LABEL_STATUS_OK"])
        )
            
        fig_est = px.bar(
            df_e, x='nome_produto', y='quantidade', color='Status_Estoque',
            color_discrete_map=s.CORES_STATUS,
            text_auto=True,
            category_orders={"Status_Estoque": [d["LABEL_STATUS_CRITICO"], d["LABEL_STATUS_ALERTA"], d["LABEL_STATUS_OK"]]}
        )
        fig_est.update_layout(height=450, margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig_est, use_container_width=True)
    else:
        st.info(d["MSG_SEM_ESTOQUE"])

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

    
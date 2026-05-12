# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px
from database import get_session, Estoque, Vendas
from utils import format_currency
import strings_config as s
from strings_config import DASH as d 

def render_dashboard():
    st.header(d["TITULO"])
    session = get_session()
    
    estoque = session.query(Estoque).all()
    vendas = session.query(Vendas).all()

    # --- MÉTRICAS PRINCIPAIS ---
    col1, col2, col3 = st.columns(3)
    
    if vendas:
        # 1. DataFrame centralizado com tratamento de tipos e status
        # Adicionamos o campo status_pagamento na tupla
        df_v = pd.DataFrame([(v.nome_prod, v.qtd_vendida, v.lucro, v.status_pagamento) for v in vendas], 
                             columns=['Produto', 'Quantidade', 'Lucro', 'Status'])
        
        df_v['Lucro'] = pd.to_numeric(df_v['Lucro'], errors='coerce').fillna(0)
        df_v['Quantidade'] = pd.to_numeric(df_v['Quantidade'], errors='coerce').fillna(0)
        
        # --- LÓGICA DE FILTRO DE LUCRO ---
        # Filtramos para somar apenas o lucro de vendas com status "Pago"
        lucro_total_pago = df_v[df_v['Status'] == "Pago"]['Lucro'].sum()
        lucro_meio_pago = df_v[df_v['Status'] == "Pago 50%"]['Lucro'].sum() * 0.5
        
        total_lucro_realizado = float(lucro_total_pago + lucro_meio_pago)
        
        # Métrica de vendas totais (independente de status)
        total_vendas_qtd = len(vendas)
        
        # Ranking de produtos (usamos todas as vendas para saber o que sai mais, independente de estar pago)
        ranking_vendas = df_v.groupby('Produto')['Quantidade'].sum().sort_values(ascending=False)
        mais_vendido_nome = ranking_vendas.idxmax()
        mais_vendido_qtd = ranking_vendas.max()
        
        col1.metric(d["METRICA_VENDAS"], total_vendas_qtd)
        col2.metric(label=d["METRICA_PROD_MAIS_VENDIDO"], value=f"{mais_vendido_nome} ({int(mais_vendido_qtd)})")
        
        # Exibimos o lucro apenas das vendas confirmadas como "Pago"
        col3.metric(d["METRICA_LUCRO"], format_currency(total_lucro_realizado))
        
        # Opcional: Mostrar um aviso se houver lucro pendente
        lucro_pendente = float(df_v[df_v['Status'] != "Pago"]['Lucro'].sum())
        if lucro_pendente > 0:
            st.caption(f"⚠️ Há {format_currency(lucro_pendente)} em lucro pendente de pagamento.")

    else:
        col1.metric(d["METRICA_VENDAS"], 0)
        col2.metric(d["METRICA_PROD_MAIS_VENDIDO"], "N/A")
        col3.metric(d["METRICA_LUCRO"], format_currency(0))

    st.divider()

    # --- GRÁFICO 1: NÍVEIS DE ESTOQUE ---
    st.subheader(d["GRAFICO_ESTOQUE"])
    if estoque:
        df_est = pd.DataFrame([(i.nome_produto, i.quantidade) for i in estoque], columns=['Produto', 'Qtd'])
        df_est['Status_Estoque'] = df_est['Qtd'].apply(
            lambda q: d["LABEL_STATUS_CRITICO"] if q < 1 else (d["LABEL_STATUS_ALERTA"] if q <= 5 else d["LABEL_STATUS_OK"])
        )
            
        fig_est = px.bar(
            df_est, x='Produto', y='Qtd', color='Status_Estoque',
            color_discrete_map=s.CORES_STATUS,
            text_auto=True,
            category_orders={"Status_Estoque": [d["LABEL_STATUS_CRITICO"], d["LABEL_STATUS_ALERTA"], d["LABEL_STATUS_OK"]]}
        )
        fig_est.update_layout(height=450, font=dict(size=14), margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig_est, use_container_width=True)
    else:
        st.info(d["MSG_SEM_ESTOQUE"])

    st.divider()

    # --- GRÁFICO 2: RANKING DE VENDAS ---
    st.subheader(d["GRAFICO_RANKING"])
    if vendas:
        df_plot_ranking = ranking_vendas.reset_index()

        fig_vendas = px.bar(
            df_plot_ranking, 
            x='Produto', 
            y='Quantidade',
            text_auto='.0f',
            color='Quantidade',
            color_continuous_scale="Viridis"
        )

        fig_vendas.update_layout(
            height=500, 
            font=dict(size=14),
            xaxis=dict(tickangle=-45, title=""),
            yaxis=dict(tickformat='d', title="Qtd Vendida"),
            coloraxis_showscale=False,
            margin=dict(t=20, b=20, l=20, r=20)
        )
        st.plotly_chart(fig_vendas, use_container_width=True)
    else:
        st.info(d["MSG_SEM_VENDAS"])

    session.close()
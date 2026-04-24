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
        # 1. Criamos o DataFrame garantindo tipos numéricos (float e int)
        df_v = pd.DataFrame([(v.nome_prod, v.qtd_vendida, v.lucro) for v in vendas], 
                             columns=['Produto', 'Quantidade', 'Lucro'])
        
        # FORÇAR CONVERSÃO (Caso o banco retorne algo estranho)
        df_v['Lucro'] = pd.to_numeric(df_v['Lucro'], errors='coerce').fillna(0)
        df_v['Quantidade'] = pd.to_numeric(df_v['Quantidade'], errors='coerce').fillna(0)
        
        # 2. Total de Vendas
        col1.metric(d["METRICA_VENDAS"], len(vendas))
        
        # 3. Produto mais vendido
        ranking_vendas = df_v.groupby('Produto')['Quantidade'].sum()
        mais_vendido_nome = ranking_vendas.idxmax()
        mais_vendido_qtd = ranking_vendas.max()
        col2.metric(label=d["METRICA_PROD_MAIS_VENDIDO"], value=f"{mais_vendido_nome} ({int(mais_vendido_qtd)})")
        
        # 4. Lucro acumulado - A SOMA AGORA VAI FUNCIONAR
        total_lucro = float(df_v['Lucro'].sum())
        col3.metric(d["METRICA_LUCRO"], format_currency(total_lucro))
    else:
        col1.metric(d["METRICA_VENDAS"], 0)
        col2.metric(d["METRICA_PROD_MAIS_VENDIDO"], "N/A")
        col3.metric(d["METRICA_LUCRO"], format_currency(0))

    st.divider()

    # --- GRÁFICO 1: NÍVEIS DE ESTOQUE ---
    st.subheader(d["GRAFICO_ESTOQUE"])
    if estoque:
        df_est = pd.DataFrame([(i.nome_produto, i.quantidade) for i in estoque], columns=['Produto', 'Qtd'])
        df_est['Status'] = df_est['Qtd'].apply(
            lambda q: d["LABEL_STATUS_CRITICO"] if q < 1 else (d["LABEL_STATUS_ALERTA"] if q <= 5 else d["LABEL_STATUS_OK"])
        )
            
        fig_est = px.bar(
            df_est, x='Produto', y='Qtd', color='Status',
            color_discrete_map=s.CORES_STATUS,
            text_auto=True
        )
        fig_est.update_layout(height=500, font=dict(size=16))
        st.plotly_chart(fig_est, use_container_width=True)
    else:
        st.info(d["MSG_SEM_ESTOQUE"])

    st.divider()

    # --- GRÁFICO 2: RANKING DE VENDAS (COM ESCALA VIRIDIS) ---
    st.subheader(d["GRAFICO_RANKING"])
    if vendas:
        df_ranking = df_v.groupby('Produto')['Quantidade'].sum().reset_index()
        df_ranking = df_ranking.sort_values(by='Quantidade', ascending=False)

        fig_vendas = px.bar(
            df_ranking, 
            x='Produto', 
            y='Quantidade',
            text='Quantidade',
            color='Quantidade', # Define que a cor segue a escala numérica
            color_continuous_scale="Viridis" # Aplica o degradê Viridis
        )

        fig_vendas.update_layout(
            height=600, 
            font=dict(size=16),
            xaxis=dict(tickangle=-45),
            yaxis=dict(tickformat='d', dtick=1),
            coloraxis_showscale=False # Esconde a barra lateral de cores para ficar mais limpo
        )
        st.plotly_chart(fig_vendas, use_container_width=True)
    else:
        st.info(d["MSG_SEM_VENDAS"])

    session.close()
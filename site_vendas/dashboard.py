# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px
from database import get_session, Vendas, Estoque
from utils import format_currency
import strings_config as s
import datetime

@st.cache_data(ttl=600)
def processar_metricas_dashboard(vendas_df, _estoque_df):
    """Realiza os cálculos considerando apenas vendas validadas."""
    if vendas_df.empty:
        return 0, 0, 0, 0, pd.DataFrame()

    # --- LÓGICA DE LUCRO: Filtrar apenas status "Pago" ou "Pago 50%" ---
    vendas_validadas = vendas_df[vendas_df['Status'].isin(['Pago', 'Pago 50%'])]
    
    total_faturamento = vendas_df['preco_venda_total'].sum() # Faturamento bruto total
    total_lucro = vendas_validadas['lucro'].sum()          # Lucro real (dinheiro em caixa)
    total_itens = vendas_df['qtd_vendida'].sum()           # Quantidade total de itens saídos
    ticket_medio = total_faturamento / len(vendas_df) if len(vendas_df) > 0 else 0
    
    # Agrupamento para o gráfico de evolução
    vendas_por_dia = vendas_df.groupby('Data')['preco_venda_total'].sum().reset_index()
    
    return total_faturamento, total_lucro, total_itens, ticket_medio, vendas_por_dia

def render_dashboard():
    
    st.header(s.DASH["TITULO"]) 
    session = get_session()

    # --- FILTROS ---
    c1, c2 = st.columns(2)
    with c1:
        d_ini = st.date_input("Início", datetime.date.today() - datetime.timedelta(days=30), key="dash_date_ini")
    with c2:
        d_fim = st.date_input("Fim", datetime.date.today(), key="dash_date_fim")

    # --- BUSCA NO BANCO ---
    vendas_raw = session.query(Vendas).filter(Vendas.data.between(
        datetime.datetime.combine(d_ini, datetime.time.min),
        datetime.datetime.combine(d_fim, datetime.time.max)
    )).all()

    estoque_raw = session.query(Estoque).all()

    # Conversão para DataFrame incluindo a coluna Status para o filtro de lucro
    df_vendas = pd.DataFrame([{
        "preco_venda_total": float(v.preco_venda_total),
        "lucro": float(v.lucro),
        "qtd_vendida": v.qtd_vendida,
        "Data": v.data.date(),
        "Produto": v.nome_prod,
        "Status": v.status_pagamento 
    } for v in vendas_raw]) if vendas_raw else pd.DataFrame()

    # Processamento com Cache (Nota: _estoque_df com sublinhado resolve o UnhashableParamError)
    total_faturamento, total_lucro, total_itens, ticket_medio, vendas_por_dia = processar_metricas_dashboard(
        df_vendas, 
        estoque_raw
    )

    # --- CARDS DE MÉTRICAS ---
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric(s.DASH["METRICA_VENDAS"], f"R$ {total_faturamento:,.2f}")
    kpi2.metric(s.DASH["METRICA_LUCRO"], f"R$ {total_lucro:,.2f}", help="Apenas vendas 'Pago' ou 'Pago 50%'")
    kpi3.metric("Itens Vendidos", int(total_itens))
    kpi4.metric("Ticket Médio", f"R$ {ticket_medio:,.2f}")

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
    st.subheader("📦 Alerta de Stock Baixo")
    df_estoque = pd.DataFrame([{
        "Produto": e.nome_produto,
        "Quantidade": e.quantidade,
        "Preço Venda": format_currency(e.preco_venda_un)
    } for e in estoque_raw]) if estoque_raw else pd.DataFrame()

    if not df_estoque.empty:
        # Estilização para destacar itens com menos de 5 unidades
        st.dataframe(df_estoque.style.apply(
            lambda x: ['background-color: #ffcccc' if v < 5 else '' for v in x], 
            axis=1, subset=['Quantidade']
        ), use_container_width=True, hide_index=True)

# """
# Sistema de Gestão e Vendas - Frenética (A.A.A.T.J.B.)
# Desenvolvido por: Edílson Alves da Silva (Edy-py)
# Contato: edilsonalvesprofissional@gmail.com
# © 2026 - Todos os direitos reservados.
# """    
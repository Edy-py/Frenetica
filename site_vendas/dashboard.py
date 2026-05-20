# -*- coding: utf-8 -*-

# """
# Sistema de Gestão e Vendas - Frenética (A.A.A.T.J.B.)
# Desenvolvido por: Edílson Alves da Silva (Edy-py)
# Contato: edilsonalvesprofissional@gmail.com
# © 2026 - Todos os direitos reservados.
# """

import streamlit as st
import pandas as pd
import plotly.express as px
from database import get_session, Vendas, Estoque, Associados
from utils import format_currency, format_telefone
import strings_config as s

def render_dashboard():
    st.markdown(f"<h2 style='color: {s.COR_AZUL_MARCA};'>📊 Painel de Controlo Financeiro e Atletas</h2>", unsafe_allow_html=True)
    
    session = get_session()
    
    # --- PROCESSAMENTO DE DADOS FINANCEIROS ---
    vendas_db = session.query(Vendas).all()
    estoque_db = session.query(Estoque).all()
    socios_db = session.query(Associados).all()
    
    # Inicialização de métricas padrão de segurança
    total_faturado = 0.0
    total_lucro = 0.0
    total_vendas = len(vendas_db)
    
    if vendas_db:
        total_faturado = sum(v.preco_venda_total for v in vendas_db)
        total_lucro = sum(v.lucro for v in vendas_db)

    # --- KPI METRICS GRIDS ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💰 Faturamento Bruto", format_currency(total_faturado))
    c2.metric("📈 Lucro Líquido", format_currency(total_lucro))
    c3.metric("📦 Pedidos Totais", f"{total_vendas} un.")
    
    # Contagem rápida de Sócios
    socios_ativos = sum(1 for socio in socios_db if socio.status == "Ativo")
    c4.metric("🦁 Sócios Ativos", f"{socios_ativos} atletas")

    st.divider()

    # --- GRÁFICOS DO DASHBOARD ---
    if vendas_db:
        col_g1, col_g2 = st.columns(2)
        
        # Estrutura de dados para gráficos
        df_vendas = pd.DataFrame([{
            "Data": v.data,
            "Valor": v.preco_venda_total,
            "Lucro": v.lucro,
            "Produto": v.nome_prod
        } for v in vendas_db])
        
        with col_g1:
            st.markdown("### 🗓️ Evolução de Vendas")
            df_vendas['Data_Agrupada'] = df_vendas['Data'].dt.strftime('%d/%m/%Y')
            fig_lin = px.line(df_vendas.groupby('Data_Agrupada').sum().reset_index(), 
                              x='Data_Agrupada', y='Valor', 
                              labels={'Data_Agrupada': 'Dia', 'Valor': 'Faturamento (R$)'},
                              color_discrete_sequence=[s.COR_AZUL_MARCA])
            st.plotly_chart(fig_lin, use_container_width=True)
            
        with col_g2:
            st.markdown("### 🏆 Produtos Mais Vendidos")
            df_prod = df_vendas.groupby('Produto').size().reset_index(name='Quantidade')
            fig_bar = px.bar(df_prod.sort_values(by='Quantidade', ascending=False).head(5), 
                             x='Quantidade', y='Produto', orientation='h',
                             color_discrete_sequence=[s.COR_AMARELO_MARCA])
            st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()

    # --- CONTROLO DE SÓCIOS EXPIRADOS ---
    st.markdown(f"<h3 style='color: #dc2626;'>⚠️ Gestão de Sócios Expirados / Inativos</h3>", unsafe_allow_html=True)
    st.caption("Estes atletas encontram-se com o plano de sócio vencido ou aguardando renovação de 30 dias.")
    
    # Filtro dinâmico na lista de associados
    socios_expirados_lista = [
        socio for socio in socios_db if socio.status == "Inativo"
    ]
    
    if socios_expirados_lista:
        # Monta um DataFrame limpo e seguro para exibição
        df_expirados = pd.DataFrame([{
            "Atleta": socio.nome,
            "CPF / Código": socio.codigo_unico,
            "Telefone de Contacto": format_telefone(socio.telefone) if socio.telefone else "Não cadastrado",
            "Estado": "🔴 EXPIRADO"
        } for socio in socios_expirados_lista])
        
        # CSS para destacar a tabela de avisos
        st.markdown("""
            <style>
                .stDataFrame div [data-testid="stTable"] {
                    border: 1px solid #fee2e2 !important;
                }
            </style>
        """, unsafe_allow_html=True)
        
        # Exibe a tabela interativa para o Admin/Financeiro poder copiar os dados e cobrar
        st.dataframe(
            df_expirados, 
            use_container_width=True, 
            hide_index=True
        )
        
        # Opção premium para baixar a lista de devedores/expirados em CSV
        csv_data = df_expirados.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 Baixar Lista de Expirados para Cobrança",
            data=csv_data,
            file_name=f"socios_expirados_{pd.Timestamp.now().strftime('%d_%m_%Y')}.csv",
            mime="text/csv"
        )
    else:
        st.success("🎉 Excelente! Não existem sócios expirados ou pendentes de ativação no momento.")

    session.close()
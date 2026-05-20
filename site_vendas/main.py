# -*- coding: utf-8 -*-

# """
# Sistema de Gestão e Vendas - Frenética (A.A.A.T.J.B.)
# Desenvolvido por: Edílson Alves da Silva (Edy-py)
# Contato: edilsonalvesprofissional@gmail.com
# © 2026 - Todos os direitos reservados.
# """

import streamlit as st
import base64
import os
from auth import login, logout
from database import init_db

# Importação dos módulos das abas
from estoque import render_estoque
from dashboard import render_dashboard
from vendas import render_vendas
from associados import render_associados
from compras import render_compras
import strings_config as s 

# 1. Configuração da Página
st.set_page_config(
    page_title=s.TITULO_PAGINA,
    page_icon="site_vendas/icons/icone_aba.png",
    layout="wide"
)

# Inicialização única do Banco de Dados
init_db()

# Cache de imagem Base64 para performance e carregamento fluido
@st.cache_data(ttl=3600)
def get_base64(bin_file):
    if bin_file and os.path.exists(bin_file):
        with open(bin_file, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    return None

# --- CSS ULTRA PREMIUM (UI/UX DESIGN) ---
st.markdown(f"""
    <style>
        /* Importação de fontes Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Montserrat:wght@700;800&display=swap');

        :root {{
            --primary: {s.COR_AZUL_MARCA};
            --secondary: {s.COR_AMARELO_MARCA};
            --bg-light: #f4f7f9;
            --white: #ffffff;
            --text-dark: #1e293b;
            --text-muted: #64748b;
        }}

        /* Reset e Tipografia Base */
        .stApp {{
            background-color: var(--bg-light);
            font-family: 'Inter', sans-serif;
        }}

        h1, h2, h3 {{
            font-family: 'Montserrat', sans-serif !important;
            font-weight: 800 !important;
        }}

        /* Banner Frenético Modernizado */
        .banner-wrapper {{
            background: linear-gradient(135deg, #0f172a 0%, var(--primary) 100%);
            padding: 50px 20px;
            border-radius: 24px;
            margin-bottom: 40px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.15);
            text-align: center;
            border-bottom: 8px solid var(--secondary);
            position: relative;
        }}

        .banner-wrapper h1 {{
            color: white !important;
            font-size: 3.5rem !important;
            text-transform: uppercase;
            letter-spacing: -1.5px;
            margin-top: 20px !important;
            text-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }}

        /* --- SISTEMA DE CARDS COM HOVER EXPANSIVO --- */
        .card-parceiro {{
            background: var(--white);
            border-radius: 22px;
            padding: 30px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            border: 1px solid rgba(0,0,0,0.05);
            display: flex;
            flex-direction: column;
            align-items: center;
            height: 380px; /* Altura padrão alinhada */
            text-align: center;
            overflow: hidden;
            position: relative;
        }}

        /* Efeito ao passar o cursor */
        .card-parceiro:hover {{
            transform: translateY(-10px);
            box-shadow: 0 25px 50px rgba(0,0,0,0.12);
            border-color: var(--secondary);
            height: auto; /* Expande para mostrar todo o conteúdo */
            min-height: 380px;
            z-index: 99;
        }}

        .card-img {{
            width: 110px;
            height: 110px;
            border-radius: 50%;
            object-fit: cover;
            border: 4px solid #f8fafc;
            box-shadow: 0 8px 15px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            transition: transform 0.3s ease;
        }}

        .card-parceiro:hover .card-img {{
            transform: scale(1.08);
            border-color: var(--secondary);
        }}

        .card-title {{
            font-size: 1.4rem !important;
            color: var(--text-dark) !important;
            margin: 10px 0 !important;
            height: 60px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        .card-text {{
            font-size: 0.95rem;
            color: var(--text-muted);
            line-height: 1.6;
            /* Limitação inicial de 3 linhas */
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            overflow: hidden;
            transition: all 0.3s ease;
        }}

        /* Expansão do texto no hover */
        .card-parceiro:hover .card-text {{
            -webkit-line-clamp: unset;
            display: block;
            overflow: visible;
            color: #334155;
        }}

        /* Estilização das Tabs (Navegação) */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 12px;
            background-color: transparent;
        }}

        .stTabs [data-baseweb="tab"] {{
            background-color: var(--white) !important;
            border-radius: 12px !important;
            padding: 12px 24px !important;
            color: var(--text-muted) !important;
            font-weight: 600 !important;
            border: 1px solid rgba(0,0,0,0.05) !important;
            transition: 0.3s;
        }}

        .stTabs [aria-selected="true"] {{
            background: var(--primary) !important;
            color: var(--white) !important;
            border: none !important;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}

        /* Botões Estilo Premium */
        div.stButton > button {{
            border-radius: 12px !important;
            padding: 10px 20px !important;
            font-weight: 600 !important;
            border: 2px solid var(--primary) !important;
            transition: all 0.3s ease !important;
        }}

        div.stButton > button:hover {{
            background-color: var(--primary) !important;
            color: white !important;
        }}
    </style>
""", unsafe_allow_html=True)

if login():
    # Sidebar - Área de Logout e Perfil
    with st.sidebar:
        st.markdown(f"### ⚡ Frenética System")
        st.write(f"Usuário: **{st.session_state.role.upper()}**")
        st.divider()
        logout()
    
    # Renderização do Header (Banner)
    logo_b64 = get_base64(s.BANNER_ARQUIVO)
    banner_html = f'<div class="banner-wrapper">'
    if logo_b64:
        banner_html += f'<img src="data:image/png;base64,{logo_b64}" width="140" style="filter: drop-shadow(0 8px 12px rgba(0,0,0,0.3));">'
    banner_html += f'<h1>{s.TEXTO_BANNER}</h1></div>'
    st.markdown(banner_html, unsafe_allow_html=True)
    
    # Definição de Menus por Perfil
    role = st.session_state.role
    n = s.NOMES_ABAS
    
    menu_map = {
        "admin": [n["dashboard"], n["estoque"], n["vendas"], n["associados"], n["compras"]],
        "financeiro": [n["dashboard"], n["vendas"], n["associados"]],
        "vendedor": [n["estoque"], n["vendas"]],
        "cliente": [n["loja"], n["parceiros"]]
    }
    
    menu = menu_map.get(role, [n["loja"]])
    
    # Criação das Tabs de Navegação
    tabs = st.tabs(menu)

    for i, nome_aba in enumerate(menu):
        with tabs[i]:
            st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
            
            if nome_aba == n["dashboard"]:
                render_dashboard() if role in ["admin", "financeiro"] else st.error("Acesso restrito.")
            
            elif n["estoque"] in nome_aba: 
                render_estoque(readonly=(role != "admin"))
            
            elif n["vendas"] in nome_aba: 
                render_vendas(can_edit_status=(role in ["admin", "financeiro"]))
            
            elif n["associados"] in nome_aba or n.get("parceiros") in nome_aba: 
                render_associados()
            
            elif n["loja"] in nome_aba or n.get("compras") in nome_aba: 
                render_compras()


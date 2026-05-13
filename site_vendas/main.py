# -*- coding: utf-8 -*-
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
    page_icon="icons/icone_aba.png",
    layout="wide"
)

# Inicialização única do Banco
init_db()

# Cache de imagem Base64 para performance
@st.cache_data(ttl=3600)
def get_base64(bin_file):
    if bin_file and os.path.exists(bin_file):
        with open(bin_file, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    return None

# --- CSS PROFISSIONAL AVANÇADO ---
st.markdown(f"""
    <style>
        /* Importação de fonte moderna */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

        :root {{
            --primary: {s.COR_AZUL_MARCA};
            --secondary: {s.COR_AMARELO_MARCA};
            --bg-light: #f8f9fa;
        }}

        /* Reset Geral */
        .stApp {{
            background-color: var(--bg-light);
            font-family: 'Inter', sans-serif;
        }}

        /* Banner Estilizado */
        .banner-wrapper {{
            background: linear-gradient(135deg, var(--primary) 0%, #1a2a6c 100%);
            padding: 40px 20px;
            border-radius: 20px;
            margin-bottom: 35px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
            text-align: center;
            border-bottom: 6px solid var(--secondary);
            position: relative;
            overflow: hidden;
        }}
        
        .banner-wrapper h1 {{
            color: white !important;
            font-weight: 800 !important;
            letter-spacing: -1px;
            font-size: 3.2rem !important;
            margin-top: 15px !important;
            text-shadow: 0 4px 10px rgba(0,0,0,0.2);
        }}

        /* Estilização das Tabs (Menu Navegação) */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 10px;
            background-color: white;
            padding: 10px;
            border-radius: 15px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        }}

        .stTabs [data-baseweb="tab"] {{
            height: 50px;
            background-color: transparent;
            border-radius: 10px;
            color: #444;
            font-weight: 600;
            transition: all 0.3s ease;
            border: none !important;
        }}

        .stTabs [aria-selected="true"] {{
            background-color: var(--primary) !important;
            color: white !important;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}

        /* Botões Estilo Premium */
        div.stButton > button {{
            border-radius: 12px !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
            text-transform: uppercase;
        }}

        /* Métricas */
        [data-testid="stMetric"] {{
            background-color: white;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.03);
            border-left: 5px solid var(--primary);
        }}

        /* --- CARDS DE PARCEIROS COM TAMANHO FIXO --- */
        .card-parceiro {{
            background: white;
            border-radius: 20px;
            padding: 25px;
            box-shadow: 0 10px 20px rgba(0,0,0,0.05);
            transition: all 0.3s ease;
            border: 1px solid #eee;
            display: flex;
            flex-direction: column;
            align-items: center;
            height: 380px; /* Altura fixa para alinhamento */
            text-align: center;
            overflow: hidden;
            margin-bottom: 20px;
        }}

        .card-parceiro:hover {{
            transform: translateY(-8px);
            box-shadow: 0 15px 30px rgba(0,0,0,0.1);
            border-color: var(--secondary);
        }}

        .card-img {{
            width: 100px;
            height: 100px;
            border-radius: 50%;
            object-fit: cover;
            border: 3px solid var(--primary);
            margin-bottom: 15px;
            background: white;
        }}

        .card-title {{
            font-size: 1.4rem !important;
            color: var(--primary) !important;
            margin: 10px 0 !important;
            height: 60px;
            display: flex;
            align-items: center;
            font-weight: 700;
        }}

        .card-text {{
            font-size: 0.95rem;
            color: #555;
            overflow: hidden;
            display: -webkit-box;
            -webkit-line-clamp: 4; /* Corta o texto em 4 linhas */
            -webkit-box-orient: vertical;
        }}
    </style>
""", unsafe_allow_html=True)

if login():
    # Sidebar - Identidade do usuário
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.role.upper()}")
        logout()
    
    # Renderização do Banner Principal
    logo_b64 = get_base64(s.BANNER_ARQUIVO)
    banner_html = f'<div class="banner-wrapper">'
    if logo_b64:
        banner_html += f'<img src="data:image/png;base64,{logo_b64}" width="150" style="filter: drop-shadow(0 4px 8px rgba(0,0,0,0.2));">'
    banner_html += f'<h1>{s.TEXTO_BANNER}</h1></div>'
    st.markdown(banner_html, unsafe_allow_html=True)
    
    # Lógica de Navegação e Permissões
    role = st.session_state.role
    n = s.NOMES_ABAS
    
    menu_map = {
        "admin": [n["dashboard"], n["estoque"], n["vendas"], n["associados"], n["compras"]],
        "financeiro": [n["dashboard"], n["vendas"], n["associados"]],
        "vendedor": [n["estoque"], n["vendas"]],
        "cliente": [n["loja"], n["parceiros"]]
    }
    
    menu = menu_map.get(role, [n["loja"]])
    tabs = st.tabs(menu)

    for i, nome_aba in enumerate(menu):
        with tabs[i]:
            st.markdown("<br>", unsafe_allow_html=True) # Espaçamento entre menu e conteúdo
            if nome_aba == n["dashboard"]:
                if role in ["admin", "financeiro"]:
                    render_dashboard()
                else:
                    st.error("Acesso restrito.")
            
            elif n["estoque"] in nome_aba: 
                render_estoque(readonly=(role != "admin"))
            
            elif n["vendas"] in nome_aba: 
                render_vendas(can_edit_status=(role in ["admin", "financeiro"]))
            
            elif n["associados"] in nome_aba or n.get("parceiros") in nome_aba: 
                render_associados()
            
            elif n["loja"] in nome_aba or n.get("compras") in nome_aba: 
                render_compras()
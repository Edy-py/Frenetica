# -*- coding: utf-8 -*-
import streamlit as st
import base64
import os
from auth import login, logout
from database import init_db

# Importação dos módulos das abas
from estoque import render_estoque
from dashboard import render_dashboard  # Ajustado o nome do arquivo para o padrão
from vendas import render_vendas
from associados import render_associados
from compras import render_compras
import strings_config as s 

# 1. Configuração da Página
st.set_page_config(
    page_title=s.TITULO_PAGINA,
    page_icon=s.ICON_PAGINA,
    layout="wide"
)

init_db()

def get_base64(bin_file):
    if bin_file and os.path.exists(bin_file):
        with open(bin_file, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    return None


st.markdown("""
    <style>
    /* Aumenta o título principal */
    h1 {
        font-size: 3rem !important;
    }
    /* Aumenta os subheader (nomes das seções) */
    h2 {
        font-size: 2.2rem !important;
    }
    /* Aumenta o texto dos botões */
    .stButton>button {
        font-size: 1.2rem !important;
        height: 3em !important;
    }
    /* Aumenta o texto das métricas no Dashboard */
    [data-testid="stMetricValue"] {
        font-size: 2.5rem !important;
    }
    </style>
""", unsafe_allow_html=True)

if login():
    # --- CSS ADAPTATIVO (Usando as cores da marca Frenética) ---
    st.markdown(f"""
    <style>
        :root {{
            --cor-primaria: {s.COR_AZUL_MARCA};
            --cor-secundaria: {s.COR_AMARELO_MARCA};
        }}

        h1, h2, h3 {{ font-family: 'sans serif'; }}

        .banner-container {{
            text-align: center; 
            padding: 25px; 
            background-color: var(--cor-primaria); 
            border-bottom: 5px solid var(--cor-secundaria); 
            border-radius: 10px;
            margin-bottom: 25px;
            color: white !important;
        }}
        .banner-container h1 {{
            color: white !important;
            margin: 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}

        .card-parceiro {{
            border: 2px solid var(--cor-primaria);
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            background-color: rgba(3, 24, 117, 0.05); 
            min-height: 260px;
            margin-bottom: 20px;
            transition: transform 0.3s;
        }}
        .card-parceiro:hover {{
            transform: translateY(-5px);
            border-color: var(--cor-secundaria);
        }}

        .card-img {{
            width: 90px; height: 90px;
            border-radius: 50%;
            border: 3px solid var(--cor-primaria);
            background-color: white;
            object-fit: cover;
            margin-bottom: 10px;
        }}

        .stTabs [data-baseweb="tab"] {{ color: var(--cor-primaria); }}
        .stTabs [aria-selected="true"] {{
            background-color: var(--cor-primaria) !important;
            color: white !important;
            border-radius: 5px;
        }}
    </style>
    """, unsafe_allow_html=True)

    logout()
    
    # --- RENDERIZAÇÃO DO BANNER ---
    logo_b64 = get_base64(s.BANNER_ARQUIVO)
    if logo_b64:
        st.markdown(
            f"""
            <div class="banner-container">
                <img src="data:image/png;base64,{logo_b64}" width="140" style="margin-bottom: 10px;">
                <h1>{s.TEXTO_BANNER}</h1>
            </div>
            """, unsafe_allow_html=True
        )
    else:
        st.markdown(f'<div class="banner-container"><h1>{s.TEXTO_BANNER}</h1></div>', unsafe_allow_html=True)
    
    # --- LÓGICA DE MENU RESTRITO ---
    role = st.session_state.role
    n = s.NOMES_ABAS
    
    # Definindo acesso por cargo usando as chaves do seu dicionário NOMES_ABAS
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
            # Trava de Segurança e Chamada das Funções
            if nome_aba == n["dashboard"]:
                if role in ["admin", "financeiro"]:
                    render_dashboard()
                else:
                    st.error("Acesso negado.")
            
            elif n["estoque"] in nome_aba: 
                render_estoque(readonly=(role != "admin"))
            
            elif n["vendas"] in nome_aba: 
                render_vendas(can_edit_status=(role in ["admin", "financeiro"]))
            
            elif n["associados"] in nome_aba or n.get("parceiros") in nome_aba: 
                render_associados()
            
            elif n["loja"] in nome_aba or n.get("compras") in nome_aba: 
                render_compras()
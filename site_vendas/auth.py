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
import bcrypt

# Dicionário com os cargos da Frenética

USERS = {
    "edy": {
        "role": "admin",
        "pass": b'$2b$12$hsQRLQAtFull/VV.jDHk0.dB5A4rtNZTcl9.dnes1MjOAPppa7OZu'
    },
    "financeiro": {
        "role": "financeiro",
        "pass": b'$2b$12$KV3LS/uIMBUsSUqkEv5R7eO4dKUzO8CgrHHBxGIBNqeVJ54YJAI9.' 
    },
    "vendedor": {
        "role": "vendedor",
        "pass": b'$2b$12$ChivGKyx5uWHhNoVoRtyDeVjsU.33BunuIPPnGBYhLRO0pNecLnb2'
    },
    "cliente": {
        "role": "cliente",
        "pass": b'$2b$12$On4lLQaOulfq/r6J2BsqseLg36oImyURLSaQOD/dKbd3pEbdcPODy' 
    },
    "parceiro":{
        "role": "parceiro",
        "pass": b'$2b$12$KUtjSSHcipMEKaiOH13kKu562nJNHEsCQany6qR40DKYyrVqvsoRi' 
    }
}

def get_base64(bin_file):
    if bin_file and os.path.exists(bin_file):
        with open(bin_file, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    return None

def apply_auth_style():
    """Aplica CSS específico para a tela de login."""
    # Buscando cores das strings ou definindo fixo se preferir
    import strings_config as s
    cor_primaria = s.COR_AZUL_MARCA
    cor_secundaria = s.COR_AMARELO_MARCA

    st.markdown(f"""
        <style>
            /* Centralização e Fundo */
            [data-testid="stForm"] {{
                background-color: white;
                padding: 40px;
                border-radius: 20px;
                box-shadow: 0 15px 35px rgba(0,0,0,0.1);
                border: 1px solid #eee;
            }}
            
            /* Título e Subtítulo */
            .login-header {{
                text-align: center;
                margin-bottom: 30px;
            }}
            
            .login-header h2 {{
                color: {cor_primaria} !important;
                font-weight: 800 !important;
                margin-bottom: 5px !important;
            }}
            
            /* Estilização dos Inputs */
            .stTextInput input {{
                border-radius: 10px !important;
                height: 45px !important;
            }}
            
            /* Ícone de Nível na Sidebar */
            .role-badge {{
                display: flex;
                align-items: center;
                padding: 10px;
                background-color: {cor_primaria};
                color: white;
                border-radius: 10px;
                margin-bottom: 10px;
                font-weight: 600;
                border-left: 5px solid {cor_secundaria};
            }}
        </style>
    """, unsafe_allow_html=True)

def login():
    """Gere o acesso ao sistema com design otimizado."""
    import strings_config as s
    apply_auth_style()

    if "auth" not in st.session_state:
        st.session_state.auth = False
        st.session_state.role = None

    if not st.session_state.auth:
        # Layout centralizado
        _, col_mid, _ = st.columns([1, 1.5, 1])
        
        with col_mid:
            # Container da Logo
            logo_b64 = get_base64(s.LOGO_ARQUIVO) 
            
            st.markdown('<div class="login-header">', unsafe_allow_html=True)
            if logo_b64:
                st.markdown(f'<img src="data:image/png;base64,{logo_b64}" width="120">', unsafe_allow_html=True)
            st.markdown(f"<h2>{s.TEXTO_BANNER}</h2>", unsafe_allow_html=True)
            st.caption("Sistema de Gestão de Vendas e Associados")
            st.markdown('</div>', unsafe_allow_html=True)

            with st.form("login_form", clear_on_submit=False):
                u = st.text_input("Usuário").lower().strip()
                p = st.text_input("Senha", type="password")
                submit = st.form_submit_button("Entrar no Sistema", use_container_width=True, type="primary")
            
            if submit:
                
                if u in USERS:
                    # O bcrypt é lento; validar apenas no clique do botão é o correto
                    if bcrypt.checkpw(p.encode('utf-8'), USERS[u]["pass"]):
                        st.session_state.auth = True
                        st.session_state.role = USERS[u]["role"]
                        st.rerun() # Único rerun necessário para libertar o menu principal
                    else:
                        st.error("Senha incorreta.")
                else:
                    st.error("Usuário não encontrado.")
        return False
    return True

def logout():
    """Exibe informações do utilizador e gere a saída de forma elegante."""
    
    
    st.sidebar.markdown("---")
    
    icon_map = {
        "admin": "⚡", 
        "financeiro": "💰", 
        "vendedor": "👕", 
        "cliente": "🎟️"
    }
    role = st.session_state.role
    
    # Badge de nível de acesso estilizado
    st.sidebar.markdown(f"""
        <div class="role-badge">
            {icon_map.get(role, '👤')} &nbsp; Nível: {role.upper()}
        </div>
    """, unsafe_allow_html=True)
    
    def perform_logout():
        for key in list(st.session_state.keys()):
            del st.session_state[key]
            
    st.sidebar.button("🚪 Encerrar Sessão", use_container_width=True, on_click=perform_logout)

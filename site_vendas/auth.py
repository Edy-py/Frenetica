# -*- coding: utf-8 -*-
import streamlit as st
import bcrypt

# Dicionário com os cargos da Frenética
# Nota: Lembre-se de gerar novos hashes se for mudar as senhas reais
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

def login():
    """Gere o acesso ao sistema sem disparar reruns excessivos."""
    if "auth" not in st.session_state:
        st.session_state.auth = False
        st.session_state.role = None

    if not st.session_state.auth:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("### 🦣 Portal Frenética")
            st.caption("Sistema de Gestão de Vendas e Associados")
            
            # Uso de formulário para agrupar inputs e evitar rerun a cada tecla digitada
            with st.form("login_form", clear_on_submit=False):
                u = st.text_input("Usuário").lower().strip()
                p = st.text_input("Senha", type="password")
                submit = st.form_submit_button("Entrar", use_container_width=True, type="primary")
            
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
    """Exibe informações do utilizador e gere a saída."""
    st.sidebar.markdown("---")
    icon_map = {
        "admin": "⚡", 
        "financeiro": "💰", 
        "vendedor": "👕", 
        "cliente": "🎟️",
        "parceiro": "🎟️"
    }
    role = st.session_state.role
    st.sidebar.write(f"{icon_map.get(role, '👤')} Nível: **{role.upper()}**")
    
    # Callback para logout evita rerun manual e limpa o estado de uma só vez
    def perform_logout():
        for key in list(st.session_state.keys()):
            del st.session_state[key]
            
    st.sidebar.button("🚪 Sair", use_container_width=True, on_click=perform_logout)
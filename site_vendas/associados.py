# -*- coding: utf-8 -*-

# """
# Sistema de Gestão e Vendas - Frenética (A.A.A.T.J.B.)
# Desenvolvido por: Edílson Alves da Silva (Edy-py)
# Contato: edilsonalvesprofissional@gmail.com
# © 2026 - Todos os direitos reservados.
# """

import streamlit as st
import pandas as pd
import os
import datetime
from database import get_session, Associados, Parceiros
from utils import clean_text, get_base64_image, format_telefone, validar_cpf, validar_telefone, salvar_imagem
import strings_config as s 
from data_manager import clear_cache

so = s.SOCIOS 

def atualizar_expiracao_socios(session):
    """Varre o banco de dados e desativa sócios com mais de 30 dias de ativação."""
    try:
        agora = datetime.datetime.now()
        prazo_limite = agora - datetime.timedelta(days=30)
        
        socios_expirados = session.query(Associados).filter(
            Associados.status == "Ativo",
            Associados.data_ativacao <= prazo_limite
        ).all()
        
        if socios_expirados:
            for socio in socios_expirados:
                socio.status = "Inativo"
                socio.data_ativacao = None
            session.commit()
            clear_cache()
    except Exception as e:
        session.rollback()

@st.fragment
def render_verificacao_cpf(session):
    st.subheader("Verificar CPF")
    cod_verificar = st.text_input("Digite o CPF", key="input_verificar_parceiro")
    if st.button("Verificar Status", use_container_width=True, type="primary"):
        _, cpf_limpo = validar_cpf(cod_verificar)
        socio = session.query(Associados).filter_by(codigo_unico=cpf_limpo).first()
        if socio:
            if socio.status == "Ativo": 
                st.success(f"✅ **{socio.nome}** é Associado ATIVO!")
            else: 
                st.warning(f"⚠️ **{socio.nome}** está INATIVO.")
        else: 
            st.error(s.MSG_ERRO_SOCIO_NAO_ENCONTRADO)

def render_associados():
    st.header(f"Parceiros da {s.ATLETICA_NOME}") 
    session = get_session()
    
    # Executa a limpeza automática silenciosa ao abrir a aba
    atualizar_expiracao_socios(session)
    
    role = st.session_state.role

    if role == "parceiro":
        render_verificacao_cpf(session)

    if role == "admin":
        tab1, tab2 = st.tabs([so["TAB_GERENCIAR_SOCIOS"], so["TAB_GERENCIAR_PARCEIROS"]])
        
        with tab1:
            with st.expander(so["EXPANDER_CADASTRO"], expanded=False):
                with st.form("form_cad_socio", clear_on_submit=True):
                    c1, c2, c3 = st.columns(3)
                    nome_s = c1.text_input(so["LABEL_NOME"])
                    tel_s = c2.text_input(so["LABEL_TEL"], placeholder=s.PLACEHOLDER_TELEFONE)
                    cpf_input = c3.text_input(so["LABEL_CPF"], placeholder=s.PLACEHOLDER_CPF)
                    
                    if st.form_submit_button(so["BOTAO_SALVAR"], use_container_width=True, type="primary"):
                        sucesso_cpf, cpf_limpo = validar_cpf(cpf_input)
                        sucesso_tel, tel_limpo = validar_telefone(tel_s)
                        
                        if not nome_s: st.error(s.MSG_ERRO_CAMPOS)
                        elif not sucesso_cpf: st.error(s.MSG_ERRO_CPF)
                        elif not sucesso_tel: st.error(s.MSG_ERRO_TELEFONE)
                        else:
                            try:
                                session.add(Associados(
                                    nome=clean_text(nome_s), telefone=tel_limpo, 
                                    codigo_unico=cpf_limpo, status="Ativo",
                                    data_ativacao=datetime.datetime.now()
                                ))
                                session.commit()
                                clear_cache()
                                st.success(so["MSG_SUCESSO"])
                                st.rerun()
                            except:
                                session.rollback()
                                st.error(so["MSG_EXISTE"])

        with tab2:
            with st.expander("➕ Cadastrar Novos Parceiros", expanded=False):
                with st.form("form_cad_parceiro", clear_on_submit=True):
                    nome_p = st.text_input("Nome da empresa")
                    vantagem_p = st.text_area("Vantagens oferecidas")
                    logo_arq = st.file_uploader("Logo da empresa", type=['png', 'jpg', 'jpeg'])
                    
                    if st.form_submit_button("Publicar Parceria", type="primary", use_container_width=True):
                        if nome_p and vantagem_p:
                            try:
                                nome_logo = salvar_imagem(logo_arq, "parceiros") if logo_arq else None
                                session.add(Parceiros(nome=nome_p.upper().strip(), vantagem=vantagem_p, logo_url=nome_logo))
                                session.commit() 
                                clear_cache()
                                st.success(s.MSG_SUCESSO_PARCERIA)
                                st.rerun()
                            except:
                                session.rollback()
                                st.error("Erro ao salvar parceiro.")

            st.divider()
            st.subheader("⚙️ Gerenciar Parceiros Existentes")
            parceiros_lista = session.query(Parceiros).all()
            
            if parceiros_lista:
                for p in parceiros_lista:
                    with st.expander(f"🏢 {p.nome}"):
                        with st.form(key=f"form_edit_parceiro_{p.id}"):
                            edit_nome = st.text_input("Nome da Empresa", value=p.nome)
                            edit_vantagem = st.text_area("Vantagens", value=p.vantagem)
                            edit_logo = st.file_uploader("Trocar Logo (opcional)", type=['png', 'jpg', 'jpeg'])
                            
                            col_b1, col_b2 = st.columns(2)
                            if col_b1.form_submit_button("💾 Salvar Alterações", use_container_width=True):
                                try:
                                    p.nome = edit_nome.upper().strip()
                                    p.vantagem = edit_vantagem
                                    if edit_logo:
                                        p.logo_url = salvar_imagem(edit_logo, "parceiros")
                                    session.commit()
                                    clear_cache()
                                    st.success("Alterações salvas!")
                                    st.rerun()
                                except:
                                    session.rollback()
                                    st.error("Erro ao atualizar parceiro.")
                            
                            if col_b2.form_submit_button("🗑️ Excluir Parceiro", use_container_width=True):
                                try:
                                    session.delete(p)
                                    session.commit()
                                    clear_cache()
                                    st.warning("Parceiro removido!")
                                    st.rerun()
                                except:
                                    session.rollback()
                                    st.error("Erro ao remover parceiro.")
            else:
                st.info("Nenhum parceiro cadastrado para gerenciar.")

    if role in ["admin", "financeiro"]:
        st.divider()
        with st.expander(so["EXPANDER_STATUS"], expanded=False):
            col1, col2 = st.columns(2)
            c_busca = col1.text_input(so["BUSCA_CPF"], key="busca_status_cpf")
            n_busca = col2.text_input(so["BUSCA_NOME"], key="busca_status_nome")
            
            socio_edit = None
            if c_busca:
                _, c_limpo = validar_cpf(c_busca)
                socio_edit = session.query(Associados).filter_by(codigo_unico=c_limpo).first()
            elif n_busca:
                socio_edit = session.query(Associados).filter(Associados.nome.ilike(f"%{n_busca}%")).first()
            
            if socio_edit:
                st.info(f"Sócio: **{socio_edit.nome}**")
                novo_status = st.selectbox("Alterar Status:", ["Ativo", "Inativo"], 
                                         index=(0 if socio_edit.status == "Ativo" else 1))
                if st.button("Confirmar Alteração", use_container_width=True, type="primary"):
                    socio_edit.status = novo_status
                    if novo_status == "Ativo":
                        socio_edit.data_ativacao = datetime.datetime.now()
                    else:
                        socio_edit.data_ativacao = None
                    session.commit() 
                    clear_cache()
                    st.success("Status Atualizado!")
                    st.rerun()
            elif c_busca or n_busca: 
                st.warning(so["MSG_NAO_ENCONTRADO"])

        st.subheader(so["LISTA_TITULO"])
        todos = session.query(Associados).all()
        if todos:
            df_as = pd.DataFrame([{"Nome": socio.nome, "CPF": socio.codigo_unico, "Status": socio.status, "Telefone": format_telefone(socio.telefone)} for socio in todos])
            st.dataframe(df_as, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader(f"Benefícios {s.ATLETICA_NOME}")
    lista_parceiros_view = session.query(Parceiros).all()
    if lista_parceiros_view:
        cols = st.columns(3)
        for idx, p in enumerate(lista_parceiros_view):
            with cols[idx % 3]:
                base_dir = os.path.dirname(os.path.abspath(__file__))
                caminho = os.path.join(base_dir, "imagens", "parceiros", p.logo_url) if p.logo_url else ""
                if not os.path.exists(caminho) and p.logo_url:
                    caminho = os.path.join("imagens", "parceiros", p.logo_url)
                b64 = get_base64_image(caminho) if os.path.exists(caminho) else None
                img_tag = f'<img src="data:image/png;base64,{b64}" class="card-img">' if b64 else '<div class="card-icon" style="height:100px;width:100px;background:#eee;border-radius:50%;margin-bottom:15px;"></div>'
                st.markdown(f'<div class="card-parceiro">{img_tag}<h3 class="card-title">{p.nome}</h3><p class="card-text">{p.vantagem}</p></div>', unsafe_allow_html=True)
    else: 
        st.info("Em breve novas parcerias!")

    session.close()
# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import os
from database import get_session, Associados, Parceiros
from utils import clean_text, get_base64_image, format_telefone, validar_cpf, validar_telefone
import strings_config as s 
from data_manager import clear_cache

so = s.SOCIOS 

def render_associados():
    st.header(f"Parceiros da {s.ATLETICA_NOME}") 
    session = get_session()
    role = st.session_state.role

    # --- PERFIL: PARCEIRO (VERIFICAÇÃO RÁPIDA) ---
    if role == "parceiro":
        st.subheader("Verificar CPF")
        cod_verificar = st.text_input("Digite o CPF", key="input_verificar_parceiro")
        if st.button("Verificar Status", use_container_width=True, type="primary", key="btn_verificar_parceiro"):
            _, cpf_limpo = validar_cpf(cod_verificar)
            socio = session.query(Associados).filter_by(codigo_unico=cpf_limpo).first()
            if socio:
                if socio.status == "Ativo": st.success(f"✅ **{socio.nome}** é Associado ATIVO!")
                else: st.warning(f"⚠️ **{socio.nome}** está INATIVO.")
            else: st.error(s.MSG_ERRO_SOCIO_NAO_ENCONTRADO)

    # --- PERFIL: ADMIN (CADASTRO DINÂMICO) ---
    if role == "admin":
        tab1, tab2 = st.tabs([so["TAB_GERENCIAR_SOCIOS"], so["TAB_GERENCIAR_PARCEIROS"]])
        
        with tab1:
            with st.expander(so["EXPANDER_CADASTRO"], expanded=False):
                c1, c2, c3 = st.columns(3)
                nome_s = c1.text_input(so["LABEL_NOME"], key="cad_nome_socio")
                tel_s = c2.text_input(so["LABEL_TEL"], placeholder=s.PLACEHOLDER_TELEFONE, key="cad_tel_socio")
                cpf_input = c3.text_input(so["LABEL_CPF"], placeholder=s.PLACEHOLDER_CPF, key="cad_cpf_socio")
                
                if st.button(so["BOTAO_SALVAR"], use_container_width=True, type="primary"):
                    sucesso_cpf, cpf_limpo = validar_cpf(cpf_input)
                    sucesso_tel, tel_limpo = validar_telefone(tel_s)
                    
                    if not nome_s: st.error(s.MSG_ERRO_CAMPOS)
                    elif not sucesso_cpf: st.error(s.MSG_ERRO_CPF)
                    elif not sucesso_tel: st.error(s.MSG_ERRO_TELEFONE)
                    else:
                        try:
                            session.add(Associados(nome=clean_text(nome_s), telefone=tel_limpo, codigo_unico=cpf_limpo, status="Ativo"))
                            session.commit()
                            clear_cache() # Limpar cache
                            st.success(so["MSG_SUCESSO"]) 
                            st.rerun()
                        except:
                            session.rollback(); st.error(so["MSG_EXISTE"])

        with tab2:
            with st.expander("Cadastrar novos parceiros", expanded=False):
                nome_p = st.text_input("Nome da empresa", key="cad_nome_empresa")
                vantagem_p = st.text_area("Vantagens oferecidas", key="cad_vantagem_empresa")
                logo_arq = st.file_uploader("Logo da empresa", type=['png', 'jpg', 'jpeg'], key="cad_logo_empresa")
                
                if st.button("Publicar Parceria", type="primary", use_container_width=True):
                    if nome_p and vantagem_p:
                        try:
                            from utils import salvar_imagem
                            nome_logo = salvar_imagem(logo_arq, "parceiros") if logo_arq else None
                            session.add(Parceiros(nome=nome_p.upper().strip(), vantagem=vantagem_p, logo_url=nome_logo))
                            session.commit() 
                            clear_cache() # Limpar cache
                            st.success(s.MSG_SUCESSO_PARCERIA) 
                            st.rerun()
                        except:
                            session.rollback(); st.error("Erro ao salvar parceiro.")

    # --- CONTROLE DE STATUS (FINANCEIRO / ADMIN) ---
    if role in ["admin", "financeiro"]:
        st.divider()
        with st.expander(so["EXPANDER_STATUS"], expanded=False):
            socio_edit = None 
            col1, col2 = st.columns(2)
            c_busca = col1.text_input(so["BUSCA_CPF"], key="busca_status_cpf")
            n_busca = col2.text_input(so["BUSCA_NOME"], key="busca_status_nome")
            
            if c_busca:
                _, c_limpo = validar_cpf(c_busca)
                socio_edit = session.query(Associados).filter_by(codigo_unico=c_limpo).first()
            elif n_busca:
                socio_edit = session.query(Associados).filter(Associados.nome.ilike(f"%{n_busca}%")).first()
            
            if socio_edit:
                st.info(f"Sócio: **{socio_edit.nome}**")
                novo_status = st.selectbox("Alterar Status:", ["Ativo", "Inativo"], index=(0 if socio_edit.status == "Ativo" else 1))
                if st.button("Confirmar Alteração", use_container_width=True, type="primary"):
                    socio_edit.status = novo_status
                    session.commit() 
                    clear_cache() # Limpar cache
                    st.success("Status Atualizado!") 
                    st.rerun()
            elif c_busca or n_busca: st.warning(so["MSG_NAO_ENCONTRADO"])

        st.subheader(so["LISTA_TITULO"])
        todos = session.query(Associados).all()
        if todos:
            df_as = pd.DataFrame([{"Nome": socio.nome, "CPF": socio.codigo_unico, "Status": socio.status, "Telefone": format_telefone(socio.telefone)} for socio in todos])
            st.dataframe(df_as, use_container_width=True, hide_index=True)

    # --- VISUALIZAÇÃO DE CARDS ---
    st.divider()
    st.subheader(f"Benefícios {s.ATLETICA_NOME}")
    lista_parceiros = session.query(Parceiros).all()
    if lista_parceiros:
        cols = st.columns(3)
        for idx, p in enumerate(lista_parceiros):
            with cols[idx % 3]:
                caminho = os.path.join("imagens", "parceiros", p.logo_url) if p.logo_url else ""
                b64 = get_base64_image(caminho)
                img_tag = f'<img src="data:image/png;base64,{b64}" class="card-img">' if b64 else '<div class="card-icon"></div>'
                st.markdown(f'<div class="card-parceiro">{img_tag}<h3 class="card-title">{p.nome}</h3><p class="card-text">{p.vantagem}</p></div>', unsafe_allow_html=True)
    else: st.info("Em breve novas parcerias!")

    session.close()
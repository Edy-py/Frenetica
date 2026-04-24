# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import os
from database import get_session, Associados, Parceiros
from utils import clean_text, get_base64_image, format_telefone, validar_cpf, validar_telefone
import strings_config as s  

# Usando o atalho sugerido para o dicionário de sócios
so = s.SOCIOS 

def render_associados():
    # Padronizado com s.ATLETICA_NOME
    st.header(f"Parceiros da {s.ATLETICA_NOME}") 
    session = get_session()
    role = st.session_state.role

    # --- PERFIL: PARCEIRO (VERIFICAÇÃO RÁPIDA) ---
    if role == "parceiro":
        st.subheader("Verificar CPF")
        # Adicionado 'key' única para evitar conflito com a busca do admin
        cod_verificar = st.text_input("Digite o CPF", key="input_verificar_parceiro")
        if st.button("Verificar", use_container_width=True, type="primary", key="btn_verificar_parceiro"):
            socio = session.query(Associados).filter_by(codigo_unico=cod_verificar).first()
            if socio:
                if socio.status == "Ativo":
                    st.success(f"✅ **{socio.nome}** é Associado ATIVO!")
                else:
                    st.warning(f"⚠️ **{socio.nome}** está INATIVO.")
            else:
                st.error(s.MSG_SOCIO_NAO_ENCONTRADO)

    # --- PERFIL: ADMIN (CADASTRO DINÂMICO) ---
    if role == "admin":
        tab1, tab2 = st.tabs([so["TAB_GERENCIAR_SOCIOS"], so["TAB_GERENCIAR_PARCEIROS"]])
        
        with tab1:
            with st.expander(so["EXPANDER_CADASTRO"], expanded=False):
                c1, c2, c3 = st.columns(3)
                # Adicionadas 'keys' únicas para o formulário de cadastro
                nome_s = c1.text_input(so["LABEL_NOME"], key="cad_nome_socio")
                tel_s = c2.text_input(so["LABEL_TEL"], placeholder=s.PLACEHOLDER_TELEFONE, key="cad_tel_socio")
                cpf_input = c3.text_input(so["LABEL_CPF"], placeholder=s.PLACEHOLDER_CPF, key="cad_cpf_socio")
                
                if st.button(so["BOTAO_SALVAR"], use_container_width=True, type="primary", key="btn_salvar_socio"):
                    sucesso_cpf, cpf_limpo = validar_cpf(cpf_input)
                    sucesso_tel, tel_limpo = validar_telefone(tel_s)
                    
                    if not nome_s:
                        st.error(s.MSG_ERRO_CAMPOS)
                    elif not sucesso_cpf:
                        st.error(s.MSG_ERRO_CPF)
                    elif not sucesso_tel:
                        st.error(s.MSG_ERRO_TELEFONE)
                    else:
                        try:
                            novo_socio = Associados(
                                nome=clean_text(nome_s), 
                                telefone=tel_limpo, 
                                codigo_unico=cpf_limpo,
                                status="Ativo" 
                            )
                            session.add(novo_socio)
                            session.commit()
                            st.success(so["MSG_SUCESSO"])
                            st.rerun()
                        except Exception as e:
                            session.rollback()
                            st.error(so["MSG_EXISTE"])

        with tab2:
            with st.expander("Cadastrar novos parceiros", expanded=False):
                # Adicionadas 'keys' para o formulário de parceiros
                nome_p = st.text_input("Nome da empresa", key="cad_nome_empresa")
                vantagem_p = st.text_area("Vantagens oferecidas", key="cad_vantagem_empresa")
                logo_arq = st.file_uploader("Adicionar logo da empresa", type=['png', 'jpg', 'jpeg'], key="cad_logo_empresa")
                
                if st.button("Publicar", type="primary", use_container_width=True, key="btn_publicar_parceria"):
                    if nome_p and vantagem_p:
                        from utils import salvar_imagem
                        nome_logo = salvar_imagem(logo_arq, "parceiros")
                        session.add(Parceiros(nome=nome_p.upper(), vantagem=vantagem_p, logo_url=nome_logo))
                        session.commit()
                        st.success(s.MSG_SUCESSO_PARCERIA)
                        st.rerun()

    # --- PERFIL: FINANCEIRO & ADMIN (CONTROLE DE STATUS) ---
    if role in ["admin", "financeiro"]:
        st.divider()
        with st.expander(so["EXPANDER_STATUS"], expanded=False):
            socio_edit = None 
            col1, col2 = st.columns(2)
            
            with col1:
                # 'key' para busca por CPF
                cpf_busca = st.text_input(so["BUSCA_CPF"], key="busca_status_cpf")
                if cpf_busca:
                    _, cpf_limpo_busca = validar_cpf(cpf_busca)
                    socio_edit = session.query(Associados).filter_by(codigo_unico=cpf_limpo_busca).first()
            
            with col2:
                # 'key' para busca por Nome
                nome_busca = st.text_input(so["BUSCA_NOME"], key="busca_status_nome")
                if nome_busca:
                    socio_edit = session.query(Associados).filter(Associados.nome.ilike(f"%{nome_busca}%")).first()
            
            if socio_edit:
                st.info(f"Sócio: **{socio_edit.nome}**")
                novo_status = st.selectbox("Status:", ["Ativo", "Inativo"], 
                                         index=0 if socio_edit.status == "Ativo" else 1,
                                         key="select_status_socio")
                
                if st.button("Atualizar Status", use_container_width=True, type="primary", key="btn_update_status"):
                    socio_edit.status = novo_status
                    session.commit()
                    st.success(f"Status de {socio_edit.nome} atualizado para {novo_status}!")
                    st.rerun()
            elif cpf_busca or nome_busca:
                st.warning(so["MSG_NAO_ENCONTRADO"])

        # --- LISTAGEM ABAIXO ---
        st.subheader(so["LISTA_TITULO"])
        todos = session.query(Associados).all()
        if todos:
            df_as = pd.DataFrame([{
                "Nome": socio.nome, 
                "CPF": socio.codigo_unico, 
                "Status": socio.status, 
                "Telefone": format_telefone(socio.telefone)
            } for socio in todos])
            st.dataframe(df_as, use_container_width=True, hide_index=True)

    # --- VISUALIZAÇÃO DE CARDS (PARA TODOS) ---
    st.divider()
    st.subheader(f"Benefício(s) por ser sócio da {s.ATLETICA_NOME}")
    
    lista_parceiros = session.query(Parceiros).all()
    if lista_parceiros:
        cols = st.columns(3)
        for idx, p in enumerate(lista_parceiros):
            with cols[idx % 3]:
                caminho_logo = os.path.join("imagens", "parceiros", p.logo_url) if p.logo_url else ""
                b64_img = get_base64_image(caminho_logo)
                
                img_html = f'<img src="data:image/png;base64,{b64_img}" class="card-img">' if b64_img else '<div class="card-icon"></div>'

                st.markdown(f"""
                <div class="card-parceiro">
                    {img_html}
                    <h3 class="card-title">{p.nome}</h3>
                    <p class="card-text">{p.vantagem}</p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Parcerias em breve")

    session.close()
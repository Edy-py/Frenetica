# -*- coding: utf-8 -*-
import streamlit as st
import os
from database import get_session, Estoque, Vendas, Associados
from utils import format_currency, clean_text, validar_cpf, validar_telefone
import strings_config as s
from strings_config import LOJA as l # Atalho para escrever menos
from strings_config import VENDAS as v # Atalho para escrever menos


def render_compras():
    session = get_session()
    desconto_ativo = st.session_state.get("socio_logado") is not None
    st.markdown(f'<h2 style="text-align: center;">{l["TITULO"]}</h2>', unsafe_allow_html=True)

    # --- Nome único para o carrinho do cliente ---
    if 'carrinho_cliente' not in st.session_state:
        st.session_state.carrinho_cliente = []

    # --- SIDEBAR: ÁREA DO SÓCIO PERSISTENTE ---
    with st.sidebar:
        st.header(l["HEADER_SOCIO"])
        
        # 1. Inicializa a variável de sessão se ela não existir
        if "socio_logado" not in st.session_state:
            st.session_state.socio_logado = None

        # 2. Se não houver ninguém logado, mostra o campo de input
        if st.session_state.socio_logado is None:
            cod_promo = st.text_input(l["LABEL_BUSCA_SOCIO"], key="input_login_socio")
            
            if cod_promo:
                _, cpf_busca = validar_cpf(cod_promo)
                socio = session.query(Associados).filter_by(codigo_unico=cpf_busca, status="Ativo").first()
                
                if socio:
                    # Salva o sócio na sessão
                    st.session_state.socio_logado = {
                        "nome": socio.nome,
                        "cpf": socio.codigo_unico,
                        "telefone": socio.telefone
                    }
                    st.rerun()
                else:
                    st.error("Sócio não encontrado ou inativo.")
        
        # 3. Se já houver alguém logado, mostra as boas-vindas e o botão de "Sair"
        else:
            s_atras = st.session_state.socio_logado
            st.success(f"Logado: **{s_atras['nome']}**")
            st.caption(l["CAPTION_DESC"])
            
            # Define a variável que os outros scripts usam para dar desconto
            desconto_ativo = True 
            
            if st.button("Sair / Trocar CPF"):
                st.session_state.socio_logado = None
                st.rerun()

        st.divider()

        st.subheader(l["HEADER_ADESAO"])
        with st.expander(l["BOTAO_ADESAO"], expanded=False):
            st.info(l["CHAMADA_ADESAO"])
            st.metric(label="Taxa de Adesão", value=format_currency(s.VALOR_ADESAO_SOCIO))
            
            # Form corrigido com indentação correta
            with st.form("form_nova_adesao_socio", clear_on_submit=True):
                novo_nome = st.text_input("Nome da empresa")
                novo_tel = st.text_input("Telefone", placeholder=s.PLACEHOLDER_TELEFONE)
                novo_cpf = st.text_input("Seu CPF", placeholder=s.PLACEHOLDER_CPF)
            
                submit_adesao = st.form_submit_button("Solicitar Adesão", use_container_width=True)
            
                if submit_adesao:
                    sucesso_tel, tel_limpo = validar_telefone(novo_tel)
                    sucesso_cpf, cpf_limpo = validar_cpf(novo_cpf)
                    
                    if not sucesso_cpf:
                        st.error(s.MSG_ERRO_CPF)
                    elif not sucesso_tel:
                        st.error(s.MSG_ERRO_TELEFONE)
                    elif novo_nome:
                        try:
                            nova_adesao = Associados(
                                nome=clean_text(novo_nome),
                                codigo_unico=cpf_limpo,
                                telefone=tel_limpo,
                                status="Inativo" 
                            )
                            session.add(nova_adesao)
                            session.commit()
                            st.success(f"Bem vido a {s.ATLETICA_NOME}")
                            st.link_button("Enviar comprovante", s.LINK_WHATSAPP_FIN)
                        except Exception as e:
                            session.rollback()
                            st.error(s.MSG_ERRO_CPF)
                    else:
                        st.warning(s.MSG_ERRO_CAMPOS)

    # --- VITRINE ---
    prods = session.query(Estoque).filter(Estoque.quantidade > 0).all()
    if prods:
        cols = st.columns(3)
        for idx, p in enumerate(prods):
            with cols[idx % 3]:
                path = f"imagens/produtos/{p.foto_url}"
                if p.foto_url and os.path.exists(path):
                    st.image(path, use_container_width=True)
                else:
                    st.warning("Produlto sem Imagem")
                
                preco_base = p.preco_venda_un
                valor_final = preco_base * (1 - s.DESCONTO_VALOR) if desconto_ativo else preco_base
                
                st.subheader(p.nome_produto)
                st.markdown(f"### {format_currency(valor_final)}")
                
                if st.button(f"🛒 Adicionar ao carrinho", key=f"btn_{p.id}", use_container_width=True):
                    st.session_state.carrinho_cliente.append({
                        "id_sessao": os.urandom(4).hex(),
                        "id_db": p.id, 
                        "nome": p.nome_produto, 
                        "preco": valor_final,
                        "personalizavel": p.personalizavel,
                        "personalizacao": ""
                    })
                    st.toast(f"{p.nome_produto} adicionado!")

    # --- CARRINHO DO CLIENTE ---
    if st.session_state.carrinho_cliente:
        st.divider()
        st.subheader("Resumo do pedido")
        
        for i, item in enumerate(list(st.session_state.carrinho_cliente)):
            col_info, col_pers, col_remove = st.columns([2, 2, 1])
            col_info.write(f"**{item['nome']}**\n{format_currency(item['preco'])}")
            
            if item['personalizavel']:
                item['personalizacao'] = col_pers.text_input(
                    f"{l['LABEL_PERS']}", 
                    key=f"pers_{item['id_sessao']}",
                    placeholder=s.PLACEHOLDER_PERSONALIZACAO
                )
            
            if col_remove.button(f"🗑️ {item['nome']}", key=f"rem_{item['id_sessao']}", help="Clique para remover este item"):
                st.session_state.carrinho_cliente.pop(i)
                st.rerun()

        # FINALIZAÇÃO
        with st.form("finalizar_compra_cliente"):

            if st.session_state.socio_logado:
                nome_s_state = st.session_state.socio_logado.get('nome', "")
                tel_s_state = st.session_state.socio_logado.get('telefone', "")
            else:
                nome_s_state = ""
                tel_s_state = ""

            nome_cli = st.text_input(v["LABEL_NOME_CLIENTE"], value=nome_s_state, key="finalizar_nome")
            tel_cli = st.text_input(v["LABEL_TEL_CLIENTE"], value=tel_s_state, key="finalizar_tel")
            total = sum(it['preco'] for it in st.session_state.carrinho_cliente)
            
            st.markdown(f"### Total: :green[{format_currency(total)}]")
            
            if st.form_submit_button("Finalizar Compra", use_container_width=True):
                # Validação de tel antes de finalizar
                sucesso_tel_fim, tel_limpo_fim = validar_telefone(tel_cli)
                
                if not sucesso_tel_fim:
                    st.error(s.MSG_ERRO_TELEFONE)
                elif nome_cli:
                    try:
                        for item in st.session_state.carrinho_cliente:
                            p_db = session.query(Estoque).filter_by(id=item['id_db']).with_for_update().first()
                            if p_db.quantidade > 0:
                                nova_venda = Vendas(
                                    nome_prod=item['nome'], qtd_vendida=1,
                                    preco_venda_total=item['preco'], nome_cliente=clean_text(nome_cli),
                                    telefone=tel_limpo_fim, personalizacao=item['personalizacao'],
                                    is_associado=desconto_ativo, status_pagamento="Pagamento Pendente"
                                )
                                session.add(nova_venda)
                                p_db.quantidade -= 1
                            else:
                                st.error(l["MSG_ESGOTADO"].format(nome=item['nome']))
                                session.rollback()
                                return
                        
                        session.commit()
                        st.success("Compra registrada com sucesso!!")
                        
                        # Mostra instruções de PIX se for o caso
                        st.markdown(s.MSG_PAGAMENTO_PIX)
                        st.link_button("📤 Enviar Comprovante", s.LINK_WHATSAPP_FIN)
                        
                        st.session_state.carrinho_cliente = []
                        
                    except Exception as e:
                        session.rollback()
                        st.error(f"Erro: {e}")
                else:
                    st.error(s.MSG_ERRO_TELEFONE)
    session.close()
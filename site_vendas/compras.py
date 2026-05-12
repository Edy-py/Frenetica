# -*- coding: utf-8 -*-
import streamlit as st
import os
from database import get_session, Estoque, Vendas, Associados
from utils import format_currency, clean_text, validar_cpf, validar_telefone
import strings_config as s
from strings_config import LOJA as l 
from strings_config import VENDAS as v 
import pandas as pd
import datetime
from data_manager import clear_cache 

def render_compras():
    session = get_session()
    # Centralização do estado de sócio
    socio_info = st.session_state.get("socio_logado")
    desconto_ativo = socio_info is not None
    
    st.markdown(f'<h2 style="text-align: center;">{l["TITULO"]}</h2>', unsafe_allow_html=True)

    if 'carrinho_cliente' not in st.session_state:
        st.session_state.carrinho_cliente = []

    # --- SIDEBAR: ÁREA DO SÓCIO ---
    with st.sidebar:
        st.header(l["HEADER_SOCIO"])
        
        if not socio_info:
            cod_promo = st.text_input(l["LABEL_BUSCA_SOCIO"], key="input_login_socio")
            if cod_promo:
                _, cpf_busca = validar_cpf(cod_promo)
                socio = session.query(Associados).filter_by(codigo_unico=cpf_busca, status="Ativo").first()
                if socio:
                    st.session_state.socio_logado = {
                        "nome": socio.nome,
                        "cpf": socio.codigo_unico,
                        "telefone": socio.telefone
                    }
                    st.rerun()
                else:
                    st.error("Sócio não encontrado ou inativo.")
        else:
            st.success(f"Logado: **{socio_info['nome']}**")
            st.caption(l["CAPTION_DESC"])
            if st.button("Sair / Trocar CPF"):
                st.session_state.socio_logado = None
                st.rerun()

        st.divider()
        st.subheader(l["HEADER_ADESAO"])
        with st.expander(l["BOTAO_ADESAO"], expanded=False):
            st.info(l["CHAMADA_ADESAO"])
            st.metric(label="Taxa de Adesão", value=format_currency(s.VALOR_ADESAO_SOCIO))
            
            with st.form("form_nova_adesao_socio", clear_on_submit=True):
                novo_nome = st.text_input("Nome da empresa")
                novo_tel = st.text_input("Telefone", placeholder=s.PLACEHOLDER_TELEFONE)
                novo_cpf = st.text_input("Seu CPF", placeholder=s.PLACEHOLDER_CPF)
                if st.form_submit_button("Solicitar Adesão", use_container_width=True):
                    sucesso_tel, tel_limpo = validar_telefone(novo_tel)
                    sucesso_cpf, cpf_limpo = validar_cpf(novo_cpf)
                    
                    if not sucesso_cpf: st.error(s.MSG_ERRO_CPF)
                    elif not sucesso_tel: st.error(s.MSG_ERRO_TELEFONE)
                    elif novo_nome:
                        try:
                            nova_adesao = Associados(nome=clean_text(novo_nome), codigo_unico=cpf_limpo, telefone=tel_limpo, status="Inativo")
                            session.add(nova_adesao)
                            session.commit()
                            clear_cache() # Limpar cache
                            st.success(f"Bem vindo a {s.ATLETICA_NOME}")
                            st.link_button("Enviar comprovante", s.LINK_WHATSAPP_FIN)
                        except:
                            session.rollback()
                            st.error(s.MSG_ERRO_CPF)
                    else: st.warning(s.MSG_ERRO_CAMPOS)

    # --- VITRINE ---
    prods = session.query(Estoque).filter(Estoque.quantidade > 0).all()
    if prods:
        cols = st.columns(3)
        for idx, p in enumerate(prods):
            with cols[idx % 3]:
                path = f"imagens/produtos/{p.foto_url}"
                if p.foto_url and os.path.exists(path): st.image(path, use_container_width=True)
                else: st.warning("Produto sem Imagem")
                
                v_unitario = p.preco_venda_un * (1 - s.DESCONTO_VALOR) if desconto_ativo else p.preco_venda_un
                st.subheader(p.nome_produto)
                st.markdown(f"### {format_currency(v_unitario)}")
                
                if st.button(f"🛒 Adicionar", key=f"btn_{p.id}", use_container_width=True):
                    st.session_state.carrinho_cliente.append({
                        "id_db": p.id, "nome": p.nome_produto, "preco": v_unitario,
                        "personalizavel": p.personalizavel, "personalizacao": ""
                    })
                    st.toast(f"{p.nome_produto} adicionado!")

    # --- CARRINHO E FINALIZAÇÃO ---
    if st.session_state.carrinho_cliente:
        st.divider()
        st.subheader("🛒 Seu Carrinho")
        
        df_cart = pd.DataFrame(st.session_state.carrinho_cliente)
        # Exibição aprimorada da tabela
        st.table(df_cart[['nome', 'preco']].assign(Preço=df_cart['preco'].apply(format_currency))[['nome', 'Preço']].rename(columns={'nome':'Produto'}))
        
        total_bruto = df_cart['preco'].sum()
        desc_total = total_bruto * s.DESCONTO_VALOR if desconto_ativo else 0.0
        total_final = total_bruto - desc_total

        if desconto_ativo:
            st.success(f"✅ Desconto de Sócio: {format_currency(desc_total)}")
        st.markdown(f"### Total: :green[{format_currency(total_final)}]")

        c1, c2 = st.columns(2)
        metodo_sel = c1.selectbox(v["LABEL_PAGAMENTO"], v["OPCOES_PAGAMENTO"], key="compra_metodo_pag")
        tamanho_sel = c2.selectbox(v["LABEL_TAMANHO"], v["OPCOES_TAMANHO"], key="compra_tamanho")
        
        personalizacao = None
        if any(item['personalizavel'] for item in st.session_state.carrinho_cliente):
            personalizacao = st.text_input("Personalização", placeholder="Nome - Número", key="compra_personalizacao")

        btn_f1, btn_f2 = st.columns(2)
        if btn_f1.button("✅ Finalizar Pedido", use_container_width=True, type="primary"):
            try:
                nome_cli = socio_info['nome'] if socio_info else "CLIENTE LOJA"
                tel_cli = socio_info['telefone'] if socio_info else ""
                desc_item = desc_total / len(st.session_state.carrinho_cliente)

                for item in st.session_state.carrinho_cliente:
                    prod_db = session.query(Estoque).filter_by(id=item['id_db']).first()
                    custo_un = float(prod_db.preco_custo or 0)
                    valor_v_item = float(item['preco'] - desc_item)
                    
                    session.add(Vendas(
                        nome_prod=item['nome'], qtd_vendida=1, preco_venda_total=valor_v_item,
                        data=datetime.datetime.now(), lucro=valor_v_item - custo_un,
                        nome_cliente=nome_cli, telefone=tel_cli, tamanho=tamanho_sel,
                        personalizacao=personalizacao, metodo_pagamento=metodo_sel,
                        is_associado=desconto_ativo
                    ))
                    if prod_db: prod_db.quantidade -= 1

                session.commit()
                st.balloons()
                clear_cache() # Limpar cache
                if metodo_sel == "Pix":
                    st.info(s.MSG_PAGAMENTO_PIX)
                    st.link_button("📤 Enviar Comprovante", s.LINK_WHATSAPP_FIN)
                
                st.session_state.carrinho_cliente = []
                st.rerun()
            except Exception as e:
                session.rollback()
                st.error(f"Erro: {e}")

        if btn_f2.button("🗑️ Limpar", use_container_width=True):
            st.session_state.carrinho_cliente = []
            st.rerun()

    session.close()
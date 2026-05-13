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

@st.fragment
def render_loja_dinamica(session):
    """Fragmento que isola a vitrine e o carrinho para evitar recarregamento total."""
    desconto_ativo = st.session_state.get("socio_logado") is not None
    
    # --- VITRINE ---
    prods = session.query(Estoque).filter(Estoque.quantidade > 0).all()
    if prods:
        cols = st.columns(3)
        for idx, p in enumerate(prods):
            with cols[idx % 3]:
                path = f"imagens/produtos/{p.foto_url}"
                if p.foto_url and os.path.exists(path): 
                    st.image(path, use_container_width=True)
                
                v_unitario = p.preco_venda_un * (1 - s.DESCONTO_VALOR) if desconto_ativo else p.preco_venda_un
                st.subheader(p.nome_produto)
                st.markdown(f"### {format_currency(v_unitario)}")
                
                # Botão com callback para adicionar sem rerun total
                def add_ao_carrinho(prod=p, preco=v_unitario):
                    st.session_state.carrinho_cliente.append({
                        "id_db": prod.id, "nome": prod.nome_produto, "preco": preco,
                        "personalizavel": prod.personalizavel, "personalizacao": ""
                    })
                    st.toast(f"{prod.nome_produto} adicionado!")

                st.button(f"🛒 Adicionar", key=f"btn_{p.id}", use_container_width=True, on_click=add_ao_carrinho)

    # --- CARRINHO ---
    if st.session_state.carrinho_cliente:
        st.divider()
        st.subheader("🛒 Seu Carrinho")
        
        df_cart = pd.DataFrame(st.session_state.carrinho_cliente)
        st.table(df_cart[['nome', 'preco']].assign(
            Preço=df_cart['preco'].apply(format_currency))[['nome', 'Preço']].rename(columns={'nome':'Produto'})
        )
        
        total_final = df_cart['preco'].sum()
        st.markdown(f"### Total: :green[{format_currency(total_final)}]")

        with st.form("form_finalizar_compra"):
            c1, c2 = st.columns(2)
            metodo_sel = c1.selectbox(v["LABEL_PAGAMENTO"], v["OPCOES_PAGAMENTO"])
            tamanho_sel = c2.selectbox(v["LABEL_TAMANHO"], v["OPCOES_TAMANHO"])
            
            perso = None
            if any(item['personalizavel'] for item in st.session_state.carrinho_cliente):
                perso = st.text_input("Personalização", placeholder="Nome - Número")

            if st.form_submit_button("✅ Finalizar Pedido", use_container_width=True, type="primary"):
                try:
                    socio_info = st.session_state.get("socio_logado")
                    nome_cli = socio_info['nome'] if socio_info else "CLIENTE LOJA"
                    tel_cli = socio_info['telefone'] if socio_info else ""

                    for item in st.session_state.carrinho_cliente:
                        prod_db = session.query(Estoque).filter_by(id=item['id_db']).first()
                        custo_un = float(prod_db.preco_custo or 0)
                        
                        session.add(Vendas(
                            nome_prod=item['nome'], qtd_vendida=1, preco_venda_total=item['preco'],
                            data=datetime.datetime.now(), lucro=item['preco'] - custo_un,
                            nome_cliente=nome_cli, telefone=tel_cli, tamanho=tamanho_sel,
                            personalizacao=perso, metodo_pagamento=metodo_sel,
                            is_associado=desconto_ativo
                        ))
                        if prod_db: prod_db.quantidade -= 1

                    session.commit()
                    st.balloons()
                    clear_cache()
                    st.session_state.carrinho_cliente = []
                    if metodo_sel == "Pix":
                        st.info(s.MSG_PAGAMENTO_PIX)
                    st.rerun()
                except Exception as e:
                    session.rollback()
                    st.error(f"Erro: {e}")

def render_compras():
    session = get_session()
    
    if 'carrinho_cliente' not in st.session_state:
        st.session_state.carrinho_cliente = []

    st.markdown(f'<h2 style="text-align: center;">{l["TITULO"]}</h2>', unsafe_allow_html=True)

    # --- SIDEBAR: ÁREA DO SÓCIO ---
    with st.sidebar:
        st.header(l["HEADER_SOCIO"])
        socio_info = st.session_state.get("socio_logado")
        
        if not socio_info:
            with st.form("login_socio"):
                cod_promo = st.text_input(l["LABEL_BUSCA_SOCIO"])
                if st.form_submit_button("Validar CPF"):
                    _, cpf_busca = validar_cpf(cod_promo)
                    socio = session.query(Associados).filter_by(codigo_unico=cpf_busca, status="Ativo").first()
                    if socio:
                        st.session_state.socio_logado = {"nome": socio.nome, "cpf": socio.codigo_unico, "telefone": socio.telefone}
                        st.rerun()
                    else:
                        st.error("Sócio não encontrado ou inativo.")
        else:
            st.success(f"Logado: **{socio_info['nome']}**")
            if st.button("Sair / Trocar CPF"):
                st.session_state.socio_logado = None
                st.rerun()

        st.divider()
        with st.expander(l["BOTAO_ADESAO"]):
            with st.form("form_adesao", clear_on_submit=True):
                n = st.text_input("Nome Completo")
                t = st.text_input("Telefone")
                c = st.text_input("Seu CPF")
                if st.form_submit_button("Solicitar Adesão"):
                    sucesso_tel, tel_limpo = validar_telefone(t)
                    sucesso_cpf, cpf_limpo = validar_cpf(c)
                    if sucesso_cpf and sucesso_tel and n:
                        try:
                            session.add(Associados(nome=clean_text(n), codigo_unico=cpf_limpo, telefone=tel_limpo, status="Inativo"))
                            session.commit()
                            clear_cache()
                            st.success("Solicitação enviada!")
                        except:
                            session.rollback()
                            st.error("CPF já cadastrado.")

    # Chamada do fragmento isolado
    render_loja_dinamica(session)
    session.close()
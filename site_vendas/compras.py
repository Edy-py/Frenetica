# -*- coding: utf-8 -*-
from data_manager import clear_cache
import streamlit as st
import pandas as pd
from database import get_session, Estoque, Vendas, Associados
from utils import format_currency, clean_text, validar_telefone, validar_cpf, get_base64_image
import datetime
import os
import strings_config as s
from strings_config import VENDAS as v 
from strings_config import LOJA as l

def render_venda_sucesso():
    """Exibe instruções de pagamento para venda de balcão com PIX destacado."""
    if "ultimo_pedido" in st.session_state:
        pedido = st.session_state.ultimo_pedido
    elif "ultimo_pedido_balcao" in st.session_state:
        pedido = st.session_state.ultimo_pedido_balcao
    else:
        return

    st.balloons()
    
    # CSS para destacar a área do PIX
    st.markdown(f"""
        <style>
            .pix-box {{
                background-color: #f0f2f6;
                padding: 20px;
                border-radius: 15px;
                border: 2px solid {s.COR_AMARELO_MARCA};
                text-align: center;
                margin: 15px 0;
            }}
            .pix-key {{
                font-family: 'Courier New', Courier, monospace;
                font-size: 1.5rem;
                font-weight: bold;
                color: {s.COR_AZUL_MARCA};
                background: white;
                padding: 10px;
                border-radius: 5px;
                display: block;
                margin-top: 10px;
                border: 1px dashed #ccc;
            }}
        </style>
    """, unsafe_allow_html=True)
    
    with st.container(border=True):
        st.success(f"### 🎉 Pedido de {pedido['cliente']} registrado!")
        st.write(f"**Valor total:** {format_currency(pedido['total'])}")
        
        if pedido['metodo'] == "Pix":
            st.markdown(f"""
                <div class="pix-box">
                    <strong>⚡ CHAVE PIX PARA PAGAMENTO</strong>
                    <span class="pix-key">{s.FINANCEIRO_PIX.replace("## ", "")}</span>
                </div>
            """, unsafe_allow_html=True)
            st.link_button("📲 Enviar Comprovante (WhatsApp Alfredo)", s.LINK_WHATSAPP_FIN, use_container_width=True, type="primary")
        
        elif "Cartão" in pedido['metodo']:
            st.warning(s.MSG_PAGAMENTO_CARTAO.format(valor=format_currency(pedido['total'])))
            st.link_button("💳 Solicitar Link de Pagamento", s.LINK_WHATSAPP_FIN, use_container_width=True, type="primary")
            
        if st.button("Nova Compra / Voltar", use_container_width=True):
            if "ultimo_pedido" in st.session_state: del st.session_state.ultimo_pedido
            if "ultimo_pedido_balcao" in st.session_state: del st.session_state.ultimo_pedido_balcao
            st.rerun()

@st.fragment
def render_loja_dinamica(session):
    """Fragmento que isola a vitrine e o carrinho para evitar recarregamento total."""
    desconto_ativo = st.session_state.get("socio_logado") is not None
    
    # --- CSS PREMIUM PARA VITRINE ---
    st.markdown(f"""
        <style>
            .card-produto {{
                background: white;
                border-radius: 22px;
                padding: 25px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.05);
                transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
                border: 1px solid rgba(0,0,0,0.05);
                display: flex;
                flex-direction: column;
                align-items: center;
                height: 450px; /* Altura fixa para alinhar a grade */
                text-align: center;
                overflow: hidden;
                margin-bottom: 20px;
                position: relative;
            }}

            .card-produto:hover {{
                transform: translateY(-10px);
                box-shadow: 0 25px 50px rgba(0,0,0,0.12);
                border-color: {s.COR_AMARELO_MARCA};
                height: auto; 
                min-height: 450px;
                z-index: 10;
            }}

            .img-produto {{
                width: 100%;
                height: 200px;
                object-fit: contain;
                border-radius: 15px;
                margin-bottom: 15px;
                background: #f8fafc;
            }}

            .titulo-produto {{
                font-size: 1.3rem !important;
                color: #1e293b !important;
                font-weight: 800 !important;
                margin: 10px 0 !important;
                height: 50px;
                display: flex;
                align-items: center;
            }}

            .preco-produto {{
                color: {s.COR_AZUL_MARCA};
                font-size: 1.6rem;
                font-weight: 800;
                margin: 5px 0;
            }}

            .desc-produto {{
                font-size: 0.95rem;
                color: #64748b;
                display: -webkit-box;
                -webkit-line-clamp: 2;
                -webkit-box-orient: vertical;
                overflow: hidden;
                transition: all 0.3s ease;
            }}

            .card-produto:hover .desc-produto {{
                -webkit-line-clamp: unset;
                display: block;
            }}
        </style>
    """, unsafe_allow_html=True)

    # --- VITRINE ---
    prods = session.query(Estoque).filter(Estoque.quantidade > 0).all()
    if prods:
        cols = st.columns(3)
        for idx, p in enumerate(prods):
            with cols[idx % 3]:
                path = f"imagens/produtos/{p.foto_url}"
                b64 = get_base64_image(path) if p.foto_url and os.path.exists(path) else None
                img_html = f'<img src="data:image/png;base64,{b64}" class="img-produto">' if b64 else '<div class="img-produto" style="display:flex;align-items:center;justify-content:center;">🖼️ Sem Foto</div>'
                
                v_unitario = p.preco_venda_un * (1 - s.DESCONTO_VALOR) if desconto_ativo else p.preco_venda_un
                
                # Render do Card HTML
                st.markdown(f"""
                    <div class="card-produto">
                        {img_html}
                        <div class="titulo-produto">{p.nome_produto}</div>
                        <div class="preco-produto">{format_currency(v_unitario)}</div>
                        <p class="desc-produto">Produto oficial da {s.ATLETICA_NOME}. Alta qualidade para o associado frenético!</p>
                    </div>
                """, unsafe_allow_html=True)
                
                # Botão integrado
                def add_ao_carrinho(prod=p, preco=v_unitario):
                    st.session_state.carrinho_cliente.append({
                        "id_db": prod.id, "nome": prod.nome_produto, "preco": preco,
                        "personalizavel": prod.personalizavel, "personalizacao": ""
                    })
                    st.toast(f"✅ {prod.nome_produto} adicionado!")

                st.button(f"🛒 Adicionar", key=f"btn_{p.id}", use_container_width=True, on_click=add_ao_carrinho)

    # --- CARRINHO E FINALIZAÇÃO ---
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
            st.markdown("### 💳 Detalhes do Pedido")
            c1, c2 = st.columns(2)
            metodo_sel = c1.selectbox(v["LABEL_PAGAMENTO"], v["OPCOES_PAGAMENTO"], key="compra_metodo_pag")
            tamanho_sel = c2.selectbox(v["LABEL_TAMANHO"], v["OPCOES_TAMANHO"], key="compra_tamanho")
            
            socio_info = st.session_state.get("socio_logado")
            
            if not socio_info:
                nome_cli_input = st.text_input(v["LABEL_NOME_CLIENTE"], placeholder="Nome para o pedido")
                tel_cli_input = st.text_input(v["LABEL_TEL_CLIENTE"], placeholder=s.PLACEHOLDER_TELEFONE)
            else:
                nome_cli_input = socio_info['nome']
                tel_cli_input = socio_info['telefone']

            perso = None
            if any(item['personalizavel'] for item in st.session_state.carrinho_cliente):
                perso = st.text_input("Personalização", placeholder="Nome - Número")

            btn_col1, btn_col2 = st.columns(2)
            finalizar = btn_col1.form_submit_button("✅ Finalizar e Pagar", use_container_width=True, type="primary")
            limpar = btn_col2.form_submit_button("🗑️ Limpar Carrinho", use_container_width=True)

            if finalizar:
                if not socio_info and (not nome_cli_input or not tel_cli_input):
                    st.error("Por favor, preencha o seu nome e telefone.")
                else:
                    try:
                        nome_final = clean_text(nome_cli_input)
                        tel_final = tel_cli_input
                        
                        if not socio_info:
                            sucesso_tel, tel_final = validar_telefone(tel_cli_input)
                            if not sucesso_tel:
                                st.error(s.MSG_ERRO_TELEFONE)
                                st.stop()

                        for item in st.session_state.carrinho_cliente:
                            prod_db = session.query(Estoque).filter_by(id=item['id_db']).first()
                            custo_un = float(prod_db.preco_custo or 0)
                            
                            session.add(Vendas(
                                nome_prod=item['nome'], qtd_vendida=1, preco_venda_total=item['preco'],
                                data=datetime.datetime.now(), lucro=item['preco'] - custo_un,
                                nome_cliente=nome_final, telefone=tel_final, tamanho=tamanho_sel,
                                personalizacao=perso, metodo_pagamento=metodo_sel,
                                is_associado=desconto_ativo
                            ))
                            if prod_db: prod_db.quantidade -= 1

                        session.commit()
                        clear_cache()
                        
                        st.session_state.ultimo_pedido = {
                            "total": total_final,
                            "metodo": metodo_sel,
                            "cliente": nome_final
                        }
                        st.session_state.carrinho_cliente = []
                        st.rerun()
                    except Exception as e:
                        session.rollback()
                        st.error(f"Erro: {e}")

            if limpar:
                st.session_state.carrinho_cliente = []
                st.rerun()

def render_compras():
    session = get_session()
    
    if 'carrinho_cliente' not in st.session_state:
        st.session_state.carrinho_cliente = []

    st.markdown(f'<h2 style="text-align: center; color: {s.COR_AZUL_MARCA};">{l["TITULO"]}</h2>', unsafe_allow_html=True)

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
                        st.session_state.socio_logado = {
                            "nome": socio.nome, "cpf": socio.codigo_unico, "telefone": socio.telefone
                        }
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

    if "ultimo_pedido" in st.session_state:
        render_venda_sucesso()
    else:
        render_loja_dinamica(session)
        
    session.close()
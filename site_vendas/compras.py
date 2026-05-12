# -*- coding: utf-8 -*-
import streamlit as st
import os
from database import get_session, Estoque, Vendas, Associados
from utils import format_currency, clean_text, validar_cpf, validar_telefone
import strings_config as s
from strings_config import LOJA as l # Atalho para escrever menos
from strings_config import VENDAS as v # Atalho para escrever menos
import pandas as pd
import datetime


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

    # --- SEÇÃO 2: CARRINHO E FINALIZAÇÃO (SINCRONIZADO COM VENDAS.PY) ---
    if st.session_state.carrinho_cliente:
        st.divider()
        st.subheader("🛒 Seu Carrinho")
        
        # Criar DataFrame para exibição limpa
        df_cart = pd.DataFrame(st.session_state.carrinho_cliente)
        
        # Renomear colunas para o usuário
        df_display = df_cart[['nome', 'personalizacao']].copy()
        df_display.columns = ['Produto', 'Personalização']
        
        st.table(df_display)
        
        # Cálculo do Total Bruto
        total_bruto = sum(item['preco'] for item in st.session_state.carrinho_cliente)
        
        # Lógica de Desconto (Persistente da Sidebar)
        desconto = 0.0
        if st.session_state.get("socio_logado"):
            desconto = total_bruto * s.DESCONTO_VALOR
            st.success(f"✅ Desconto de Sócio aplicado: {format_currency(desconto)}")

        total_final = total_bruto - desconto
        st.markdown(f"### Total a Pagar: :green[{format_currency(total_final)}]")

        # Informações de Pagamento
        metodo_sel, tamanho_sel = st.columns(2)
        with metodo_sel:
            metodo_sel = st.selectbox(v["LABEL_PAGAMENTO"], v["OPCOES_PAGAMENTO"], key="compra_metodo_pag")

        with tamanho_sel:
            tamanho_sel = st.selectbox(v["LABEL_TAMANHO"], v["OPCOES_TAMANHO"], key="compra_tamanho")
        
        if any(item['personalizavel'] for item in st.session_state.carrinho_cliente):
            personalizacao = st.text_input("Personalização", placeholder="Digite o nome e número neste modelo <nome-número>", key="compra_personalizacao")

        col_btn1, col_btn2 = st.columns(2)
        
        if col_btn1.button("✅ Finalizar Pedido", use_container_width=True, type="primary"):
            try:
                # Dados do cliente (se logado como sócio ou anônimo)
                info_socio = st.session_state.get("socio_logado")
                nome_cli = info_socio['nome'] if info_socio else "CLIENTE LOJA"
                tel_cli = info_socio['telefone'] if info_socio else ""
                
                qtd_itens = len(st.session_state.carrinho_cliente)
                desc_por_item = desconto / qtd_itens if qtd_itens > 0 else 0.0

                for item in st.session_state.carrinho_cliente:
                    # Busca produto no DB para custos e estoque
                    prod_db = session.query(Estoque).filter_by(id=item['id_db']).first()
                    custo_un = float(prod_db.preco_custo) if prod_db and prod_db.preco_custo else 0.0
                    
                    # Cálculo financeiro
                    valor_venda_item = float(item['preco'] - desc_por_item)
                    lucro_item = valor_venda_item - custo_un
                    
                    # Registra a Venda
                    nova_venda = Vendas(
                        nome_prod=item['nome'],
                        qtd_vendida=1,
                        preco_venda_total=valor_venda_item,
                        data=datetime.datetime.now(),
                        lucro=lucro_item,
                        nome_cliente=nome_cli,
                        telefone=tel_cli,
                        tamanho=tamanho_sel,
                        personalizacao=personalizacao if personalizacao else None,
                        metodo_pagamento=metodo_sel,
                        status_pagamento="Pagamento Pendente",
                        is_associado=(desconto > 0)
                    )
                    session.add(nova_venda)
                    
                    # Baixa no Estoque
                    if prod_db and prod_db.quantidade > 0:
                        prod_db.quantidade -= 1

                session.commit()
                st.balloons()
                st.success("Pedido realizado com sucesso!")
                
                # Instruções de PIX se necessário
                if metodo_sel == "Pix":
                    st.info(s.MSG_PAGAMENTO_PIX)
                    st.link_button("📤 Enviar Comprovante", s.LINK_WHATSAPP_FIN)
                
                # Limpa carrinho e recarrega
                st.session_state.carrinho_cliente = []
                st.rerun()

            except Exception as e:
                session.rollback()
                st.error(f"Erro ao processar compra: {e}")

        if col_btn2.button("🗑️ Esvaziar Carrinho", use_container_width=True):
            st.session_state.carrinho_cliente = []
            st.rerun()

    session.close()
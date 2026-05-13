# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from database import get_session, Estoque
from utils import clean_text, format_currency, salvar_imagem
from data_manager import get_estoque_df, clear_cache
import strings_config as s
from strings_config import ESTOQUE as es

def render_estoque(readonly=True):
    st.header(es["TITULO"])
    session = get_session()
    
    # 1. Menu de Operações
    tipo_operacao = st.radio(es["OPERACAO_LABEL"], es["OPERACAO_OPCOES"], horizontal=True) if not readonly else es["OPERACAO_OPCOES"][0]

    st.divider()

    # --- LÓGICA 1: VISUALIZAR / CADASTRAR NOVO PRODUTO ---
    if tipo_operacao == es["OPERACAO_OPCOES"][0] and not readonly:
        with st.expander(es["CAD_PROD_EXPANDER"], expanded=False):
            with st.form("form_cadastro_prod", clear_on_submit=True):
                nome = st.text_input(es["LABEL_NOME"], placeholder=s.PLACEHOLDER_PRODUTO)
                c1, c2, c3 = st.columns(3)
                qtd = c1.number_input(es["LABEL_QTD"], min_value=0)
                p_custo = c2.number_input(es["LABEL_CUSTO"], min_value=0.0, format="%.2f")
                p_venda = c3.number_input(es["LABEL_VENDA"], min_value=0.0, format="%.2f")
                
                p_opcao = st.selectbox(es["LABEL_PERGUNTA_PERS"], es["OPCOES_SIM_NAO"])
                foto_arq = st.file_uploader(es["LABEL_FOTO"], type=['png', 'jpg', 'jpeg'])
                
                if st.form_submit_button(es["BOTAO_SALVAR"], use_container_width=True):
                    nome_up = clean_text(nome)
                    if nome_up:
                        if session.query(Estoque).filter_by(nome_produto=nome_up).first():
                            st.warning(es["MSG_PRODUTO_EXISTE"])
                        else:
                            try:
                                novo = Estoque(
                                    nome_produto=nome_up, quantidade=qtd, 
                                    preco_custo=p_custo, preco_venda_un=p_venda,
                                    personalizavel=(p_opcao == "Sim"), 
                                    foto_url=salvar_imagem(foto_arq, "produtos") if foto_arq else None
                                )
                                session.add(novo)
                                session.commit()
                                clear_cache()
                                st.success(f"Sucesso: {nome_up} cadastrado!")
                            except Exception as e:
                                session.rollback()
                                st.error(f"Erro: {e}")
                    else: 
                        st.error(es["MSG_NOME_OBRIGATORIO"])

    # --- LÓGICA 2: ATUALIZAR POR ID ---
    elif tipo_operacao == es["OPERACAO_OPCOES"][1] and not readonly:
        st.subheader("Editar Produto")
        id_editar = st.number_input(es["LABEL_ID_EDITAR"], min_value=0, step=1)
        
        if id_editar > 0:
            item = session.query(Estoque).filter_by(id=id_editar).first()
            if item:
                st.info(f"Editando: {item.nome_produto}")
                with st.form(key=f"form_edit_{id_editar}"):
                    edit_nome = st.text_input(es["LABEL_NOVO_NOME"], value=item.nome_produto)
                    ce1, ce2, ce3 = st.columns(3)
                    edit_qtd = ce1.number_input(es["LABEL_NOVA_QTD"], value=item.quantidade)
                    edit_pc = ce2.number_input(es["LABEL_NOVO_CUSTO"], value=item.preco_custo)
                    edit_pv = ce3.number_input(es["LABEL_NOVO_VENDA"], value=item.preco_venda_un)
                    edit_foto = st.file_uploader(es["LABEL_TROCAR_FOTO"], type=['png', 'jpg', 'jpeg'])

                    if st.form_submit_button(es["BOTAO_CONFIRMAR"], use_container_width=True):
                        try:
                            item.nome_produto = clean_text(edit_nome)
                            item.quantidade = edit_qtd
                            item.preco_custo = edit_pc
                            item.preco_venda_un = edit_pv
                            if edit_foto: 
                                item.foto_url = salvar_imagem(edit_foto, "produtos")
                            session.commit()
                            st.success(es["MSG_EDIT_SUCESSO"])
                            st.rerun() # Necessário para atualizar a tabela visual abaixo
                        except Exception as e:
                            session.rollback()
                            st.error(f"Erro: {e}")
            else: 
                st.warning("ID não encontrado")

    # --- LÓGICA 3: GERENCIAR KITS ---
    elif tipo_operacao == es["OPERACAO_OPCOES"][2] and not readonly:
        st.subheader(es["CAD_KIT_EXPANDER"])
        with st.form("form_cad_kit", clear_on_submit=True):
            nome_kit = st.text_input(es["LABEL_NOME_KIT"], placeholder=es["PLACEHOLDER_KIT"])
            
            # Busca produtos para o multiselect
            produtos_disponiveis = session.query(Estoque).all()
            opcoes_dict = {p.nome_produto: p for p in produtos_disponiveis}
            
            selecionados = st.multiselect("Selecione os produtos", options=list(opcoes_dict.keys()))
            
            val_kit = st.number_input(es["LABEL_VALOR_KIT"], min_value=0.0, format="%.2f")
            foto_kit = st.file_uploader("Imagem do Kit", type=['png', 'jpg', 'jpeg'])

            if st.form_submit_button(es["BOTAO_SALVAR_KIT"], use_container_width=True):
                nome_k_up = clean_text(nome_kit)
                if nome_k_up and selecionados:
                    custo_total = sum(opcoes_dict[it].preco_custo for it in selecionados)
                    nome_img_k = salvar_imagem(foto_kit, "produtos")
                    
                    novo_kit = Estoque(
                        nome_produto=f"[KIT] {nome_k_up}",
                        quantidade=999, # Kits dependem dos itens individuais
                        preco_custo=custo_total,
                        preco_venda_un=val_kit,
                        personalizavel=any(opcoes_dict[it].personalizavel for it in selecionados),
                        foto_url=nome_img_k
                    )
                    session.add(novo_kit)
                    session.commit()
                    st.success(es["MSG_KIT_SUCESSO"].format(nome=nome_k_up))
                    st.rerun()
                else:
                    st.error(es["MSG_ERRO_ITENS_KIT"])

    st.divider()

    # --- TABELA DE VISUALIZAÇÃO ---
    st.subheader(es["SUB_ESTOQUE_DISPONIVEL"])
    dados = session.query(Estoque).order_by(Estoque.id.desc()).all()
    
    if dados:
        # Usa os nomes das colunas definidos no dicionário ESTOQUE
        df = pd.DataFrame([{
            es["COLUNAS"][0]: i.id,
            es["COLUNAS"][1]: i.nome_produto,
            es["COLUNAS"][2]: i.quantidade,
            es["COLUNAS"][3]: format_currency(i.preco_venda_un),
            es["COLUNAS"][4]: "✅" if i.personalizavel else "❌"
        } for i in dados])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info(s.MSG_ESTOQUE_VAZIO)
    
    session.close()
# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from database import get_session, Estoque
from utils import clean_text, format_currency, salvar_imagem
from data_manager import clear_cache
import strings_config as s
from strings_config import ESTOQUE as es

def render_estoque(readonly=True):
    st.header(es["TITULO"])
    session = get_session()
    
    # Menu de Operações - Adicionado "Excluir Item" às opções
    opcoes_menu = list(es["OPERACAO_OPCOES"])
    if "Excluir Item" not in opcoes_menu:
        opcoes_menu.append("Excluir Item")
    
    tipo_operacao = st.radio(es["OPERACAO_LABEL"], opcoes_menu, horizontal=True) if not readonly else es["OPERACAO_OPCOES"][0]

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
                            st.rerun()
                        except Exception as e:
                            session.rollback()
                            st.error(f"Erro: {e}")
                    else: 
                        st.error(es["MSG_NOME_OBRIGATORIO"])

    # --- LÓGICA 2: ATUALIZAR POR ID (EDIÇÃO) ---
    elif tipo_operacao == es["OPERACAO_OPCOES"][1] and not readonly:
        st.subheader("Editar Produto ou Kit")
        id_editar = st.number_input(es["LABEL_ID_EDITAR"], min_value=0, step=1)
        
        if id_editar > 0:
            item = session.query(Estoque).filter_by(id=id_editar).first()
            if item:
                st.info(f"Editando: {item.nome_produto}")
                with st.form(key=f"form_edit_{id_editar}"):
                    edit_nome = st.text_input(es["LABEL_NOVO_NOME"], value=item.nome_produto)
                    ce1, ce2, ce3 = st.columns(3)
                    
                    # Se for Kit, a quantidade é automática baseada nos componentes
                    is_kit = "[KIT]" in item.nome_produto
                    edit_qtd = ce1.number_input(es["LABEL_NOVA_QTD"], value=item.quantidade, disabled=is_kit)
                    
                    edit_pc = ce2.number_input(es["LABEL_NOVO_CUSTO"], value=item.preco_custo)
                    edit_pv = ce3.number_input(es["LABEL_NOVO_VENDA"], value=item.preco_venda_un)
                    edit_foto = st.file_uploader(es["LABEL_TROCAR_FOTO"], type=['png', 'jpg', 'jpeg'])

                    if st.form_submit_button(es["BOTAO_CONFIRMAR"], use_container_width=True):
                        try:
                            item.nome_produto = clean_text(edit_nome)
                            if not is_kit:
                                item.quantidade = edit_qtd
                            item.preco_custo = edit_pc
                            item.preco_venda_un = edit_pv
                            if edit_foto: 
                                item.foto_url = salvar_imagem(edit_foto, "produtos")
                            session.commit()
                            st.success(es["MSG_EDIT_SUCESSO"])
                            st.rerun()
                        except Exception as e:
                            session.rollback()
                            st.error(f"Erro: {e}")
            else: 
                st.warning("ID não encontrado")

    # --- LÓGICA 3: GERENCIAR KITS (CRIAÇÃO E EDIÇÃO DINÂMICA) ---
    elif tipo_operacao == es["OPERACAO_OPCOES"][2] and not readonly:
        st.subheader(es["CAD_KIT_EXPANDER"])
        
        # Busca apenas produtos que NÃO são kits para compor os novos kits
        produtos_disponiveis = session.query(Estoque).filter(~Estoque.nome_produto.contains("[KIT]")).all()
        opcoes_dict = {p.nome_produto: p for p in produtos_disponiveis}
        
        with st.form("form_cad_kit", clear_on_submit=True):
            nome_kit = st.text_input(es["LABEL_NOME_KIT"], placeholder=es["PLACEHOLDER_KIT"])
            selecionados = st.multiselect("Selecione os produtos que compõem este Kit", options=list(opcoes_dict.keys()))
            val_kit = st.number_input(es["LABEL_VALOR_KIT"], min_value=0.0, format="%.2f")
            foto_kit = st.file_uploader("Imagem do Kit", type=['png', 'jpg', 'jpeg'])

            if st.form_submit_button(es["BOTAO_SALVAR_KIT"], use_container_width=True):
                nome_k_up = clean_text(nome_kit)
                if nome_k_up and selecionados:
                    # Cálculo automático de custo e estoque (menor estoque entre os componentes)
                    custo_total = sum(opcoes_dict[it].preco_custo for it in selecionados)
                    estoque_possivel = min(opcoes_dict[it].quantidade for it in selecionados)
                    
                    nome_final = f"[KIT] {nome_k_up}"
                    kit_existente = session.query(Estoque).filter_by(nome_produto=nome_final).first()
                    
                    if kit_existente:
                        kit_existente.preco_venda_un = val_kit
                        kit_existente.preco_custo = custo_total
                        kit_existente.quantidade = estoque_possivel
                    else:
                        novo_kit = Estoque(
                            nome_produto=nome_final,
                            quantidade=estoque_possivel,
                            preco_custo=custo_total,
                            preco_venda_un=val_kit,
                            personalizavel=any(opcoes_dict[it].personalizavel for it in selecionados),
                            foto_url=salvar_imagem(foto_kit, "produtos") if foto_kit else None
                        )
                        session.add(novo_kit)
                    
                    session.commit()
                    st.success(es["MSG_KIT_SUCESSO"].format(nome=nome_k_up))
                    st.rerun()
                else:
                    st.error("Selecione os produtos e dê um nome ao Kit.")

    # --- LÓGICA 4: EXCLUIR ITEM ---
    elif tipo_operacao == "Excluir Item" and not readonly:
        st.subheader("🗑️ Remover Produto ou Kit")
        id_del = st.number_input("Digite o ID do item para excluir", min_value=0, step=1)
        if id_del > 0:
            item_del = session.query(Estoque).filter_by(id=id_del).first()
            if item_del:
                st.warning(f"Atenção: Você está prestes a excluir permanentemente: **{item_del.nome_produto}**")
                if st.button("Confirmar Exclusão", type="primary", use_container_width=True):
                    try:
                        session.delete(item_del)
                        session.commit()
                        clear_cache()
                        st.success("Item removido com sucesso!")
                        st.rerun()
                    except Exception as e:
                        session.rollback()
                        
            else:
                st.warning("ID não encontrado.")

    st.divider()

    # --- TABELA DE VISUALIZAÇÃO COM ATUALIZAÇÃO AUTOMÁTICA DE KITS ---
    st.subheader(es["SUB_ESTOQUE_DISPONIVEL"])
    
    # 1. Busca todos os itens para processamento
    todos_itens = session.query(Estoque).order_by(Estoque.id.desc()).all()
    
    # 2. Mapeia estoque de produtos reais para calcular o gargalo dos kits
    estoque_real = {i.nome_produto: i.quantidade for i in todos_itens if "[KIT]" not in i.nome_produto}

    for item in todos_itens:
        if "[KIT]" in item.nome_produto:
            # Tenta encontrar os componentes do kit dentro do nome para atualizar a quantidade
            componentes_encontrados = []
            for nome_prod_base in estoque_real.keys():
                if nome_prod_base in item.nome_produto:
                    componentes_encontrados.append(estoque_real[nome_prod_base])
            
            if componentes_encontrados:
                item.quantidade = min(componentes_encontrados)
    
    # Salva as quantidades atualizadas dos kits antes da exibição
    session.commit()

    if todos_itens:
        df = pd.DataFrame([{
            es["COLUNAS"][0]: i.id,
            es["COLUNAS"][1]: i.nome_produto,
            es["COLUNAS"][2]: i.quantidade,
            es["COLUNAS"][3]: format_currency(i.preco_venda_un),
            es["COLUNAS"][4]: "✅" if i.personalizavel else "❌"
        } for i in todos_itens])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info(s.MSG_ESTOQUE_VAZIO)
    
    session.close()

# """
# Sistema de Gestão e Vendas - Frenética (A.A.A.T.J.B.)
# Desenvolvido por: Edílson Alves da Silva (Edy-py)
# Contato: edilsonalvesprofissional@gmail.com
# © 2026 - Todos os direitos reservados.
# """
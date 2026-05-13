# -*- coding: utf-8 -*-
from data_manager import clear_cache
import streamlit as st
import pandas as pd
from database import get_session, Estoque, Vendas, Associados
from utils import format_currency, clean_text, format_telefone, validar_telefone
import datetime
import strings_config as s
from strings_config import VENDAS as v 

@st.fragment
def render_carrinho_venda(session, metodo_pagamento_opcoes):
    """Fragmento isolado para gerir o carrinho de balcão sem recarregar a página toda."""
    if st.session_state.carrinho:
        st.subheader("🛒 Carrinho")
        df_cart = pd.DataFrame(st.session_state.carrinho)
        st.table(df_cart[['produto', 'qtd', 'tamanho', 'subtotal']])
        
        total_venda = float(df_cart['subtotal'].sum())
        
        c1, c2 = st.columns(2)
        cod_assoc = c1.text_input(v["LABEL_COD_DESCONTO"], key="venda_cupom")
        metodo_sel = c2.selectbox(v["LABEL_PAGAMENTO"], metodo_pagamento_opcoes, key="venda_metodo_pag")
        
        desconto = 0.0
        if cod_assoc:
            socio = session.query(Associados).filter_by(codigo_unico=cod_assoc, status="Ativo").first()
            if socio:
                desconto = float(total_venda * s.DESCONTO_VALOR)
                st.success(v["MSG_DESCONTO_OK"].format(nome=socio.nome))
            else: 
                st.error(v["MSG_DESCONTO_ERRO"])

        valor_final_venda = float(total_venda - desconto)
        st.markdown(f"### Total: :green[{format_currency(valor_final_venda)}]")

        btn_c1, btn_c2 = st.columns(2)
        
        if btn_c1.button(v["BOTAO_CONFIRMAR"], use_container_width=True, type="primary"):
            try:
                qtd_total_itens = len(st.session_state.carrinho)
                desc_por_item = float(desconto / qtd_total_itens) if qtd_total_itens > 0 else 0.0

                for item in st.session_state.carrinho:
                    prod_db = session.query(Estoque).filter_by(nome_produto=item['produto']).first()
                    custo_un = float(prod_db.preco_custo or 0)
                    v_venda_item = float(item['subtotal'] - desc_por_item)
                    lucro_calc = v_venda_item - (custo_un * item['qtd'])
                    
                    session.add(Vendas(
                        nome_prod=item['produto'], qtd_vendida=item['qtd'],
                        preco_venda_total=v_venda_item, data=datetime.datetime.now(), 
                        lucro=lucro_calc, nome_cliente=item['cliente'], 
                        telefone=item['telefone'], tamanho=item['tamanho'], 
                        personalizacao=item['personalizacao'], metodo_pagamento=metodo_sel,
                        is_associado=(desconto > 0)
                    ))
                    if prod_db: 
                        prod_db.quantidade -= item['qtd']
                
                session.commit()
                clear_cache()
                st.success(v["MSG_SUCESSO"])
                if metodo_sel == "Pix": 
                    st.info(s.MSG_PAGAMENTO_PIX)
                
                st.session_state.carrinho = []
                st.rerun() 
            except Exception as e:
                session.rollback()
                st.error(f"Erro ao salvar: {e}")

        def limpar_carrinho_callback():
            st.session_state.carrinho = []

        btn_c2.button(v["BOTAO_LIMPAR_CARRINHO"], use_container_width=True, on_click=limpar_carrinho_callback)

def render_vendas(can_edit_status=False):
    st.header(v["TITULO"])
    session = get_session()

    if 'carrinho' not in st.session_state:
        st.session_state.carrinho = []

    # --- SEÇÃO 1: REGISTRO DE VENDA (BALCÃO) ---
    if st.session_state.role in ["admin", "vendedor"]:
        with st.expander(v["EXPANDER_NOVA"], expanded=False):
            produtos_db = session.query(Estoque).all()
            dict_produtos = {p.nome_produto: p for p in produtos_db}
            
            if dict_produtos:
                with st.form("form_venda_balcao", clear_on_submit=True):
                    c1, c2 = st.columns(2)
                    nome_c = c1.text_input(v["LABEL_CLIENTE"])
                    tel_c = c2.text_input(s.LABEL_TEL_CLIENTE_VENDA, placeholder=s.PLACEHOLDER_TELEFONE)

                    st.divider()
                    
                    col_p, col_q, col_v = st.columns([2, 1, 1])
                    prod_sel = col_p.selectbox(v["LABEL_PROD"], options=sorted(dict_produtos.keys()))
                    
                    obj_p = dict_produtos[prod_sel] if prod_sel else None
                    qtd = col_q.number_input(f"Quantidade", min_value=1, value=1)
                    tipo_p = st.radio(v["LABEL_TIPO_PRECO"], v["OPCOES_PRECO"], horizontal=True)
                    
                    tamanho_sel = st.selectbox(v["LABEL_TAMANHO"], v["OPCOES_TAMANHO"])
                    
                    pers_texto = ""
                    if obj_p and obj_p.personalizavel:
                        pers_texto = st.text_input("Personalização", placeholder=s.PLACEHOLDER_PERSONALIZACAO)

                    if st.form_submit_button(v["BOTAO_ADD"], use_container_width=True, type="primary"):
                        sucesso_tel, tel_limpo = validar_telefone(tel_c)
                        
                        if not sucesso_tel: st.error(s.MSG_ERRO_TELEFONE)
                        elif not nome_c: st.error(s.MSG_ERRO_CAMPOS)
                        elif obj_p and qtd > obj_p.quantidade: st.error(f"Estoque insuficiente ({obj_p.quantidade})")
                        else:
                            preco_base = obj_p.preco_kit if tipo_p == "Kit" and obj_p.preco_kit else obj_p.preco_venda_un
                            st.session_state.carrinho.append({
                                "produto": prod_sel, 
                                "qtd": int(qtd),
                                "preco": float(preco_base),
                                "subtotal": float(round((qtd * preco_base), 2)), 
                                "tamanho": tamanho_sel, 
                                "personalizacao": pers_texto,
                                "cliente": clean_text(nome_c), 
                                "telefone": tel_limpo 
                            })
                            st.rerun() 
            else:
                st.warning("⚠️ Nenhum produto no estoque.")

    # --- SEÇÃO 2: CARRINHO (FRAGMENTO) ---
    render_carrinho_venda(session, v["OPCOES_PAGAMENTO"])

    st.divider()

    # --- SEÇÃO 3: HISTÓRICO E GESTÃO ---
    st.subheader(v["HISTORICO_SUB"])
    cf1, cf2 = st.columns(2)
    d_ini = cf1.date_input("Início", datetime.date.today() - datetime.timedelta(days=30))
    d_fim = cf2.date_input("Fim", datetime.date.today())

    vendas_db = session.query(Vendas).filter(Vendas.data.between(
        datetime.datetime.combine(d_ini, datetime.time.min),
        datetime.datetime.combine(d_fim, datetime.time.max)
    )).order_by(Vendas.id.desc()).all()
    
    if st.session_state.role in ["admin", "financeiro", "vendedor"] and vendas_db:
        df_vendas = pd.DataFrame([{
            "ID": vd.id, "Data": vd.data.strftime("%d/%m/%Y"), "Cliente": vd.nome_cliente,
            "Telefone": format_telefone(vd.telefone), "Produto": vd.nome_prod, 
            "Qtd": vd.qtd_vendida, "Total": format_currency(vd.preco_venda_total),
            "Pagamento": vd.metodo_pagamento, "Status": vd.status_pagamento
        } for vd in vendas_db])

        if can_edit_status:
            edited_df = st.data_editor(df_vendas, column_config={"Status": st.column_config.SelectboxColumn(options=v["STATUS_PAG"])},
                                     disabled=["ID", "Data", "Cliente", "Telefone", "Produto", "Qtd", "Total", "Pagamento"],
                                     hide_index=True, use_container_width=True, key="editor_status_vendas")
            
            if st.button("Salvar Alterações"):
                for _, row in edited_df.iterrows():
                    v_up = session.query(Vendas).filter_by(id=row['ID']).first()
                    if v_up: 
                        v_up.status_pagamento = row['Status']
                session.commit() 
                clear_cache()
                st.success("Atualizado!")
                st.rerun()
        else: 
            st.dataframe(df_vendas, use_container_width=True, hide_index=True)
        
        st.download_button("📥 Exportar CSV", df_vendas.to_csv(index=False).encode('utf-8-sig'), f"vendas_{d_ini}.csv", "text/csv")

    # --- SEÇÃO 4: ESTORNO (ADMIN) ---
    if st.session_state.role == "admin":
        with st.expander(v["EXPANDER_ESTORNO"]):
            with st.form("form_estorno", clear_on_submit=True):
                id_est = st.number_input("ID da venda", min_value=1, step=1)
                if st.form_submit_button("Confirmar Estorno"):
                    v_rem = session.query(Vendas).filter_by(id=id_est).first()
                    if v_rem:
                        p_est = session.query(Estoque).filter_by(nome_produto=v_rem.nome_prod).first()
                        if p_est: 
                            p_est.quantidade += v_rem.qtd_vendida
                        session.delete(v_rem)
                        session.commit()
                        clear_cache()
                        st.rerun()

    session.close()
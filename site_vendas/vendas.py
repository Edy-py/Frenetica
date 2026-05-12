# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from database import get_session, Estoque, Vendas, Associados
from utils import format_currency, clean_text, format_telefone, validar_telefone
import datetime
import strings_config as s
from strings_config import VENDAS as v 

def render_vendas(can_edit_status=False):
    st.header(v["TITULO"])
    session = get_session()

    # Inicializa o carrinho na sessão se não existir
    if 'carrinho' not in st.session_state:
        st.session_state.carrinho = []

    # --- SEÇÃO 1: REGISTRO DE VENDA (BALCÃO) ---
    if st.session_state.role in ["admin", "vendedor"]:
        with st.expander(v["EXPANDER_NOVA"], expanded=False):
            produtos_db = session.query(Estoque).all()
            dict_produtos = {p.nome_produto: p for p in produtos_db}
            
            if dict_produtos:
                c1, c2 = st.columns(2)
                nome_c = c1.text_input(v["LABEL_CLIENTE"], key="venda_nome_cliente")
                tel_c = c2.text_input(s.LABEL_TEL_CLIENTE_VENDA, placeholder=s.PLACEHOLDER_TELEFONE, key="venda_tel_cliente")

                st.divider()
                
                col_p, col_q, col_v = st.columns([2, 1, 1])
                prod_sel = col_p.selectbox(v["LABEL_PROD"], options=sorted(dict_produtos.keys()), key="venda_select_prod")
                
                if prod_sel:
                    obj_p = dict_produtos[prod_sel]
                    qtd = col_q.number_input(f"Qtd (Est: {obj_p.quantidade})", 
                                           min_value=1, 
                                           max_value=max(1, obj_p.quantidade),
                                           key="venda_qtd_prod")
                    
                    tipo_p = st.radio(v["LABEL_TIPO_PRECO"], v["OPCOES_PRECO"], horizontal=True, key="venda_tipo_preco")
                    
                    # Preço Unitário ou Kit
                    preco_base = obj_p.preco_venda_un if tipo_p == "Unitário" else (obj_p.preco_kit if obj_p.preco_kit else obj_p.preco_venda_un)
                    
                    tamanho_sel = st.selectbox(v["LABEL_TAMANHO"], v["OPCOES_TAMANHO"], key="venda_tamanho_prod")
                    
                    pers_texto = ""
                    if obj_p.personalizavel:
                        pers_texto = st.text_input("Personalização", placeholder=s.PLACEHOLDER_PERSONALIZACAO, key="venda_pers_prod")

                    if st.button(v["BOTAO_ADD"], use_container_width=True, type="primary", key="venda_btn_add"):
                        sucesso_tel, tel_limpo = validar_telefone(tel_c)
                        
                        if not sucesso_tel:
                            st.error(s.MSG_ERRO_TELEFONE)
                        elif not nome_c:
                            st.error(s.MSG_ERRO_CAMPOS)
                        else:
                            # Proteção de tipos: float e int nativos
                            preco_formatado = float(round((qtd * preco_base), 2))
                            st.session_state.carrinho.append({
                                "produto": prod_sel, 
                                "qtd": int(qtd),
                                "preco": float(preco_base),
                                "subtotal": preco_formatado, 
                                "tamanho": tamanho_sel, 
                                "personalizacao": pers_texto,
                                "cliente": clean_text(nome_c), 
                                "telefone": tel_limpo 
                            })
                            st.rerun()
            else:
                st.warning("⚠️ Nenhum produto no estoque.")

    # --- SEÇÃO 2: CARRINHO E FINALIZAÇÃO ---
    if st.session_state.carrinho:
        st.subheader("🛒 Carrinho")
        df_cart = pd.DataFrame(st.session_state.carrinho)
        st.table(df_cart[['produto', 'qtd', 'tamanho', 'subtotal']])
        
        total_venda = float(df_cart['subtotal'].sum())
        
        c1, c2 = st.columns(2)
        cod_assoc = c1.text_input(v["LABEL_COD_DESCONTO"], key="venda_cupom")
        metodo_sel = c2.selectbox(v["LABEL_PAGAMENTO"], v["OPCOES_PAGAMENTO"], key="venda_metodo_pag")
        
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
        
        if btn_c1.button(v["BOTAO_CONFIRMAR"], use_container_width=True, type="primary", key="venda_btn_confirmar"):
            try:
                qtd_itens = len(st.session_state.carrinho)
                desc_por_item = float(desconto / qtd_itens) if qtd_itens > 0 else 0.0

                for item in st.session_state.carrinho:
                    # BUSCA O CUSTO DIRETAMENTE DO BANCO (Evita o erro de lucro NULL)
                    prod_db = session.query(Estoque).filter_by(nome_produto=item['produto']).first()
                    custo_un = float(prod_db.preco_custo) if prod_db and prod_db.preco_custo else 0.0
                    
                    # CÁLCULO DO LUCRO ITEM POR ITEM
                    valor_venda_item = float(item['subtotal'] - desc_por_item)
                    custo_total_item = float(custo_un * item['qtd'])
                    lucro_calculado = float(valor_venda_item - custo_total_item)
                    print(f"DEBUG: Produto: {item['produto']}, Preço Base: {item['preco']}, Subtotal: {item['subtotal']}, Desconto por item: {desc_por_item}, Valor final item: {valor_venda_item}, Custo total item: {custo_total_item}, Lucro calculado: {lucro_calculado}")
                    
                    nova_venda = Vendas(
                        nome_prod=item['produto'], 
                        qtd_vendida=int(item['qtd']),
                        preco_venda_total=valor_venda_item,
                        data=datetime.datetime.now(), 
                        lucro=lucro_calculado, # Salvando valor real no banco
                        nome_cliente=item['cliente'], 
                        telefone=item['telefone'],
                        tamanho=item['tamanho'], 
                        personalizacao=item['personalizacao'],
                        metodo_pagamento=metodo_sel,
                        status_pagamento="Pagamento Pendente",
                        is_associado=(desconto > 0)
                    )
                    session.add(nova_venda)
                    print(f"DEBUG: lucro_calculado para {item['produto']}: {lucro_calculado}")
                    # pegar do bd e ver o lucro real que tá salvando, comparar com o calculado, ver se tem algo estranho acontecendo
                    lucro_real = session.query(Vendas.lucro).filter(Vendas.nome_prod == item['produto']).first()
                    print(f"DEBUG: lucro_real do banco para {item['produto']}: {lucro_real}")
                    
                    # Baixa no estoque
                    if prod_db: 
                        prod_db.quantidade -= int(item['qtd'])
                
                session.commit()
                st.success(v["MSG_SUCESSO"])
                st.session_state.carrinho = []  # Limpa o carrinho após a venda
                
                if metodo_sel == "Pix":
                    st.info(s.MSG_PAGAMENTO_PIX)
                    st.link_button("📤 Enviar comprovante", s.LINK_WHATSAPP_FIN)
                
                # st.session_state.carrinho = []
                st.rerun()
                
            except Exception as e:
                session.rollback()
                st.error(f"Erro ao salvar venda: {e}")

        if btn_c2.button(v["BOTAO_LIMPAR_CARRINHO"], use_container_width=True, key="venda_btn_limpar"):
            st.session_state.carrinho = []
            st.rerun()

    st.divider()

    # --- SEÇÃO 3: HISTÓRICO E GESTÃO ---
    st.subheader(v["HISTORICO_SUB"])
    cf1, cf2 = st.columns(2)
    d_ini = cf1.date_input("Data inicial", datetime.date.today() - datetime.timedelta(days=30), key="venda_data_ini")
    d_fim = cf2.date_input("Data final", datetime.date.today(), key="venda_data_fim")

    dt_ini = datetime.datetime.combine(d_ini, datetime.time.min)
    dt_fim = datetime.datetime.combine(d_fim, datetime.time.max)

    vendas_db = session.query(Vendas).filter(Vendas.data.between(dt_ini, dt_fim)).order_by(Vendas.id.desc()).all()
    
    if st.session_state.role in ["admin", "financeiro", "vendedor"]:
        if vendas_db:
            df_vendas = pd.DataFrame([{
                "ID": vd.id, 
                "Data": vd.data.strftime("%d/%m/%Y"), 
                "Cliente": vd.nome_cliente,
                "Telefone": format_telefone(vd.telefone),
                "Produto": vd.nome_prod, 
                "Qtd": vd.qtd_vendida, 
                "Total": format_currency(vd.preco_venda_total),
                "Pagamento": vd.metodo_pagamento,
                "Status": vd.status_pagamento, 
                "Personalização": vd.personalizacao
            } for vd in vendas_db])

            if can_edit_status:
                edited_df = st.data_editor(
                    df_vendas,
                    column_config={
                        "Status": st.column_config.SelectboxColumn(options=v["STATUS_PAG"])
                    },
                    disabled=["ID", "Data", "Cliente", "Telefone", "Produto", "Qtd", "Total", "Pagamento"],
                    hide_index=True, use_container_width=True,
                    key="editor_status_vendas"
                )
                if st.button("Salvar Alterações", key="btn_salvar_status_vendas"):
                    for _, row in edited_df.iterrows():
                        v_db = session.query(Vendas).filter_by(id=row['ID']).first()
                        if v_db: v_db.status_pagamento = row['Status']
                    session.commit()
                    st.success("Status atualizados!"); st.rerun()
            else:
                st.dataframe(df_vendas, use_container_width=True, hide_index=True)

            csv = df_vendas.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 Exportar CSV", csv, f"vendas_{d_ini}.csv", "text/csv", key="btn_export_csv")

        # --- SEÇÃO 4: ESTORNO ---
        if st.session_state.role == "admin":
            st.divider()
            with st.expander(v["EXPANDER_ESTORNO"]):
                id_est = st.number_input("ID da venda", min_value=1, step=1, key="input_estorno_id")
                if st.button("Confirmar Estorno", type="secondary", key="btn_confirmar_estorno"):
                    v_rem = session.query(Vendas).filter_by(id=id_est).first()
                    if v_rem:
                        p_est = session.query(Estoque).filter_by(nome_produto=v_rem.nome_prod).first()
                        if p_est: p_est.quantidade += v_rem.qtd_vendida
                        session.delete(v_rem)
                        session.commit()
                        st.success(f"Venda #{id_est} cancelada!"); st.rerun()
    else:
        st.info("Nenhuma venda no período.")

    session.close()
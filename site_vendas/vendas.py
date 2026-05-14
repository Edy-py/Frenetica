# -*- coding: utf-8 -*-
from data_manager import clear_cache
import streamlit as st
import pandas as pd
from database import get_session, Estoque, Vendas, Associados
from utils import format_currency, clean_text, format_telefone, validar_telefone
import datetime
import strings_config as s
from strings_config import VENDAS as v 

def render_venda_sucesso():
    """Exibe instruções de pagamento para venda de balcão com PIX destacado."""
    if "ultimo_pedido_balcao" not in st.session_state:
        return

    pedido = st.session_state.ultimo_pedido_balcao
    st.balloons()
    
    st.markdown(f"""
        <style>
            .pix-box {{
                background-color: #f0f2f6;
                padding: 20px;
                border-radius: 10px;
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
            }}
        </style>
    """, unsafe_allow_html=True)
    
    with st.container(border=True):
        st.success(f"### 🎉 Venda para {pedido['cliente']} registrada!")
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
            
        if st.button("Nova Venda de Balcão", use_container_width=True):
            del st.session_state.ultimo_pedido_balcao
            st.rerun()

@st.fragment
def render_historico_vendas(session, can_edit_status):
    """Fragmento para que a busca no histórico não recarregue a página toda."""
    st.subheader(v["HISTORICO_SUB"])
    cf1, cf2 = st.columns(2)
    d_ini = cf1.date_input("Início", datetime.date.today() - datetime.timedelta(days=30), key="busc_ini")
    d_fim = cf2.date_input("Fim", datetime.date.today(), key="busc_fim")

    vendas_db = session.query(Vendas).filter(Vendas.data.between(
        datetime.datetime.combine(d_ini, datetime.time.min),
        datetime.datetime.combine(d_fim, datetime.time.max)
    )).order_by(Vendas.id.desc()).all()
    
    if vendas_db:
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
                    if v_up: v_up.status_pagamento = row['Status']
                session.commit() 
                clear_cache()
                st.success("Atualizado!")
                st.rerun()
        else: 
            st.dataframe(df_vendas, use_container_width=True, hide_index=True)
        
        st.download_button("📥 Exportar CSV", df_vendas.to_csv(index=False).encode('utf-8-sig'), f"vendas_{d_ini}.csv", "text/csv")

@st.fragment
def render_carrinho_venda(session, metodo_pagamento_opcoes):
    """Fragmento isolado para gerir o carrinho sem travar o restante da página."""
    if not st.session_state.carrinho:
        return

    st.subheader("🛒 Carrinho Atual")
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

    valor_final_venda = float(total_venda - desconto)
    st.markdown(f"### Total: :green[{format_currency(valor_final_venda)}]")

    col_btn1, col_btn2 = st.columns(2)
    if col_btn1.button(v["BOTAO_CONFIRMAR"], use_container_width=True, type="primary"):
        try:
            qtd_items = len(st.session_state.carrinho)
            desc_item = float(desconto / qtd_items) if qtd_items > 0 else 0.0

            for item in st.session_state.carrinho:
                prod_db = session.query(Estoque).filter_by(nome_produto=item['produto']).first()
                custo_un = float(prod_db.preco_custo or 0)
                v_venda_item = float(item['subtotal'] - desc_item)
                
                session.add(Vendas(
                    nome_prod=item['produto'], qtd_vendida=item['qtd'],
                    preco_venda_total=v_venda_item, data=datetime.datetime.now(), 
                    lucro=v_venda_item - (custo_un * item['qtd']), 
                    nome_cliente=item['cliente'], telefone=item['telefone'], 
                    tamanho=item['tamanho'], personalizacao=item['personalizacao'], 
                    metodo_pagamento=metodo_sel, is_associado=(desconto > 0)
                ))
                if prod_db: prod_db.quantidade -= item['qtd']
            
            session.commit()
            clear_cache()
            st.session_state.ultimo_pedido_balcao = {"total": valor_final_venda, "metodo": metodo_sel, "cliente": st.session_state.carrinho[0]['cliente']}
            st.session_state.carrinho = []
            st.rerun()
        except Exception as e:
            session.rollback()
            st.error(f"Erro: {e}")

    if col_btn2.button(v["BOTAO_LIMPAR_CARRINHO"], use_container_width=True):
        st.session_state.carrinho = []
        st.rerun()

def render_vendas(can_edit_status=False):
    st.header(v["TITULO"])
    
    if "ultimo_pedido_balcao" in st.session_state:
        render_venda_sucesso()
        return

    session = get_session()
    if 'carrinho' not in st.session_state:
        st.session_state.carrinho = []

    # --- SEÇÃO 1: REGISTRO (FORMULÁRIO OTIMIZADO) ---
    if st.session_state.role in ["admin", "vendedor"]:
        with st.expander(v["EXPANDER_NOVA"], expanded=True):
            produtos_db = session.query(Estoque).all()
            dict_prods = {p.nome_produto: p for p in produtos_db}
            
            if dict_prods:
                with st.form("form_venda_balcao", clear_on_submit=True):
                    c1, c2 = st.columns(2)
                    nome_c = c1.text_input(v["LABEL_CLIENTE"])
                    tel_c = c2.text_input(s.LABEL_TEL_CLIENTE_VENDA, placeholder=s.PLACEHOLDER_TELEFONE)
                    
                    st.divider()
                    cp, cq, ct = st.columns([2, 1, 1])
                    prod_sel = cp.selectbox(v["LABEL_PROD"], options=sorted(dict_prods.keys()))
                    qtd = cq.number_input("Qtd", min_value=1, value=1)
                    tipo_p = st.radio("Preço", v["OPCOES_PRECO"], horizontal=True)
                    
                    tamanho = st.selectbox(v["LABEL_TAMANHO"], v["OPCOES_TAMANHO"])
                    obj_p = dict_prods[prod_sel]
                    
                    perso = ""
                    if obj_p.personalizavel:
                        perso = st.text_input("Personalização", placeholder="Ex: Nome e número para camisa <nome-número>")

                    if st.form_submit_button(v["BOTAO_ADD"], use_container_width=True):
                        sucesso_tel, tel_limpo = validar_telefone(tel_c)
                        if not sucesso_tel: st.error(s.MSG_ERRO_TELEFONE)
                        elif not nome_c: st.error("Nome obrigatório")
                        elif qtd > obj_p.quantidade: st.error("Sem estoque disponível")
                        else:
                            preco = obj_p.preco_kit if tipo_p == "Kit" and obj_p.preco_kit else obj_p.preco_venda_un
                            st.session_state.carrinho.append({
                                "produto": prod_sel, "qtd": int(qtd), "preco": float(preco),
                                "subtotal": float(qtd * preco), "tamanho": tamanho, 
                                "personalizacao": perso, "cliente": clean_text(nome_c), "telefone": tel_limpo 
                            })
                            st.rerun()

    render_carrinho_venda(session, v["OPCOES_PAGAMENTO"])
    st.divider()
    render_historico_vendas(session, can_edit_status)

    # --- ESTORNO ---
    if st.session_state.role == "admin":
        with st.expander(v["EXPANDER_ESTORNO"]):
            with st.form("form_estorno", clear_on_submit=True):
                id_est = st.number_input("ID", min_value=1)
                if st.form_submit_button("Confirmar Estorno"):
                    v_rem = session.query(Vendas).filter_by(id=id_est).first()
                    if v_rem:
                        p_est = session.query(Estoque).filter_by(nome_produto=v_rem.nome_prod).first()
                        if p_est: p_est.quantidade += v_rem.qtd_vendida
                        session.delete(v_rem)
                        session.commit()
                        clear_cache()
                        st.rerun()
    session.close()

"""
Sistema de Gestão e Vendas - Frenética (A.A.A.T.J.B.)
Desenvolvido por: Edílson Alves da Silva (Edy-py)
Contato: edilsonalvesprofissional@gmail.com
© 2026 - Todos os direitos reservados.
"""
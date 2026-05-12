# -*- coding: utf-8 -*-
from utils import format_currency

# ==============================================================================
# 1. IDENTIDADE E CONFIGURAÇÕES GERAIS
# ==============================================================================
ATLETICA_NOME = "Frenética"
MOEDA = "R$"
DESCONTO_VALOR = 0.10  # 10%
VALOR_ADESAO_SOCIO = 10.00

COR_AZUL_MARCA = "#031875"
COR_AMARELO_MARCA = "#FFD700"
BANNER_ARQUIVO = "midia/LOGOFNC.png"

# --- FINANCEIRO ---
FINANCEIRO_RESPONSAVEL = "Alfredo"
FINANCEIRO_WHATSAPP = "6499485869"
FINANCEIRO_PIX = "## freneticaufcat@gmail.com"
LINK_WHATSAPP_FIN = f"https://wa.me/55{FINANCEIRO_WHATSAPP}?text=Olá! Segue o comprovante da compra na {ATLETICA_NOME}: "

# ==============================================================================
# 2. MENU PRINCIPAL (Usado no main.py)
# ==============================================================================
TITULO_PAGINA = f"Portal {ATLETICA_NOME} - Gestão"
ICON_PAGINA = "🛒"
TEXTO_BANNER = f"ATLÉTICA {ATLETICA_NOME.upper()}"

NOMES_ABAS = {
    "dashboard": "📊 Dashboard",
    "estoque": "📦 Estoque",
    "vendas": "💰 Vendas",
    "associados": "👥 Associados",
    "compras": "🛒 Compras",
    "loja": "🛒 Loja " + ATLETICA_NOME,
    "parceiros": "🌟 Parceiros"
}

# ==============================================================================
# 3. ABA: COMPRAS / LOJA (Usado em compras.py)
# ==============================================================================
LOJA = {
    "TITULO": "🛒 Loja Oficial " + ATLETICA_NOME,
    "HEADER_SOCIO": "🎟️ Área do Sócio",
    "LABEL_BUSCA_SOCIO": "Já é sócio? Digite seu CPF:",
    "CAPTION_DESC": f"{int(DESCONTO_VALOR*100)}% de desconto aplicado!",
    "HEADER_ADESAO": "Não é associado?",
    "BOTAO_ADESAO": "💎 TORNE-SE SÓCIO AGORA",
    "CHAMADA_ADESAO": f"Ganhe {int(DESCONTO_VALOR*100)}% de desconto e benefícios em parceiros!",
    "BOTAO_REMOVER": "❌ Remover",
    "LABEL_PERS": "Personalização (Nome/Número):",
    "MSG_ESGOTADO": "Infelizmente o produto {nome} esgotou!",
    "VALOR_ADESAO": f"Valor da Adesão: **{format_currency(VALOR_ADESAO_SOCIO)}**",
}

# ==============================================================================
# 4. ABA: ASSOCIADOS (Usado em associados.py)
# ==============================================================================
SOCIOS = {
    "EXPANDER_CADASTRO": "➕ CADASTRAR NOVO SÓCIO",
    "EXPANDER_STATUS": "🔄 ATIVAR / DESATIVAR ASSINATURA",
    "LABEL_NOME": "Nome Completo",
    "LABEL_CPF": "CPF (Apenas números)",
    "LABEL_TEL": "WhatsApp (DDD + Número)",
    "BOTAO_SALVAR": "Salvar Sócio",
    "BUSCA_CPF": "Buscar Sócio pelo CPF:",
    "BUSCA_NOME": "Buscar Sócio pelo Nome:",
    "LISTA_TITULO": "Lista de Associados",
    "MSG_SUCESSO": "✅ Sócio cadastrado!",
    "MSG_EXISTE": "❌ Erro: CPF já cadastrado.",
    "MSG_NAO_ENCONTRADO": "⚠️ Nenhum associado encontrado.",
    "TAB_GERENCIAR_SOCIOS": "Gerenciar Sócios",
    "TAB_GERENCIAR_PARCEIROS": "Gerenciar Empresas Parceiras"
}

# ==============================================================================
# 5. ABA: VENDAS (Usado em vendas.py)
# ==============================================================================
VENDAS = {
    "TITULO": "Gerenciamento de Vendas",
    "EXPANDER_NOVA": "🛒 NOVA VENDA (BALCÃO)",
    "LABEL_CLIENTE": "Nome do Cliente",
    "LABEL_PROD": "Produto",
    "LABEL_TAMANHO": "Tamanho",
    "OPCOES_TAMANHO": ["N/A", "P", "M", "G", "GG", "XG"],
    "BOTAO_ADD": "➕ Adicionar ao Pedido",
    "LABEL_PAGAMENTO": "Forma de Pagamento:",
    "OPCOES_PAGAMENTO": ["Pix", "Dinheiro", "Cartão de Crédito", "Cartão de Débito"],
    "BOTAO_CONFIRMAR": "✅ Confirmar Venda",
    "MSG_SUCESSO": "🔥 Venda registrada com sucesso!",
    "HISTORICO_SUB": "Histórico de Pedidos",
    "STATUS_PAG": ["Pagamento Pendente", "Pago 50%", "Pago"],
    "EXPANDER_ESTORNO": "❌ CANCELAR VENDA / ESTORNO",
    "MSG_DESCONTO_OK": "✅ Desconto aplicado",
    "MSG_DESCONTO_ERRO": "❌ Erro ao aplicar o desconto",
    "BOTAO_LIMPAR_CARRINHO": "Limpar carrinho",
    "LABEL_COD_DESCONTO": f"Código de Associado para Desconto ({int(DESCONTO_VALOR*100)}%)",
    "LABEL_TIPO_PRECO": "Tipo de Preço:",
    "OPCOES_PRECO": ["Unitário", "Kit"],
    "LABEL_NOME_CLIENTE": "Nome Completo",
    "LABEL_TEL_CLIENTE": "WhatsApp (com DDD)"
}

# ==============================================================================
# 6. ABA: ESTOQUE (Usado em estoque.py)
# ==============================================================================
ESTOQUE = {
    "TITULO": "Gestão de Estoque",
    "OPERACAO_LABEL": "Escolha a operação:",
    "OPERACAO_OPCOES": ["Visualizar / Cadastrar", "Atualizar por ID", "📦 Gerenciar Kits"],
    "CAD_PROD_EXPANDER": "➕ CADASTRAR NOVO PRODUTO",
    "CAD_KIT_EXPANDER": "📦 CADASTRAR NOVO KIT",
    "LABEL_NOME": "Nome do Produto/Kit",
    "LABEL_QTD": "Quantidade Inicial",
    "LABEL_CUSTO": "Custo Unitário (R$)",
    "LABEL_VENDA": "Venda Unitária (R$)",
    "LABEL_FOTO": "Foto do Produto",
    "LABEL_NOVO_NOME": "Novo Nome",
    "LABEL_NOVA_QTD": "Nova Qtd",
    "LABEL_NOVO_CUSTO": "Novo Custo",
    "LABEL_NOVO_VENDA": "Novo Venda",
    "LABEL_TROCAR_FOTO": "Trocar foto (Vazio para manter)",
    "LABEL_ID_EDITAR": "ID do Produto:",
    "LABEL_PERGUNTA_PERS": "Pode personalizar?",
    "LABEL_NOME_KIT": "Nome do Kit",
    "LABEL_PRODS_KIT": "Produtos no Kit:",
    "LABEL_VALOR_KIT": "Valor do Kit (R$)",
    "MSG_EXISTE": "⚠️ Produto já existe no sistema.",
    "MSG_SUCESSO": "✅ {nome} cadastrado com sucesso!",
    "MSG_NOME_OBRIGATORIO": "O nome do produto é obrigatório.",
    "MSG_KIT_SUCESSO": "✅ Kit {nome} cadastrado com sucesso!",
    "MSG_ERRO_ITENS_KIT": "❌ Kit {nome} não foi cadastrado!",
    "MSG_ERRO_ITENS": "Selecione pelo menos um produto.",
    "MSG_EDIT_SUCESSO": "Produto atualizado com sucesso!",
    "MSG_NAO_ENCONTRADO": "Produto não encontrado.",
    "BOTAO_SALVAR_KIT": "SALVAR KIT",
    "BOTAO_SALVAR": "SALVAR NO ESTOQUE",
    "BOTAO_CONFIRMAR": "CONFIRMAR ALTERAÇÃO",
    "INFO_EDITANDO": "Editando: **{nome}**",
    "COLUNAS": ["ID", "PRODUTO", "QTD", "VENDA UN.", "PERSONALIZA"],
    "OPCOES_SIM_NAO": ["Não", "Sim"],
    "EDITOR_TITULO": "📝 EDITOR DE PRODUTO",
    "PLACEHOLDER_KIT": "Ex: KIT CALOURO 2026",
    "SUB_DISPONIVEL": "Estoque Disponível",
    "SUB_ESTOQUE_DISPONIVEL": "📦 Estoque Disponível para Venda"
}

# ==============================================================================
# 7. DASHBOARD (Usado em dashboard.py)
# ==============================================================================
DASH = {
    "TITULO": "Painel de Controle",
    "METRICA_VENDAS": "Vendas Realizadas",
    "METRICA_LUCRO": "Lucro Acumulado",
    "METRICA_PROD_MAIS_VENDIDO": "Produto Mais Vendido",
    "GRAFICO_ESTOQUE": "Níveis de Estoque Atual",
    "GRAFICO_RANKING": "Produtos Mais Vendidos (Qtd)",
    "LABEL_STATUS_OK": "Ok",
    "LABEL_STATUS_ALERTA": "Alerta",
    "LABEL_STATUS_CRITICO": "Crítico",
    "LABEL_PRODUTO": "Produto",
    "LABEL_QUANTIDADE": "Quantidade Vendida",
    "MSG_SEM_ESTOQUE": "Nenhum produto cadastrado para exibir o gráfico.",
    "MSG_SEM_VENDAS": "Nenhuma venda registrada para gerar o ranking."
}

CORES_STATUS = {
    DASH["LABEL_STATUS_OK"]: 'green', 
    DASH["LABEL_STATUS_ALERTA"]: 'orange', 
    DASH["LABEL_STATUS_CRITICO"]: 'red'
}

# ==============================================================================
# 8. MENSAGENS DE ERRO E VALIDAÇÃO (Globais)
# ==============================================================================
MSG_ERRO_CPF = "⚠️ CPF inválido! Verifique os números digitados."
MSG_ERRO_TELEFONE = "⚠️ Telefone inválido! Use o formato: (XX) XXXXX-XXXX."
MSG_ERRO_CAMPOS = "⚠️ Preencha todos os campos obrigatórios."

# ORIENTAÇÕES DE PAGAMENTO
MSG_PAGAMENTO_PIX = f"⚡ **PAGAMENTO VIA PIX**\nChave: `{FINANCEIRO_PIX}`\n\nFavor enviar o comprovante para **{FINANCEIRO_RESPONSAVEL}**"
MSG_PAGAMENTO_CARTAO = "💳 **PAGAMENTO VIA CARTÃO**\nPeça seu link no valor de **{valor}** para o financeiro."

LABEL_PRODUTO = DASH["LABEL_PRODUTO"]
LABEL_QUANTIDADE = DASH["LABEL_QUANTIDADE"]


MSG_ESTOQUE_VAZIO = "Sem estoque!!"

PLACEHOLDER_PRODUTO = "Ex: camisa da " + ATLETICA_NOME
PLACEHOLDER_TELEFONE = "Ex: (XX) XXXXX-XXXX"
PLACEHOLDER_PERSONALIZACAO = "Ex: Nome - Número"
PLACEHOLDER_CPF = "XXX.XXX.XX-XX"
LABEL_TEL_CLIENTE_VENDA = "WhatsApp (DDD + Número)"
MSG_SUCESSO_PARCERIA = "Parceria adicionada com sucesso"

MSG_ERRO_SOCIO_NAO_ENCONTRADO = "CPF não encontrado!"
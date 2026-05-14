# 🦁 Frenética - Sistema de Gestão e Vendas (A.A.A.T.J.B.)

Sistema de e-commerce e gestão interna desenvolvido para a **Associação Atlética Acadêmica Thiago Jabur Bittar (Frenética)** da UFCAT. O projeto automatiza desde a venda de produtos e kits até o controle de associados e dashboards financeiros.

## 🚀 Funcionalidades Principais

### 🛒 Módulo de Vendas (Loja)
- **Catálogo Dinâmico:** Visualização de produtos com fotos, preços e disponibilidade em tempo real.
- **Sistema de Kits:** Venda de conjuntos de produtos (ex: Kit Calça + Camisa) com preços diferenciados.
- **Regras de Desconto:** - Aplicação automática de desconto para **Sócios Ativos**.
  - **Trava de Desconto:** Kits possuem preços fixos e não recebem descontos adicionais de sócio.
- **Checkout Integrado:** Coleta de dados do comprador, escolha de tamanho/personalização e geração de pedidos.

### 📦 Gestão de Estoque Inteligente
- **Controle por ID:** Cadastro, edição e exclusão de produtos individuais.
- **Logística de Kits:** - A quantidade disponível de um Kit é calculada automaticamente com base no "gargalo" do estoque real (ex: se há 10 camisas e 2 canecas, o estoque do kit é 2).
    - Atualização em tempo real: ao vender um produto individual, o estoque de todos os kits que o contêm é atualizado.
- **Personalização:** Identificação de produtos que permitem inserção de nome/número (Ex: Samba-canção ou Tirante).

### 👥 Gestão de Associados
- **Banco de Dados de Sócios:** Cadastro e verificação de status (Ativo/Inativo).
- **Validação de CPF:** Garante que apenas sócios legítimos usufruam dos benefícios na loja.

### 📊 Dashboard e Relatórios (Admin)
- **Visão Financeira:** Gráficos de vendas mensais, faturamento bruto e lucro estimado.
- **Produtos Mais Vendidos:** Ranking de saída para auxiliar no planejamento de novas compras.
- **Gestão de Pedidos:** Lista completa para controle de entrega e status de pagamento.

## 🛠️ Tecnologias Utilizadas

- **Linguagem:** [Python 3.x](https://www.python.org/)
- **Interface Web:** [Streamlit](https://streamlit.io/)
- **Banco de Dados:** SQLAlchemy (SQLite/PostgreSQL)
- **Manipulação de Dados:** Pandas
- **Estilização:** CSS customizado para as cores da atlética (Laranja/Preto).

## 📁 Estrutura do Projeto

- `main.py`: Ponto de entrada da aplicação e navegação entre abas.
- `estoque.py`: Lógica de gerenciamento de produtos, kits e cálculos de estoque.
- `compras.py`: Interface da loja para o usuário final.
- `database.py`: Modelagem das tabelas (Estoque, Associados, Vendas).
- `utils.py`: Funções auxiliares (formatação de moeda, limpeza de texto, upload de imagens).
- `strings_config.py`: Centralização de textos e rótulos para facilitar manutenção.

---
## 👤 Autor

Desenvolvido com 🧡 por **[Seu Nome]** *Vice-Presidente da Atlética Frenética - Gestão 2026*

[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Edy-py/Edy-py.git)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](www.linkedin.com/in/edy-py)
# 🤖 Sistema de Automação de Mensagens - Atlética Frenética

Este projeto foi desenvolvido para automatizar e otimizar o processo de confirmação de pedidos e gestão de vendas da **Atlética Frenética (UFCAT)**. O sistema realiza desde o tratamento de dados brutos vindos do Google Forms até o envio de mensagens personalizadas via WhatsApp.

---

## 🚀 Funcionalidades

- **📥 Processamento de Planilhas:** Leitura e padronização de dados exportados do Excel.
- **🧹 Limpeza de Dados:** Script dedicado para formatar telefones, tratar nomes de colunas e organizar listas de tamanhos e personalizações.
- **💰 Cálculo de Valores Dinâmico:** Sistema que diferencia preços para membros da "Gestão" e aplica lógica de descontos para kits (ex: Kit Camisa + Calça ou Kit Top + Calça).
- **✍️ Templates Personalizados:** Geração de mensagens automáticas que validam itens, tamanhos, cores, e informações de personalização (nome/número).
- **📲 Envio Automatizado:** Integração com WhatsApp Desktop utilizando `PyAutoGUI` para disparos em lote.
- **📄 Logs de Operação:** Monitorização de sucessos e erros durante o processo de envio.

---

## 🛠️ Tecnologias Utilizadas

- **Python** (Core do projeto)
- **Pandas:** Manipulação e limpeza de dados
- **PyAutoGUI:** Automação de interface gráfica para envio de mensagens
- **Pyperclip:** Gestão da área de transferência para textos formatados
- **Regular Expressions (re):** Normalização e extração de padrões de texto

---

## ⚙️ Como Funciona

1. **Limpeza:** O script `limpar_tabela.py` lê o ficheiro `Formulário de Pedido - Atlética Frenética (respostas).xlsx`, normaliza os dados e gera o `pedidos_frenetica_final.xlsx`.
2. **Processamento:** O módulo `funcoes.py` processa cada linha, calculando o valor total e montando a mensagem personalizada.
3. **Automação:** O sistema utiliza comandos de teclado e rato para abrir o WhatsApp, procurar o contacto e colar a mensagem preparada.

---

## 📦 Estrutura do Repositório

- `limpar_tabela.py`: Motor de pré-processamento e normalização.
- `funcoes.py`: Lógica de negócio, templates de mensagens e rotinas de automação.
- `.gitignore`: Protege ficheiros sensíveis, ambientes virtuais (`.venv`) e dados reais de clientes.
- `pedidos_frenetica_final.xlsx`: Base de dados pronta para o disparo das mensagens.

---

## 📧 Contacto e Suporte
- **E-mail:** `edilsonalvesprofissional@gmail.com`
- **Instagram:** `edy-py`
- **Linkedin:** [edy-py](www.linkedin.com/in/edy-py)  

Projeto desenvolvido por **Edy-py**.

- **Financeiro / Chave PIX:** `freneticaufcat@gmail.com`
- **Responsável Financeiro:** Alfredo
- **Instituição:** Universidade Federal de Catalão (UFCAT)

---
> **Nota:** Certifique-se de que o WhatsApp Desktop está aberto e em primeiro plano antes de iniciar o envio em lote.

# Edson Portões - Sistema Inteligente de Gestão (Versão Cloud)

Este projeto foi desenvolvido para resolver um problema real de gestão na oficina familiar **Edson Portões**. O foco foi transformar processos manuais em uma plataforma digital intuitiva, integrando controle de inventário, fluxo de vendas e análise de dados financeiros em tempo real.

---

## 🚀 Novidades da Versão 2.0 (Portfólio Full-Stack)
Recentemente, o sistema foi migrado de uma arquitetura local para uma infraestrutura **Cloud**, trazendo:
* **Banco de Dados em Nuvem:** Migração de SQLite para **PostgreSQL (Supabase)**, garantindo persistência global de dados.
* **Segurança Robusta:** Implementação de autenticação com **Hashing de Senhas (Bcrypt)** e controle de acesso baseado em funções (Admin vs. Viewer).
* **Infraestrutura Segura:** Gerenciamento de credenciais sensíveis via **Streamlit Secrets**.

---

## Stack Tecnológica

Para este projeto, escolhi tecnologias que priorizam a robustez dos dados e a escalabilidade:

* **Linguagem:** Python 3.14+
* **Interface (UI/UX):** [Streamlit](https://streamlit.io/) - Foco em usabilidade e design responsivo.
* **Banco de Dados:** [PostgreSQL](https://www.postgresql.org/) hospedado no [Supabase](https://supabase.com/).
* **ORM:** [SQLAlchemy](https://www.sqlalchemy.org/) - Para garantir a integridade dos dados e facilitar a manutenção.
* **Segurança:** [Bcrypt](https://pypi.org/project/bcrypt/) - Criptografia de senhas para proteção de contas.
* **Análise de Dados:** [Pandas](https://pandas.pydata.org/) & [Plotly](https://plotly.com/) - Processamento e visualização de métricas financeiras.

---

## 🛠️ Desafios Técnicos Superados

* **Persistência Full-Cloud:** Configuração de conexão segura entre Streamlit Cloud e Supabase, superando desafios de protocolo IPv6 e bloqueios de porta de rede.
* **Resiliência de Conexão:** Implementação de **Connection Pooling (PgBouncer)** via porta 6543, otimizando o tráfego de dados e evitando quedas de sessão em ambientes serverless.
* **Arquitetura de Segurança:** Criação de uma camada de autenticação que injeta CSS customizado para ocultar funcionalidades de escrita (Admin) para usuários comuns, garantindo a integridade do banco.
* **Gerenciamento de Estado:** Uso de `st.session_state` para um carrinho de compras persistente e sincronização imediata de transações financeiras (Venda -> Baixa no Estoque -> Cálculo de Lucro).

---

## 📋 Módulos do Sistema

1.  **📊 Visualização:** Visão estratégica com gráficos de pizza para distribuição de lucro e barras para níveis críticos de estoque.
2.  **📦 Estoque Centralizado:** CRUD completo com lógica de padronização de texto e formatação monetária automática.
3.  **💰 Ponto de Venda (PDV):** Carrinho de compras dinâmico com estorno automático e geração de histórico para auditoria.

---

## 🔗 Acesso e Contato

- **Link do App:** [Edson Portões - Gestão](https://gerenciamentoedsonportoes.streamlit.app/))
- **Acesso como Visitante:** usuário -> `visitante` senha -> `visitante123`
- **Autor:** Edílson Alves da Silva (Edy)
- **LinkedIn:** [edy-py](https://www.linkedin.com/in/edy-py)
- **Instagram:** [@edy-py](https://www.instagram.com/edy_python/)
- **Formação:** *Estudante de Ciência da Computação - Universidade Federal de Catalão (UFCAT)*

---
> *Nota: Este repositório é um exemplo prático de como utilizo a tecnologia para gerar valor direto e automação em negócios reais.*

# 🤖 Sistema de Automação de Mensagens - Atlética Frenética

Este projeto automatiza o envio de mensagens no WhatsApp para confirmação de pedidos realizados via Google Forms.

A ideia principal é eliminar tarefas manuais repetitivas, organizando os dados automaticamente e enviando mensagens personalizadas para cada cliente.

---

## 🚀 Funcionalidades

- 📥 Leitura de planilha (Excel) gerada pelo Google Forms  
- 🧹 Limpeza e padronização de dados (telefones, nomes, valores)  
- 📊 Consolidação de pedidos (kits, peças avulsas, personalização)  
- ✍️ Geração automática de mensagens personalizadas  
- 📲 Envio automático via WhatsApp Desktop com PyAutoGUI  
- 📄 Geração de logs de envio (sucesso e erro)  

---

## 🧠 Como funciona

1. O usuário faz um pedido via Google Forms  
2. Os dados são exportados para uma planilha `.xlsx`  
3. O script:
   - organiza os dados com Pandas  
   - monta mensagens personalizadas  
   - envia automaticamente no WhatsApp  
4. Um log é gerado com todos os envios realizados  

---

## 🛠️ Tecnologias utilizadas

- Python  
- Pandas  
- PyAutoGUI  
- Pyperclip  
- Excel  

---

## ⚙️ Instalação

Clone o repositório:

```bash
git clone https://github.com/seu-usuario/seu-repo.git
cd seu-repo


## Criado por Edy-py


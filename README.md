# 🤖 Gestão Inteligente de Chats no Bitrix24 com API Flask 🇧🇷  
(Scroll down for English version 🇺🇸)

Este projeto foi desenvolvido para automatizar tarefas operacionais envolvendo chats no Bitrix24 — como transferências entre filas ou responsáveis, finalização de atendimentos e atualização de campos personalizados em negócios (deals).

## ✅ O que ele faz?
- Transfere automaticamente o chat de um contato entre filas (queues) ou operadores (agents).
- Finaliza o atendimento diretamente via API.
- Move atividades entre negócios diferentes.
- Monitora mudanças de responsável e sincroniza o atendimento em tempo real.

## 🔧 Como funciona?
- Se conecta à API oficial do Bitrix24 usando credenciais seguras via `.env`.
- Expõe endpoints REST que você pode integrar a sistemas como Dialog360, bots, automações e CRMs externos.
- Executa ações contextuais com base em eventos recebidos (como webhooks de alteração de responsável).

## 🛡️ Segurança
- Totalmente integrado à API oficial do Bitrix24.
- Dados sensíveis protegidos por variáveis de ambiente.
- Logging detalhado e tratamento de erros para maior confiabilidade.

## 📈 Benefícios para sua operação
- Reduz o tempo de atendimento e troca de operadores.
- Minimiza erros humanos em transferências manuais.
- Permite integração nativa com provedores externos como Dialog360.
- Automatiza ações críticas sem intervenção manual.

> Quer implementar este tipo de automação no seu Bitrix24? Fale com a gente e vamos customizar isso para o seu fluxo. 😉

---

# 🤖 Smart Chat Management in Bitrix24 with Flask API 🇺🇸

This project automates critical chat-related tasks in Bitrix24 — such as transferring conversations between queues or agents, ending chats, and updating deal fields automatically.

## ✅ What does it do?
- Automatically transfers a contact’s chat between queues or agents.
- Ends conversations via API.
- Moves activities between deals.
- Monitors deal ownership changes and updates the chat accordingly.

## 🔧 How does it work?
- Connects securely to the Bitrix24 API using `.env` credentials.
- Offers REST endpoints you can call from Dialog360, bots, automations, or other platforms.
- Executes context-aware actions triggered by events (like webhooks for deal changes).

## 🛡️ Security
- Fully integrated using the official Bitrix24 API.
- Sensitive data is stored using environment variables.
- Robust error handling and logging included.

## 📈 Business Benefits
- Speeds up chat routing and agent handovers.
- Reduces manual errors during conversation transfers.
- Easily integrates with external platforms like Dialog360.
- Automates critical flows with no manual work.

> Want to implement this kind of automation in your Bitrix24? Let’s talk and customize it for your workflow. 😉

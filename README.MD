# Meu Controle Financeiro

Este é um projeto pessoal desenvolvido para ajudar no controle das minhas finanças, permitindo o registro, acompanhamento e análise de receitas, despesas, cartões de crédito e objetivos financeiros. O sistema foi criado utilizando [Streamlit](https://streamlit.io/) para interface web, [MongoDB](https://www.mongodb.com/) como banco de dados e diversas bibliotecas Python para visualização e manipulação de dados.

## Funcionalidades

- **Dashboard**: Visão geral das receitas, despesas e saldo do mês.
- **Transações**: Cadastro e filtro de receitas e despesas, com relatórios rápidos e gráficos interativos.
- **Cartões de Crédito**: Gerenciamento de cartões, registro de compras parceladas, acompanhamento do limite e faturas.
- **Objetivos Financeiros**: Definição de metas, acompanhamento do progresso e prazo para realização.
- **Autenticação**: Sistema de login e cadastro de usuários para segurança dos dados.

## Tecnologias Utilizadas

- Python 3.13+
- Streamlit
- Pandas
- Plotly
- PyMongo
- Bcrypt

## Estrutura do Projeto

- `app.py`: Página principal do dashboard.
- `pages/`: Outras páginas do sistema (transações, cartões, objetivos).
- `services/`: Lógica de negócio e integração com banco de dados.
- `auth/`: Autenticação de usuários.
- `config/`: Configuração do banco de dados.
- `images/`: Imagens utilizadas na interface.

## Observações

Este projeto é de uso pessoal, mas pode ser adaptado para outras pessoas que desejam controlar suas finanças de forma simples e visual.

---

Desenvolvido por Lucas Moreira
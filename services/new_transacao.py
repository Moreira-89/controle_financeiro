from config.db_config import connect_db
import streamlit as st

db = connect_db()
colecao = db.get_collection("transacoes")

@st.dialog("Nova Receita")
def new_receita():
    data = st.date_input("Data da Receita")
    data_str = data.strftime("%d/%m/%Y")
    descricao = st.text_input("Descrição da Receita")
    subcategoria = st.selectbox("Subcategoria", sorted(["Salário", "Investimentos", "Dividendos", "Pix Recebido", "Renda Anterior"]))
    valor = st.number_input("Valor da Receita", min_value=0.0, format="%.2f")
    
    if st.button("Adicionar Receita"):
        colecao.insert_one({
            "data": data_str,
            "valor": valor,
            "descricao": descricao,
            "categoria_principal": "Receita",
            "subcategoria": subcategoria
        })
        st.success("Receita adicionada com sucesso!")


@st.dialog("Nova Despesa")
def new_despesa():
    data = st.date_input("Data da Despesa")
    data_str = data.strftime("%d/%m/%Y")
    descricao = st.text_input("Descrição da Despesa")
    subcategoria = st.selectbox("Subcategoria", sorted([
        "Casa", "Fatura de Cartão", "Pix para outros", "Compras Online", "Transporte", "Alimentação", "Mercado", "Outros", "Farmacia", "Faculdade", "Educação"
    ]))
    valor = st.number_input("Valor da Despesa", min_value=0.0, format="%.2f")
    
    if st.button("Adicionar Despesa"):
        colecao.insert_one({
            "data": data_str,
            "valor": valor,
            "descricao": descricao,
            "categoria_principal": "Despesa",
            "subcategoria": subcategoria
        })
        st.success("Despesa adicionada com sucesso!")
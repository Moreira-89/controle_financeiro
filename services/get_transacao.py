from config.db_config import connect_db
import streamlit as st
import pandas as pd

def get_transacao():
    db = connect_db()
    colecao = db.get_collection("transacoes")
    transacao = list(colecao.find())

    if not transacao:
        st.warning("Nenhuma transação encontrada.")

    else:
        df = pd.DataFrame(transacao)
        if '_id' in df.columns:
            df = df.drop(columns=['_id'])

        df['data'] = pd.to_datetime(df['data'], format='%d/%m/%Y')

        df = df.sort_values(by='data', ascending=False).reset_index(drop=True)

        data = {
            "Data": df["data"].dt.strftime('%d/%m/%Y'),
            "Descrição": df["descricao"],
            "Categoria Principal": df["categoria_principal"],
            "Subcategoria": df["subcategoria"],
            "Valor R$": df["valor"]
        }

        return data

from config.db_config import connect_db
import streamlit as st
import pandas as pd

@st.cache_data(ttl=300)
def get_transacao():

    try:
        db = connect_db()
        colecao = db.get_collection("transacoes")
        transacoes = list(colecao.find())
        
        if not transacoes:
            return pd.DataFrame()
        
        df = pd.DataFrame(transacoes)
        df = df.drop(columns=['_id'], errors='ignore')
        df['data'] = pd.to_datetime(df['data'], format='%d/%m/%Y', errors='coerce')
        df = df.sort_values(by='data', ascending=False).reset_index(drop=True)
        
        return df.rename(columns={
            'data': 'Data',
            'descricao': 'Descrição', 
            'categoria_principal': 'Categoria Principal',
            'subcategoria': 'Subcategoria',
            'valor': 'Valor R$'
        })
        
    except Exception as e:
        st.error(f"Erro ao carregar transações: {str(e)}")
        return pd.DataFrame()

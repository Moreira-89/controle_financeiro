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
    

@st.cache_data(ttl=300)
def get_transacao_credito():

    try:
        db = connect_db()
        colecao = db.get_collection("compras_cartao")
        transacoes_credito = list(colecao.find())

        if not transacoes_credito:
            return pd.DataFrame()

        df = pd.DataFrame(transacoes_credito)

        df = df.drop(columns=['_id', 'user_email', "cartao_id", 'parcelas', 'valor_parcela'], errors='ignore')

        data = {
            'Data': df['data_compra'],
            'Descrição': df['descricao'],
            'Categoria Principal': df['categoria'],
            'Valor R$': df['valor']
        }

        data = pd.DataFrame(data)
        data['Data'] = pd.to_datetime(data['Data'])
        data = data.sort_values('Data', ascending=False)
        data['Data'] = data['Data'].dt.strftime('%d/%m/%Y')
        data['Valor R$'] = pd.to_numeric(data['Valor R$'], errors='coerce')

        data["Valor R$"] = data.apply(lambda row: f"\U0001F4B8 -R$ {row['Valor R$']:,.2f}" if row['Valor R$'] < 0 else f"R$ {row['Valor R$']:,.2f}", axis=1)

        return data

    except Exception as e:
        st.error(f"Erro ao carregar transações: {str(e)}")
        return pd.DataFrame()

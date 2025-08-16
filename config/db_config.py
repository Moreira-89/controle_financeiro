from pymongo import MongoClient
import streamlit as st

def connect_db():

    try:
        url_connection = st.secrets.get("URL_CONNECTION_MONGO")
        if not url_connection:
            st.error("\u274C URL de conexão MongoDB não configurada")
            return None
            
        client = MongoClient(url_connection, serverSelectionTimeoutMS=5000)
        client.admin.command('ping') 
        
        db = client.get_database("controle_financeiro")
        return db
        
    except Exception as e:
        st.error(f"\u274C Erro de conexão com MongoDB: {str(e)}")
        st.info("\U0001F4A1 Verifique se o MongoDB está rodando e as credenciais estão corretas")
        return None
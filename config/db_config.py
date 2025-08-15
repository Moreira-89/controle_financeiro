from pymongo import MongoClient
import streamlit as st

def connect_db():

    try:
        url_connection = st.secrets["URL_CONNECTION_MONGO"]

        Connect_Mongo = MongoClient(url_connection)

        if Connect_Mongo.server_info() is None:
            st.error("Erro ao conectar ao MongoDB")

        db = Connect_Mongo.get_database("controle_financeiro")

        if db is None:
            st.error("Erro ao conectar ao banco de dados")

        return db

    except Exception as e:
        print(f"Erro ao conectar ao MongoDB: {e}")
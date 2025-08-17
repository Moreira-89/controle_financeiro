from config.db_config import connect_db
from auth.register import cadastro
import streamlit as st
import bcrypt

def login():
    db = connect_db()

    users = db.get_collection("usuarios")  

    col1, col2 = st.columns([2,2])
    with col1:
        st.image("images/img01.png", width=200)
        st.markdown("### Controle Financeiro")
        st.markdown("Faça login para acessar o sistema.")

    with col2:
        st.title("Login")
        search_email = st.text_input("Email:", key="email_login", width=500)
        search_senha = st.text_input("Senha:", type="password", key="senha_login", width=500)

        if st.button("Continue", width=500, type="primary"):
            usuario = users.find_one({"email": search_email})
            if usuario == None:
                st.error("Usuário não encontrado!")
            else:
                senha_hash = usuario['senha']
                if bcrypt.checkpw(search_senha.encode("utf-8"), senha_hash):
                    st.success("Logado com sucesso!")
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.warning("Senha incorreta! Digite novamente")

        st.markdown("---")
        if st.button("Criar Conta", width=500):
            cadastro(users=users)
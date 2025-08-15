import streamlit as st
import bcrypt


@st.dialog("Criar conta")
def cadastro(users):

    nome = st.text_input("Nome:", key="nome")
    email = st.text_input("Email:", key="email")
    senha = st.text_input("Senha:", type="password", key="senha")

    if st.button("Cadastrar"):
        if not nome or not email or not senha:
            st.warning("Preencha todos os campos.")
            st.rerun

        elif len(senha) < 6:
            st.warning("A senha deve ter pelo menos 6 caracteres.")

        elif users.find_one({'email': email}):
            st.warning("E-mail já cadastrado. Digite outro!")

        else:
            senha_hash = bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt())
            senha_hash_str = senha_hash.decode("utf-8")
            users.insert_one({"nome": nome, "email": email, "senha": senha_hash_str})
            st.success("Conta criada com sucesso!")
            st.rerun()
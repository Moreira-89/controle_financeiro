import streamlit as st

st.set_page_config(layout="wide",
                   page_title="Objetivos")

st.sidebar.markdown("### Navegação")
st.sidebar.page_link("pages/transacao.py", label="Extrato de Transações", icon=":material/list_alt:")
st.sidebar.page_link("app.py", label="Home", icon=":material/home:")
st.sidebar.markdown("---")

st.title("Defina seus objetivos financeiros")
st.write("Aqui você pode definir seus objetivos financeiros de curto, médio e longo prazo.")

objetivo_curto = st.text_input("Objetivo de curto prazo")
objetivo_medio = st.text_input("Objetivo de médio prazo")
objetivo_longo = st.text_input("Objetivo de longo prazo")

if st.button("Salvar objetivos"):
    st.success("Objetivos salvos com sucesso!")
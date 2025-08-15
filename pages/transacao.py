from services.new_transacao import new_receita, new_despesa
from services.get_transacao import get_transacao
import pandas as pd
import streamlit as st

st.set_page_config(layout="wide",
                   page_title="Transações")

st.sidebar.markdown("### Ações")
if st.sidebar.button("Nova Receita", icon=":material/trending_up:"):
    new_receita()
if st.sidebar.button("Nova Despesa", icon=":material/arrow_downward:"):
    new_despesa()
st.sidebar.markdown("### Navegação")
st.sidebar.page_link("pages/objetivos.py", label="Objetivos", icon=":material/star:")
st.sidebar.page_link("app.py", label="Home", icon=":material/home:")
st.sidebar.markdown("---")

st.markdown("### Extrato de Transações")

df = get_transacao()

df['Valor R$'] = df['Valor R$'].apply(lambda x: f"R$ {x:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))


st.dataframe(df)

if st.sidebar.button("Sair", icon=":material/logout:"):
    st.session_state.authenticated = False
    st.rerun()


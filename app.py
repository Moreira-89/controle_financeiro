from services.new_transacao import new_receita, new_despesa
from services.get_transacao import get_transacao
from services.criar_cards import card_html
from services.criar_grafic import gerar_graficos
import pandas as pd
from auth.login import login
import streamlit as st

def main():


    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        login()
        st.stop()

    if st.session_state.authenticated:

        st.set_page_config(
            page_title="Controle Financeiro",
            layout="wide"
        )

        st.sidebar.markdown("### Ações")
        if st.sidebar.button("Nova Receita", icon=":material/trending_up:"):
            new_receita()
        if st.sidebar.button("Nova Despesa", icon=":material/arrow_downward:"):
            new_despesa()

        st.sidebar.markdown("### Navegação")
        st.sidebar.page_link("pages/transacao.py", label="Extrato de Transações", icon=":material/list_alt:")
        st.sidebar.page_link("pages/objetivos.py", label="Objetivos", icon=":material/star:")
        st.sidebar.markdown("---")

        df = pd.DataFrame(get_transacao())
        df["Valor R$"] = df["Valor R$"].astype(float)

        total_receitas = df[df["Categoria Principal"] == "Receita"]["Valor R$"].sum()
        total_despesas = df[df["Categoria Principal"] == "Despesa"]["Valor R$"].sum()
        saldo_conta = total_receitas - total_despesas

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(card_html("Receitas", total_receitas, "#28a745"), unsafe_allow_html=True)
        with col2:
            st.markdown(card_html("Despesas", total_despesas, "#dc3545"), unsafe_allow_html=True)
        with col3:
            st.markdown(card_html("Saldo em Conta", saldo_conta, "#007bff"), unsafe_allow_html=True)

        st.markdown("---")

        gerar_graficos(df)

    if st.sidebar.button("Sair", icon=":material/logout:"):
        st.session_state.authenticated = False
        st.rerun()


if __name__ == "__main__":
    main()
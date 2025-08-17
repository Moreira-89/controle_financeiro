from config.db_config import connect_db
from services.get_transacao import get_transacao
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import time


# ---------------- NOVA RECEITA ----------------
@st.dialog("\U0001F4B0 Nova Receita")
def new_receita():

    col1, col2 = st.columns(2)
    
    with col1:        
        data = st.date_input(label="Data da Receita")

        valor = st.number_input(
            "\U0001F4B0 Valor da Receita (R$)",
            min_value=0.01, 
            format="%.2f",
        )
    
    with col2:
        st.markdown("**\U0001F4DD Descrição da Receita**")
        descricao = st.text_input(label="", placeholder="Ex: Salário - Janeiro")

        subcategoria = st.selectbox(
            "\U0001F3F7 Subcategoria",   # 🏷
            sorted([
                "Salário", "Investimentos", "Dividendos", "Pix Recebido", 
                "Renda Anterior", "Freelance", "Bonificação", "Outros"
            ])
        )
    
    col_btn1, col_btn2, _ = st.columns([1, 1, 2])  # centraliza botões
    with col_btn1:
        if st.button("\U0001F4BE Salvar Receita", type="primary"):
            try:
                db = connect_db()
                colecao = db.get_collection("transacoes")
                
                result = colecao.insert_one({
                    "data": data.strftime("%d/%m/%Y"),
                    "valor": valor,
                    "descricao": descricao.strip(),
                    "categoria_principal": "Receita",
                    "subcategoria": subcategoria,
                    "criado_em": datetime.now().isoformat()
                })
                
                if result.inserted_id:
                    st.success("\u2705 Receita adicionada com sucesso!")
                else:
                    st.error("\u274C Erro ao salvar. Tente novamente.")
                    
            except Exception as e:
                st.error(f"\u274C Erro: {str(e)}")
    
    with col_btn2:
        if st.button("\U0001F6AB Cancelar"):
            st.rerun()


# ---------------- NOVA DESPESA ----------------
@st.dialog("\U0001F4B8 Nova Despesa")
def new_despesa():

    col1, col2 = st.columns(2)
    
    with col1:
        data = st.date_input("\U0001F4C5 Data da Despesa")

        valor = st.number_input(
            "\U0001F4B0 Valor da Despesa (R$)",
            min_value=0.01, 
            format="%.2f")
    
    with col2:
        st.markdown("**\U0001F4DD Descrição da Despesa**")
        descricao = st.text_input(label="", placeholder="Ex: Supermercado - Compras Mensais")

        subcategorias_ordenadas = [
            "Alimentação", "Mercado", "Transporte", "Casa", 
            "Fatura de Cartão", "Compras Online", "Farmácia",
            "Faculdade", "Educação", "Pix para outros", "Outros"
        ]
        subcategoria = st.selectbox("\U0001F3F7 Subcategoria", subcategorias_ordenadas)  # 🏷
    
    col_btn1, col_btn2, _ = st.columns([1, 1, 2])  # centraliza botões
    with col_btn1:
        if st.button("\U0001F4BE Salvar Despesa", type="primary"):
            try:
                db = connect_db()
                colecao = db.get_collection("transacoes")
                
                result = colecao.insert_one({
                    "data": data.strftime("%d/%m/%Y"),
                    "valor": valor,
                    "descricao": descricao.strip(),
                    "categoria_principal": "Despesa",
                    "subcategoria": subcategoria,
                    "criado_em": datetime.now().isoformat()
                })
                
                if result.inserted_id:
                    st.success("\u2705 Despesa registrada com sucesso!")
                    
                    # Sugestões pós-despesa
                    if subcategoria in ["Mercado", "Compras Online"]:
                        st.info("\U0001F4A1 **Dica:** Considere anotar os itens comprados para melhor controle")
                    elif valor > 500:
                        st.info("\U0001F4A1 **Sugestão:** Que tal revisar seus objetivos financeiros?")
                    
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("\u274C Erro ao salvar")
                    
            except Exception as e:
                st.error(f"\u274C Erro: {str(e)}")
    
    with col_btn2:
        if st.button("\U0001F6AB Cancelar"):
            st.rerun()
            

# ---------------- RELATÓRIO RÁPIDO ----------------
def quick_report():
    """Relatório rápido das transações recentes"""
    try:
        df = get_transacao()
        if df.empty:
            return "Nenhuma transação encontrada"
        
        # Últimos 7 dias
        df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y', errors='coerce')
        ultimos_7_dias = df[df['Data'] >= (datetime.now() - timedelta(days=7))]
        
        if ultimos_7_dias.empty:
            return "Nenhuma transação nos últimos 7 dias"
        
        receitas_7d = ultimos_7_dias[ultimos_7_dias["Categoria Principal"] == "Receita"]["Valor R$"].sum()
        despesas_7d = ultimos_7_dias[ultimos_7_dias["Categoria Principal"] == "Despesa"]["Valor R$"].sum()
        
        return f"""
\U0001F4CA **Últimos 7 dias:**   # 📊
- Receitas: R$ {receitas_7d:,.2f}
- Despesas: R$ {despesas_7d:,.2f}
- Saldo: R$ {receitas_7d - despesas_7d:,.2f}
        """
    except Exception as e:
        return f"Erro ao gerar relatório: {str(e)}"

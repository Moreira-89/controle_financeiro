from services.new_transacao import new_receita, new_despesa
from services.criar_grafic import gerar_graficos
from services.get_transacao import get_transacao
from datetime import datetime, timedelta
from auth.login import login
import streamlit as st
import pandas as pd

def format_brl(valor):
    """Formata número para padrão brasileiro: R$ 1.381,86"""
    try:
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "R$ 0,00"

def main():

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        login()
        st.stop()

    if st.session_state.authenticated:
        st.set_page_config(
            page_title="Meu Controle Financeiro",
            page_icon="\U0001F4B0",
            layout="wide",
            initial_sidebar_state="expanded"
        )

        col_header1, col_header3 = st.columns([3, 1])

        with col_header1:
            st.title("\U0001F4B0 Meu Controle Financeiro")

        with col_header3:
            st.markdown("**Status do Mês:**")
            mes_atual = datetime.now().strftime("%d/%m/%Y")
            st.info(f"\U0001F4C5 {mes_atual}")

        setup_sidebar()

        df = get_transacao()

        df_numeric = df.copy()
        df_numeric["Valor R$"] = pd.to_numeric(df_numeric["Valor R$"], errors='coerce', downcast='float')

        render_dashboard_metrics(df_numeric)
        
        render_smart_insights(df_numeric)
        
        st.markdown("---")
    
        gerar_graficos(df_numeric)


def setup_sidebar():
    """Configura sidebar melhorada"""
    st.sidebar.markdown("### \U0001F680 Ações Rápidas")
    
    if st.sidebar.button("\U0001F4B0 Nova Receita", icon=":material/trending_up:", key="sidebar_receita"):
        new_receita()
    if st.sidebar.button("\U0001F4B8 Nova Despesa", icon=":material/arrow_downward:", key="sidebar_despesa"):
        new_despesa()
    
    st.sidebar.markdown("### \U0001F4CA Navegação")
    st.sidebar.page_link("pages/transacao.py", label="\U0001F4CB Extrato Completo", icon=":material/list_alt:")
    st.sidebar.page_link("pages/objetivos.py", label="\U0001F3AF Meus Objetivos", icon=":material/star:")
    st.sidebar.page_link("pages/cartao_credito.py", label="\U0001F4B3 Cartões de Crédito", icon=":material/credit_card:")
    
    st.sidebar.markdown("---")
    
    if st.sidebar.button("\U0001F6AA Sair", icon=":material/logout:"):
        st.session_state.authenticated = False
        st.rerun()

def render_dashboard_metrics(df):
    """Dashboard com métricas inteligentes"""
    hoje = datetime.now()
    mes_atual = hoje.month
    ano_atual = hoje.year
    
    df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y', errors='coerce')
    df_mes = df[
        (df['Data'].dt.month == mes_atual) & 
        (df['Data'].dt.year == ano_atual)
    ]
    
    total_receitas = df[df["Categoria Principal"] == "Receita"]["Valor R$"].sum()
    total_despesas = df[df["Categoria Principal"] == "Despesa"]["Valor R$"].sum()
    saldo_total = total_receitas - total_despesas

    receitas_mes = df_mes[df_mes["Categoria Principal"] == "Receita"]["Valor R$"].sum()
    despesas_mes = df_mes[df_mes["Categoria Principal"] == "Despesa"]["Valor R$"].sum()
    
    col1, col2, col3= st.columns(3)

    with col1:        
        st.metric(
            "\U0001F49A Receitas Total",
            format_brl(receitas_mes)
        )
    
    with col2:        
        st.metric(
            "\U0001F4B8 Despesas Total",
            format_brl(despesas_mes)
        )
    
    with col3:
        st.metric(
            "\U0001F4B0 Saldo Total",
            format_brl(saldo_total),
        )
    
def render_smart_insights(df):
    """Insights automáticos inteligentes"""
    st.markdown("### \U0001F9E0 Insights Automáticos")
    
    insights = []
    
    despesas = df[df["Categoria Principal"] == "Despesa"]
    if not despesas.empty:
        gasto_por_categoria = despesas.groupby("Subcategoria")["Valor R$"].sum().sort_values(ascending=False)
        categoria_maior_gasto = gasto_por_categoria.index[0]
        valor_maior_gasto = gasto_por_categoria.iloc[0]
        
        insights.append({
            "tipo": "info",
            "titulo": "\U0001F4B3 Maior Categoria de Gasto",
            "texto": f"Você gastou mais em **{categoria_maior_gasto}**: {format_brl(valor_maior_gasto)}"
        })
    
    hoje = datetime.now()
    df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y', errors='coerce')
    ultimos_7_dias = df[df['Data'] >= (hoje - timedelta(days=7))]
    
    if not ultimos_7_dias.empty:
        despesas_semana = ultimos_7_dias[ultimos_7_dias["Categoria Principal"] == "Despesa"]["Valor R$"].sum()
        media_diaria = despesas_semana / 7
        
        if media_diaria > 50:
            insights.append({
                "tipo": "warning",
                "titulo": "\U0001F4C8 Gastos da Semana",
                "texto": f"Média diária: {format_brl(media_diaria)}. Considere revisar os gastos."
            })
        else:
            insights.append({
                "tipo": "success",
                "titulo": "\U0001F4C9 Gastos Controlados",
                "texto": f"Média diária: {format_brl(media_diaria)}. Parabéns pelo controle!"
            })
    
    receitas_total = df[df["Categoria Principal"] == "Receita"]["Valor R$"].sum()
    despesas_total = df[df["Categoria Principal"] == "Despesa"]["Valor R$"].sum()
    
    if receitas_total > 0:
        percentual_gasto = (despesas_total / receitas_total) * 100
        
        if percentual_gasto > 90:
            insights.append({
                "tipo": "error",
                "titulo": "\U0001F6A8 Alto Percentual de Gastos",
                "texto": f"Você está gastando {percentual_gasto:.1f}% das suas receitas!"
            })
        elif percentual_gasto > 70:
            insights.append({
                "tipo": "warning",
                "titulo": "\u26A0 Atenção aos Gastos",
                "texto": f"Gastos representam {percentual_gasto:.1f}% das receitas"
            })
        else:
            insights.append({
                "tipo": "success",
                "titulo": "\u2705 Gastos Equilibrados",
                "texto": f"Gastos representam {percentual_gasto:.1f}% das receitas"
            })
    
    cols_insights = st.columns(len(insights) if len(insights) <= 3 else 3)
    
    for i, insight in enumerate(insights[:3]):
        with cols_insights[i]:
            if insight["tipo"] == "success":
                st.success(f"**{insight['titulo']}**\n\n{insight['texto']}")
            elif insight["tipo"] == "warning":
                st.warning(f"**{insight['titulo']}**\n\n{insight['texto']}")
            elif insight["tipo"] == "error":
                st.error(f"**{insight['titulo']}**\n\n{insight['texto']}")
            else:
                st.info(f"**{insight['titulo']}**\n\n{insight['texto']}")

def get_receitas_mes_anterior(df, hoje):
    """Calcula receitas do mês anterior"""
    mes_anterior = hoje.month - 1 if hoje.month > 1 else 12
    ano = hoje.year if hoje.month > 1 else hoje.year - 1
    
    df_mes_anterior = df[
        (df['Data'].dt.month == mes_anterior) & 
        (df['Data'].dt.year == ano) &
        (df["Categoria Principal"] == "Receita")
    ]
    
    return df_mes_anterior["Valor R$"].sum()

def get_despesas_mes_anterior(df, hoje):
    """Calcula despesas do mês anterior"""
    mes_anterior = hoje.month - 1 if hoje.month > 1 else 12
    ano = hoje.year if hoje.month > 1 else hoje.year - 1
    
    df_mes_anterior = df[
        (df['Data'].dt.month == mes_anterior) & 
        (df['Data'].dt.year == ano) &
        (df["Categoria Principal"] == "Despesa")
    ]
    
    return df_mes_anterior["Valor R$"].sum()

if __name__ == "__main__":
    main()
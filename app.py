from services.new_transacao import new_receita, new_despesa
from services.objetivos_service import ObjetivosService
from services.criar_grafic import gerar_graficos
from services.get_transacao import get_transacao
from datetime import datetime, timedelta
from auth.login import login
import streamlit as st
import pandas as pd


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

        st.markdown("""
        <style>
        .main-header {
            padding: 1rem 0;
            border-bottom: 2px solid #f0f2f6;
            margin-bottom: 2rem;
        }
        .quick-stats {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 1rem;
        }
        .metric-card {
            background: white;
            padding: 1rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-left: 4px solid #3498db;
        }
        </style>
        """, unsafe_allow_html=True)

       # Header principal
        col_header1, col_header3 = st.columns([3, 1])

        with col_header1:
            st.title("\U0001F4B0 Meu Controle Financeiro")
            hoje = datetime.now()
            st.markdown(f"**{hoje.strftime('%A, %d de %B de %Y')}**")

        with col_header3:
            st.markdown("**Status do Mês:**")
            mes_atual = datetime.now().strftime("%m/%Y")
            st.info(f"\U0001F4C5 {mes_atual}")
        
        st.markdown('</div>', unsafe_allow_html=True)

        setup_sidebar()

        df = get_transacao()
        
        if df.empty:
            st.warning("\U0001F4DD Ainda não há transações. Que tal adicionar a primeira?")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("\U0001F3AF Começar com uma Receita", type="primary"):
                    new_receita()
            with col2:
                if st.button("\U0001F4B3 Ou uma Despesa", type="secondary"):
                    new_despesa()
            return

        df_numeric = df.copy()
        df_numeric["Valor R$"] = pd.to_numeric(df_numeric["Valor R$"], errors='coerce')
        
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
    saldo_mes = receitas_mes - despesas_mes
    
    col1, col2, col3= st.columns(3)
    
    with col1:
        receitas_mes_anterior = get_receitas_mes_anterior(df, hoje)
        delta_receitas = receitas_mes - receitas_mes_anterior if receitas_mes_anterior > 0 else 0
        
        st.metric(
            "\U0001F49A Receitas Total",
            f"R$ {total_receitas:,.2f}",
            f"Mês: R$ {receitas_mes:,.2f}"
        )
        
        if delta_receitas != 0:
            delta_text = f"R$ {abs(delta_receitas):,.2f}" + (" \u2B06" if delta_receitas > 0 else " \u2B07")
            if delta_receitas > 0:
                st.success(f"vs mês anterior: +{delta_text}")
            else:
                st.error(f"vs mês anterior: -{delta_text}")
    
    with col2:
        despesas_mes_anterior = get_despesas_mes_anterior(df, hoje)
        delta_despesas = despesas_mes - despesas_mes_anterior if despesas_mes_anterior > 0 else 0
        
        st.metric(
            "\U0001F4B8 Despesas Total",
            f"R$ {total_despesas:,.2f}",
            f"Mês: R$ {despesas_mes:,.2f}"
        )
        
        if delta_despesas != 0:
            delta_text = f"R$ {abs(delta_despesas):,.2f}" + (" \u2B06" if delta_despesas > 0 else " \u2B07")
            if delta_despesas > 0:
                st.warning(f"vs mês anterior: +{delta_text}")
            else:
                st.success(f"vs mês anterior: -{delta_text}")
    
    with col3:
        st.metric(
            "\U0001F4B0 Saldo Total",
            f"R$ {saldo_total:,.2f}",
            f"Mês: R$ {saldo_mes:,.2f}"
        )
        
        if saldo_total > 1000:
            st.success("\U0001F389 Situação excelente!")
        elif saldo_total > 0:
            st.info("\U0001F44D Situação positiva")
        elif saldo_total > -500:
            st.warning("\u26A0 Atenção ao saldo")
        else:
            st.error("\U0001F6A8 Situação crítica")
    
def render_smart_insights(df):
    """Insights automáticos inteligentes"""
    st.markdown("### \U0001F9E0 Insights Automáticos")
    
    insights = []
    
    # Análise de gastos por categoria
    despesas = df[df["Categoria Principal"] == "Despesa"]
    if not despesas.empty:
        gasto_por_categoria = despesas.groupby("Subcategoria")["Valor R$"].sum().sort_values(ascending=False)
        categoria_maior_gasto = gasto_por_categoria.index[0]
        valor_maior_gasto = gasto_por_categoria.iloc[0]
        
        insights.append({
            "tipo": "info",
            "titulo": "\U0001F4B3 Maior Categoria de Gasto",
            "texto": f"Você gastou mais em **{categoria_maior_gasto}**: R$ {valor_maior_gasto:,.2f}"
        })
    
    # Análise de tendência
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
                "texto": f"Média diária: R$ {media_diaria:.2f}. Considere revisar os gastos."
            })
        else:
            insights.append({
                "tipo": "success",
                "titulo": "\U0001F4C9 Gastos Controlados",
                "texto": f"Média diária: R$ {media_diaria:.2f}. Parabéns pelo controle!"
            })
    
    # Análise de receitas vs despesas
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
    
    # Renderiza insights
    cols_insights = st.columns(len(insights) if len(insights) <= 3 else 3)
    
    for i, insight in enumerate(insights[:3]):  # Máximo 3 insights
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
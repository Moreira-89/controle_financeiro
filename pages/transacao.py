from services.new_transacao import new_receita, new_despesa, quick_report
from services.get_transacao import get_transacao
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
import plotly.express as px

def format_brl(valor):
    """Formata número para padrão brasileiro: R$ 1.381,86"""
    try:
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "R$ 0,00"

def main():
    st.set_page_config(
        layout="wide",
        page_title="Minhas Transações",
        page_icon="\U0001F4CB"
    )
    
    # Header da página
    col_h1, col_h2, col_h3 = st.columns([2, 2, 1])
    
    with col_h1:
        st.title("\U0001F4CB Minhas Transações")
        st.markdown("**Controle completo das suas movimentações**")
    
    with col_h2:
        col_a1, col_a2 = st.columns(2)
        with col_a1:
            if st.button("\U0001F49A Nova Receita", type="primary", use_container_width=True):
                new_receita()
        with col_a2:
            if st.button("\U0001F4B8 Nova Despesa", type="secondary", use_container_width=True):
                new_despesa()
    
    with col_h3:
        if st.button("\U0001F4CA Relatório", use_container_width=True):
            st.session_state.show_quick_report = not st.session_state.get('show_quick_report', False)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Sidebar
    setup_sidebar()
    
    # Relatório rápido (se ativado)
    if st.session_state.get('show_quick_report', False):
        with st.expander("\U0001F4CA Relatório Rápido", expanded=True):
            st.markdown(quick_report())
    
    # Carrega e processa dados
    df = get_transacao()
    
    # Filtros avançados
    df_filtered = render_filtros_avancados(df)
    
    # Métricas do período filtrado
    render_metricas_periodo(df_filtered)
    
    # Visualizações
    render_visualizacoes(df_filtered)
    
    st.markdown("---")
    
    # Tabela de transações melhorada
    render_tabela_transacoes(df_filtered)

def setup_sidebar():
    """Sidebar melhorada para transações"""
    st.sidebar.markdown("### \U0001F680 Ações Rápidas")
    
    if st.sidebar.button("\U0001F4B0 Nova Receita", icon=":material/trending_up:", key="sidebar_receita"):
        new_receita()
    if st.sidebar.button("\U0001F4B8 Nova Despesa", icon=":material/arrow_downward:", key="sidebar_despesa"):
        new_despesa()
    
    st.sidebar.markdown("### \U0001F4CA Navegação")
    st.sidebar.page_link("app.py", label="\U0001F3E0 Dashboard", icon=":material/home:")
    st.sidebar.page_link("pages/objetivos.py", label="\U0001F3AF Objetivos", icon=":material/star:")
    st.sidebar.page_link("pages/cartao_credito.py", label="\U0001F4B3 Cartões de Crédito", icon=":material/credit_card:")
    
    st.sidebar.markdown("---")
    
    if st.sidebar.button("\U0001F6AA Sair", icon=":material/logout:"):
        st.session_state.authenticated = False
        st.rerun()

def render_filtros_avancados(df):
    """Filtros avançados para as transações"""
    st.markdown('<div class="filtro-box">', unsafe_allow_html=True)
    st.markdown("### \U0001F50D Filtros Avançados")
    
    col_f1, col_f2, col_f3, col_f4 = st.columns(4)
    
    with col_f1:
        # Filtro por período
        periodo_opcoes = {
            "Todos": None,
            "Últimos 7 dias": 7,
            "Últimos 30 dias": 30,
            "Últimos 3 meses": 90,
            "Este ano": "ano_atual"
        }
        
        periodo_selecionado = st.selectbox("\U0001F4C5 Período", list(periodo_opcoes.keys()))
        
    with col_f2:
        # Filtro por categoria
        categorias = ["Todas"] + df["Categoria Principal"].unique().tolist()
        categoria_selecionada = st.selectbox("\U0001F3F7 Categoria", categorias)
        
    with col_f3:
        # Filtro por subcategoria
        if categoria_selecionada != "Todas":
            subcategorias = ["Todas"] + df[df["Categoria Principal"] == categoria_selecionada]["Subcategoria"].unique().tolist()
        else:
            subcategorias = ["Todas"] + df["Subcategoria"].unique().tolist()
        
        subcategoria_selecionada = st.selectbox("\U0001F516 Subcategoria", subcategorias)
    
    with col_f4:
        # Filtro por valor
        valor_min = st.number_input("\U0001F4B0 Valor mínimo", min_value=0.0, value=0.0, step=10.0)
    
    # Busca textual
    busca_texto = st.text_input("\U0001F50D Buscar na descrição", placeholder="Digite para buscar...")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Aplica filtros
    df_filtered = df.copy()
    
    # Filtro por período
    if periodo_opcoes[periodo_selecionado] is not None:
        df_filtered['Data'] = pd.to_datetime(df_filtered['Data'], format='%d/%m/%Y', errors='coerce')
        
        if periodo_selecionado == "Este ano":
            ano_atual = datetime.now().year
            df_filtered = df_filtered[df_filtered['Data'].dt.year == ano_atual]
        else:
            dias = periodo_opcoes[periodo_selecionado]
            data_limite = datetime.now() - timedelta(days=dias)
            df_filtered = df_filtered[df_filtered['Data'] >= data_limite]
    
    # Outros filtros
    if categoria_selecionada != "Todas":
        df_filtered = df_filtered[df_filtered["Categoria Principal"] == categoria_selecionada]
    
    if subcategoria_selecionada != "Todas":
        df_filtered = df_filtered[df_filtered["Subcategoria"] == subcategoria_selecionada]
    
    if valor_min > 0:
        df_filtered["Valor R$"] = pd.to_numeric(df_filtered["Valor R$"], errors='coerce')
        df_filtered = df_filtered[df_filtered["Valor R$"] >= valor_min]
    
    if busca_texto:
        df_filtered = df_filtered[df_filtered["Descrição"].str.contains(busca_texto, case=False, na=False)]
    
    # Mostra quantas transações foram encontradas
    total_encontradas = len(df_filtered)
    total_original = len(df)
    
    if total_encontradas != total_original:
        st.info(f"\U0001F50D Encontradas {total_encontradas} de {total_original} transações")
    
    return df_filtered

def render_metricas_periodo(df):
    """Métricas do período filtrado"""
    if df.empty:
        st.warning("\U0001F4CA Nenhuma transação encontrada com os filtros aplicados")
        return
    
    df_numeric = df.copy()
    df_numeric["Valor R$"] = pd.to_numeric(df_numeric["Valor R$"], errors='coerce')
    
    receitas = df_numeric[df_numeric["Categoria Principal"] == "Receita"]["Valor R$"].sum()
    despesas = df_numeric[df_numeric["Categoria Principal"] == "Despesa"]["Valor R$"].sum()
    saldo = receitas - despesas
    transacoes_count = len(df)
    
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    
    with col_m1:
        st.metric("\U0001F4CA Transações", transacoes_count)
    
    with col_m2:
        st.metric("\U0001F49A Receitas", format_brl(receitas))
    
    with col_m3:
        st.metric("\U0001F4B8 Despesas", format_brl(despesas))
    
    with col_m4:
        delta_color = "normal" if saldo >= 0 else "inverse"
        st.metric("\U0001F4B0 Saldo Período", format_brl(saldo), delta_color=delta_color)


def render_visualizacoes(df):
    """Visualizações das transações"""
    if df.empty:
        return
    
    st.markdown("### \U0001F4C8 Visualizações")
    
    df_numeric = df.copy()
    df_numeric["Valor R$"] = pd.to_numeric(df_numeric["Valor R$"], errors='coerce')
    df_numeric['Data'] = pd.to_datetime(df_numeric['Data'], format='%d/%m/%Y', errors='coerce')
    
    col_v1, col_v2 = st.columns(2)
    
    with col_v1:
        # Gráfico pizza por subcategoria (só despesas)
        despesas = df_numeric[df_numeric["Categoria Principal"] == "Despesa"]
        if not despesas.empty:
            gastos_por_sub = despesas.groupby("Subcategoria")["Valor R$"].sum().sort_values(ascending=False)
            
            fig_pizza = px.pie(
                values=gastos_por_sub.values,
                names=gastos_por_sub.index,
                title="\U0001F4B8 Despesas por Categoria",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            
            fig_pizza.update_traces(textposition='inside', textinfo='percent+label')
            fig_pizza.update_layout(showlegend=True, height=400)
            
            st.plotly_chart(fig_pizza, use_container_width=True)
    
    with col_v2:
        # Gráfico de evolução temporal
        df_tempo = df_numeric.groupby(['Data', 'Categoria Principal'])['Valor R$'].sum().reset_index()
        
        if not df_tempo.empty:
            fig_linha = px.line(
                df_tempo,
                x='Data',
                y='Valor R$',
                color='Categoria Principal',
                title='\U0001F4CA Evolução Temporal',
                color_discrete_map={'Receita': '#27ae60', 'Despesa': '#e74c3c'},
                markers=True
            )
            
            fig_linha.update_layout(
                hovermode='x unified',
                height=400,
                showlegend=True
            )
            
            st.plotly_chart(fig_linha, use_container_width=True)

def render_tabela_transacoes(df):
    """Tabela de transações melhorada"""
    if df.empty:
        return
    
    st.markdown("### \U0001F4CB Lista de Transações")
    
    # Preparar dados para exibição
    df_display = df.copy()
    df_display["Valor R$"] = pd.to_numeric(df_display["Valor R$"], errors='coerce')
    
    df_display["Valor Formatado"] = df_display.apply(lambda row: 
        f"\U0001F49A +{format_brl(row['Valor R$'])}" if row['Categoria Principal'] == 'Receita' 
        else f"\U0001F4B8 -{format_brl(row['Valor R$'])}", axis=1)
    
    # Ordenar por data (mais recente primeiro)
    df_display['Data'] = pd.to_datetime(df_display['Data'], format='%d/%m/%Y', errors='coerce')
    df_display = df_display.sort_values('Data', ascending=False)
    df_display['Data'] = df_display['Data'].dt.strftime('%d/%m/%Y')
    
    # Selecionar colunas para exibir
    colunas_exibir = ['Data', 'Descrição', 'Subcategoria', 'Valor Formatado']
    df_final = df_display[colunas_exibir].reset_index(drop=True)
    
    # Renomear colunas
    df_final.columns = ['\U0001F4C5 Data', '\U0001F4DD Descrição', '\U0001F3F7 Categoria', '\U0001F4B0 Valor']
    
    # Configurações da tabela
    st.dataframe(
        df_final,
        use_container_width=True,
        hide_index=True,
        height=400,
        column_config={
            "\U0001F4C5 Data": st.column_config.TextColumn(width="small"),
            "\U0001F4DD Descrição": st.column_config.TextColumn(width="medium"),
            "\U0001F3F7 Categoria": st.column_config.TextColumn(width="small"),
            "\U0001F4B0 Valor": st.column_config.TextColumn(width="small"),
        }
    )

if __name__ == "__main__":
    main()
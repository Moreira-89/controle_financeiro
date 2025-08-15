import pandas as pd
import plotly.express as px
import streamlit as st

def gerar_graficos(df: pd.DataFrame):
    # Garantir tipo numérico e data
    df["Valor R$"] = df["Valor R$"].astype(float)
    df["Data"] = pd.to_datetime(df["Data"], format="%d/%m/%Y")

    df_mes = df.copy()
    df_mes["AnoMes"] = df_mes["Data"].dt.to_period("M").astype(str)
    df_mes_group = df_mes.groupby(["AnoMes", "Categoria Principal"])["Valor R$"].sum().reset_index()

    fig_barras = px.bar(
        df_mes_group,
        x="AnoMes",
        y="Valor R$",
        color="Categoria Principal",
        barmode="group",
        title="Receitas vs Despesas (Mensal)",
        color_discrete_map={"Receita": "#2ecc71", "Despesa": "#e74c3c"},
    )
    fig_barras.update_layout(
        template="plotly_white",
        title_font=dict(size=18, family="Arial", color="#333"),
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="rgba(200,200,200,0.3)"),
        legend_title_text="Categoria",
    )

    df_diario = df.groupby(["Data", "Categoria Principal"])["Valor R$"].sum().reset_index()
    fig_linha = px.line(
        df_diario,
        x="Data",
        y="Valor R$",
        color="Categoria Principal",
        title="Evolução Diária de Receitas e Despesas",
        color_discrete_map={"Receita": "#2ecc71", "Despesa": "#e74c3c"},
        markers=True
    )
    fig_linha.update_layout(
        template="plotly_white",
        title_font=dict(size=18, family="Arial", color="#333"),
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="rgba(200,200,200,0.3)"),
        legend_title_text="Categoria",
    )

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig_barras, use_container_width=True)
    with col2:
        st.plotly_chart(fig_linha, use_container_width=True)

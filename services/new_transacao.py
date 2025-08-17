from config.db_config import connect_db
from services.get_transacao import get_transacao
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta


def validar_transacao_avancada(valor, descricao, data, tipo):
    """Validação avançada com feedback personalizado"""
    erros = []
    alertas = []
    
    # Validações básicas
    if valor <= 0:
        erros.append("\U000026A0 Valor deve ser maior que zero")
    if not descricao.strip():
        erros.append("\U000026A0 Descrição é obrigatória")
    if data > datetime.now().date():
        erros.append("\U000026A0 Data não pode ser no futuro")
    
    # Validações inteligentes
    if valor > 10000:
        alertas.append("\U0001F4B0 Valor alto detectado. Confirme se está correto.")
    
    if tipo == "despesa":
        # Verifica se é fim de semana (possível lazer)
        if data.weekday() >= 5:  # Sábado ou domingo
            alertas.append("\U0001F389 Transação de fim de semana - lazer?")
    
    # Verifica padrões suspeitos
    if len(descricao) < 5:
        alertas.append("\U0001F4DD Descrição muito curta. Considere ser mais específico.")
    
    return erros, alertas

@st.dialog("\U0001F4B0 Nova Receita Inteligente")
def new_receita():
    st.markdown("### Adicionar nova receita")
    
    col1, col2 = st.columns(2)
    
    with col1:        
        data = st.date_input(
            "\U0001F4C5 Data da Receita",
            help="\U0001F4A1 Dica: Use as setas ←→ para navegar entre os meses"
        )
        
        # Subcategoria com sugestões de valores
        subcategoria = st.selectbox(
            "\U0001F3F7 Subcategoria", 
            sorted(["Salário", "Investimentos", "Dividendos", "Pix Recebido", "Renda Anterior", "Freelance", "Bonificação", "Outros"])
        )
        
        valor = st.number_input(
            "\U0001F4B0 Valor da Receita (R$)", 
            min_value=0.01, 
            format="%.2f",
        )
    
    with col2:
        # Descrição com autocompletar
        st.markdown("**\U0001F4DD Descrição da Receita**")
        descricao = st.text_input(
            label="\U0001F4DD Descrição da Receita",
            placeholder="Ex: Salário - Janeiro"
        )

    # Validação em tempo real
    erros, alertas = validar_transacao_avancada(valor, descricao, data, "receita")
    
    # Mostra alertas
    for alerta in alertas:
        st.info(alerta)
    
    # Mostra erros
    for erro in erros:
        st.error(erro)
    
    # Botão de salvar com estado dinâmico
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        pode_salvar = len(erros) == 0 and valor > 051 and descricao.strip()
        
        if st.button(
            "\U0001F4BE Salvar Receita", 
            type="primary", 
            disabled=not pode_salvar,
            use_container_width=True
        ):
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
                    st.success("\U00002705 Receita adicionada com sucesso!")
                    st.balloons()
                    
                    # Mostra próxima sugestão
                    st.info("\U0001F4A1 **Próxima ação sugerida:** Que tal definir um objetivo para essa receita?")
                    
                    # Aguarda um pouco e fecha
                    import time
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("\U0000274C Erro ao salvar. Tente novamente.")
                    
            except Exception as e:
                st.error(f"\U0000274C Erro: {str(e)}")
    
    with col_btn2:
        if st.button("\U0001F6AB Cancelar", use_container_width=True):
            st.rerun()

@st.dialog("\U0001F4B8 Nova Despesa Inteligente")
def new_despesa():
    st.markdown("### Adicionar nova despesa")
    
    col1, col2 = st.columns(2)
    
    with col1:
        data = st.date_input(
            "\U0001F4C5 Data da Despesa",
            help="\U0001F4A1 Dica: Use as setas ←→ para navegar entre os meses"
        )
        
        # Subcategorias organizadas por frequência de uso
        subcategorias_ordenadas = [
            "Alimentação", "Mercado", "Transporte", "Casa", 
            "Fatura de Cartão", "Compras Online", "Farmácia",
            "Faculdade", "Educação", "Pix para outros", "Outros"
        ]
        
        subcategoria = st.selectbox("\U0001F3F7 Subcategoria", subcategorias_ordenadas)
        
        valor = st.number_input(
            "\U0001F4B0 Valor da Despesa (R$)", 
            min_value=0.01, 
            format="%.2f")
        
        # Alertas por categoria
        if subcategoria == "Fatura de Cartão" and valor > 1000:
            st.warning("\U0001F4B3 Fatura alta! Revise os gastos do cartão")
        elif subcategoria == "Mercado" and valor > 300:
            st.info("\U0001F6D2 Compra grande no mercado - estoque para o mês?")
        elif subcategoria == "Transporte" and valor > 150:
            st.info("\U0001F695 Despesa alta com transporte - viagem ou manutenção?")
    
    with col2:
        # Descrição inteligente
        st.markdown("**\U0001F4DD Descrição da Despesa**")
        descricao = st.text_input(
            label="\U0001F4DD Descrição da Despesa",
            placeholder="Ex: McDonald's, Nubank"
        )
        
        # Dicas contextuais
        if subcategoria == "Fatura de Cartão":
            st.info("\U0001F4A1 **Dica:** Inclua o banco (ex: 'Nubank', 'Itaú')")
        elif subcategoria in ["Alimentação", "Mercado"]:
            st.info("\U0001F4A1 **Dica:** Inclua o local (ex: 'McDonald\'s', 'Extra')")
        
        # Preview da transação
        if valor > 0 and descricao:
            st.markdown("### \U0001F440 Preview")
            st.error(f"""
            **Data:** {data.strftime('%d/%m/%Y')}
            **Categoria:** {subcategoria}
            **Descrição:** {descricao}
            **Valor:** -R$ {valor:,.2f}
            """)
    
    # Validação avançada
    erros, alertas = validar_transacao_avancada(valor, descricao, data, "despesa")
    
    # Análise de impacto no orçamento
    try:
        df = get_transacao()
        if not df.empty:
            df_numeric = df.copy()
            df_numeric["Valor R$"] = pd.to_numeric(df_numeric["Valor R$"], errors='coerce')
            saldo_atual = (
                df_numeric[df_numeric["Categoria Principal"] == "Receita"]["Valor R$"].sum() - 
                df_numeric[df_numeric["Categoria Principal"] == "Despesa"]["Valor R$"].sum()
            )
            saldo_apos = saldo_atual - valor
            
            col_impact1, col_impact2 = st.columns(2)
            with col_impact1:
                st.metric("\U0001F4B0 Saldo Atual", f"R$ {saldo_atual:,.2f}")
            with col_impact2:
                st.metric("\U0001F52E Saldo Após Compra", f"R$ {saldo_apos:,.2f}", f"-R$ {valor:,.2f}")
            
            if saldo_apos < 0:
                st.error("\U0001F6A8 **ATENÇÃO:** Esta despesa deixará seu saldo negativo!")
            elif saldo_apos < 100:
                st.warning("\U000026A0 **CUIDADO:** Saldo ficará muito baixo após esta despesa")
    except:
        pass  # Se der erro, apenas não mostra o impacto
    
    # Mostra alertas e erros
    for alerta in alertas:
        st.info(alerta)
    for erro in erros:
        st.error(erro)
    
    # Controle de gastos do dia
    try:
        df = get_transacao()
        if not df.empty:
            df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y', errors='coerce')
            gastos_hoje = df[
                (df['Data'].dt.date == data) & 
                (df['Categoria Principal'] == 'Despesa')
            ]['Valor R$'].sum()
            
            gastos_hoje = pd.to_numeric(gastos_hoje, errors='coerce')
            if pd.notna(gastos_hoje) and gastos_hoje > 0:
                gastos_total_dia = gastos_hoje + valor
                if gastos_total_dia > 200:
                    st.warning(f"\U0001F4CA **Gastos do dia:** R$ {gastos_hoje:.2f} + R$ {valor:.2f} = R$ {gastos_total_dia:.2f}")
    except:
        pass
    
    # Botões de ação
    col_btn1, col_btn2, col_btn3 = st.columns(3)
    
    with col_btn1:
        pode_salvar = len(erros) == 0 and valor > 0 and descricao.strip()
        
        if st.button(
            "\U0001F4BE Confirmar Despesa", 
            type="primary", 
            disabled=not pode_salvar,
            use_container_width=True
        ):
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
                    st.success("\U00002705 Despesa registrada com sucesso!")
                    
                    # Sugestões pós-despesa
                    if subcategoria in ["Mercado", "Compras Online"]:
                        st.info("\U0001F4A1 **Dica:** Considere anotar os itens comprados para melhor controle")
                    elif valor > 500:
                        st.info("\U0001F4A1 **Sugestão:** Que tal revisar seus objetivos financeiros?")
                    
                    import time
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("\U0000274C Erro ao salvar")
                    
            except Exception as e:
                st.error(f"\U0000274C Erro: {str(e)}")
    
    with col_btn2:
        # Botão para parcelar (futuro)
        if st.button("\U0001F4B3 Parcelar", use_container_width=True, disabled=True):
            st.info("\U0001F6A7 Funcionalidade em desenvolvimento")
    
    with col_btn3:
        if st.button("\U0001F6AB Cancelar", use_container_width=True):
            st.rerun()
            

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
        **\U0001F4CA Últimos 7 dias:**
        - Receitas: R$ {receitas_7d:,.2f}
        - Despesas: R$ {despesas_7d:,.2f}
        - Saldo: R$ {receitas_7d - despesas_7d:,.2f}
        """
    except:
        return "Erro ao gerar relatório"
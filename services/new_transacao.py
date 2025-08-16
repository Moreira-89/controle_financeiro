from config.db_config import connect_db
from services.get_transacao import get_transacao
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Cache para sugestões inteligentes
@st.cache_data(ttl=600)  # Cache por 10 minutos
def get_sugestoes_inteligentes():
    """Obtém sugestões baseadas no histórico"""
    try:
        df = get_transacao()
        if df.empty:
            return {
                "descricoes_receita": [],
                "descricoes_despesa": [],
                "valores_receita": [],
                "valores_despesa": []
            }
        
        # Separar receitas e despesas
        receitas = df[df["Categoria Principal"] == "Receita"]
        despesas = df[df["Categoria Principal"] == "Despesa"]
        
        return {
            "descricoes_receita": receitas["Descrição"].unique().tolist()[-10:],  # Últimas 10
            "descricoes_despesa": despesas["Descrição"].unique().tolist()[-10:],
            "valores_receita": receitas.groupby("Subcategoria")["Valor R$"].mean().to_dict(),
            "valores_despesa": despesas.groupby("Subcategoria")["Valor R$"].mean().to_dict()
        }
    except:
        return {"descricoes_receita": [], "descricoes_despesa": [], "valores_receita": {}, "valores_despesa": {}}

def validar_transacao_avancada(valor, descricao, data, tipo):
    """Validação avançada com feedback personalizado"""
    erros = []
    alertas = []
    
    # Validações básicas
    if valor <= 0:
        erros.append("\u26A0 Valor deve ser maior que zero")
    if not descricao.strip():
        erros.append("\u26A0 Descrição é obrigatória")
    if data > datetime.now().date():
        erros.append("\u26A0 Data não pode ser no futuro")
    
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
    
    # Obtém sugestões
    sugestoes = get_sugestoes_inteligentes()
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Data com valor padrão inteligente
        data_padrao = datetime.now().date()
        # Se é início do mês, sugere dia do salário
        if data_padrao.day <= 5:
            data_padrao = data_padrao.replace(day=5)
        
        data = st.date_input(
            "\U0001F4C5 Data da Receita", 
            value=data_padrao,
            help="\U0001F4A1 Dica: Use as setas ←→ para navegar entre os meses"
        )
        
        # Subcategoria com sugestões de valores
        subcategoria = st.selectbox(
            "\U0001F3F7 Subcategoria", 
            sorted(["Salário", "Investimentos", "Dividendos", "Pix Recebido", "Renda Anterior", "Freelance", "Bonificação", "Outros"])
        )
        
        # Valor com sugestão baseada na categoria
        valor_sugerido = sugestoes["valores_receita"].get(subcategoria, 0.0)
        if valor_sugerido > 0:
            st.info(f"\U0001F4A1 Valor médio para {subcategoria}: R$ {valor_sugerido:.2f}")
        
        valor = st.number_input(
            "\U0001F4B0 Valor da Receita (R$)", 
            min_value=0.01, 
            format="%.2f",
            value=float(valor_sugerido) if valor_sugerido > 0 else 0.01,
            help="\U0001F4A1 Valores positivos aumentam seu saldo"
        )
    
    with col2:
        # Descrição com autocompletar
        st.markdown("**\U0001F4DD Descrição da Receita**")
        
        if sugestoes["descricoes_receita"]:
            descricao_sugerida = st.selectbox(
                "Usar descrição anterior:",
                [""] + sugestoes["descricoes_receita"],
                help="\U0001F4A1 Selecione uma descrição usada antes ou digite uma nova abaixo"
            )
        else:
            descricao_sugerida = ""
        
        descricao = st.text_input(
            "Ou digite uma nova:",
            value=descricao_sugerida,
            placeholder=f"Ex: {subcategoria} - {datetime.now().strftime('%B %Y')}",
            help="\U0001F4A1 Seja específico para melhor controle"
        )
        
        # Preview da transação
        if valor > 0 and descricao:
            st.markdown("### \U0001F440 Preview")
            st.success(f"""
            **Data:** {data.strftime('%d/%m/%Y')}
            **Tipo:** {subcategoria}
            **Descrição:** {descricao}
            **Valor:** R$ {valor:,.2f}
            """)
    
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
        pode_salvar = len(erros) == 0 and valor > 0 and descricao.strip()
        
        if st.button(
            "\U0001F4BE Salvar Receita", 
            type="primary", 
            disabled=not pode_salvar,
            use_container_width=True
        ):
            try:
                db = connect_db()
                colecao = db.get_collection("transacoes")
                
                # Limpa cache antes de inserir
                get_sugestoes_inteligentes.clear()
                
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
                    st.balloons()
                    
                    # Mostra próxima sugestão
                    st.info("\U0001F4A1 **Próxima ação sugerida:** Que tal definir um objetivo para essa receita?")
                    
                    # Aguarda um pouco e fecha
                    import time
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("\u274C Erro ao salvar. Tente novamente.")
                    
            except Exception as e:
                st.error(f"\u274C Erro: {str(e)}")
    
    with col_btn2:
        if st.button("\U0001F6AB Cancelar", use_container_width=True):
            st.rerun()

@st.dialog("\U0001F4B8 Nova Despesa Inteligente")
def new_despesa():
    st.markdown("### Adicionar nova despesa")
    
    # Obtém sugestões
    sugestoes = get_sugestoes_inteligentes()
    
    col1, col2 = st.columns(2)
    
    with col1:
        data = st.date_input(
            "\U0001F4C5 Data da Despesa",
            help="\U0001F4A1 Dica: Para despesas recorrentes, use o mesmo dia do mês"
        )
        
        # Subcategorias organizadas por frequência de uso
        subcategorias_ordenadas = [
            "Alimentação", "Mercado", "Transporte", "Casa", 
            "Fatura de Cartão", "Compras Online", "Farmácia",
            "Faculdade", "Educação", "Pix para outros", "Outros"
        ]
        
        subcategoria = st.selectbox("\U0001F3F7 Subcategoria", subcategorias_ordenadas)
        
        # Valor com sugestão e alertas
        valor_sugerido = sugestoes["valores_despesa"].get(subcategoria, 0.0)
        if valor_sugerido > 0:
            st.info(f"\U0001F4A1 Valor médio para {subcategoria}: R$ {valor_sugerido:.2f}")
        
        valor = st.number_input(
            "\U0001F4B0 Valor da Despesa (R$)", 
            min_value=0.01, 
            format="%.2f",
            value=float(valor_sugerido) if valor_sugerido > 0 else 0.01,
            help="\U0001F4A1 Valores de despesa reduzem seu saldo"
        )
        
        # Alertas por categoria
        if subcategoria == "Fatura de Cartão" and valor > 1000:
            st.warning("\U0001F4B3 Fatura alta! Revise os gastos do cartão")
        elif subcategoria == "Mercado" and valor > 300:
            st.info("\U0001F6D2 Compra grande no mercado - estoque para o mês?")
        elif subcategoria == "Transporte" and valor > 150:
            st.info("\U0001F695 Despesa alta com transporte - viagem ou manutenção?")
    
        with col2:
        # Descrição inteligente
            st.markdown("**📝 Descrição da Despesa**")
        
        # Sugestões baseadas na categoria
        sugestoes_categoria = {
            "Alimentação": ["Almoço", "Jantar", "Lanche", "Delivery", "Restaurante"],
            "Mercado": ["Compras mensais", "Feira", "Supermercado", "Açougue"],
            "Transporte": ["Uber", "Gasolina", "Ônibus", "Metrô", "Taxi"],
            "Casa": ["Conta de luz", "Água", "Internet", "Gás", "Aluguel"],
            "Compras Online": ["Amazon", "Magazine Luiza", "Mercado Livre", "Shopee"],
            "Farmácia": ["Medicamentos", "Remédios", "Farmácia"],
            "Outros": ["Diversos", "Variados"]
        }
        
        sugestoes_desc = sugestoes_categoria.get(subcategoria, [])
        if sugestoes_desc:
            descricao_sugerida = st.selectbox(
                "Sugestões rápidas:",
                [""] + sugestoes_desc + (sugestoes["descricoes_despesa"] if sugestoes["descricoes_despesa"] else [])
            )
        else:
            descricao_sugerida = ""
        
        descricao = st.text_input(
            "Ou digite uma nova:",
            value=descricao_sugerida,
            placeholder=f"Ex: {subcategoria} - {data.strftime('%d/%m')}",
            help="💡 Detalhe o que foi comprado para melhor controle"
        )
        
        # Dicas contextuais
        if subcategoria == "Fatura de Cartão":
            st.info("💡 **Dica:** Inclua o banco (ex: 'Nubank', 'Itaú')")
        elif subcategoria in ["Alimentação", "Mercado"]:
            st.info("💡 **Dica:** Inclua o local (ex: 'McDonald\'s', 'Extra')")
        
        # Preview da transação
        if valor > 0 and descricao:
            st.markdown("### 👀 Preview")
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
                st.metric("💰 Saldo Atual", f"R$ {saldo_atual:,.2f}")
            with col_impact2:
                st.metric("🔮 Saldo Após Compra", f"R$ {saldo_apos:,.2f}", f"-R$ {valor:,.2f}")
            
            if saldo_apos < 0:
                st.error("🚨 **ATENÇÃO:** Esta despesa deixará seu saldo negativo!")
            elif saldo_apos < 100:
                st.warning("⚠️ **CUIDADO:** Saldo ficará muito baixo após esta despesa")
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
                    st.warning(f"📊 **Gastos do dia:** R$ {gastos_hoje:.2f} + R$ {valor:.2f} = R$ {gastos_total_dia:.2f}")
    except:
        pass
    
    # Botões de ação
    col_btn1, col_btn2, col_btn3 = st.columns(3)
    
    with col_btn1:
        pode_salvar = len(erros) == 0 and valor > 0 and descricao.strip()
        
        if st.button(
            "💾 Confirmar Despesa", 
            type="primary", 
            disabled=not pode_salvar,
            use_container_width=True
        ):
            try:
                db = connect_db()
                colecao = db.get_collection("transacoes")
                
                # Limpa cache
                get_sugestoes_inteligentes.clear()
                
                result = colecao.insert_one({
                    "data": data.strftime("%d/%m/%Y"),
                    "valor": valor,
                    "descricao": descricao.strip(),
                    "categoria_principal": "Despesa",
                    "subcategoria": subcategoria,
                    "criado_em": datetime.now().isoformat()
                })
                
                if result.inserted_id:
                    st.success("✅ Despesa registrada com sucesso!")
                    
                    # Sugestões pós-despesa
                    if subcategoria in ["Mercado", "Compras Online"]:
                        st.info("💡 **Dica:** Considere anotar os itens comprados para melhor controle")
                    elif valor > 500:
                        st.info("💡 **Sugestão:** Que tal revisar seus objetivos financeiros?")
                    
                    import time
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Erro ao salvar")
                    
            except Exception as e:
                st.error(f"❌ Erro: {str(e)}")
    
    with col_btn2:
        # Botão para parcelar (futuro)
        if st.button("💳 Parcelar", use_container_width=True, disabled=True):
            st.info("🚧 Funcionalidade em desenvolvimento")
    
    with col_btn3:
        if st.button("🚫 Cancelar", use_container_width=True):
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
        **📊 Últimos 7 dias:**
        - Receitas: R$ {receitas_7d:,.2f}
        - Despesas: R$ {despesas_7d:,.2f}
        - Saldo: R$ {receitas_7d - despesas_7d:,.2f}
        """
    except:
        return "Erro ao gerar relatório"
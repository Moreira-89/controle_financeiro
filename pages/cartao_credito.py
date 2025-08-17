import streamlit as st
from datetime import datetime
from services.cartao_service import CartaoService
import pandas as pd
import plotly.express as px

def main():
    st.set_page_config(
        page_title="Cartões de Crédito",
        layout="wide",
        page_icon="\U0001F4B3"
    )
    
    # CSS customizado
    st.markdown("""
    <style>
    .cartao-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 1rem;
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    .limite-bar {
        background: rgba(255,255,255,0.3);
        border-radius: 10px;
        height: 8px;
        margin-top: 0.5rem;
    }
    .limite-usado {
        background: #27ae60;
        height: 100%;
        border-radius: 10px;
        transition: width 0.3s ease;
    }
    .limite-alerta {
        background: #e74c3c;
    }
    .limite-aviso {
        background: #f39c12;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    col_h1, col_h2, col_h3 = st.columns([2, 2, 1])
    
    with col_h1:
        st.title("\U0001F4B3 Meus Cartões de Crédito")
        st.markdown("**Gerencie seus cartões e faturas**")
    
    with col_h2:
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("\u2795 Novo Cartão", type="primary", use_container_width=True):
                novo_cartao_modal()
        with col_btn2:
            if st.button("\U0001F6D2 Nova Compra", type="secondary", use_container_width=True):
                nova_compra_modal()
    
    with col_h3:
        if st.button("\U0001F4CA Relatórios", use_container_width=True):
            st.session_state.show_relatorio_cartoes = not st.session_state.get('show_relatorio_cartoes', False)
    
    # Sidebar
    setup_sidebar()
    
    # Serviço
    service = CartaoService()
    
    # Estatísticas gerais
    render_estatisticas_gerais(service)
    
    # Relatório (se ativado)
    if st.session_state.get('show_relatorio_cartoes', False):
        render_relatorio_completo(service)
    
    # Lista de cartões
    render_cartoes(service)

    # Visualizar transações de crédito
    view_transacoes_credito()

def setup_sidebar():
    """Configuração da sidebar"""
    st.sidebar.markdown("### \U0001F680 Ações Rápidas")
    
    if st.sidebar.button("\U0001F4B3 Novo Cartão", key="sidebar_cartao"):
        novo_cartao_modal()
    if st.sidebar.button("\U0001F6D2 Nova Compra", key="sidebar_compra"):
        nova_compra_modal()
    
    st.sidebar.markdown("### \U0001F4CA Navegação")
    st.sidebar.page_link("app.py", label="\U0001F3E0 Dashboard", icon=":material/home:")
    st.sidebar.page_link("pages/transacao.py", label="\U0001F4CB Transações", icon=":material/list_alt:")
    st.sidebar.page_link("pages/objetivos.py", label="\U0001F3AF Objetivos", icon=":material/star:")
    
    st.sidebar.markdown("---")
    
    if st.sidebar.button("\U0001F6AA Sair", icon=":material/logout:"):
        st.session_state.authenticated = False
        st.rerun()

def render_estatisticas_gerais(service):
    """Renderiza estatísticas gerais dos cartões"""
    stats = service.get_estatisticas_cartoes()
    
    if stats["total_cartoes"] == 0:
        st.info("\U0001F4DD Você ainda não possui cartões cadastrados. Adicione seu primeiro cartão!")
        return
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("\U0001F4B3 Total de Cartões", stats["total_cartoes"])
    
    with col2:
        st.metric("\U0001F4B0 Limite Total", f"R$ {stats['limite_total']:,.2f}")
    
    with col3:
        delta = f"R$ {stats['valor_usado']:,.2f}"
        delta_color = "normal" if stats["percentual_usado"] < 50 else "inverse"
        st.metric("\U0001F6D2 Valor Usado", delta, delta_color=delta_color)
    
    with col4:
        st.metric("\U0001F513 Limite Disponível", f"R$ {stats['limite_disponivel']:,.2f}")
    
    # Barra de progresso geral
    if stats["limite_total"] > 0:
        progress = stats["percentual_usado"] / 100
        
        if stats["percentual_usado"] > 90:
            st.error(f"\U0001F6A8 **ATENÇÃO:** Você está usando {stats['percentual_usado']:.1f}% do seu limite total!")
        elif stats["percentual_usado"] > 70:
            st.warning(f"\u26A0\uFE0F **CUIDADO:** {stats['percentual_usado']:.1f}% do limite total em uso")
        elif stats["percentual_usado"] > 50:
            st.info(f"\U0001F4CA {stats['percentual_usado']:.1f}% do limite total utilizado")
        else:
            st.success(f"\u2705 Apenas {stats['percentual_usado']:.1f}% do limite total em uso")
        st.progress(progress)

def render_cartoes(service):
    """Renderiza lista de cartões"""
    cartoes = service.listar_cartoes()
    
    st.markdown("### \U0001F4B3 Seus Cartões")
    
    # Grid de cartões
    cols_per_row = 1
    for i in range(0, len(cartoes), cols_per_row):
        cols = st.columns(cols_per_row)
        
        for j, col in enumerate(cols):
            if i + j < len(cartoes):
                with col:
                    render_cartao_card(service, cartoes[i + j])

def render_cartao_card(service, cartao):
    """Renderiza um card individual de cartão"""
    try:
        # Validação de dados essenciais
        if not cartao or not isinstance(cartao, dict):
            st.error("Dados do cartão inválidos")
            return
        
        campos_obrigatorios = ['_id', 'nome', 'banco', 'bandeira', 'limite', 'dia_vencimento', 'dia_fechamento']
        for campo in campos_obrigatorios:
            if campo not in cartao:
                st.error(f"Campo obrigatório '{campo}' não encontrado no cartão")
                return
        
        # Calcular valores com validação
        valor_usado = service.calcular_fatura_atual(cartao["_id"])
        valor_usado = max(0, valor_usado)  # Garantir que não seja negativo
        
        limite = max(0, cartao["limite"])  # Garantir que limite não seja negativo
        limite_disponivel = limite - valor_usado
        
        # Calcular percentual usado
        percentual_usado = 0
        if limite > 0:
            percentual_usado = (valor_usado / limite) * 100
            percentual_usado = min(100, max(0, percentual_usado))  # Limitar entre 0 e 100
        
        # Cor da barra de limite com lógica melhorada
        cor_limite = "limite-usado"
        if percentual_usado > 90:
            cor_limite += " limite-alerta"
        elif percentual_usado > 70:
            cor_limite += " limite-aviso"
        
        # Formatação segura dos valores
        def formatar_moeda(valor):
            """Formata valor para moeda brasileira"""
            try:
                return f"R$ {float(valor):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            except (ValueError, TypeError):
                return "R$ 0,00"
        
        # Validação e formatação de datas
        dia_vencimento = str(cartao.get('dia_vencimento', '??')).zfill(2)
        dia_fechamento = str(cartao.get('dia_fechamento', '??')).zfill(2)
        
        # HTML do cartão com escape de dados
        nome_cartao = str(cartao['nome']).strip() or "Cartão sem nome"
        banco_cartao = str(cartao['banco']).strip() or "Banco não informado"
        bandeira_display = str(cartao['bandeira']).upper().strip() or "BANDEIRA"
        
        # Layout usando componentes Streamlit nativos
        with st.container(border=True):
            # Cabeçalho do cartão
            col_info, col_limite = st.columns([2, 1])
            
            with col_info:
                st.markdown(f"### {nome_cartao}")
                st.markdown(f"**{banco_cartao}** • {bandeira_display}")
            
            with col_limite:
                st.markdown("**Limite**")
                st.markdown(f"## {formatar_moeda(limite)}")
            
            # Informações de uso
            st.markdown("---")
            
            col_usado, col_percent = st.columns([2, 1])
            with col_usado:
                st.markdown(f"**Usado:** {formatar_moeda(valor_usado)}")
            with col_percent:
                st.markdown(f"**{percentual_usado:.1f}%**")
            
            # Barra de progresso nativa do Streamlit
            st.progress(percentual_usado / 100)
            
            # Informações finais
            st.markdown(f"**Disponível:** {formatar_moeda(limite_disponivel)}")
            st.markdown(f"*Venc: dia {dia_vencimento} • Fech: dia {dia_fechamento}*")
    
                
    except Exception as e:
        st.error(f"Erro ao renderizar cartão: {str(e)}")
        st.exception(e)

def render_relatorio_completo(service):
    """Renderiza relatório completo dos cartões"""
    with st.expander("\U0001F4CA Relatório Detalhado", expanded=True):
        cartoes = service.listar_cartoes()
        
        if not cartoes:
            st.info("Nenhum cartão para gerar relatório")
            return
        
        # Preparar dados para gráficos
        dados_limite = []
        dados_gastos_categoria = {}
        
        for cartao in cartoes:
            valor_usado = service.calcular_fatura_atual(cartao["_id"])
            dados_limite.append({
                "Cartão": cartao["nome"],
                "Limite": cartao["limite"],
                "Usado": valor_usado,
                "Disponível": cartao["limite"] - valor_usado
            })
            
            # Compras por categoria
            compras = service.listar_compras(cartao["_id"])
            for compra in compras:
                categoria = compra["categoria"]
                valor = compra["valor_parcela"] if compra["parcelas"] > 1 else compra["valor"]
                
                if categoria not in dados_gastos_categoria:
                    dados_gastos_categoria[categoria] = 0
                dados_gastos_categoria[categoria] += valor
        
        col_g1, col_g2 = st.columns(2)
        
        with col_g1:
            # Gráfico de limite usado vs disponível
            if dados_limite:
                import pandas as pd
                df_limite = pd.DataFrame(dados_limite)
                
                fig_limite = px.bar(
                    df_limite,
                    x="Cartão",
                    y=["Usado", "Disponível"],
                    title="\U0001F4B3 Limite Usado vs Disponível",
                    color_discrete_map={"Usado": "#e74c3c", "Disponível": "#27ae60"}
                )
                st.plotly_chart(fig_limite, use_container_width=True)
        
        with col_g2:
            # Gráfico de gastos por categoria
            if dados_gastos_categoria:
                fig_categoria = px.pie(
                    values=list(dados_gastos_categoria.values()),
                    names=list(dados_gastos_categoria.keys()),
                    title="\U0001F6D2 Gastos por Categoria"
                )
                st.plotly_chart(fig_categoria, use_container_width=True)

@st.dialog("\u2795 Novo Cartão")  # ➕
def novo_cartao_modal():
    """Modal para adicionar novo cartão"""
    st.markdown("### Cadastrar novo cartão de crédito")
    
    col1, col2 = st.columns(2)
    
    with col1:
        nome = st.text_input("\U0001F4B3 Nome do Cartão", placeholder="Ex: Cartão Principal")
        banco = st.text_input("\U0001F3E6 Banco", placeholder="Ex: Nubank, Itaú, Bradesco")
    
        bandeira = st.selectbox("\U0001F3F7\uFE0F Bandeira", [  # 🏷️
            "Visa", "Mastercard", "Elo", "American Express", "Hipercard"
        ])
        limite = st.number_input("\U0001F4B0 Limite (R$)", min_value=100.0, step=100.0, value=1000.0)
    
    with col2:
        dia_vencimento = st.number_input("\U0001F4C5 Dia do Vencimento", min_value=1, max_value=31, value=10)
        dia_fechamento = st.number_input("\U0001F4CA Dia do Fechamento", min_value=1, max_value=31, value=5)
        
    # Validações
    erros = []
    if not nome.strip():
        erros.append("Nome do cartão é obrigatório")
    if not banco.strip():
        erros.append("Banco é obrigatório")
    if limite <= 0:
        erros.append("Limite deve ser maior que zero")
    if dia_vencimento == dia_fechamento:
        erros.append("Dia do vencimento deve ser diferente do fechamento")
    
    for erro in erros:
        st.error(f"\u26A0\uFE0F {erro}")
    
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        if st.button("\U0001F4BE Salvar Cartão", type="primary", disabled=len(erros) > 0, use_container_width=True):
            service = CartaoService()
            dados = {
                "nome": nome.strip(),
                "banco": banco.strip(),
                "bandeira": bandeira,
                "limite": limite,
                "dia_vencimento": dia_vencimento,
                "dia_fechamento": dia_fechamento
            }
            
            if service.criar_cartao(dados):
                st.success("\u2705 Cartão cadastrado com sucesso!")
                st.rerun()
            else:
                st.error("\u274C Erro ao cadastrar cartão")
    
    with col_btn2:
        if st.button("\U0001F6AB Cancelar", use_container_width=True):
            st.rerun()

@st.dialog("\U0001F6D2 Nova Compra")  # 🛒
def nova_compra_modal(cartao_id=None):
    """Modal para adicionar nova compra"""
    st.markdown("### Registrar nova compra no cartão")
    
    service = CartaoService()
    cartoes = service.listar_cartoes()
    
    if not cartoes:
        st.error("\u274C Você precisa cadastrar um cartão primeiro!")
        if st.button("\u2795 Cadastrar Cartão", type="primary"):
            st.rerun()
            novo_cartao_modal()
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Seleção do cartão
        if cartao_id:
            cartao_selecionado = next((c for c in cartoes if c["_id"] == cartao_id), cartoes[0])
            cartao_opcoes = [cartao_selecionado["nome"]]
            cartao_index = 0
        else:
            cartao_opcoes = [c["nome"] for c in cartoes]
            cartao_index = 0
        
        cartao_nome = st.selectbox("\U0001F4B3 Cartão", cartao_opcoes, index=cartao_index)
        cartao_escolhido = next(c for c in cartoes if c["nome"] == cartao_nome)
        
        # Mostrar limite disponível
        valor_usado = service.calcular_fatura_atual(cartao_escolhido["_id"])
        
        data_compra = st.date_input("\U0001F4C5 Data da Compra", value=datetime.now().date())

        parcelas = st.number_input("\U0001F522 Parcelas", min_value=1, max_value=24, value=1)
        
        if parcelas > 1:
            valor_parcela = valor / parcelas
            st.info(f"\U0001F4A1 {parcelas}x de R$ {valor_parcela:.2f}")
    
    with col2:
        descricao = st.text_input("\U0001F4DD Descrição", placeholder="Ex: Notebook Dell")
        categorias = sorted([
            "Alimentação", "Mercado", "Transporte", "Roupas", "Eletrônicos",
            "Casa e Decoração", "Saúde", "Educação", "99 App",
            "Uber", "Farmácia", "Serviços de Streaming", "Outros"
        ])
        categoria = st.selectbox("\U0001F3F7\uFE0F Categoria", categorias)
        
        valor = st.number_input("\U0001F4B0 Valor (R$)", min_value=0.01, step=0.01)

    
    # Validações
    erros = []
    if not descricao.strip():
        erros.append("Descrição é obrigatória")
    if valor <= 0:
        erros.append("Valor deve ser maior que zero")
    if data_compra > datetime.now().date():
        erros.append("Data não pode ser no futuro")
    
    # Alertas
    alertas = []
    if valor > 1000:
        alertas.append("\U0001F4B0 Compra de alto valor! Confirme se está correto.")
    if parcelas > 12:
        alertas.append("\U0001F4C5 Muitas parcelas podem comprometer o orçamento futuro")
    
    for alerta in alertas:
        st.warning(alerta)
    for erro in erros:
        st.error(f"\u26A0\uFE0F {erro}")

    
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        if st.button("\U0001F6D2 Registrar Compra", type="primary", disabled=len(erros) > 0, use_container_width=True):
            dados_compra = {
                "cartao_id": cartao_escolhido["_id"],
                "descricao": descricao.strip(),
                "valor": valor,
                "categoria": categoria,
                "data_compra": data_compra,
                "parcelas": parcelas
            }
            
            if service.adicionar_compra(dados_compra):
                st.success("\u2705 Compra registrada com sucesso!")
                
                # Alertas pós-compra
                novo_valor_usado = valor_usado + (valor / parcelas if parcelas > 1 else valor)
                novo_percentual = (novo_valor_usado / cartao_escolhido["limite"]) * 100
                
                if novo_percentual > 80:
                    st.warning(f"\u26A0\uFE0F Cartão agora está com {novo_percentual:.1f}% do limite usado!")
                
                import time
                time.sleep(1)
                st.rerun()
            else:
                st.error("\u274C Erro ao registrar compra")  # ❌
    
    with col_btn2:
        if st.button("\U0001F6AB Cancelar", use_container_width=True):
            st.rerun()

def view_transacoes_credito():
    service = CartaoService()
    cartoes = service.listar_cartoes()
    
    if not cartoes:
        st.info("Nenhum cartão cadastrado.")
        return
    
    nomes_cartoes = [c["nome"] for c in cartoes]
    cartao_selecionado = st.selectbox("Selecione o cartão", nomes_cartoes)
    cartao_obj = next(c for c in cartoes if c["nome"] == cartao_selecionado)
    
    # Filtro de mês/ano
    hoje = datetime.now()
    mes_ano = st.selectbox(
        "Filtrar por mês/ano",
        options=[hoje.strftime("%Y-%m")] + [
            (hoje.replace(month=m)).strftime("%Y-%m") for m in range(1, 13)
        ]
    )
    
    compras = service.listar_compras(cartao_obj["_id"], mes_ano=mes_ano)
    
    if not compras:
        st.info("Nenhuma transação encontrada para este cartão neste período.")
        return
    
    df = pd.DataFrame(compras)
    df = df[["data_compra", "descricao", "categoria", "valor"]]
    df.rename(columns={
        "data_compra": "Data",
        "descricao": "Descrição",
        "categoria": "Categoria",
        "valor": "Valor (R$)"
    }, inplace=True)
    
    st.subheader(f"Transações do Cartão: {cartao_selecionado} ({mes_ano})")
    st.dataframe(df, use_container_width=True, hide_index=True, height=400)

if __name__ == "__main__":
    main()
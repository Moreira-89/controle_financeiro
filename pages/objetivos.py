from services.objetivos_service import ObjetivosService
import streamlit as st
from datetime import datetime, timedelta

def renderizar_objetivos():

    st.set_page_config(
    page_title="\U0001F3AF Objetivos Financeiros",
    layout="wide"
    )
    st.sidebar.markdown("### Navegação")
    st.sidebar.page_link("pages/transacao.py", label="\U0001F4CB Transações", icon=":material/list_alt:")
    st.sidebar.page_link("pages/objetivos.py", label="\U0001F3AF Objetivos", icon=":material/star:")
    st.sidebar.page_link("app.py", label="\U0001F3E0 Home", icon=":material/home:")

    st.sidebar.markdown("---")
    
    if st.sidebar.button("\U0001F6AA Sair", icon=":material/logout:"):
        st.session_state.authenticated = False
        st.rerun()
    
    st.title("\U0001F3AF Meus Objetivos Financeiros")
    
    service = ObjetivosService()
    
    if st.button("\u2795 Novo Objetivo", type="primary"):
        novo_objetivo_modal()
    
    objetivos = service.listar_objetivos()
    
    if not objetivos:
        st.info("\U0001F4DD Você ainda não possui objetivos cadastrados. Crie seu primeiro objetivo!")
        return
    
    for objetivo in objetivos:
        with st.expander(f"\U0001F3AF {objetivo['titulo']}", expanded=True):
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:

                progresso = service.calcular_progresso(
                    objetivo['valor_atual'], 
                    objetivo['valor_meta']
                )
                st.progress(progresso / 100)
                st.write(f"**Progresso:** {progresso:.1f}%")
                st.write(f"**Descrição:** {objetivo['descricao']}")
            
            with col2:
                st.metric(
                    "\U0001F4B0 Valor Atual",
                    f"R$ {objetivo['valor_atual']:,.2f}",
                    f"R$ {objetivo['valor_meta'] - objetivo['valor_atual']:,.2f} restantes"
                )
            
            with col3:
                dias = service.dias_restantes(objetivo['prazo'])
                cor_prazo = "\U0001F534" if dias < 30 else "\U0001F7E1" if dias < 90 else "\U0001F7E2"
                st.metric(
                    f"{cor_prazo} Prazo",
                    f"{dias} dias",
                    objetivo['prazo']
                )
            
            # Ações
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                if st.button(f"📈 Atualizar", key=f"update_{objetivo['_id']}"):
                    atualizar_objetivo_modal(objetivo)
            with col_b:
                if st.button(f"✏️ Editar", key=f"edit_{objetivo['_id']}"):
                    editar_objetivo_modal(objetivo)
            with col_c:
                if st.button(f"✅ Concluir", key=f"complete_{objetivo['_id']}"):
                    service.colecao.update_one(
                        {"_id": objetivo['_id']},
                        {"$set": {"status": "concluido"}}
                    )
                    st.success("Objetivo concluído! 🎉")
                    st.rerun()


@st.dialog("Novo Objetivo")
def novo_objetivo_modal():
    service = ObjetivosService()
    
    titulo = st.text_input("\U0001F3AF Título do Objetivo", placeholder="Ex: Comprar casa própria")
    descricao = st.text_area("\U0001F4DD Descrição", placeholder="Descreva seu objetivo...")
    
    col1, col2 = st.columns(2)
    with col1:
        valor_meta = st.number_input("\U0001F48E Valor da Meta (R$)", min_value=1.0, step=100.0)
        valor_atual = st.number_input("\U0001F4B0 Valor Atual (R$)", min_value=0.0, step=100.0)
    
    with col2:
        categoria = st.selectbox("\U0001F4C5 Categoria", [
            "curto_prazo", "medio_prazo", "longo_prazo"
        ], format_func=lambda x: {
            "curto_prazo": "Curto Prazo (até 1 ano)",
            "medio_prazo": "Médio Prazo (1-5 anos)", 
            "longo_prazo": "Longo Prazo (5+ anos)"
        }[x])
        
        prazo = st.date_input(
            "\U0001F5D3 Data Limite",
            value=datetime.now() + timedelta(days=365)
        )
    
    if st.button("\U0001F4BE Salvar Objetivo", type="primary"):
        if not titulo:
            st.error("\u26A0 Título é obrigatório")
            return
        
        dados = {
            "titulo": titulo,
            "descricao": descricao,
            "valor_meta": valor_meta,
            "valor_atual": valor_atual,
            "categoria": categoria,
            "prazo": prazo
        }
        
        if service.criar_objetivo(dados):
            st.success("\u2705 Objetivo criado com sucesso!")
            st.rerun()
        else:
            st.error("\u274C Erro ao criar objetivo")


@st.dialog("Atualizar Progresso")
def atualizar_objetivo_modal(objetivo):
    """Modal para atualizar apenas o progresso do objetivo"""
    service = ObjetivosService()
    
    st.write(f"**Objetivo:** {objetivo['titulo']}")
    st.write(f"**Meta:** R$ {objetivo['valor_meta']:,.2f}")
    
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Valor Atual:** R$ {objetivo['valor_atual']:,.2f}")
        progresso_atual = service.calcular_progresso(objetivo['valor_atual'], objetivo['valor_meta'])
        st.progress(progresso_atual / 100)
        st.write(f"**Progresso:** {progresso_atual:.1f}%")
    
    with col2:

        novo_valor = st.number_input(
            "\U0001F4B0 Novo Valor Atual (R$)",
            min_value=0.0,
            value=float(objetivo['valor_atual']),
            step=10.0,
            key=f"novo_valor_{objetivo['_id']}"
        )
        
        if novo_valor != objetivo['valor_atual']:
            novo_progresso = service.calcular_progresso(novo_valor, objetivo['valor_meta'])
            diferenca = novo_valor - objetivo['valor_atual']
            
            if diferenca > 0:
                st.success(f"\U0001F4C8 +R$ {diferenca:,.2f}")
            else:
                st.error(f"\U0001F4C9 R$ {diferenca:,.2f}")
            
            st.info(f"\U0001F3AF Novo progresso: {novo_progresso:.1f}%")
    
    st.markdown("**\u26A1 Adição Rápida:**")
    col_add1, col_add2, col_add3, col_add4 = st.columns(4)
    
    with col_add1:
        if st.button("+ R$ 50", key=f"add50_{objetivo['_id']}"):
            novo_valor = objetivo['valor_atual'] + 50
            st.session_state[f"novo_valor_{objetivo['_id']}"] = novo_valor
            st.rerun()
    
    with col_add2:
        if st.button("+ R$ 100", key=f"add100_{objetivo['_id']}"):
            novo_valor = objetivo['valor_atual'] + 100
            st.session_state[f"novo_valor_{objetivo['_id']}"] = novo_valor
            st.rerun()
    
    with col_add3:
        if st.button("+ R$ 500", key=f"add500_{objetivo['_id']}"):
            novo_valor = objetivo['valor_atual'] + 500
            st.session_state[f"novo_valor_{objetivo['_id']}"] = novo_valor
            st.rerun()
    
    with col_add4:
        if st.button("+ R$ 1000", key=f"add1000_{objetivo['_id']}"):
            novo_valor = objetivo['valor_atual'] + 1000
            st.session_state[f"novo_valor_{objetivo['_id']}"] = novo_valor
            st.rerun()
    
    st.markdown("---")
    
    if st.button("\U0001F4BE Salvar Atualização", type="primary"):
        if novo_valor < 0:
            st.error("\u26A0 Valor não pode ser negativo")
            return
        
        if service.atualizar_progresso(objetivo['_id'], novo_valor):

            if novo_valor >= objetivo['valor_meta']:
                st.balloons()
                st.success("\U0001F389 **PARABÉNS!** Você atingiu sua meta!")
                
                if st.button("\u2705 Marcar como Concluído", type="primary"):
                    service.colecao.update_one(
                        {"_id": objetivo['_id']},
                        {"$set": {"status": "concluido"}}
                    )
                    st.success("Objetivo marcado como concluído!")
            else:
                st.success("\u2705 Progresso atualizado com sucesso!")
            
            st.rerun()
        else:
            st.error("\u274C Erro ao atualizar progresso")

@st.dialog("Editar Objetivo")
def editar_objetivo_modal(objetivo):
    """Modal para editar objetivo completo"""
    service = ObjetivosService()
    
    st.write(f"**Editando:** {objetivo['titulo']}")
    
    # Campos editáveis
    titulo = st.text_input(
        "\U0001F3AF Título do Objetivo", 
        value=objetivo['titulo'],
        key=f"edit_titulo_{objetivo['_id']}"
    )
    
    descricao = st.text_area(
        "\U0001F4DD Descrição", 
        value=objetivo.get('descricao', ''),
        key=f"edit_desc_{objetivo['_id']}"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        valor_meta = st.number_input(
            "\U0001F48E Valor da Meta (R$)", 
            min_value=1.0,
            value=float(objetivo['valor_meta']),
            step=100.0,
            key=f"edit_meta_{objetivo['_id']}"
        )
        
        valor_atual = st.number_input(
            "\U0001F4B0 Valor Atual (R$)", 
            min_value=0.0,
            value=float(objetivo['valor_atual']),
            step=100.0,
            key=f"edit_atual_{objetivo['_id']}"
        )
    
    with col2:
        categoria = st.selectbox(
            "\U0001F4C5 Categoria",
            ["curto_prazo", "medio_prazo", "longo_prazo"],
            index=["curto_prazo", "medio_prazo", "longo_prazo"].index(objetivo['categoria']),
            format_func=lambda x: {
                "curto_prazo": "Curto Prazo (até 1 ano)",
                "medio_prazo": "Médio Prazo (1-5 anos)", 
                "longo_prazo": "Longo Prazo (5+ anos)"
            }[x],
            key=f"edit_cat_{objetivo['_id']}"
        )
        
        prazo_atual = datetime.strptime(objetivo['prazo'], "%Y-%m-%d").date()
        prazo = st.date_input(
            "\U0001F5D3 Data Limite",
            value=prazo_atual,
            key=f"edit_prazo_{objetivo['_id']}"
        )
    
    # Preview das mudanças
    mudancas = []
    if titulo != objetivo['titulo']:
        mudancas.append(f"\U0001F4DD Título: {objetivo['titulo']} → {titulo}")
    if valor_meta != objetivo['valor_meta']:
        mudancas.append(f"\U0001F48E Meta: R$ {objetivo['valor_meta']:,.2f} → R$ {valor_meta:,.2f}")
    if valor_atual != objetivo['valor_atual']:
        mudancas.append(f"\U0001F4B0 Atual: R$ {objetivo['valor_atual']:,.2f} → R$ {valor_atual:,.2f}")
    if str(prazo) != objetivo['prazo']:
        mudancas.append(f"\U0001F4C5 Prazo: {objetivo['prazo']} → {prazo}")
    
    if mudancas:
        st.markdown("**\U0001F504 Mudanças detectadas:**")
        for mudanca in mudancas:
            st.markdown(f"- {mudanca}")
    
    col_save, col_cancel = st.columns(2)
    
    with col_save:
        if st.button("\U0001F4BE Salvar Alterações", type="primary"):
            if not titulo:
                st.error("\u26A0 Título é obrigatório")
                return
            
            dados_atualizados = {
                "titulo": titulo,
                "descricao": descricao,
                "valor_meta": valor_meta,
                "valor_atual": valor_atual,
                "categoria": categoria,
                "prazo": prazo
            }
            
            if service.editar_objetivo(objetivo['_id'], dados_atualizados):
                st.success("\u2705 Objetivo editado com sucesso!")
                st.rerun()
            else:
                st.error("\u274C Erro ao editar objetivo")
    
    with col_cancel:
        if st.button("\u274C Cancelar"):
            st.rerun()


if __name__ == "__main__":
    renderizar_objetivos()
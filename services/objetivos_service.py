import streamlit as st
from datetime import datetime, timedelta
from config.db_config import connect_db 

class ObjetivosService:
    def __init__(self):
        self.db = connect_db()
        self.colecao = self.db.get_collection("objetivos")
    
    def criar_objetivo(self, dados_objetivo: dict):
        """Cria novo objetivo financeiro"""
        objetivo = {
            "user_email": st.session_state.get("user_email", ""),
            "titulo": dados_objetivo["titulo"],
            "descricao": dados_objetivo.get("descricao", ""),
            "valor_meta": float(dados_objetivo["valor_meta"]),
            "valor_atual": float(dados_objetivo.get("valor_atual", 0)),
            "prazo": dados_objetivo["prazo"].strftime("%Y-%m-%d"),
            "categoria": dados_objetivo["categoria"],
            "status": "ativo",
            "data_criacao": datetime.now().strftime("%Y-%m-%d"),
            "data_ultima_atualizacao": datetime.now().strftime("%Y-%m-%d")
        }
        
        result = self.colecao.insert_one(objetivo)
        return result.inserted_id is not None
    
    def listar_objetivos(self, status="ativo"):
        """Lista objetivos do usuário logado"""
        user_email = st.session_state.get("user_email", "")
        objetivos = list(self.colecao.find({
            "user_email": user_email,
            "status": status
        }).sort("data_criacao", -1))
        
        return objetivos
    
    def atualizar_progresso(self, objetivo_id, novo_valor):
        """Atualiza progresso de um objetivo"""
        result = self.colecao.update_one(
            {"_id": objetivo_id},
            {
                "$set": {
                    "valor_atual": float(novo_valor),
                    "data_ultima_atualizacao": datetime.now().strftime("%Y-%m-%d")
                }
            }
        )
        return result.modified_count > 0
    
    def editar_objetivo(self, objetivo_id, dados_atualizados):
        """Edita objetivo completo"""
        update_data = {
            "data_ultima_atualizacao": datetime.now().strftime("%Y-%m-%d")
        }
        
        # Atualiza apenas campos fornecidos
        if "titulo" in dados_atualizados:
            update_data["titulo"] = dados_atualizados["titulo"]
        if "descricao" in dados_atualizados:
            update_data["descricao"] = dados_atualizados["descricao"]
        if "valor_meta" in dados_atualizados:
            update_data["valor_meta"] = float(dados_atualizados["valor_meta"])
        if "valor_atual" in dados_atualizados:
            update_data["valor_atual"] = float(dados_atualizados["valor_atual"])
        if "prazo" in dados_atualizados:
            update_data["prazo"] = dados_atualizados["prazo"].strftime("%Y-%m-%d")
        if "categoria" in dados_atualizados:
            update_data["categoria"] = dados_atualizados["categoria"]
            
        result = self.colecao.update_one(
            {"_id": objetivo_id},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    def calcular_progresso(self, valor_atual, valor_meta):
        """Calcula percentual de progresso"""
        if valor_meta <= 0:
            return 0
        return min((valor_atual / valor_meta) * 100, 100)
    
    def dias_restantes(self, prazo_str):
        """Calcula dias restantes para meta"""
        prazo = datetime.strptime(prazo_str, "%Y-%m-%d")
        hoje = datetime.now()
        delta = prazo - hoje
        return delta.days
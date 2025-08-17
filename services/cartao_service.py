import streamlit as st
from datetime import datetime, timedelta, date
from config.db_config import connect_db
import pandas as pd

class CartaoService:
    def __init__(self):
        self.db = connect_db()
        self.colecao = self.db.get_collection("cartoes")
        self.colecao_faturas = self.db.get_collection("faturas_cartao")
        self.colecao_compras = self.db.get_collection("compras_cartao")
    
    def criar_cartao(self, dados_cartao: dict):
        """Cria um novo cartão de crédito"""
        try:
            cartao = {
                "user_email": st.session_state.get("user_email", ""),
                "nome": dados_cartao["nome"],
                "bandeira": dados_cartao["bandeira"],
                "banco": dados_cartao["banco"],
                "limite": float(dados_cartao["limite"]),
                "dia_vencimento": int(dados_cartao["dia_vencimento"]),
                "dia_fechamento": int(dados_cartao["dia_fechamento"]),
                "ativo": True,
                "data_criacao": datetime.now().isoformat()
            }
            
            result = self.colecao.insert_one(cartao)
            return result.inserted_id is not None
            
        except Exception as e:
            st.error(f"Erro ao criar cartão: {str(e)}")
            return False
    
    def listar_cartoes(self, apenas_ativos=True):
        """Lista cartões do usuário"""
        try:
            user_email = st.session_state.get("user_email", "")
            filtro = {"user_email": user_email}
            
            if apenas_ativos:
                filtro["ativo"] = True
            
            cartoes = list(self.colecao.find(filtro).sort("nome", 1))
            return cartoes
            
        except Exception as e:
            st.error(f"Erro ao listar cartões: {str(e)}")
            return []
    
    def get_cartao(self, cartao_id):
        """Busca cartão por ID"""
        try:
            return self.colecao.find_one({"_id": cartao_id})
        except Exception as e:
            st.error(f"Erro ao buscar cartão: {str(e)}")
            return None
    
    def adicionar_compra(self, dados_compra: dict):
        """Adiciona uma compra no cartão"""
        try:
            compra = {
                "user_email": st.session_state.get("user_email", ""),
                "cartao_id": dados_compra["cartao_id"],
                "descricao": dados_compra["descricao"],
                "valor": float(dados_compra["valor"]),
                "categoria": dados_compra["categoria"],
                "data_compra": dados_compra["data_compra"].strftime("%Y-%m-%d"),
                "parcelas": int(dados_compra.get("parcelas", 1)),
                "valor_parcela": float(dados_compra["valor"]) / int(dados_compra.get("parcelas", 1)),
                "data_criacao": datetime.now().isoformat()
            }
            
            result = self.colecao_compras.insert_one(compra)
            return result.inserted_id is not None
            
        except Exception as e:
            st.error(f"Erro ao adicionar compra: {str(e)}")
            return False
    
    def listar_compras(self, cartao_id=None, mes_ano=None):
        """Lista compras do cartão"""
        try:
            user_email = st.session_state.get("user_email", "")
            filtro = {"user_email": user_email}
            
            if cartao_id:
                filtro["cartao_id"] = cartao_id
            
            compras = list(self.colecao_compras.find(filtro).sort("data_compra", -1))
            
            if mes_ano:
                # Filtrar por mês/ano específico
                compras_filtradas = []
                for compra in compras:
                    data_compra = datetime.strptime(compra["data_compra"], "%Y-%m-%d")
                    if data_compra.strftime("%Y-%m") == mes_ano:
                        compras_filtradas.append(compra)
                return compras_filtradas
            
            return compras
            
        except Exception as e:
            st.error(f"Erro ao listar compras: {str(e)}")
            return []
    
    def calcular_fatura_atual(self, cartao_id):
        """Calcula o valor da fatura atual do cartão"""
        try:
            cartao = self.get_cartao(cartao_id)
            if not cartao:
                return 0.0
            
            hoje = datetime.now()
            dia_fechamento = cartao["dia_fechamento"]
            
            # Determinar período da fatura atual
            if hoje.day <= dia_fechamento:
                # Fatura atual: mês anterior até hoje
                inicio_periodo = (hoje.replace(day=dia_fechamento) - timedelta(days=30)).replace(day=dia_fechamento+1)
            else:
                # Fatura atual: dia do fechamento até hoje
                inicio_periodo = hoje.replace(day=dia_fechamento+1)
            
            # Buscar compras do período
            compras = self.listar_compras(cartao_id)
            total_fatura = 0.0
            
            for compra in compras:
                data_compra = datetime.strptime(compra["data_compra"], "%Y-%m-%d")
                
                if data_compra >= inicio_periodo and data_compra <= hoje:
                    # Se for parcelado, considera apenas uma parcela
                    if compra["parcelas"] > 1:
                        total_fatura += compra["valor_parcela"]
                    else:
                        total_fatura += compra["valor"]
            
            return total_fatura
            
        except Exception as e:
            st.error(f"Erro ao calcular fatura: {str(e)}")
            return 0.0
    
    def gerar_fatura(self, cartao_id, mes_ano):
        """Gera fatura detalhada do cartão para um mês específico"""
        try:
            cartao = self.get_cartao(cartao_id)
            compras = self.listar_compras(cartao_id, mes_ano)
            
            if not cartao or not compras:
                return None
            
            # Agrupar compras por categoria
            categorias = {}
            total_fatura = 0.0
            
            for compra in compras:
                categoria = compra["categoria"]
                valor = compra["valor_parcela"] if compra["parcelas"] > 1 else compra["valor"]
                
                if categoria not in categorias:
                    categorias[categoria] = []
                
                categorias[categoria].append({
                    "descricao": compra["descricao"],
                    "valor": valor,
                    "data": compra["data_compra"],
                    "estabelecimento": compra.get("estabelecimento", ""),
                    "parcelas": compra["parcelas"]
                })
                
                total_fatura += valor
            
            return {
                "cartao": cartao,
                "mes_ano": mes_ano,
                "categorias": categorias,
                "total": total_fatura,
                "limite_disponivel": cartao["limite"] - total_fatura,
                "percentual_usado": (total_fatura / cartao["limite"]) * 100 if cartao["limite"] > 0 else 0
            }
            
        except Exception as e:
            st.error(f"Erro ao gerar fatura: {str(e)}")
            return None
    
    def atualizar_cartao(self, cartao_id, dados_atualizados):
        """Atualiza dados do cartão"""
        try:
            update_data = {"data_atualizacao": datetime.now().isoformat()}
            
            # Campos permitidos para atualização
            campos_permitidos = ["nome", "limite", "dia_vencimento", "dia_fechamento", "cor", "ativo"]
            
            for campo in campos_permitidos:
                if campo in dados_atualizados:
                    if campo in ["limite"]:
                        update_data[campo] = float(dados_atualizados[campo])
                    elif campo in ["dia_vencimento", "dia_fechamento"]:
                        update_data[campo] = int(dados_atualizados[campo])
                    else:
                        update_data[campo] = dados_atualizados[campo]
            
            result = self.colecao.update_one(
                {"_id": cartao_id},
                {"$set": update_data}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            st.error(f"Erro ao atualizar cartão: {str(e)}")
            return False
    
    def excluir_compra(self, compra_id):
        """Exclui uma compra"""
        try:
            result = self.colecao_compras.delete_one({"_id": compra_id})
            return result.deleted_count > 0
        except Exception as e:
            st.error(f"Erro ao excluir compra: {str(e)}")
            return False
    
    def get_limite_utilizado(self, cartao_id):
        """Calcula percentual do limite utilizado"""
        try:
            cartao = self.get_cartao(cartao_id)
            if not cartao:
                return 0
            
            valor_atual = self.calcular_fatura_atual(cartao_id)
            
            if cartao["limite"] <= 0:
                return 0
            
            return (valor_atual / cartao["limite"]) * 100
            
        except Exception as e:
            return 0
    
    def get_estatisticas_cartoes(self):
        """Retorna estatísticas gerais dos cartões"""
        try:
            cartoes = self.listar_cartoes()
            
            if not cartoes:
                return {
                    "total_cartoes": 0,
                    "limite_total": 0,
                    "valor_usado": 0,
                    "limite_disponivel": 0
                }
            
            limite_total = sum(c["limite"] for c in cartoes)
            valor_usado = sum(self.calcular_fatura_atual(c["_id"]) for c in cartoes)
            
            return {
                "total_cartoes": len(cartoes),
                "limite_total": limite_total,
                "valor_usado": valor_usado,
                "limite_disponivel": limite_total - valor_usado,
                "percentual_usado": (valor_usado / limite_total * 100) if limite_total > 0 else 0
            }
            
        except Exception as e:
            st.error(f"Erro ao calcular estatísticas: {str(e)}")
            return {"total_cartoes": 0, "limite_total": 0, "valor_usado": 0, "limite_disponivel": 0}
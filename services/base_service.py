import json
import traceback
from datetime import datetime
from contextlib import contextmanager

class BaseService:
    """Classe base para serviços com funcionalidades compartilhadas"""
    
    def __init__(self, firebase, db):
        self.firebase = firebase
        self.db = db
    
    @contextmanager
    def transaction(self):
        """Gerenciador de contexto para transações de banco de dados"""
        try:
            yield self.db.conn
            self.db.conn.commit()
        except Exception as e:
            self.db.conn.rollback()
            print(f"Erro na transação: {e}")
            traceback.print_exc()
            raise
    
    def log_error(self, message, error=None):
        """Registra erros de forma padronizada"""
        error_msg = f"{message}: {str(error)}" if error else message
        print(error_msg)
        traceback.print_exc()
        return error_msg
    
    def sync_with_firebase(self, collection, doc_id, data, operation):
        """Sincroniza dados com o Firebase ou adiciona à fila de sincronização"""
        try:
            if self.firebase.online_mode:
                if operation in ['add', 'update']:
                    self.firebase.db.collection(collection).document(doc_id).set(data)
                    print(f"Dados sincronizados com Firebase: {collection}/{doc_id}")
                    return True
                elif operation == 'delete':
                    self.firebase.db.collection(collection).document(doc_id).delete()
                    print(f"Documento excluído do Firebase: {collection}/{doc_id}")
                    return True
            else:
                # Adicionar à fila de sincronização
                self.db.add_sync_operation(operation, collection, doc_id, data)
                print(f"Operação adicionada à fila de sincronização: {operation} {collection}/{doc_id}")
                return True
        except Exception as e:
            self.log_error(f"Erro ao sincronizar com Firebase", e)
            # Adicionar à fila de sincronização em caso de erro
            self.db.add_sync_operation(operation, collection, doc_id, data)
            return False
    
    def validate_required_fields(self, data, required_fields):
        """Valida campos obrigatórios em um dicionário de dados"""
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            error_msg = f"Campos obrigatórios não preenchidos: {', '.join(missing_fields)}"
            print(error_msg)
            return False, error_msg
        return True, ""
    
    def get_current_date(self):
        """Retorna a data atual no formato padrão"""
        return datetime.now().strftime("%d/%m/%Y")
    
    def get_current_timestamp(self):
        """Retorna o timestamp atual"""
        return datetime.now().timestamp()
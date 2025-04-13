import firebase_admin
from firebase_admin import credentials, firestore
import os
import json

class FirebaseConfig:
    def __init__(self):
        self.app = None
        self.db = None
        self.online_mode = False
        self.initialize()
    
    def initialize(self):
        """Inicializa a conexão com o Firebase"""
        try:
            # Verificar se já existe uma instância inicializada
            if not self.app:
                # Verificar se o arquivo de credenciais existe
                cred_path = 'config/chave.json'
                
                if os.path.exists(cred_path):
                    # Inicializar com credenciais do arquivo
                    cred = credentials.Certificate(cred_path)
                    self.app = firebase_admin.initialize_app(cred)
                    self.db = firestore.client()
                    self.online_mode = True
                    print("Firebase inicializado com sucesso usando credenciais do arquivo.")
                else:
                    # Tentar inicializar com credenciais de ambiente (para produção)
                    try:
                        self.app = firebase_admin.initialize_app()
                        self.db = firestore.client()
                        self.online_mode = True
                        print("Firebase inicializado com sucesso usando credenciais de ambiente.")
                    except Exception as e:
                        print(f"Não foi possível inicializar o Firebase: {e}")
                        print("Operando em modo offline.")
                        self.online_mode = False
        except Exception as e:
            print(f"Erro ao inicializar Firebase: {e}")
            print("Operando em modo offline.")
            self.online_mode = False
    
    def check_connection(self):
        """Verifica se a conexão com o Firebase está ativa"""
        if not self.online_mode:
            self.initialize()  # Tentar inicializar novamente
            
        if not self.online_mode:
            return False
            
        try:
            # Tentar uma operação simples para verificar a conexão
            test_ref = self.db.collection('connection_test').document('ping')
            test_ref.set({'timestamp': firestore.SERVER_TIMESTAMP})
            return True
        except Exception as e:
            print(f"Erro ao verificar conexão com Firebase: {e}")
            self.online_mode = False
            return False
    
    def get_collection(self, collection_name):
        """Obtém uma referência para uma coleção, verificando a conexão primeiro"""
        if self.check_connection():
            return self.db.collection(collection_name)
        return None
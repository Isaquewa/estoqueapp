import flet as ft
from datetime import datetime
import json
import time
import threading
import traceback

class DataService:
    """Serviço central para gerenciamento de dados da aplicação"""
    
    def __init__(self):
        """Inicializa o serviço de dados"""
        # Importar serviços
        from config.firebase_config import FirebaseConfig
        from services.database_service import DatabaseService
        from services.product_service import ProductService
        from services.residue_service import ResidueService
        from services.notification_service import NotificationService
        from services.settings_service import SettingsService
        from services.group_service import GroupService
        
        # Inicializar serviços
        self.firebase = FirebaseConfig()
        self.db = DatabaseService()
        
        # Verificar integridade do banco de dados
        self.db.verify_database_integrity()
        
        # Verificar tabelas específicas
        self.db.verify_products_table()
        self.db.verify_product_history_table()
        
        # Inicializar serviços específicos
        self.product_service = ProductService(self.firebase, self.db)
        self.residue_service = ResidueService(self.firebase, self.db)
        self.notification_service = NotificationService(self.firebase, self.db)
        self.settings_service = SettingsService(self.firebase, self.db)
        self.group_service = GroupService(self.firebase, self.db)
        
        # Cache local
        self._stock_products = []
        self._low_stock_products = []
        self._expiring_products = []
        self._residues = []
        self._notifications = []
        self._settings = None
        self._weekly_usage_data = []
        self._product_groups = []
        self._residue_groups = []
        
        # Dados para novos itens
        self.new_product = self._get_empty_product()
        self.new_residue = self._get_empty_residue()
        
        # Estado de conexão
        self.online_mode = self.firebase.online_mode
        
        # Referência à navegação (será definida em main.py)
        self.navigation = None
        
        # Carregar dados iniciais
        self.refresh_data()
        
        # Iniciar thread de sincronização
        self._start_sync_thread()
        
        # Iniciar thread de backup automático
        self._start_backup_thread()
    
    def _start_sync_thread(self):
        """Inicia uma thread para sincronização periódica com o Firebase"""
        def sync_worker():
            retry_count = 0
            max_retries = 3
            
            while True:
                try:
                    # Tentar sincronizar a cada 30 segundos
                    time.sleep(30)
                    success = self.sync_with_firebase()
                    
                    if success:
                        retry_count = 0
                    else:
                        retry_count += 1
                        
                    # Se falhar várias vezes seguidas, aumentar o intervalo
                    if retry_count >= max_retries:
                        print(f"Sincronização falhou {retry_count} vezes. Aumentando intervalo.")
                        time.sleep(60)  # Esperar mais tempo
                except Exception as e:
                    print(f"Erro na thread de sincronização: {e}")
                    traceback.print_exc()
                    time.sleep(60)  # Esperar mais tempo em caso de erro
        
        # Iniciar thread como daemon para que ela termine quando o programa principal terminar
        sync_thread = threading.Thread(target=sync_worker, daemon=True)
        sync_thread.start()
        print("Thread de sincronização iniciada")
    
    def _start_backup_thread(self):
        """Inicia uma thread para backup automático do banco de dados"""
        def backup_worker():
            while True:
                try:
                    # Fazer backup a cada 24 horas
                    time.sleep(24 * 60 * 60)  # 24 horas
                    
                    # Verificar se backup está habilitado nas configurações
                    if self._settings and self._settings.get("backupEnabled", True):
                        self.db.backup_database()
                except Exception as e:
                    print(f"Erro na thread de backup: {e}")
                    traceback.print_exc()
                    time.sleep(60 * 60)  # Esperar 1 hora em caso de erro
        
        # Iniciar thread como daemon
        backup_thread = threading.Thread(target=backup_worker, daemon=True)
        backup_thread.start()
        print("Thread de backup automático iniciada")
    
    def sync_with_firebase(self):
        """Sincroniza dados locais com o Firebase"""
        if not self.firebase.check_connection():
            print("Firebase indisponível, sincronização adiada")
            return False
        
        print("Iniciando sincronização com Firebase...")
        self.online_mode = True
        
        # Buscar operações pendentes
        pending_ops = self.db.get_pending_sync_operations()
        if not pending_ops:
            print("Nenhuma operação pendente para sincronizar")
            return True
        
        print(f"Encontradas {len(pending_ops)} operações pendentes")
        success_count = 0
        
        for op in pending_ops:
            try:
                collection = op['collection']
                doc_id = op['document_id']
                data = op['data']
                
                print(f"Processando operação: {op['operation_type']} para {collection}/{doc_id}")
                
                if op['operation_type'] == 'add' or op['operation_type'] == 'update':
                    # Adicionar ou atualizar documento
                    self.firebase.db.collection(collection).document(doc_id).set(data)
                    print(f"Documento {doc_id} adicionado/atualizado no Firebase")
                elif op['operation_type'] == 'delete':
                    # Excluir documento
                    self.firebase.db.collection(collection).document(doc_id).delete()
                    print(f"Documento {doc_id} excluído do Firebase")
                
                # Marcar como sincronizado
                self.db.mark_sync_operation_completed(op['id'])
                success_count += 1
                
            except Exception as e:
                print(f"Erro ao sincronizar operação {op['id']}: {e}")
                import traceback
                traceback.print_exc()
        
        print(f"Sincronização concluída: {success_count}/{len(pending_ops)} operações processadas")
        
        # Atualizar dados após sincronização
        self.refresh_data()
        return True
        
    def refresh_data(self):
        """Atualiza todos os dados do cache local"""
        try:
            print("Atualizando dados do cache local...")
            
            # Verificar conexão com Firebase
            self.online_mode = self.firebase.check_connection()
            
            # Limpar cache atual
            self._stock_products = []
            self._residues = []
            self._product_groups = []
            self._residue_groups = []
            
            # Buscar dados locais
            self._stock_products = self.product_service.get_all_products()
            print(f"Produtos carregados: {len(self._stock_products)}")
            
            self._residues = self.residue_service.get_all_residues()
            print(f"Resíduos carregados: {len(self._residues)}")
            
            self._notifications = self.notification_service.get_unread_notifications()
            self._settings = self.settings_service.get_settings()
            
            # Carregar grupos
            self._product_groups = self.group_service.get_all_product_groups()
            print(f"Grupos de produtos carregados: {len(self._product_groups)}")
            
            self._residue_groups = self.group_service.get_all_residue_groups()
            print(f"Grupos de resíduos carregados: {len(self._residue_groups)}")
            
            # Atualizar listas filtradas
            self._update_filtered_lists()
            
            # Atualizar dados de uso semanal
            self._weekly_usage_data = self.product_service.get_weekly_usage_data()
            
            # Verificar e criar notificações automáticas
            self.notification_service.check_and_create_notifications()
            
            print(f"Dados atualizados: {len(self._stock_products)} produtos, {len(self._residues)} resíduos")
            return True
        except Exception as e:
            print(f"ERRO ao atualizar dados: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _add_sample_data(self):
        """Adiciona dados de exemplo para teste"""
        try:
            print("Adicionando dados de exemplo...")
            
            # Adicionar produtos de exemplo
            from datetime import datetime, timedelta
            
            today = datetime.now().strftime("%d/%m/%Y")
            next_month = (datetime.now() + timedelta(days=30)).strftime("%d/%m/%Y")
            
            # Produtos de exemplo
            sample_products = [
                {
                    "name": "Farinha de Trigo Tipo 1",
                    "quantity": 100,
                    "lot": "LOT123",
                    "expiry": next_month,
                    "entryDate": today,
                    "fabDate": today,
                    "exitDate": "",
                    "category": "Matéria-Prima",
                    "location": "Prateleira A1",
                    "weeklyUsage": [10, 15, 12, 8, 20, 5, 10]
                },
                {
                    "name": "Óleo Vegetal",
                    "quantity": 50,
                    "lot": "LOT456",
                    "expiry": next_month,
                    "entryDate": today,
                    "fabDate": today,
                    "exitDate": "",
                    "category": "Matéria-Prima",
                    "location": "Prateleira B2",
                    "weeklyUsage": [5, 8, 6, 4, 10, 3, 5]
                },
                {
                    "name": "Açúcar Refinado",
                    "quantity": 80,
                    "lot": "LOT789",
                    "expiry": next_month,
                    "entryDate": today,
                    "fabDate": today,
                    "exitDate": "",
                    "category": "Matéria-Prima",
                    "location": "Prateleira C3",
                    "weeklyUsage": [8, 12, 10, 6, 15, 4, 8]
                },
                {
                    "name": "Produto com Estoque Baixo",
                    "quantity": 3,
                    "lot": "LOT999",
                    "expiry": next_month,
                    "entryDate": today,
                    "fabDate": today,
                    "exitDate": "",
                    "category": "Produto Acabado",
                    "location": "Prateleira D4",
                    "weeklyUsage": [1, 1, 0, 1, 0, 1, 0]
                }
            ]
            
            for product in sample_products:
                # Criar cópia para não modificar o original
                self.new_product = product.copy()
                self.add_product()
            
            # Resíduos de exemplo
            sample_residues = [
                {
                    "name": "Tambores Plásticos",
                    "type": "Plástico",
                    "quantity": 5,
                    "entryDate": today,
                    "exitDate": "",
                    "destination": "Reciclagem",
                    "notes": "Tambores de 200L usados"
                },
                {
                    "name": "Sacos Nylon",
                    "type": "Têxtil",
                    "quantity": 10,
                    "entryDate": today,
                    "exitDate": "",
                    "destination": "Reuso",
                    "notes": "Sacos de 50kg em bom estado"
                },
                {
                    "name": "Resíduo Químico",
                    "type": "Químico",
                    "quantity": 3,
                    "entryDate": today,
                    "exitDate": "",
                    "destination": "Tratamento Especial",
                    "notes": "Armazenar separadamente"
                }
            ]
            
            for residue in sample_residues:
                # Criar cópia para não modificar o original
                self.new_residue = residue.copy()
                self.add_residue()
            
            # Atualizar dados novamente
            self._stock_products = self.product_service.get_all_products()
            self._residues = self.residue_service.get_all_residues()
            self._update_filtered_lists()
            
            print(f"Dados de exemplo adicionados: {len(self._stock_products)} produtos, {len(self._residues)} resíduos")
            return True
        except Exception as e:
            print(f"Erro ao adicionar dados de exemplo: {e}")
            traceback.print_exc()
            return False
    
    def _update_filtered_lists(self):
        """Atualiza as listas de produtos com estoque baixo e próximos ao vencimento"""
        try:
            settings = self._settings or {}
            threshold = settings.get("notifications", {}).get("lowStockThreshold", 5)
            expiry_days = settings.get("notifications", {}).get("expiryWarningDays", 30)
            
            self._low_stock_products = self.product_service.get_low_stock_products(threshold)
            self._expiring_products = self.product_service.get_expiring_products(expiry_days)
        except Exception as e:
            print(f"Erro ao atualizar listas filtradas: {e}")
            traceback.print_exc()
            self._low_stock_products = []
            self._expiring_products = []
    
    def _get_empty_product(self):
        """Retorna um produto vazio com a data atual"""
        today = datetime.now().strftime("%d/%m/%Y")
        return {
            "name": "",
            "quantity": "",
            "lot": "",
            "expiry": "",
            "fabDate": "",
            "entryDate": today,
            "exitDate": "",
            "category": "",
            "location": "",
            "weeklyUsage": [0] * 7,
            "group_id": ""
        }
    
    def _get_empty_residue(self):
        """Retorna um resíduo vazio com a data atual"""
        today = datetime.now().strftime("%d/%m/%Y")
        return {
            "name": "",
            "type": "",
            "quantity": "",
            "entryDate": today,
            "exitDate": "",
            "destination": "",
            "notes": "",
            "group_id": ""
        }
    
    # Getters para acesso aos dados em cache
    @property
    def stock_products(self):
        return self._stock_products or []
    
    @property
    def low_stock_products(self):
        return self._low_stock_products or []
    
    @property
    def expiring_products(self):
        return self._expiring_products or []
    
    @property
    def residues(self):
        return self._residues or []
    
    @property
    def notifications(self):
        return self._notifications or []
    
    @property
    def settings(self):
        return self._settings or self.settings_service.get_settings()
    
    @property
    def weekly_usage_data(self):
        return self._weekly_usage_data or []
    
    @property
    def product_groups(self):
        return self._product_groups or []
    
    @property
    def residue_groups(self):
        return self._residue_groups or []
    
    # Métodos para adicionar novos itens
    def add_product(self):
        """Adiciona um novo produto ao estoque"""
        try:
            print("Método add_product chamado no DataService")
            if all(self.new_product[field] for field in ["name", "quantity", "lot", "expiry"]):
                # Converter quantidade para inteiro
                try:
                    self.new_product["quantity"] = int(self.new_product["quantity"])
                except ValueError:
                    print("Erro: quantidade deve ser um número inteiro")
                    return False
                
                # Verificar se há um grupo selecionado ou extrair do nome
                if not self.new_product.get("group_id"):
                    group_name = self.group_service.extract_group_name(self.new_product["name"])
                    if group_name:
                        group = self.group_service.get_or_create_product_group(group_name)
                        self.new_product["group_id"] = group["id"]
                
                # Adicionar produto
                product = self.product_service.add_product(self.new_product)
                
                if product:
                    # Atualizar cache
                    self.refresh_data()
                    
                    # Resetar formulário
                    self.reset_new_product()
                    
                    # Atualizar a interface se a navegação estiver disponível
                    self._update_ui()
                    
                    return True
                else:
                    print("Erro: produto não foi adicionado pelo product_service")
                    return False
            else:
                print("Erro: campos obrigatórios não preenchidos")
                print(f"Campos: name={self.new_product.get('name')}, quantity={self.new_product.get('quantity')}, lot={self.new_product.get('lot')}, expiry={self.new_product.get('expiry')}")
                return False
        except Exception as e:
            print(f"Erro ao adicionar produto: {e}")
            traceback.print_exc()
            return False
    
    def add_residue(self):
        """Adiciona um novo resíduo"""
        try:
            print("Método add_residue chamado no DataService")
            if all(self.new_residue[field] for field in ["name", "type", "quantity"]):
                # Converter quantidade para inteiro
                try:
                    self.new_residue["quantity"] = int(self.new_residue["quantity"])
                except ValueError:
                    print("Erro: quantidade deve ser um número inteiro")
                    return False
                
                # Verificar se há um grupo selecionado ou extrair do tipo/nome
                if not self.new_residue.get("group_id"):
                    # Usar o tipo como grupo, ou extrair do nome
                    group_name = self.new_residue["type"] or self.group_service.extract_residue_group_name(self.new_residue["name"])
                    if group_name:
                        group = self.group_service.get_or_create_residue_group(group_name)
                        self.new_residue["group_id"] = group["id"]
                
                # Adicionar resíduo
                residue = self.residue_service.add_residue(self.new_residue)
                
                if residue:
                    # Atualizar cache
                    self.refresh_data()
                    
                    # Resetar formulário
                    self.reset_new_residue()
                    
                    # Atualizar a interface
                    self._update_ui()
                    
                    return True
                else:
                    print("Erro: resíduo não foi adicionado pelo residue_service")
                    return False
            else:
                print("Erro: campos obrigatórios não preenchidos")
                print(f"Campos: name={self.new_residue.get('name')}, type={self.new_residue.get('type')}, quantity={self.new_residue.get('quantity')}")
                return False
        except Exception as e:
            print(f"Erro ao adicionar resíduo: {e}")
            traceback.print_exc()
            return False
    
    def _update_ui(self):
        """Atualiza a interface do usuário se a navegação estiver disponível"""
        if hasattr(self, 'navigation') and self.navigation:
            print("Chamando update_view da navegação")
            self.navigation.update_view()
        else:
            print("Navegação não disponível para atualizar a interface")
    
    # Métodos para atualizar novos itens
    def update_new_product(self, field, value):
        """Atualiza um campo do novo produto"""
        try:
            self.new_product[field] = value
        except Exception as e:
            print(f"Erro ao atualizar campo do produto: {e}")
    
    def update_new_residue(self, field, value):
        """Atualiza um campo do novo resíduo"""
        try:
            self.new_residue[field] = value
        except Exception as e:
            print(f"Erro ao atualizar campo do resíduo: {e}")
    
    # Métodos para resetar formulários
    def reset_new_product(self):
        """Reseta o formulário de novo produto"""
        self.new_product = self._get_empty_product()
    
    def reset_new_residue(self):
        """Reseta o formulário de novo resíduo"""
        self.new_residue = self._get_empty_residue()
    
    # Métodos para atualizar configurações
    def update_settings(self, settings):
        """Atualiza as configurações do usuário"""
        try:
            self.settings_service.update_settings(settings)
            self._settings = settings
            self._update_filtered_lists()
            return True
        except Exception as e:
            print(f"Erro ao atualizar configurações: {e}")
            traceback.print_exc()
            return False
    
    # Métodos para excluir itens
    def delete_product(self, product_id):
        """Exclui um produto do estoque"""
        try:
            print(f"DataService: Iniciando exclusão do produto com ID: {product_id}")
            
            # Buscar produto antes de excluir
            product = next((p for p in self._stock_products if p["id"] == product_id), None)
            if not product:
                print(f"DataService: Produto com ID {product_id} não encontrado no cache")
                return False
            
            product_name = product.get("name", "Produto")
            print(f"DataService: Excluindo produto: {product_name}")
            
            # Excluir produto
            success = self.product_service.delete_product(product_id)
            print(f"DataService: Resultado da exclusão do produto: {success}")
            
            if success:
                # Criar notificação
                try:
                    self.notification_service.create_notification(
                        "PRODUCT_DELETED",
                        f"Produto '{product_name}' foi excluído do estoque",
                        None
                    )
                except Exception as e:
                    print(f"Erro ao criar notificação de exclusão de produto: {e}")
                
                # Atualizar cache local - remover o produto excluído da lista
                self._stock_products = [p for p in self._stock_products if p["id"] != product_id]
                print(f"DataService: Produto removido do cache. Restantes: {len(self._stock_products)}")
                
                # Atualizar listas filtradas
                self._update_filtered_lists()
                
                # Forçar atualização completa dos dados
                self.refresh_data()
                
                return True
            return False
        except Exception as e:
            print(f"DataService: Erro ao excluir produto: {e}")
            import traceback
            traceback.print_exc()
            return False

    def delete_residue(self, residue_id):
        """Exclui um resíduo"""
        try:
            print(f"DataService: Iniciando exclusão do resíduo com ID: {residue_id}")
            
            # Buscar resíduo antes de excluir
            residue = next((r for r in self._residues if r["id"] == residue_id), None)
            if not residue:
                print(f"DataService: Resíduo com ID {residue_id} não encontrado no cache")
                return False
            
            residue_name = residue.get("name", "Resíduo")
            print(f"DataService: Excluindo resíduo: {residue_name}")
            
            # Excluir resíduo do banco de dados
            cursor = self.db.conn.cursor()
            cursor.execute('DELETE FROM residues WHERE id = ?', (residue_id,))
            rows_affected = cursor.rowcount
            self.db.conn.commit()
            print(f"DataService: Resíduo com ID {residue_id} excluído localmente. Linhas afetadas: {rows_affected}")
            
            # Verificar se a exclusão foi bem-sucedida
            cursor.execute('SELECT COUNT(*) FROM residues WHERE id = ?', (residue_id,))
            count = cursor.fetchone()[0]
            if count > 0:
                print(f"ERRO: Resíduo ainda existe no banco de dados após exclusão!")
                return False
            
            # Tentar excluir no Firebase se estiver online
            if self.firebase and hasattr(self.firebase, 'online_mode') and self.firebase.online_mode:
                try:
                    self.firebase.db.collection('residues').document(residue_id).delete()
                    print(f"Resíduo com ID {residue_id} excluído do Firebase")
                except Exception as e:
                    print(f"Erro ao excluir resíduo do Firebase: {e}")
                    # Adicionar à fila de sincronização
                    self.db.add_sync_operation('delete', 'residues', residue_id, {})
            else:
                # Adicionar à fila de sincronização
                self.db.add_sync_operation('delete', 'residues', residue_id, {})
            
            # Criar notificação
            try:
                self.notification_service.create_notification(
                    "RESIDUE_DELETED",
                    f"Resíduo '{residue_name}' foi excluído",
                    None
                )
            except Exception as e:
                print(f"Erro ao criar notificação de exclusão de resíduo: {e}")
            
            # Atualizar cache local - remover o resíduo excluído da lista
            self._residues = [r for r in self._residues if r["id"] != residue_id]
            print(f"DataService: Resíduo removido do cache. Restantes: {len(self._residues)}")
            
            # Forçar atualização completa dos dados
            self.refresh_data()
            
            print(f"Exclusão do resíduo com ID {residue_id} concluída com sucesso")
            return True
        except Exception as e:
            print(f"DataService: Erro ao excluir resíduo: {e}")
            import traceback
            traceback.print_exc()
            try:
                self.db.conn.rollback()
            except:
                pass
            return False
    
    # Métodos para gerenciar grupos
    def create_product_group(self, group_name, description="", icon="INVENTORY_2_ROUNDED", color="blue"):
        """Cria um novo grupo de produtos"""
        try:
            group = self.group_service.get_or_create_product_group(group_name)
            
            # Atualizar descrição, ícone e cor se fornecidos
            if description or icon or color:
                group["description"] = description or group["description"]
                group["icon"] = icon or group["icon"]
                group["color"] = color or group["color"]
                self.group_service.update_group(group["id"], group)
            
            # Atualizar cache
            self.refresh_data()
            return group
        except Exception as e:
            print(f"Erro ao criar grupo de produtos: {e}")
            traceback.print_exc()
            return None
    
    def create_residue_group(self, group_name, description="", icon="DELETE_OUTLINE", color="purple"):
        """Cria um novo grupo de resíduos"""
        try:
            group = self.group_service.get_or_create_residue_group(group_name)
            
            # Atualizar descrição, ícone e cor se fornecidos
            if description or icon or color:
                group["description"] = description or group["description"]
                group["icon"] = icon or group["icon"]
                group["color"] = color or group["color"]
                self.group_service.update_group(group["id"], group, is_residue=True)
            
            # Atualizar cache
            self.refresh_data()
            return group
        except Exception as e:
            print(f"Erro ao criar grupo de resíduos: {e}")
            traceback.print_exc()
            return None
        
    def check_connection_status(self):
        """Verifica o status da conexão com o Firebase e atualiza o modo online/offline"""
        previous_mode = self.online_mode
        self.online_mode = self.firebase.check_connection()
        
        if not previous_mode and self.online_mode:
            # Se voltou a ficar online, tentar sincronizar
            print("Conexão com Firebase restaurada, iniciando sincronização...")
            self.sync_with_firebase()
        
        return self.online_mode
    
    def delete_group(self, group_id, is_product_group=True):
        """Exclui um grupo"""
        try:
            print(f"DataService: Iniciando exclusão do grupo com ID: {group_id}, is_product_group: {is_product_group}")
            
            # Importar serviço de grupo se ainda não estiver disponível
            from services.group_service import GroupService
            if not hasattr(self, 'group_service'):
                self.group_service = GroupService(self.firebase, self.db)
            
            # Buscar grupo antes de excluir
            if is_product_group:
                groups = self._product_groups
            else:
                groups = self._residue_groups
                    
            group = next((g for g in groups if g["id"] == group_id), None)
            if not group:
                print(f"DataService: Grupo com ID {group_id} não encontrado no cache")
                return False
            
            group_name = group.get("name", "Grupo")
            print(f"DataService: Excluindo grupo: {group_name}, is_product_group: {is_product_group}")
            
            # Chamar o método de exclusão no serviço de grupo
            success = self.group_service.delete_group(group_id, not is_product_group)
                    
            print(f"DataService: Resultado da exclusão do grupo: {success}")
            
            if success:
                # Criar notificação
                try:
                    self.notification_service.create_notification(
                        "GROUP_DELETED",
                        f"Grupo '{group_name}' foi excluído",
                        None
                    )
                except Exception as e:
                    print(f"Erro ao criar notificação de exclusão de grupo: {e}")
            
                # Atualizar cache local - remover o grupo excluído da lista
                if is_product_group:
                    self._product_groups = [g for g in self._product_groups if g["id"] != group_id]
                    print(f"DataService: Grupo de produtos removido do cache. Restantes: {len(self._product_groups)}")
                else:
                    self._residue_groups = [g for g in self._residue_groups if g["id"] != group_id]
                    print(f"DataService: Grupo de resíduos removido do cache. Restantes: {len(self._residue_groups)}")
                
                # Forçar atualização completa dos dados
                print("DataService: Iniciando atualização completa dos dados após exclusão")
                self.refresh_data()
                print("DataService: Atualização completa dos dados concluída")
                
                return True
            return False
        except Exception as e:
            print(f"DataService: Erro ao excluir grupo: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_product_movement_history(self, product_name=None, days=30):
        """
        Obtém o histórico de movimentação de produtos.
        
        Args:
            product_name (str, optional): Nome do produto para filtrar. Se None, retorna todos.
            days (int, optional): Número de dias para buscar o histórico. Padrão é 30.
            
        Returns:
            list: Lista de movimentações de produtos.
        """
        try:
            from datetime import datetime, timedelta
            
            # Calcular data limite
            cutoff_date = datetime.now() - timedelta(days=days)
            cutoff_timestamp = cutoff_date.timestamp()
            
            # Consultar histórico de movimentação
            cursor = self.db.conn.cursor()
            
            if product_name:
                # Filtrar por nome do produto
                cursor.execute('''
                SELECT * FROM product_history 
                WHERE product_name LIKE ? AND timestamp >= ? 
                ORDER BY timestamp DESC
                ''', (f'%{product_name}%', cutoff_timestamp))
            else:
                # Todos os produtos
                cursor.execute('''
                SELECT * FROM product_history 
                WHERE timestamp >= ? 
                ORDER BY timestamp DESC
                ''', (cutoff_timestamp,))
            
            results = cursor.fetchall()
            movement_history = []
            
            for row in results:
                try:
                    movement = {
                        "id": row[0],
                        "productId": row[1],
                        "productName": row[2],
                        "quantity": row[3],
                        "reason": row[4],
                        "date": row[5],
                        "timestamp": row[6],
                        "type": row[7]  # entry, exit, adjustment
                    }
                    movement_history.append(movement)
                except Exception as e:
                    print(f"Erro ao processar movimento: {e}")
                    continue
            
            return movement_history
        except Exception as e:
            print(f"Erro ao obter histórico de movimentação: {e}")
            import traceback
            traceback.print_exc()
            return []
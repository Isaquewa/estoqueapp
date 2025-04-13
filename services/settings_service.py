import json
import traceback

class SettingsService:
    """Serviço para gerenciamento de configurações do sistema"""
    
    def __init__(self, firebase, db):
        self.firebase = firebase
        self.db = db
        self._init_default_settings()
    
    def _init_default_settings(self):
        """Inicializa as configurações padrão se não existirem"""
        default_settings = {
            "notifications": {
                "enabled": True,
                "lowStockThreshold": 5,
                "expiryWarningDays": 30
            },
            "weeklyReportEnabled": True,
            "backupEnabled": True,
            "theme": {
                "mode": "light",
                "primaryColor": "blue",
                "accentColor": "amber"
            },
            "display": {
                "showQuantityWarnings": True,
                "defaultView": "list",
                "itemsPerPage": 20
            }
        }
        
        try:
            cursor = self.db.conn.cursor()
            cursor.execute('SELECT * FROM settings WHERE id = "user_settings"')
            if not cursor.fetchone():
                # Salvar no Firebase
                if self.firebase.online_mode:
                    try:
                        self.firebase.db.collection('settings').document('user_settings').set(default_settings)
                    except Exception as e:
                        print(f"Erro ao salvar configurações padrão no Firebase: {e}")
                        # Adicionar à fila de sincronização
                        self.db.add_sync_operation('add', 'settings', 'user_settings', default_settings)
                else:
                    # Adicionar à fila de sincronização
                    self.db.add_sync_operation('add', 'settings', 'user_settings', default_settings)
                
                # Salvar localmente
                cursor.execute('''
                INSERT INTO settings (id, settings_data)
                VALUES (?, ?)
                ''', ('user_settings', json.dumps(default_settings)))
                self.db.conn.commit()
                print("Configurações padrão inicializadas com sucesso")
        except Exception as e:
            print(f"Erro ao inicializar configurações padrão: {e}")
            traceback.print_exc()
    
    def get_settings(self):
        """Retorna as configurações do usuário"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute('SELECT settings_data FROM settings WHERE id = "user_settings"')
            result = cursor.fetchone()
            
            if result:
                return json.loads(result[0])
            else:
                # Se não encontrar, inicializar novamente e retornar padrão
                self._init_default_settings()
                return self.get_default_settings()
        except Exception as e:
            print(f"Erro ao obter configurações: {e}")
            traceback.print_exc()
            return self.get_default_settings()
    
    def get_default_settings(self):
        """Retorna as configurações padrão"""
        return {
            "notifications": {
                "enabled": True,
                "lowStockThreshold": 5,
                "expiryWarningDays": 30
            },
            "weeklyReportEnabled": True,
            "backupEnabled": True,
            "theme": {
                "mode": "light",
                "primaryColor": "blue",
                "accentColor": "amber"
            },
            "display": {
                "showQuantityWarnings": True,
                "defaultView": "list",
                "itemsPerPage": 20
            }
        }
    
    def update_settings(self, settings):
        """Atualiza as configurações do usuário"""
        try:
            # Validar configurações
            if not self._validate_settings(settings):
                print("Configurações inválidas")
                return False
            
            # Atualizar no Firebase
            if self.firebase.online_mode:
                try:
                    self.firebase.db.collection('settings').document('user_settings').set(settings)
                except Exception as e:
                    print(f"Erro ao atualizar configurações no Firebase: {e}")
                    # Adicionar à fila de sincronização
                    self.db.add_sync_operation('update', 'settings', 'user_settings', settings)
            else:
                # Adicionar à fila de sincronização
                self.db.add_sync_operation('update', 'settings', 'user_settings', settings)
            
            # Atualizar localmente
            cursor = self.db.conn.cursor()
            cursor.execute('''
            UPDATE settings 
            SET settings_data = ?
            WHERE id = "user_settings"
            ''', (json.dumps(settings),))
            self.db.conn.commit()
            
            print("Configurações atualizadas com sucesso")
            return True
        except Exception as e:
            print(f"Erro ao atualizar configurações: {e}")
            traceback.print_exc()
            return False
    
    def _validate_settings(self, settings):
        """Valida as configurações antes de salvar"""
        try:
            # Verificar estrutura básica
            required_sections = ["notifications", "weeklyReportEnabled", "backupEnabled"]
            for section in required_sections:
                if section not in settings:
                    print(f"Seção obrigatória ausente: {section}")
                    return False
            
            # Verificar configurações de notificações
            notifications = settings.get("notifications", {})
            if not isinstance(notifications, dict):
                print("Configurações de notificações inválidas")
                return False
            
            # Verificar campos obrigatórios em notificações
            required_notification_fields = ["enabled", "lowStockThreshold", "expiryWarningDays"]
            for field in required_notification_fields:
                if field not in notifications:
                    print(f"Campo obrigatório ausente em notificações: {field}")
                    return False
            
            # Validar tipos de dados
            if not isinstance(notifications["enabled"], bool):
                print("Campo 'enabled' deve ser booleano")
                return False
            
            try:
                threshold = int(notifications["lowStockThreshold"])
                if threshold < 0:
                    print("Limite de estoque baixo não pode ser negativo")
                    return False
            except (ValueError, TypeError):
                print("Limite de estoque baixo deve ser um número inteiro")
                return False
            
            try:
                days = int(notifications["expiryWarningDays"])
                if days < 0:
                    print("Dias para alerta de vencimento não pode ser negativo")
                    return False
            except (ValueError, TypeError):
                print("Dias para alerta de vencimento deve ser um número inteiro")
                return False
            
            # Validar campos booleanos
            if not isinstance(settings["weeklyReportEnabled"], bool):
                print("Campo 'weeklyReportEnabled' deve ser booleano")
                return False
            
            if not isinstance(settings["backupEnabled"], bool):
                print("Campo 'backupEnabled' deve ser booleano")
                return False
            
            return True
        except Exception as e:
            print(f"Erro ao validar configurações: {e}")
            traceback.print_exc()
            return False
    
    def reset_to_defaults(self):
        """Restaura as configurações para os valores padrão"""
        try:
            default_settings = self.get_default_settings()
            success = self.update_settings(default_settings)
            return success
        except Exception as e:
            print(f"Erro ao restaurar configurações padrão: {e}")
            traceback.print_exc()
            return False
    
    def get_notification_settings(self):
        """Retorna apenas as configurações de notificações"""
        try:
            settings = self.get_settings()
            return settings.get("notifications", {
                "enabled": True,
                "lowStockThreshold": 5,
                "expiryWarningDays": 30
            })
        except Exception as e:
            print(f"Erro ao obter configurações de notificações: {e}")
            traceback.print_exc()
            return {
                "enabled": True,
                "lowStockThreshold": 5,
                "expiryWarningDays": 30
            }
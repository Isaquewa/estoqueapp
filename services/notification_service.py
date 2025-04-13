from datetime import datetime
import json

class NotificationService:
    def __init__(self, firebase, db):
        self.firebase = firebase
        self.db = db
    
    def create_notification(self, notification_type, message, product_id=None):
        """Cria uma nova notificação com tratamento de erros e sincronização"""
        try:
            # Gerar ID único com timestamp em milissegundos e um número aleatório
            import random
            import time
            notification_id = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{int(time.time() * 1000) % 1000}_{random.randint(1000, 9999)}"
            
            # Preparar dados da notificação
            notification = {
                "id": notification_id,
                "type": notification_type,
                "message": message,
                "date": datetime.now().strftime("%d/%m/%Y"),
                "read": False,
                "productId": product_id
            }
            
            # Salvar localmente primeiro (sempre funciona mesmo offline)
            self._save_notification_locally(notification)
            
            # Tentar salvar no Firebase se estiver online
            if self.firebase.online_mode:
                try:
                    self.firebase.db.collection('notifications').document(notification_id).set(notification)
                    print(f"Notificação criada no Firebase: {message}")
                except Exception as e:
                    print(f"Erro ao salvar notificação no Firebase: {e}")
                    # Adicionar à fila de sincronização
                    self.db.add_sync_operation('add', 'notifications', notification_id, notification)
            else:
                # Adicionar à fila de sincronização para quando ficar online
                self.db.add_sync_operation('add', 'notifications', notification_id, notification)
                print(f"Notificação adicionada à fila de sincronização: {message}")
            
            return notification
        except Exception as e:
            print(f"Erro ao criar notificação: {e}")
            return None
    
    def _save_notification_locally(self, notification):
        """Salva a notificação no banco de dados local"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute('''
            INSERT INTO notifications (id, type, message, date, read, productId)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                notification["id"], notification["type"], notification["message"],
                notification["date"], 0 if notification["read"] == False else 1, notification["productId"]
            ))
            self.db.conn.commit()
            print(f"Notificação salva localmente: {notification['message']}")
            return True
        except Exception as e:
            print(f"Erro ao salvar notificação localmente: {e}")
            # Tentar novamente com uma nova conexão
            try:
                self.db.conn.rollback()
                cursor = self.db.conn.cursor()
                cursor.execute('''
                INSERT INTO notifications (id, type, message, date, read, productId)
                VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    notification["id"], notification["type"], notification["message"],
                    notification["date"], 0 if notification["read"] == False else 1, notification["productId"]
                ))
                self.db.conn.commit()
                print(f"Notificação salva localmente na segunda tentativa: {notification['message']}")
                return True
            except Exception as e2:
                print(f"Erro na segunda tentativa de salvar notificação localmente: {e2}")
                return False
    
    def get_unread_notifications(self):
        """Retorna notificações não lidas com tratamento de erros"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute('SELECT * FROM notifications WHERE read = 0 ORDER BY date DESC')
            results = cursor.fetchall()
            return self._convert_to_dict(results)
        except Exception as e:
            print(f"Erro ao buscar notificações não lidas: {e}")
            # Tentar novamente com uma nova conexão
            try:
                cursor = self.db.conn.cursor()
                cursor.execute('SELECT * FROM notifications WHERE read = 0 ORDER BY date DESC')
                results = cursor.fetchall()
                return self._convert_to_dict(results)
            except Exception as e2:
                print(f"Erro na segunda tentativa de buscar notificações não lidas: {e2}")
                return []
    
    def get_all_notifications(self):
        """Retorna todas as notificações com tratamento de erros"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute('SELECT * FROM notifications ORDER BY date DESC')
            results = cursor.fetchall()
            return self._convert_to_dict(results)
        except Exception as e:
            print(f"Erro ao buscar todas as notificações: {e}")
            # Tentar novamente com uma nova conexão
            try:
                cursor = self.db.conn.cursor()
                cursor.execute('SELECT * FROM notifications ORDER BY date DESC')
                results = cursor.fetchall()
                return self._convert_to_dict(results)
            except Exception as e2:
                print(f"Erro na segunda tentativa de buscar todas as notificações: {e2}")
                return []
    
    def mark_as_read(self, notification_id):
        """Marca uma notificação como lida com tratamento de erros e sincronização"""
        try:
            # Atualizar localmente
            cursor = self.db.conn.cursor()
            cursor.execute('UPDATE notifications SET read = 1 WHERE id = ?', (notification_id,))
            self.db.conn.commit()
            
            # Buscar notificação atualizada para sincronização
            cursor.execute('SELECT * FROM notifications WHERE id = ?', (notification_id,))
            notification_data = cursor.fetchone()
            
            if not notification_data:
                print(f"Notificação com ID {notification_id} não encontrada")
                return False
            
            # Converter para dicionário
            notification = self._convert_to_dict([notification_data])[0]
            
            # Tentar atualizar no Firebase se estiver online
            if self.firebase.online_mode:
                try:
                    self.firebase.db.collection('notifications').document(notification_id).update({
                        'read': True
                    })
                    print(f"Notificação marcada como lida no Firebase: {notification_id}")
                except Exception as e:
                    print(f"Erro ao marcar notificação como lida no Firebase: {e}")
                    # Adicionar à fila de sincronização
                    self.db.add_sync_operation('update', 'notifications', notification_id, notification)
            else:
                # Adicionar à fila de sincronização para quando ficar online
                self.db.add_sync_operation('update', 'notifications', notification_id, notification)
                print(f"Marcação de leitura da notificação adicionada à fila de sincronização: {notification_id}")
            
            return True
        except Exception as e:
            print(f"Erro ao marcar notificação como lida: {e}")
            self.db.conn.rollback()
            return False
    
    def delete_notification(self, notification_id):
        """Exclui uma notificação com tratamento de erros e sincronização"""
        try:
            # Buscar notificação antes de excluir para ter os dados para sincronização
            cursor = self.db.conn.cursor()
            cursor.execute('SELECT * FROM notifications WHERE id = ?', (notification_id,))
            notification_data = cursor.fetchone()
            
            if not notification_data:
                print(f"Notificação com ID {notification_id} não encontrada")
                return False
            
            # Converter para dicionário para uso na sincronização
            notification = self._convert_to_dict([notification_data])[0]
            
            # Excluir localmente
            cursor.execute('DELETE FROM notifications WHERE id = ?', (notification_id,))
            self.db.conn.commit()
            
            # Tentar excluir no Firebase se estiver online
            if self.firebase.online_mode:
                try:
                    self.firebase.db.collection('notifications').document(notification_id).delete()
                    print(f"Notificação excluída do Firebase: {notification_id}")
                except Exception as e:
                    print(f"Erro ao excluir notificação do Firebase: {e}")
                    # Adicionar à fila de sincronização
                    self.db.add_sync_operation('delete', 'notifications', notification_id, notification)
            else:
                # Adicionar à fila de sincronização para quando ficar online
                self.db.add_sync_operation('delete', 'notifications', notification_id, notification)
                print(f"Exclusão da notificação adicionada à fila de sincronização: {notification_id}")
            
            return True
        except Exception as e:
            print(f"Erro ao excluir notificação: {e}")
            self.db.conn.rollback()
            return False
    
    def _convert_to_dict(self, rows):
        """Converte resultados do banco de dados em dicionários com tratamento de erros"""
        notifications = []
        for row in rows:
            try:
                notification = {
                    "id": row[0],
                    "type": row[1],
                    "message": row[2],
                    "date": row[3],
                    "read": bool(row[4]),
                    "productId": row[5]
                }
                notifications.append(notification)
            except Exception as e:
                print(f"Erro ao converter notificação: {e}")
                # Continuar com a próxima notificação
                continue
        return notifications
    
    def check_and_create_notifications(self):
        """Verifica condições para criar notificações automáticas"""
        try:
            # Importar serviços necessários
            from services.product_service import ProductService
            from services.settings_service import SettingsService
            
            # Inicializar serviços
            product_service = ProductService(self.firebase, self.db)
            settings_service = SettingsService(self.firebase, self.db)
            
            # Obter configurações
            settings = settings_service.get_settings()
            if not settings:
                print("Configurações não encontradas, usando valores padrão")
                threshold = 5
                expiry_days = 30
            else:
                threshold = settings.get("notifications", {}).get("lowStockThreshold", 5)
                expiry_days = settings.get("notifications", {}).get("expiryWarningDays", 30)
            
            # Verificar produtos com estoque baixo
            low_stock_products = product_service.get_low_stock_products(threshold)
            for product in low_stock_products:
                # Verificar se já existe notificação para este produto
                cursor = self.db.conn.cursor()
                cursor.execute('''
                SELECT * FROM notifications 
                WHERE type = 'LOW_STOCK' AND productId = ? AND read = 0
                ''', (product["id"],))
                
                if not cursor.fetchone():
                    # Criar nova notificação
                    self.create_notification(
                        "LOW_STOCK",
                        f"Estoque baixo: {product['name']} ({product['quantity']} unidades)",
                        product["id"]
                    )
            
            # Verificar produtos próximos ao vencimento
            expiring_products = product_service.get_expiring_products(expiry_days)
            for product in expiring_products:
                # Verificar se já existe notificação para este produto
                cursor = self.db.conn.cursor()
                cursor.execute('''
                SELECT * FROM notifications 
                WHERE type = 'EXPIRY' AND productId = ? AND read = 0
                ''', (product["id"],))
                
                if not cursor.fetchone():
                    # Calcular dias até o vencimento
                    try:
                        expiry_date = datetime.strptime(product["expiry"], "%d/%m/%Y")
                        days_remaining = (expiry_date - datetime.now()).days
                        
                        # Criar nova notificação
                        self.create_notification(
                            "EXPIRY",
                            f"Produto próximo ao vencimento: {product['name']} (vence em {days_remaining} dias)",
                            product["id"]
                        )
                    except:
                        pass
            
            return True
        except Exception as e:
            print(f"Erro ao verificar e criar notificações automáticas: {e}")
            return False
from datetime import datetime, timedelta
import json
import time
import uuid
from .base_service import BaseService

class ProductService(BaseService):
    """Serviço para gerenciamento de produtos"""

    def identify_product_group(self, product_name):
        """Identifica o grupo de um produto com base no nome"""
        from services.group_service import GroupService
        group_service = GroupService(self.firebase, self.db)
        
        # Normalizar nome do produto (remover acentos, converter para minúsculas)
        import unicodedata
        import re
        
        def normalize_text(text):
            # Remover acentos e converter para minúsculas
            text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII').lower()
            # Remover caracteres especiais
            text = re.sub(r'[^a-z0-9\s]', '', text)
            return text
        
        normalized_name = normalize_text(product_name)
        
        # Obter todos os grupos existentes
        all_groups = group_service.get_all_product_groups()
        
        # Verificar se o nome do produto contém o nome de algum grupo
        for group in all_groups:
            group_name = normalize_text(group["name"])
            
            # Verificar se o nome do grupo está contido no nome do produto
            if group_name in normalized_name:
                return group
            
            # Verificar palavras-chave específicas
            keywords = group.get("keywords", [])
            for keyword in keywords:
                if normalize_text(keyword) in normalized_name:
                    return group
        
        # Se não encontrou grupo, extrair a primeira palavra como grupo
        words = normalized_name.split()
        if words:
            first_word = words[0].capitalize()
            # Verificar se já existe um grupo com esse nome
            for group in all_groups:
                if normalize_text(group["name"]) == normalize_text(first_word):
                    return group
            
            # Criar novo grupo
            return group_service.get_or_create_product_group(first_word)
        
        # Fallback: grupo "Outros"
        return group_service.get_or_create_product_group("Outros")
    
    def add_product(self, product_data):
        """Adiciona um novo produto com tratamento de erros, sincronização e agrupamento automático"""
        try:
            # Validar dados do produto
            valid, error_msg = self.validate_required_fields(
                product_data, ["name", "quantity", "lot", "expiry"]
            )
            if not valid:
                return None
            
            # Validações adicionais
            try:
                quantity = int(product_data["quantity"])
                if quantity <= 0:
                    return self.log_error("Quantidade deve ser maior que zero")
            except (ValueError, TypeError):
                return self.log_error("Quantidade deve ser um número inteiro válido")
            
            # Validar formato de data
            try:
                expiry_date = datetime.strptime(product_data["expiry"], "%d/%m/%Y")
                current_date = datetime.now()
                
                # Verificar se a data não está muito no passado (mais de 1 ano)
                if expiry_date < current_date - timedelta(days=365):
                    return self.log_error("Data de validade está muito no passado. Verifique o formato (DD/MM/AAAA).")
                
                # Verificar se a data não está no passado
                if expiry_date < current_date:
                    print("Aviso: Data de validade está no passado")
            except ValueError:
                return self.log_error("Formato de data inválido. Use DD/MM/AAAA")
            
            # Identificar grupo do produto
            group = self.identify_product_group(product_data["name"])
            
            # Verificar se já existe produto com mesmo nome e validade no grupo
            cursor = self.db.conn.cursor()
            cursor.execute('''
            SELECT * FROM products 
            WHERE group_id = ? AND name = ? AND expiry = ?
            ''', (group["id"], product_data["name"], product_data["expiry"]))
            
            existing_product = cursor.fetchone()
            
            if existing_product:
                # Converter para dicionário
                existing_product_dict = self._convert_to_dict([existing_product])[0]
                
                # Atualizar quantidade
                updated_product = existing_product_dict.copy()
                updated_product["quantity"] = existing_product_dict["quantity"] + int(product_data["quantity"])
                updated_product["lastUpdateDate"] = self.get_current_date()
                
                # Se tiver fabricante, atualizar
                if "manufacturer" in product_data and product_data["manufacturer"]:
                    updated_product["manufacturer"] = product_data["manufacturer"]
                
                # Atualizar produto existente
                return self.update_product(existing_product_dict["id"], updated_product)
            
            # Gerar ID único
            product_id = datetime.now().strftime('%Y%m%d%H%M%S')
            
            # Preparar dados do produto
            product = {
                "id": product_id,
                "name": product_data["name"],
                "quantity": int(product_data["quantity"]),
                "lot": product_data["lot"],
                "expiry": product_data["expiry"],
                "entryDate": product_data.get("entryDate", self.get_current_date()),
                "fabDate": product_data.get("fabDate", ""),
                "exitDate": product_data.get("exitDate", ""),
                "category": product_data.get("category", ""),
                "location": product_data.get("location", ""),
                "weeklyUsage": product_data.get("weeklyUsage", [0] * 7),
                "lastUpdateDate": self.get_current_date(),
                "group_id": product_data.get("group_id", ""),
                "manufacturer": product_data.get("manufacturer", "")
            }
            
            # Salvar localmente usando transação
            with self.transaction():
                cursor = self.db.conn.cursor()
                cursor.execute('''
                INSERT INTO products (
                    id, name, quantity, lot, expiry, entryDate, 
                    fabDate, exitDate, weeklyUsage, lastUpdateDate,
                    category, location, group_id, manufacturer
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    product["id"], product["name"], product["quantity"],
                    product["lot"], product["expiry"], product["entryDate"],
                    product["fabDate"], product["exitDate"],
                    json.dumps(product["weeklyUsage"]),
                    product["lastUpdateDate"],
                    product["category"], product["location"],
                    product["group_id"], product["manufacturer"]
                ))
            
            # Sincronizar com Firebase
            self.sync_with_firebase('products', product_id, product, 'add')
            
            # Criar notificação
            self._create_product_notification(product)
            
            return product
        except Exception as e:
            return self.log_error("Erro ao adicionar produto", e)
    
    def get_all_products(self):
        """Retorna todos os produtos com tratamento de erros"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute('''
            SELECT id, name, quantity, lot, expiry, entryDate, 
                fabDate, exitDate, weeklyUsage, lastUpdateDate
            FROM products 
            ORDER BY name
            ''')
            results = cursor.fetchall()
            products = self._convert_to_dict(results)
            print(f"get_all_products: {len(products)} produtos encontrados")
            return products
        except Exception as e:
            print(f"Erro ao buscar produtos: {e}")
            import traceback
            traceback.print_exc()
            
            # Tentar novamente com uma nova conexão
            try:
                cursor = self.db.conn.cursor()
                cursor.execute('''
                SELECT id, name, quantity, lot, expiry, entryDate, 
                    fabDate, exitDate, weeklyUsage, lastUpdateDate
                FROM products 
                ORDER BY name
                ''')
                results = cursor.fetchall()
                products = self._convert_to_dict(results)
                print(f"Segunda tentativa: {len(products)} produtos encontrados")
                return products
            except Exception as e2:
                print(f"Erro na segunda tentativa de buscar produtos: {e2}")
                traceback.print_exc()
                return []
    
    def update_product(self, product_id, updated_product):
        """Atualiza um produto existente com tratamento de erros e sincronização"""
        try:
            # Validar dados do produto
            valid, _ = self.validate_required_fields(
                updated_product, ["name", "quantity", "lot", "expiry"]
            )
            if not valid:
                return None
            
            # Garantir que o ID não seja alterado
            updated_product["id"] = product_id
            
            # Atualizar data de última atualização
            updated_product["lastUpdateDate"] = self.get_current_date()
            
            # Atualizar localmente usando transação
            with self.transaction():
                cursor = self.db.conn.cursor()
                cursor.execute('''
                UPDATE products SET 
                    name = ?, quantity = ?, lot = ?, expiry = ?, 
                    fabDate = ?, exitDate = ?, weeklyUsage = ?, lastUpdateDate = ?,
                    category = ?, location = ?
                WHERE id = ?
                ''', (
                    updated_product["name"], updated_product["quantity"],
                    updated_product["lot"], updated_product["expiry"],
                    updated_product.get("fabDate", ""), updated_product.get("exitDate", ""),
                    json.dumps(updated_product.get("weeklyUsage", [0] * 7)),
                    updated_product["lastUpdateDate"],
                    updated_product.get("category", ""), updated_product.get("location", ""),
                    product_id
                ))
            
            # Sincronizar com Firebase
            self.sync_with_firebase('products', product_id, updated_product, 'update')
            
            return updated_product
        except Exception as e:
            self.log_error("Erro ao atualizar produto", e)
            return None
    
    def delete_product(self, product_id):
        """Exclui um produto com tratamento de erros e sincronização"""
        try:
            print(f"Iniciando exclusão do produto com ID: {product_id}")
            
            # Buscar produto antes de excluir para ter os dados para sincronização
            cursor = self.db.conn.cursor()
            cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
            product_data = cursor.fetchone()
            
            if not product_data:
                print(f"Produto com ID {product_id} não encontrado")
                return False
            
            # Excluir diretamente do banco de dados, sem converter para dicionário
            cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))
            rows_affected = cursor.rowcount
            self.db.conn.commit()
            print(f"Produto com ID {product_id} excluído localmente. Linhas afetadas: {rows_affected}")
            
            # Verificar se a exclusão foi bem-sucedida
            cursor.execute('SELECT COUNT(*) FROM products WHERE id = ?', (product_id,))
            count = cursor.fetchone()[0]
            if count > 0:
                print(f"ERRO: Produto ainda existe no banco de dados após exclusão!")
                return False
            
            # Tentar excluir no Firebase se estiver online
            if self.firebase and hasattr(self.firebase, 'online_mode') and self.firebase.online_mode:
                try:
                    self.firebase.db.collection('products').document(product_id).delete()
                    print(f"Produto com ID {product_id} excluído do Firebase")
                except Exception as e:
                    print(f"Erro ao excluir produto do Firebase: {e}")
                    # Adicionar à fila de sincronização
                    self.db.add_sync_operation('delete', 'products', product_id, {})
            else:
                # Adicionar à fila de sincronização
                self.db.add_sync_operation('delete', 'products', product_id, {})
            
            print(f"Exclusão do produto com ID {product_id} concluída com sucesso")
            return True
        except Exception as e:
            print(f"Erro ao excluir produto: {e}")
            import traceback
            traceback.print_exc()
            try:
                self.db.conn.rollback()
            except:
                pass
            return False
    
    def _convert_to_dict(self, rows):
        """Converte resultados do banco de dados em dicionários com tratamento de erros"""
        products = []
        if not rows:
            return products
            
        for row in rows:
            try:
                # Verificar se temos dados suficientes
                if len(row) < 10:
                    print(f"Aviso: Linha com dados incompletos: {row}")
                    continue
                
                # Extrair valores com tratamento de nulos
                product = {
                    "id": row[0] or str(uuid.uuid4()),
                    "name": row[1] or "Produto sem nome",
                    "quantity": int(row[2]) if row[2] is not None else 0,
                    "lot": row[3] or "",
                    "expiry": row[4] or self.get_current_date(),
                    "entryDate": row[5] or self.get_current_date(),
                    "fabDate": row[6] or "",
                    "exitDate": row[7] or "",
                    "weeklyUsage": json.loads(row[8]) if row[8] else [0] * 7,
                    "lastUpdateDate": row[9] or self.get_current_date()
                }
                
                # Adicionar campos opcionais se disponíveis
                if len(row) > 10:
                    product["category"] = row[10] or ""
                if len(row) > 11:
                    product["location"] = row[11] or ""
                
                products.append(product)
            except Exception as e:
                self.log_error(f"Erro ao converter produto", e)
                continue
        
        return products
    
    def _create_product_notification(self, product):
        """Cria notificações relacionadas ao produto"""
        try:
            from services.notification_service import NotificationService
            notification_service = NotificationService(self.firebase, self.db)
            
            # Notificação de produto adicionado
            notification_service.create_notification(
                "PRODUCT_ADDED",
                f"Produto '{product['name']}' foi adicionado ao estoque",
                product["id"]
            )
            
            # Verificar se o produto já está com estoque baixo
            threshold = 5  # Valor padrão, idealmente baseado nas configurações
            if product["quantity"] <= threshold:
                notification_service.create_notification(
                    "LOW_STOCK",
                    f"Produto '{product['name']}' foi adicionado com estoque baixo ({product['quantity']} unidades)",
                    product["id"]
                )
            
            # Verificar se o produto já está próximo ao vencimento
            try:
                expiry_date = datetime.strptime(product["expiry"], "%d/%m/%Y")
                days_remaining = (expiry_date - datetime.now()).days
                
                if days_remaining <= 30:  # Valor padrão, idealmente baseado nas configurações
                    notification_service.create_notification(
                        "EXPIRY",
                        f"Produto '{product['name']}' vence em {days_remaining} dias ({product['expiry']})",
                        product["id"]
                    )
            except Exception as e:
                self.log_error("Erro ao verificar data de validade", e)
            
            return True
        except Exception as e:
            self.log_error("Erro ao criar notificações para o produto", e)
            return False
    
    # Métodos adicionais refatorados
    def get_low_stock_products(self, threshold=5):
        """Retorna produtos com estoque abaixo do limiar especificado"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute('SELECT * FROM products WHERE quantity <= ? ORDER BY quantity', (threshold,))
            results = cursor.fetchall()
            return self._convert_to_dict(results)
        except Exception as e:
            self.log_error("Erro ao buscar produtos com estoque baixo", e)
            return []

    def get_expiring_products(self, days_threshold=30):
        """Retorna produtos que vencem dentro do número de dias especificado"""
        try:
            # Buscar todos os produtos e filtrar em memória
            # Isso é mais seguro que tentar comparar datas no SQLite
            products = self.get_all_products()
            expiring = []
            
            for product in products:
                if self._is_expiring_soon(product.get("expiry", ""), days_threshold):
                    expiring.append(product)
            
            return expiring
        except Exception as e:
            self.log_error("Erro ao buscar produtos próximos ao vencimento", e)
            return []

    def get_weekly_usage_data(self):
        """Retorna dados de uso semanal para todos os produtos"""
        try:
            products = self.get_all_products()
            weekly_data = []
            
            for product in products:
                if "weeklyUsage" in product and product["weeklyUsage"]:
                    product_data = {
                        "id": product["id"],
                        "name": product["name"],
                        "weeklyUsage": product["weeklyUsage"]
                    }
                    weekly_data.append(product_data)
            
            return weekly_data
        except Exception as e:
            self.log_error("Erro ao buscar dados de uso semanal", e)
            return []
        
    def _is_expiring_soon(self, expiry_date_str, days_threshold):
        """Verifica se um produto está próximo da data de validade"""
        try:
            if not expiry_date_str:
                return False
                
            expiry_date = datetime.strptime(expiry_date_str, "%d/%m/%Y")
            days_remaining = (expiry_date - datetime.now()).days
            return 0 <= days_remaining <= days_threshold
        except Exception as e:
            self.log_error(f"Erro ao verificar data de validade: {expiry_date_str}", e)
            return False
    
    def update_weekly_usage(self, product_id, usage_data):
        """Atualiza os dados de uso semanal de um produto"""
        try:
            # Buscar produto atual
            cursor = self.db.conn.cursor()
            cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
            product_data = cursor.fetchone()
            
            if not product_data:
                return self.log_error(f"Produto com ID {product_id} não encontrado")
            
            # Converter para dicionário
            product = self._convert_to_dict([product_data])[0]
            
            # Atualizar dados de uso semanal
            product["weeklyUsage"] = usage_data
            
            # Atualizar produto
            return self.update_product(product_id, product)
        except Exception as e:
            self.log_error("Erro ao atualizar uso semanal", e)
            return False
    
    def register_product_exit(self, product_id, quantity, reason, exit_type="venda"):
        """Registra a saída de um produto do estoque"""
        try:
            print(f"Iniciando registro de saída para produto ID: {product_id}, quantidade: {quantity}, tipo: {exit_type}")
            
            # Obter o produto do banco de dados local
            cursor = self.db.conn.cursor()
            cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
            product_data = cursor.fetchone()
            
            if not product_data:
                print(f"Produto com ID {product_id} não encontrado")
                return False, "Produto não encontrado"
            
            # Converter para dicionário
            product = self._convert_to_dict([product_data])[0]
            current_quantity = int(product.get('quantity', 0))
            
            print(f"Produto encontrado: {product.get('name')}, estoque atual: {current_quantity}")
            
            # Verificar se há quantidade suficiente
            if current_quantity < quantity:
                print(f"Quantidade insuficiente. Disponível: {current_quantity}, solicitado: {quantity}")
                return False, f"Quantidade insuficiente. Disponível: {current_quantity}"
            
            # Atualizar a quantidade
            new_quantity = current_quantity - quantity
            product["quantity"] = new_quantity
            product["lastUpdateDate"] = self.get_current_date()
            
            print(f"Nova quantidade após saída: {new_quantity}")
            
            # Atualizar o uso semanal APENAS se o tipo for "uso_semanal"
            weekly_usage = product.get("weeklyUsage", [0] * 7)
            
            # Garantir que weekly_usage seja uma lista
            if not isinstance(weekly_usage, list):
                try:
                    import json
                    weekly_usage = json.loads(weekly_usage)
                except:
                    weekly_usage = [0] * 7
            
            # Garantir que a lista tenha 7 elementos
            while len(weekly_usage) < 7:
                weekly_usage.append(0)
            
            # Limitar a 7 elementos se tiver mais
            weekly_usage = weekly_usage[:7]
            
            # Atualizar o uso semanal apenas se o tipo for "uso_semanal"
            if exit_type == "uso_semanal":
                try:
                    # Obter o dia da semana atual (0 = segunda, 6 = domingo)
                    from datetime import datetime
                    today = datetime.now().weekday()
                    # Converter para formato onde 0 = domingo, 6 = sábado
                    day_index = (today + 1) % 7
                    
                    # Adicionar a quantidade à saída do dia atual
                    try:
                        current_usage = int(weekly_usage[day_index]) if weekly_usage[day_index] else 0
                        weekly_usage[day_index] = current_usage + quantity
                        print(f"Uso semanal atualizado para o dia {day_index}: {weekly_usage[day_index]}")
                    except (ValueError, TypeError, IndexError):
                        weekly_usage[day_index] = quantity
                        print(f"Uso semanal definido para o dia {day_index}: {quantity}")
                    
                    print(f"Uso semanal atualizado: {weekly_usage}")
                except Exception as weekly_error:
                    print(f"Erro ao atualizar uso semanal: {weekly_error}")
                    import traceback
                    traceback.print_exc()
            else:
                print(f"Tipo de saída '{exit_type}' não atualiza o uso semanal")
            
            # Atualizar o produto no banco de dados com todas as alterações
            try:
                cursor.execute('''
                UPDATE products SET 
                    quantity = ?,
                    lastUpdateDate = ?,
                    weeklyUsage = ?
                WHERE id = ?
                ''', (new_quantity, self.get_current_date(), json.dumps(weekly_usage), product_id))
                
                self.db.conn.commit()
                print(f"Produto atualizado no banco de dados com novo estoque e uso semanal")
                
                # Verificar se a atualização foi bem-sucedida
                cursor.execute('SELECT quantity, weeklyUsage FROM products WHERE id = ?', (product_id,))
                updated_data = cursor.fetchone()
                if updated_data:
                    updated_quantity, updated_weekly_usage = updated_data
                    print(f"Verificação após atualização: Quantidade = {updated_quantity}, Uso semanal = {updated_weekly_usage}")
                
            except Exception as update_error:
                print(f"Erro ao atualizar produto: {update_error}")
                import traceback
                traceback.print_exc()
                return False, f"Erro ao atualizar produto: {str(update_error)}"
            
            # Registrar no histórico
            history_success = self._register_exit_history(product, quantity, reason, exit_type)
            if not history_success:
                print("Aviso: Falha ao registrar histórico de saída, mas o estoque foi atualizado")
            
            # Adicionar à fila de sincronização
            try:
                # Obter o produto atualizado
                cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
                updated_product_data = cursor.fetchone()
                updated_product = self._convert_to_dict([updated_product_data])[0]
                
                # Sincronizar com Firebase
                self.sync_with_firebase('products', product_id, updated_product, 'update')
                print(f"Produto adicionado à fila de sincronização")
            except Exception as sync_error:
                print(f"Erro ao adicionar à fila de sincronização: {sync_error}")
            
            return True, f"Saída de {quantity} unidades registrada com sucesso"
        except Exception as e:
            print(f"Erro ao registrar saída: {e}")
            import traceback
            traceback.print_exc()
            return False, f"Erro ao registrar saída: {str(e)}"
    
    def _register_exit_history(self, product, quantity, reason, exit_type="venda"):
        """Registra a saída no histórico"""
        try:
            # Criar registro de histórico
            exit_record = {
                "id": f"exit_{product['id']}_{int(time.time())}",
                "productId": product.get("id"),
                "productName": product.get("name"),
                "quantity": quantity,
                "reason": reason,
                "date": self.get_current_date(),
                "timestamp": self.get_current_timestamp(),
                "type": "exit",
                "exit_type": exit_type  # Novo campo para o tipo de saída
            }
            
            # Verificar se a coluna exit_type existe
            cursor = self.db.conn.cursor()
            cursor.execute("PRAGMA table_info(product_history)")
            columns = cursor.fetchall()
            column_names = [column[1] for column in columns]
            
            # Salvar no banco de dados
            with self.transaction():
                if "exit_type" in column_names:
                    # Se a coluna existir, incluir no INSERT
                    cursor.execute('''
                    INSERT INTO product_history (
                        id, productId, productName, quantity, reason, date, timestamp, type, exit_type
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        exit_record["id"], exit_record["productId"], exit_record["productName"],
                        exit_record["quantity"], exit_record["reason"], exit_record["date"],
                        exit_record["timestamp"], exit_record["type"], exit_record["exit_type"]
                    ))
                else:
                    # Se a coluna não existir, omitir do INSERT
                    cursor.execute('''
                    INSERT INTO product_history (
                        id, productId, productName, quantity, reason, date, timestamp, type
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        exit_record["id"], exit_record["productId"], exit_record["productName"],
                        exit_record["quantity"], exit_record["reason"], exit_record["date"],
                        exit_record["timestamp"], exit_record["type"]
                    ))
                    
                    # Tentar adicionar a coluna exit_type
                    try:
                        cursor.execute("ALTER TABLE product_history ADD COLUMN exit_type TEXT DEFAULT 'venda'")
                        print("Coluna exit_type adicionada à tabela product_history")
                    except:
                        print("Não foi possível adicionar a coluna exit_type, continuando sem ela")
            
            # Sincronizar com Firebase
            self.sync_with_firebase('product_history', exit_record["id"], exit_record, 'add')
            
            # Criar notificação
            from services.notification_service import NotificationService
            notification_service = NotificationService(self.firebase, self.db)
            notification_service.create_notification(
                "PRODUCT_EXIT",
                f"Saída de {quantity} unidades de '{product.get('name')}' - Motivo: {reason}",
                product.get("id")
            )
            
            return True
        except Exception as e:
            self.log_error("Erro ao registrar histórico de saída", e)
            return False
   
    def get_product_exits(self, product_id, limit=5, exit_type=None):
        """Obtém o histórico de saídas de um produto"""
        try:
            # Referência à coleção de saídas
            exits_ref = self.firebase.db.collection('product_exits')
            
            # Consultar saídas para o produto específico, ordenadas por data (mais recentes primeiro)
            from google.cloud.firestore_v1.base_query import FieldFilter

            # Criar a consulta base
            query = exits_ref.where(filter=FieldFilter("product_id", "==", product_id))
            
            # Se um tipo de saída foi especificado, adicionar filtro
            if exit_type:
                query = query.where(filter=FieldFilter("exit_type", "==", exit_type))
            
            # Executar a consulta
            exits = query.get()
            
            # Converter para lista de dicionários
            exit_list = []
            for exit_doc in exits:
                exit_data = exit_doc.to_dict()
                exit_data['id'] = exit_doc.id
                exit_list.append(exit_data)
            
            return exit_list
        except Exception as e:
            print(f"Erro ao buscar histórico de saídas: {e}")
            return []
        
    def get_product(self, product_id):
        """Obtém um produto pelo ID, independentemente do grupo"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
            product_data = cursor.fetchone()
            
            if not product_data:
                print(f"Produto com ID {product_id} não encontrado")
                return None
            
            # Converter para dicionário
            product = self._convert_to_dict([product_data])[0]
            
            # Obter informações do grupo, se existir
            if "group_id" in product and product["group_id"]:
                from services.group_service import GroupService
                group_service = GroupService(self.firebase, self.db)
                group = group_service.get_product_group(product["group_id"])
                if group:
                    product["group_name"] = group.get("name", "")
            
            return product
        except Exception as e:
            print(f"Erro ao obter produto: {e}")
            import traceback
            traceback.print_exc()
            return None
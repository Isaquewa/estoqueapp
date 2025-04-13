from datetime import datetime
import traceback

class GroupService:
    """Serviço para gerenciar grupos de produtos e resíduos"""
    
    def __init__(self, firebase, db):
        self.firebase = firebase
        self.db = db
        self.product_groups_collection = "product_groups"
        self.residue_groups_collection = "residue_groups"
    
    def get_all_product_groups(self):
        """Obtém todos os grupos de produtos"""
        try:
            groups = []
            
            # Verificar se estamos usando Firebase ou SQLite
            if hasattr(self.db, 'collection'):
                # Usando Firebase
                docs = self.db.collection(self.product_groups_collection).get()
                
                for doc in docs:
                    group = doc.to_dict()
                    group["id"] = doc.id
                    groups.append(group)
            else:
                # Usando SQLite
                cursor = self.db.execute_query(f"SELECT * FROM {self.product_groups_collection}")
                if cursor:
                    for row in cursor.fetchall():
                        # Converter a linha em um dicionário
                        cursor.execute(f"PRAGMA table_info({self.product_groups_collection})")
                        columns = [info[1] for info in cursor.fetchall()]
                        
                        group = {}
                        for i, col in enumerate(columns):
                            group[col] = row[i]
                        
                        # Garantir que o ID esteja presente
                        if "id" not in group and len(row) > 0:
                            group["id"] = row[0]
                            
                        groups.append(group)
            
            return groups
        except Exception as e:
            print(f"Erro ao obter grupos de produtos: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_all_residue_groups(self):
        """Obtém todos os grupos de resíduos"""
        try:
            groups = []
            
            # Verificar se estamos usando Firebase ou SQLite
            if hasattr(self.db, 'collection'):
                # Usando Firebase
                docs = self.db.collection(self.residue_groups_collection).get()
                
                for doc in docs:
                    group = doc.to_dict()
                    group["id"] = doc.id
                    groups.append(group)
            else:
                # Usando SQLite
                cursor = self.db.execute_query(f"SELECT * FROM {self.residue_groups_collection}")
                if cursor:
                    for row in cursor.fetchall():
                        # Converter a linha em um dicionário
                        cursor.execute(f"PRAGMA table_info({self.residue_groups_collection})")
                        columns = [info[1] for info in cursor.fetchall()]
                        
                        group = {}
                        for i, col in enumerate(columns):
                            group[col] = row[i]
                        
                        # Garantir que o ID esteja presente
                        if "id" not in group and len(row) > 0:
                            group["id"] = row[0]
                            
                        groups.append(group)
            
            return groups
        except Exception as e:
            print(f"Erro ao obter grupos de resíduos: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_product_group(self, group_id):
        """Obtém um grupo de produtos pelo ID"""
        try:
            if hasattr(self.db, 'collection'):
                # Usando Firebase
                doc = self.db.collection(self.product_groups_collection).document(group_id).get()
                
                if doc.exists:
                    group = doc.to_dict()
                    group["id"] = doc.id
                    return group
                else:
                    return None
            else:
                # Usando SQLite
                cursor = self.db.execute_query(
                    f"SELECT * FROM {self.product_groups_collection} WHERE id = ?", 
                    (group_id,)
                )
                if cursor:
                    row = cursor.fetchone()
                    if row:
                        # Converter a linha em um dicionário
                        cursor.execute(f"PRAGMA table_info({self.product_groups_collection})")
                        columns = [info[1] for info in cursor.fetchall()]
                        
                        group = {}
                        for i, col in enumerate(columns):
                            group[col] = row[i]
                        
                        # Garantir que o ID esteja presente
                        if "id" not in group:
                            group["id"] = group_id
                            
                        return group
                return None
        except Exception as e:
            print(f"Erro ao obter grupo de produtos: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_residue_group(self, group_id):
        """Obtém um grupo de resíduos pelo ID"""
        try:
            if hasattr(self.db, 'collection'):
                # Usando Firebase
                doc = self.db.collection(self.residue_groups_collection).document(group_id).get()
                
                if doc.exists:
                    group = doc.to_dict()
                    group["id"] = doc.id
                    return group
                else:
                    return None
            else:
                # Usando SQLite
                cursor = self.db.execute_query(
                    f"SELECT * FROM {self.residue_groups_collection} WHERE id = ?", 
                    (group_id,)
                )
                if cursor:
                    row = cursor.fetchone()
                    if row:
                        # Converter a linha em um dicionário
                        cursor.execute(f"PRAGMA table_info({self.residue_groups_collection})")
                        columns = [info[1] for info in cursor.fetchall()]
                        
                        group = {}
                        for i, col in enumerate(columns):
                            group[col] = row[i]
                        
                        # Garantir que o ID esteja presente
                        if "id" not in group:
                            group["id"] = group_id
                            
                        return group
                return None
        except Exception as e:
            print(f"Erro ao obter grupo de resíduos: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def create_product_group(self, group):
        """Cria um novo grupo de produtos"""
        try:
            group_id = group.get("id", "")
            
            if not group_id:
                return False
            
            # Remover ID do objeto antes de salvar
            group_data = {k: v for k, v in group.items() if k != "id"}
            
            if hasattr(self.db, 'collection'):
                # Usando Firebase
                self.db.collection(self.product_groups_collection).document(group_id).set(group_data)
            else:
                # Usando SQLite
                # Criar colunas e valores para a query SQL
                columns = ", ".join(group_data.keys())
                placeholders = ", ".join(["?" for _ in group_data])
                values = tuple(group_data.values())
                
                # Verificar se o grupo já existe
                cursor = self.db.execute_query(
                    f"SELECT id FROM {self.product_groups_collection} WHERE id = ?",
                    (group_id,)
                )
                
                if cursor and cursor.fetchone():
                    # Atualizar grupo existente
                    set_clause = ", ".join([f"{k} = ?" for k in group_data.keys()])
                    self.db.execute_query(
                        f"UPDATE {self.product_groups_collection} SET {set_clause} WHERE id = ?",
                        values + (group_id,)
                    )
                else:
                    # Inserir novo grupo
                    self.db.execute_query(
                        f"INSERT INTO {self.product_groups_collection} (id, {columns}) VALUES (?, {placeholders})",
                        (group_id,) + values
                    )
            
            return True
        except Exception as e:
            print(f"Erro ao criar grupo de produtos: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def create_residue_group(self, group_data):
        """Cria um novo grupo de resíduos"""
        try:
            # Remover a propriedade type se existir
            group_data_to_save = group_data.copy()
            if "type" in group_data_to_save:
                del group_data_to_save["type"]
                
            # Inserir no banco de dados
            cursor = self.db.conn.cursor()
            cursor.execute('''
            INSERT INTO residue_groups (id, name, description, icon, color, created_at, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                group_data_to_save["id"], 
                group_data_to_save["name"], 
                group_data_to_save.get("description", ""),
                group_data_to_save.get("icon", "DELETE_OUTLINE"), 
                group_data_to_save.get("color", "PURPLE_500"),
                group_data_to_save.get("created_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                group_data_to_save.get("last_updated", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            ))
            self.db.conn.commit()
            
            # Adicionar a propriedade type ao objeto retornado
            group_data["type"] = "residue"
            
            return group_data
        except Exception as e:
            print(f"Erro ao criar grupo de resíduos: {e}")
            traceback.print_exc()
            return None
    
    def update_product_group(self, group_id, group_data):
        """Atualiza um grupo de produtos"""
        try:
            # Remover ID do objeto antes de salvar
            group_data = {k: v for k, v in group_data.items() if k != "id"}
            
            if hasattr(self.db, 'collection'):
                # Usando Firebase
                self.db.collection(self.product_groups_collection).document(group_id).update(group_data)
            else:
                # Usando SQLite
                set_clause = ", ".join([f"{k} = ?" for k in group_data.keys()])
                values = tuple(group_data.values())
                
                self.db.execute_query(
                    f"UPDATE {self.product_groups_collection} SET {set_clause} WHERE id = ?",
                    values + (group_id,)
                )
            
            return True
        except Exception as e:
            print(f"Erro ao atualizar grupo de produtos: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def update_residue_group(self, group_id, group_data):
        """Atualiza um grupo de resíduos"""
        try:
            # Remover ID do objeto antes de salvar
            group_data = {k: v for k, v in group_data.items() if k != "id"}
            
            if hasattr(self.db, 'collection'):
                # Usando Firebase
                self.db.collection(self.residue_groups_collection).document(group_id).update(group_data)
            else:
                # Usando SQLite
                set_clause = ", ".join([f"{k} = ?" for k in group_data.keys()])
                values = tuple(group_data.values())
                
                self.db.execute_query(
                    f"UPDATE {self.residue_groups_collection} SET {set_clause} WHERE id = ?",
                    values + (group_id,)
                )
            
            return True
        except Exception as e:
            print(f"Erro ao atualizar grupo de resíduos: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def delete_product_group(self, group_id):
        """Exclui um grupo de produtos"""
        try:
            if hasattr(self.db, 'collection'):
                # Usando Firebase
                self.db.collection(self.product_groups_collection).document(group_id).delete()
            else:
                # Usando SQLite
                self.db.execute_query(
                    f"DELETE FROM {self.product_groups_collection} WHERE id = ?",
                    (group_id,)
                )
            
            return True
        except Exception as e:
            print(f"Erro ao excluir grupo de produtos: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def delete_group(self, group_id, is_residue=False):
        """Exclui um grupo do banco de dados"""
        try:
            print(f"GroupService: Excluindo grupo com ID {group_id}, is_residue={is_residue}")
            
            # Determinar a tabela correta
            table = "residue_groups" if is_residue else "product_groups"
            
            # Primeiro, remover a associação de produtos/resíduos com o grupo
            if not is_residue:
                self.remove_products_from_group(group_id)
            else:
                # Implementar método similar para resíduos se necessário
                pass
            
            # Excluir do banco de dados
            cursor = self.db.conn.cursor()
            cursor.execute(f'DELETE FROM {table} WHERE id = ?', (group_id,))
            rows_affected = cursor.rowcount
            self.db.conn.commit()
            
            print(f"GroupService: Grupo excluído do banco de dados. Linhas afetadas: {rows_affected}")
            
            # Verificar se a exclusão foi bem-sucedida
            cursor.execute(f'SELECT COUNT(*) FROM {table} WHERE id = ?', (group_id,))
            count = cursor.fetchone()[0]
            if count > 0:
                print(f"ERRO: Grupo ainda existe no banco de dados após exclusão!")
                return False
            
            # Sincronizar com Firebase
            if self.firebase and hasattr(self.firebase, 'online_mode') and self.firebase.online_mode:
                try:
                    collection = "residue_groups" if is_residue else "product_groups"
                    self.firebase.db.collection(collection).document(group_id).delete()
                    print(f"Grupo excluído do Firebase")
                except Exception as e:
                    print(f"Erro ao excluir grupo do Firebase: {e}")
                    # Adicionar à fila de sincronização
                    self.db.add_sync_operation('delete', collection, group_id, {})
            else:
                # Adicionar à fila de sincronização
                collection = "residue_groups" if is_residue else "product_groups"
                self.db.add_sync_operation('delete', collection, group_id, {})
            
            return True
        except Exception as e:
            print(f"Erro ao excluir grupo: {e}")
            import traceback
            traceback.print_exc()
            try:
                self.db.conn.rollback()
            except:
                pass
            return False
    def remove_products_from_group(self, group_id):
        """Remove a associação de produtos com o grupo"""
        try:
            print(f"GroupService: Removendo associação de produtos com o grupo {group_id}")
            
            # Atualizar produtos no banco de dados
            cursor = self.db.conn.cursor()
            cursor.execute('UPDATE products SET group_id = NULL WHERE group_id = ?', (group_id,))
            rows_affected = cursor.rowcount
            self.db.conn.commit()
            
            print(f"GroupService: {rows_affected} produtos desassociados do grupo")
            return True
        except Exception as e:
            print(f"Erro ao remover produtos do grupo: {e}")
            import traceback
            traceback.print_exc()
            try:
                self.db.conn.rollback()
            except:
                pass
            return False
    
    def assign_product_to_group(self, product_id, group_id):
        """Atribui um produto a um grupo"""
        try:
            if hasattr(self.db, 'collection'):
                # Usando Firebase
                self.db.collection("stock_products").document(product_id).update({
                    "group_id": group_id
                })
            else:
                # Usando SQLite
                self.db.execute_query(
                    "UPDATE products SET group_id = ? WHERE id = ?",
                    (group_id, product_id)
                )
            
            return True
        except Exception as e:
            print(f"Erro ao atribuir produto ao grupo: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def assign_residue_to_group(self, residue_id, group_id):
        """Atribui um resíduo a um grupo"""
        try:
            if hasattr(self.db, 'collection'):
                # Usando Firebase
                self.db.collection("residues").document(residue_id).update({
                    "group_id": group_id
                })
            else:
                # Usando SQLite
                self.db.execute_query(
                    "UPDATE residues SET group_id = ? WHERE id = ?",
                    (group_id, residue_id)
                )
            
            return True
        except Exception as e:
            print(f"Erro ao atribuir resíduo ao grupo: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_products_in_group(self, group_id):
        """Obtém todos os produtos em um grupo"""
        try:
            products = []
            # Adicionar log para depuração
            print(f"Buscando produtos do grupo {group_id}")
            
            # Verificar se estamos usando o Firebase ou o SQLite
            if hasattr(self, 'db') and hasattr(self.db, 'conn'):
                # Usando SQLite
                cursor = self.db.conn.cursor()
                cursor.execute("SELECT * FROM products WHERE group_id = ?", (group_id,))
                rows = cursor.fetchall()
                
                # Obter nomes das colunas
                cursor.execute("PRAGMA table_info(products)")
                columns = [info[1] for info in cursor.fetchall()]
                
                for row in rows:
                    product = {columns[i]: row[i] for i in range(len(columns))}
                    product["id"] = product.get("id", "")  # Garantir que o ID esteja presente
                    products.append(product)
                
                print(f"SQLite: Encontrados {len(products)} produtos para o grupo {group_id}")
            else:
                # Usando Firebase
                docs = self.db.collection("stock_products").where("group_id", "==", group_id).get()
                
                for doc in docs:
                    product = doc.to_dict()
                    product["id"] = doc.id
                    products.append(product)
                
                print(f"Firebase: Encontrados {len(products)} produtos para o grupo {group_id}")
            
            return products
        except Exception as e:
            print(f"Erro ao obter produtos do grupo: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_residues_in_group(self, group_id):
        """Obtém todos os resíduos de um grupo específico"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute('''
            SELECT * FROM residues WHERE group_id = ?
            ''', (group_id,))
            
            rows = cursor.fetchall()
            
            # Converter para dicionários
            residues = []
            for row in rows:
                residue = {}
                cursor.execute("PRAGMA table_info(residues)")
                columns = [info[1] for info in cursor.fetchall()]
                
                for i, column in enumerate(columns):
                    if i < len(row):
                        residue[column] = row[i]
                
                residues.append(residue)
            
            return residues
        except Exception as e:
            print(f"Erro ao obter resíduos do grupo: {e}")
            import traceback
            traceback.print_exc()
        return []
            
    def extract_group_name(self, product_name):
        """Extrai um possível nome de grupo do nome do produto"""
        # Implementação simples: usar a primeira palavra do nome como grupo
        if not product_name:
            return ""
            
        # Tentar extrair o primeiro substantivo ou palavra significativa
        words = product_name.split()
        if len(words) > 0:
            return words[0].capitalize()
        return ""
        
    def extract_residue_group_name(self, residue_name):
        """Extrai um possível nome de grupo do nome do resíduo"""
        # Implementação simples: usar a primeira palavra do nome como grupo
        if not residue_name:
            return ""
            
        # Tentar extrair o primeiro substantivo ou palavra significativa
        words = residue_name.split()
        if len(words) > 0:
            return words[0].capitalize()
        return ""
        
    def get_or_create_product_group(self, group_name):
        """Obtém um grupo de produtos pelo nome ou cria um novo se não existir"""
        try:
            # Normalizar o nome do grupo
            group_name = group_name.strip().capitalize()
            
            if not group_name:
                return None
                
            # Verificar se o grupo já existe
            if hasattr(self.db, 'collection'):
                # Usando Firebase
                docs = self.db.collection(self.product_groups_collection).where("name", "==", group_name).get()
                
                for doc in docs:
                    group = doc.to_dict()
                    group["id"] = doc.id
                    return group
            else:
                # Usando SQLite
                cursor = self.db.execute_query(
                    f"SELECT * FROM {self.product_groups_collection} WHERE name = ?",
                    (group_name,)
                )
                
                if cursor:
                    row = cursor.fetchone()
                    if row:
                        # Converter a linha em um dicionário
                        cursor.execute(f"PRAGMA table_info({self.product_groups_collection})")
                        columns = [info[1] for info in cursor.fetchall()]
                        
                        group = {}
                        for i, col in enumerate(columns):
                            group[col] = row[i]
                        
                        # Garantir que o ID esteja presente
                        if "id" not in group and len(row) > 0:
                            group["id"] = row[0]
                            
                        return group
            
            # Se não existir, criar um novo grupo
            import uuid
            import time
            from datetime import datetime
            
            group_id = str(uuid.uuid4())
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            new_group = {
                "id": group_id,
                "name": group_name,
                "description": f"Grupo de produtos: {group_name}",
                "icon": "INVENTORY_2_ROUNDED",
                "color": "BLUE_500",
                "created_at": now,
                "last_updated": now
            }
            
            # Salvar o novo grupo
            self.create_product_group(new_group)
            
            return new_group
        except Exception as e:
            print(f"Erro ao obter ou criar grupo de produtos: {e}")
            import traceback
            traceback.print_exc()
            return None
            
    def get_or_create_residue_group(self, group_name):
        """Obtém um grupo de resíduos pelo nome ou cria um novo se não existir"""
        try:
            # Normalizar o nome do grupo
            group_name = group_name.strip().capitalize()
            
            if not group_name:
                return None
                    
            # Verificar se o grupo já existe
            if hasattr(self.db, 'collection'):
                # Usando Firebase
                docs = self.db.collection(self.residue_groups_collection).where("name", "==", group_name).get()
                
                for doc in docs:
                    group = doc.to_dict()
                    group["id"] = doc.id
                    
                    # Garantir que o tipo seja "residue"
                    if "type" not in group:
                        group["type"] = "residue"
                        self.firebase.db.collection(self.residue_groups_collection).document(doc.id).update({"type": "residue"})
                    
                    return group
            else:
                # Usando SQLite
                cursor = self.db.execute_query(
                    f"SELECT * FROM {self.residue_groups_collection} WHERE name = ?",
                    (group_name,)
                )
                
                if cursor:
                    row = cursor.fetchone()
                    if row:
                        # Converter a linha em um dicionário
                        cursor.execute(f"PRAGMA table_info({self.residue_groups_collection})")
                        columns = [info[1] for info in cursor.fetchall()]
                        
                        group = {}
                        for i, col in enumerate(columns):
                            group[col] = row[i]
                        
                        # Garantir que o ID esteja presente
                        if "id" not in group and len(row) > 0:
                            group["id"] = row[0]
                        
                        # Garantir que o tipo seja "residue"
                        if "type" not in group or group["type"] != "residue":
                            group["type"] = "residue"
                            self.db.execute_query(
                                f"UPDATE {self.residue_groups_collection} SET type = ? WHERE id = ?",
                                ("residue", group["id"])
                            )
                            
                        return group
            
            # Se não existir, criar um novo grupo
            import uuid
            import time
            from datetime import datetime
            
            group_id = str(uuid.uuid4())
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            new_group = {
                "id": group_id,
                "name": group_name,
                "description": f"Grupo de resíduos: {group_name}",
                "icon": "DELETE_OUTLINE",
                "color": "PURPLE_500",
                "created_at": now,
                "last_updated": now,
                "type": "residue"  # Definir explicitamente o tipo como "residue"
            }
            
            # Salvar o novo grupo
            self.create_residue_group(new_group)
            
            return new_group
        except Exception as e:
            print(f"Erro ao obter ou criar grupo de resíduos: {e}")
            import traceback
            traceback.print_exc()
            return None

    def update_group(self, group_id, group_data, is_residue=False):
        """Atualiza um grupo existente"""
        try:
            # Determinar a tabela com base no tipo de grupo
            table = "residue_groups" if is_residue else "product_groups"
            
            # Atualizar no banco de dados local
            cursor = self.db.conn.cursor()
            cursor.execute(f'''
            UPDATE {table} SET
                name = ?,
                description = ?,
                icon = ?,
                color = ?,
                last_updated = ?
            WHERE id = ?
            ''', (
                group_data["name"],
                group_data.get("description", ""),
                group_data.get("icon", "FOLDER"),
                group_data.get("color", "blue"),
                datetime.now().strftime("%d/%m/%Y"),
                group_id
            ))
            self.db.conn.commit()
            
            # Sincronizar com Firebase
            collection = "residue_groups" if is_residue else "product_groups"
            if self.firebase and self.firebase.online_mode:
                try:
                    self.firebase.db.collection(collection).document(group_id).update(group_data)
                except Exception as e:
                    print(f"Erro ao sincronizar atualização de grupo com Firebase: {e}")
                    # Adicionar à fila de sincronização
                    self.db.add_sync_operation('update', collection, group_id, group_data)
            else:
                # Adicionar à fila de sincronização
                self.db.add_sync_operation('update', collection, group_id, group_data)
            
            return True
        except Exception as e:
            print(f"Erro ao atualizar grupo: {e}")
            import traceback
            traceback.print_exc()
            return False
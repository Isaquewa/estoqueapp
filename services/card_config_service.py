class CardConfigService:
    """Serviço para gerenciar configurações de cards no dashboard"""
    
    def __init__(self, firebase, db):
        self.firebase = firebase
        self.db = db
        self.collection_name = "dashboard_config"
        
        # Garantir que a tabela exista se estiver usando SQLite
        if not hasattr(self.db, 'collection'):
            self._ensure_config_table_exists()
    
    def _ensure_config_table_exists(self):
        """Garante que a tabela de configuração existe no SQLite"""
        try:
            # Verificar se a tabela existe
            cursor = self.db.execute_query(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                (self.collection_name,)
            )
            
            if not cursor or not cursor.fetchone():
                # Criar tabela
                print(f"Criando tabela {self.collection_name} no SQLite...")
                self.db.execute_query(f"""
                CREATE TABLE {self.collection_name} (
                    id TEXT PRIMARY KEY,
                    config_data TEXT NOT NULL
                )
                """)
                print(f"Tabela {self.collection_name} criada com sucesso")
                
                # Inserir configurações padrão
                self._insert_default_configs()
            else:
                print(f"Tabela {self.collection_name} já existe")
                
            return True
        except Exception as e:
            print(f"Erro ao criar tabela de configuração: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _insert_default_configs(self):
        """Insere configurações padrão na tabela"""
        try:
            import json
            
            # Configuração padrão para grupos de produtos do dashboard
            product_groups_config = {"group_ids": []}
            self.db.execute_query(
                f"INSERT INTO {self.collection_name} (id, config_data) VALUES (?, ?)",
                ("dashboard_product_groups", json.dumps(product_groups_config))
            )
            
            # Configuração padrão para grupos de resíduos do dashboard
            residue_groups_config = {"group_ids": []}
            self.db.execute_query(
                f"INSERT INTO {self.collection_name} (id, config_data) VALUES (?, ?)",
                ("dashboard_residue_groups", json.dumps(residue_groups_config))
            )
            
            print("Configurações padrão inseridas com sucesso")
            return True
        except Exception as e:
            print(f"Erro ao inserir configurações padrão: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_product_group_config(self, group_id):
        """Obtém a configuração de um grupo de produtos pelo ID"""
        try:
            config_id = f"product_{group_id}"
            
            if hasattr(self.db, 'collection'):
                # Usando Firebase
                doc = self.db.collection(self.collection_name).document(config_id).get()
                
                if doc.exists:
                    return doc.to_dict()
            else:
                # Usando SQLite
                cursor = self.db.execute_query(
                    f"SELECT * FROM {self.collection_name} WHERE id = ?",
                    (config_id,)
                )
                
                if cursor:
                    row = cursor.fetchone()
                    if row:
                        # Converter a linha em um dicionário
                        cursor.execute(f"PRAGMA table_info({self.collection_name})")
                        columns = [info[1] for info in cursor.fetchall()]
                        
                        config = {}
                        for i, col in enumerate(columns):
                            if col == "config_data":
                                # Se tiver um campo JSON, fazer parse
                                import json
                                try:
                                    config = json.loads(row[i])
                                except:
                                    pass
                            else:
                                config[col] = row[i]
                        
                        return config
            
            # Configuração padrão se não encontrar
            return {
                "icon": "INVENTORY_2_ROUNDED",
                "color": "BLUE_500",
                "bgcolor": "#FFFFFF",
                "show_quantity": True,
                "show_details": True,
                "custom_title": "",
                "priority": "normal"
            }
        except Exception as e:
            print(f"Erro ao obter configuração do grupo de produtos: {e}")
            return {
                "icon": "INVENTORY_2_ROUNDED",
                "color": "BLUE_500",
                "bgcolor": "#FFFFFF",
                "show_quantity": True,
                "show_details": True,
                "custom_title": "",
                "priority": "normal"
            }
    
    def get_residue_group_config(self, group_id):
        """Obtém a configuração de um grupo de resíduos pelo ID"""
        try:
            config_id = f"residue_{group_id}"
            
            if hasattr(self.db, 'collection'):
                # Usando Firebase
                doc = self.db.collection(self.collection_name).document(config_id).get()
                
                if doc.exists:
                    return doc.to_dict()
            else:
                # Usando SQLite
                cursor = self.db.execute_query(
                    f"SELECT * FROM {self.collection_name} WHERE id = ?",
                    (config_id,)
                )
                
                if cursor:
                    row = cursor.fetchone()
                    if row:
                        # Converter a linha em um dicionário
                        cursor.execute(f"PRAGMA table_info({self.collection_name})")
                        columns = [info[1] for info in cursor.fetchall()]
                        
                        config = {}
                        for i, col in enumerate(columns):
                            if col == "config_data":
                                # Se tiver um campo JSON, fazer parse
                                import json
                                try:
                                    config = json.loads(row[i])
                                except:
                                    pass
                            else:
                                config[col] = row[i]
                        
                        return config
            
            # Configuração padrão se não encontrar
            return {
                "icon": "DELETE_OUTLINE",
                "color": "PURPLE_500",
                "bgcolor": "#FFFFFF",
                "show_quantity": True,
                "show_details": True,
                "custom_title": "",
                "priority": "normal"
            }
        except Exception as e:
            print(f"Erro ao obter configuração do grupo de resíduos: {e}")
            return {
                "icon": "DELETE_OUTLINE",
                "color": "PURPLE_500",
                "bgcolor": "#FFFFFF",
                "show_quantity": True,
                "show_details": True,
                "custom_title": "",
                "priority": "normal"
            }
    
    def save_product_group_config(self, group_id, config):
        """Salva a configuração de um grupo de produtos pelo ID"""
        try:
            config_id = f"product_{group_id}"
            
            if hasattr(self.db, 'collection'):
                # Usando Firebase
                self.db.collection(self.collection_name).document(config_id).set(config)
            else:
                # Usando SQLite
                # Verificar se a tabela existe
                self._ensure_config_table_exists()
                
                # Converter config para JSON
                import json
                config_json = json.dumps(config)
                
                # Verificar se o registro já existe
                cursor = self.db.execute_query(
                    f"SELECT id FROM {self.collection_name} WHERE id = ?",
                    (config_id,)
                )
                
                if cursor and cursor.fetchone():
                    # Atualizar registro existente
                    self.db.execute_query(
                        f"UPDATE {self.collection_name} SET config_data = ? WHERE id = ?",
                        (config_json, config_id)
                    )
                else:
                    # Inserir novo registro
                    self.db.execute_query(
                        f"INSERT INTO {self.collection_name} (id, config_data) VALUES (?, ?)",
                        (config_id, config_json)
                    )
            
            return True
        except Exception as e:
            print(f"Erro ao salvar configuração do grupo de produtos: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def save_residue_group_config(self, group_id, config):
        """Salva a configuração de um grupo de resíduos pelo ID"""
        try:
            config_id = f"residue_{group_id}"
            
            if hasattr(self.db, 'collection'):
                # Usando Firebase
                self.db.collection(self.collection_name).document(config_id).set(config)
            else:
                # Usando SQLite
                # Verificar se a tabela existe
                self._ensure_config_table_exists()
                
                # Converter config para JSON
                import json
                config_json = json.dumps(config)
                
                # Verificar se o registro já existe
                cursor = self.db.execute_query(
                    f"SELECT id FROM {self.collection_name} WHERE id = ?",
                    (config_id,)
                )
                
                if cursor and cursor.fetchone():
                    # Atualizar registro existente
                    self.db.execute_query(
                        f"UPDATE {self.collection_name} SET config_data = ? WHERE id = ?",
                        (config_json, config_id)
                    )
                else:
                    # Inserir novo registro
                    self.db.execute_query(
                        f"INSERT INTO {self.collection_name} (id, config_data) VALUES (?, ?)",
                        (config_id, config_json)
                    )
            
            return True
        except Exception as e:
            print(f"Erro ao salvar configuração do grupo de resíduos: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_dashboard_product_group_ids(self):
        """Obtém a lista de IDs de grupos de produtos configurados para o dashboard"""
        try:
            config_id = "dashboard_product_groups"
            
            if hasattr(self.db, 'collection'):
                # Usando Firebase
                doc = self.db.collection(self.collection_name).document(config_id).get()
                
                if doc.exists:
                    return doc.to_dict().get("group_ids", [])
            else:
                # Usando SQLite
                # Garantir que a tabela existe
                self._ensure_config_table_exists()
                
                cursor = self.db.execute_query(
                    f"SELECT config_data FROM {self.collection_name} WHERE id = ?",
                    (config_id,)
                )
                
                if cursor:
                    row = cursor.fetchone()
                    if row and row[0]:
                        # Converter JSON para dicionário
                        import json
                        try:
                            config = json.loads(row[0])
                            return config.get("group_ids", [])
                        except:
                            pass
            
            return []
        except Exception as e:
            print(f"Erro ao obter grupos de produtos do dashboard: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_dashboard_residue_group_ids(self):
        """Obtém a lista de IDs de grupos de resíduos configurados para o dashboard"""
        try:
            config_id = "dashboard_residue_groups"
            
            if hasattr(self.db, 'collection'):
                # Usando Firebase
                doc = self.db.collection(self.collection_name).document(config_id).get()
                
                if doc.exists:
                    return doc.to_dict().get("group_ids", [])
            else:
                # Usando SQLite
                # Garantir que a tabela existe
                self._ensure_config_table_exists()
                
                cursor = self.db.execute_query(
                    f"SELECT config_data FROM {self.collection_name} WHERE id = ?",
                    (config_id,)
                )
                
                if cursor:
                    row = cursor.fetchone()
                    if row and row[0]:
                        # Converter JSON para dicionário
                        import json
                        try:
                            config = json.loads(row[0])
                            return config.get("group_ids", [])
                        except:
                            pass
            
            return []
        except Exception as e:
            print(f"Erro ao obter grupos de resíduos do dashboard: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_dashboard_residue_group_ids(self):
        """Obtém a lista de IDs de grupos de resíduos configurados para o dashboard"""
        try:
            config_id = "dashboard_residue_groups"
            
            if hasattr(self.db, 'collection'):
                # Usando Firebase
                doc = self.db.collection(self.collection_name).document(config_id).get()
                
                if doc.exists:
                    return doc.to_dict().get("group_ids", [])
            else:
                # Usando SQLite
                cursor = self.db.execute_query(
                    f"SELECT config_data FROM {self.collection_name} WHERE id = ?",
                    (config_id,)
                )
                
                if cursor:
                    row = cursor.fetchone()
                    if row and row[0]:
                        # Converter JSON para dicionário
                        import json
                        try:
                            config = json.loads(row[0])
                            return config.get("group_ids", [])
                        except:
                            pass
            
            return []
        except Exception as e:
            print(f"Erro ao obter grupos de resíduos do dashboard: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def save_dashboard_product_group_ids(self, group_ids):
        """Salva a lista de IDs de grupos de produtos configurados para o dashboard"""
        try:
            config_id = "dashboard_product_groups"
            config = {"group_ids": group_ids}
            
            if hasattr(self.db, 'collection'):
                # Usando Firebase
                self.db.collection(self.collection_name).document(config_id).set(config)
            else:
                # Usando SQLite
                # Verificar se a tabela existe
                self._ensure_config_table_exists()
                
                # Converter config para JSON
                import json
                config_json = json.dumps(config)
                
                # Verificar se o registro já existe
                cursor = self.db.execute_query(
                    f"SELECT id FROM {self.collection_name} WHERE id = ?",
                    (config_id,)
                )
                
                if cursor and cursor.fetchone():
                    # Atualizar registro existente
                    self.db.execute_query(
                        f"UPDATE {self.collection_name} SET config_data = ? WHERE id = ?",
                        (config_json, config_id)
                    )
                else:
                    # Inserir novo registro
                    self.db.execute_query(
                        f"INSERT INTO {self.collection_name} (id, config_data) VALUES (?, ?)",
                        (config_id, config_json)
                    )
            
            return True
        except Exception as e:
            print(f"Erro ao salvar grupos de produtos do dashboard: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def save_dashboard_residue_group_ids(self, group_ids):
        """Salva a lista de IDs de grupos de resíduos configurados para o dashboard"""
        try:
            config_id = "dashboard_residue_groups"
            config = {"group_ids": group_ids}
            
            if hasattr(self.db, 'collection'):
                # Usando Firebase
                self.db.collection(self.collection_name).document(config_id).set(config)
            else:
                # Usando SQLite
                # Verificar se a tabela existe
                self._ensure_config_table_exists()
                
                # Converter config para JSON
                import json
                config_json = json.dumps(config)
                
                # Verificar se o registro já existe
                cursor = self.db.execute_query(
                    f"SELECT id FROM {self.collection_name} WHERE id = ?",
                    (config_id,)
                )
                
                if cursor and cursor.fetchone():
                    # Atualizar registro existente
                    self.db.execute_query(
                        f"UPDATE {self.collection_name} SET config_data = ? WHERE id = ?",
                        (config_json, config_id)
                    )
                else:
                    # Inserir novo registro
                    self.db.execute_query(
                        f"INSERT INTO {self.collection_name} (id, config_data) VALUES (?, ?)",
                        (config_id, config_json)
                    )
            
            return True
        except Exception as e:
            print(f"Erro ao salvar grupos de resíduos do dashboard: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def add_product_group_to_dashboard(self, group):
        """Adiciona um grupo de produtos ao dashboard"""
        try:
            group_id = group.get("id", "")
            if not group_id:
                return False
                
            # Obter IDs de grupos atuais
            current_group_ids = self.get_dashboard_product_group_ids()
            
            # Verificar se o grupo já existe
            if group_id in current_group_ids:
                return False
            
            # Adicionar novo ID de grupo
            current_group_ids.append(group_id)
            
            # Salvar IDs de grupos atualizados
            return self.save_dashboard_product_group_ids(current_group_ids)
        except Exception as e:
            print(f"Erro ao adicionar grupo de produtos ao dashboard: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def add_residue_group_to_dashboard(self, group):
        """Adiciona um grupo de resíduos ao dashboard"""
        try:
            group_id = group.get("id", "")
            if not group_id:
                return False
                
            # Obter IDs de grupos atuais
            current_group_ids = self.get_dashboard_residue_group_ids()
            
            # Verificar se o grupo já existe
            if group_id in current_group_ids:
                return False
            
            # Adicionar novo ID de grupo
            current_group_ids.append(group_id)
            
            # Salvar IDs de grupos atualizados
            return self.save_dashboard_residue_group_ids(current_group_ids)
        except Exception as e:
            print(f"Erro ao adicionar grupo de resíduos ao dashboard: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def remove_product_group_from_dashboard(self, group_id):
        """Remove um grupo de produtos do dashboard"""
        try:
            # Obter IDs de grupos atuais
            current_group_ids = self.get_dashboard_product_group_ids()
            
            # Filtrar ID de grupo a ser removido
            if group_id in current_group_ids:
                current_group_ids.remove(group_id)
                
                # Salvar IDs de grupos atualizados
                return self.save_dashboard_product_group_ids(current_group_ids)
            return False
        except Exception as e:
            print(f"Erro ao remover grupo de produtos do dashboard: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def remove_residue_group_from_dashboard(self, group_id):
        """Remove um grupo de resíduos do dashboard"""
        try:
            # Obter IDs de grupos atuais
            current_group_ids = self.get_dashboard_residue_group_ids()
            
            # Filtrar ID de grupo a ser removido
            if group_id in current_group_ids:
                current_group_ids.remove(group_id)
                
                # Salvar IDs de grupos atualizados
                return self.save_dashboard_residue_group_ids(current_group_ids)
            return False
        except Exception as e:
            print(f"Erro ao remover grupo de resíduos do dashboard: {e}")
            import traceback
            traceback.print_exc()
            return False
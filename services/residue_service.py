from datetime import datetime
import json
import time
import traceback

class ResidueService:
    """Serviço para gerenciamento de resíduos"""
    
    def __init__(self, firebase, db):
        self.firebase = firebase
        self.db = db
    
    def add_residue(self, residue_data):
        """Adiciona um novo resíduo com tratamento de erros, sincronização e agrupamento automático"""
        try:
            # Validar dados do resíduo
            self._validate_residue_data(residue_data)
            
            # Identificar grupo do resíduo com base no nome
            group = self.identify_residue_group(residue_data["name"])
            
            # Adicionar grupo_id e type aos dados do resíduo
            residue_data["group_id"] = group["id"]
            residue_data["group_name"] = group["name"]
            residue_data["type"] = group["name"]  # Usar o nome do grupo como tipo
            
            # Verificar se já existe resíduo com mesmo nome e tipo no grupo
            cursor = self.db.conn.cursor()
            cursor.execute('''
            SELECT * FROM residues 
            WHERE group_id = ? AND name = ?
            ''', (group["id"], residue_data["name"]))
            
            existing_residue = cursor.fetchone()
            
            if existing_residue:
                # Converter para dicionário
                existing_residue_dict = self._convert_to_dict([existing_residue])[0]
                
                # Atualizar quantidade
                updated_residue = existing_residue_dict.copy()
                updated_residue["quantity"] = existing_residue_dict["quantity"] + int(residue_data["quantity"])
                
                # Se tiver destino, atualizar
                if "destination" in residue_data and residue_data["destination"]:
                    updated_residue["destination"] = residue_data["destination"]
                
                # Se tiver notas, atualizar
                if "notes" in residue_data and residue_data["notes"]:
                    updated_residue["notes"] = residue_data["notes"]
                
                # Atualizar resíduo existente
                return self.update_residue(existing_residue_dict["id"], updated_residue)
            
            # Gerar ID único
            import uuid
            residue_id = str(uuid.uuid4())
            
            # Garantir que a data de entrada seja a data atual se não for fornecida
            if "entryDate" not in residue_data or not residue_data["entryDate"]:
                from datetime import datetime
                residue_data["entryDate"] = datetime.now().strftime("%d/%m/%Y")
            
            # Converter quantidade para inteiro
            try:
                residue_data["quantity"] = int(residue_data["quantity"])
            except (ValueError, TypeError):
                residue_data["quantity"] = 0
            
            # Inserir no banco de dados local
            try:
                cursor.execute('''
                INSERT INTO residues (
                    id, name, type, quantity, entryDate, destination, 
                    exitDate, notes, group_id, group_name
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    residue_id,
                    residue_data["name"],
                    residue_data["type"],
                    residue_data["quantity"],
                    residue_data["entryDate"],
                    residue_data.get("destination", ""),
                    residue_data.get("exitDate", ""),
                    residue_data.get("notes", ""),
                    residue_data["group_id"],
                    residue_data["group_name"]
                ))
                self.db.conn.commit()
            except Exception as e:
                print(f"Erro ao inserir resíduo no banco de dados: {e}")
                traceback.print_exc()
                return False
            
            # Sincronizar com Firebase
            try:
                if self.firebase.online_mode:
                    self.firebase.db.collection("residues").document(residue_id).set(residue_data)
                else:
                    # Adicionar à fila de sincronização
                    self.db.add_sync_operation('add', 'residues', residue_id, residue_data)
            except Exception as e:
                print(f"Erro ao sincronizar resíduo com Firebase: {e}")
                # Adicionar à fila de sincronização
                self.db.add_sync_operation('add', 'residues', residue_id, residue_data)
            
            return True
        except Exception as e:
            print(f"Erro ao adicionar resíduo: {e}")
            import traceback
            traceback.print_exc()
            return False

    def update_residue(self, residue_id, residue_data):
        """Atualiza um resíduo existente com tratamento de erros e sincronização"""
        try:
            # Validar dados do resíduo
            self._validate_residue_data(residue_data)
            
            # Identificar grupo do resíduo
            from services.group_service import GroupService
            group_service = GroupService(self.firebase, self.db)
            group = group_service.get_or_create_residue_group(residue_data["type"])
            
            # Adicionar grupo_id e group_name aos dados do resíduo
            residue_data["group_id"] = group["id"]
            residue_data["group_name"] = group["name"]
            
            # Converter quantidade para inteiro
            try:
                residue_data["quantity"] = int(residue_data["quantity"])
            except (ValueError, TypeError):
                residue_data["quantity"] = 0
            
            # Atualizar no banco de dados local
            cursor = self.db.conn.cursor()
            cursor.execute('''
            UPDATE residues SET
                name = ?, type = ?, quantity = ?, entryDate = ?, destination = ?,
                exitDate = ?, notes = ?, group_id = ?, group_name = ?
            WHERE id = ?
            ''', (
                residue_data["name"],
                residue_data["type"],
                residue_data["quantity"],
                residue_data["entryDate"],
                residue_data.get("destination", ""),
                residue_data.get("exitDate", ""),
                residue_data.get("notes", ""),
                residue_data["group_id"],
                residue_data["group_name"],
                residue_id
            ))
            self.db.conn.commit()
            
            # Sincronizar com Firebase se estiver online
            if self.firebase.online_mode:
                try:
                    self.firebase.db.collection("residues").document(residue_id).update(residue_data)
                except Exception as e:
                    print(f"Erro ao sincronizar atualização de resíduo com Firebase: {e}")
                    # Adicionar à fila de sincronização
                    self.db.add_sync_operation('update', 'residues', residue_id, residue_data)
            else:
                # Adicionar à fila de sincronização
                self.db.add_sync_operation('update', 'residues', residue_id, residue_data)
            
            return True
        except Exception as e:
            print(f"Erro ao atualizar resíduo: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _validate_residue_data(self, residue_data):
        """Valida os dados do resíduo"""
        if not residue_data.get("name"):
            raise ValueError("Nome do resíduo é obrigatório")
        
        # Verificar se a quantidade é um número válido
        try:
            quantity = int(residue_data.get("quantity", 0))
            if quantity < 0:
                raise ValueError("Quantidade não pode ser negativa")
        except (ValueError, TypeError):
            raise ValueError("Quantidade deve ser um número inteiro")
        
        return True

    def _convert_to_dict(self, rows):
        """Converte linhas do banco de dados em dicionários"""
        cursor = self.db.conn.cursor()
        cursor.execute("PRAGMA table_info(residues)")
        columns = [info[1] for info in cursor.fetchall()]
        
        result = []
        for row in rows:
            item = {}
            for i, col in enumerate(columns):
                if i < len(row):
                    item[col] = row[i]
            result.append(item)
        
        return result

    def get_all_residues(self):
        """Obtém todos os resíduos do banco de dados"""
        try:
            # Obter do banco de dados local
            cursor = self.db.conn.cursor()
            cursor.execute("SELECT * FROM residues")
            rows = cursor.fetchall()
            
            # Converter para dicionários
            residues = self._convert_to_dict(rows)
            
            return residues
        except Exception as e:
            print(f"Erro ao obter todos os resíduos: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_residue_by_id(self, residue_id):
        """Busca um resíduo pelo ID"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute('SELECT * FROM residues WHERE id = ?', (residue_id,))
            result = cursor.fetchone()
            
            if not result:
                return None
                
            return self._convert_to_dict([result])[0]
        except Exception as e:
            print(f"Erro ao buscar resíduo por ID: {e}")
            traceback.print_exc()
            return None
    
    def register_residue_exit(self, residue_id, exit_quantity, destination, notes=""):
        """Registra a saída de um resíduo"""
        try:
            # Validar quantidade
            try:
                exit_qty = int(exit_quantity)
                if exit_qty <= 0:
                    return False, "A quantidade deve ser maior que zero"
            except (ValueError, TypeError):
                return False, "Quantidade inválida. Digite um número inteiro."
            
            # Buscar resíduo
            residue = self.get_residue_by_id(residue_id)
            
            if not residue:
                return False, f"Resíduo com ID {residue_id} não encontrado"
            
            # Verificar se há quantidade suficiente
            if exit_qty > residue.get("quantity", 0):
                return False, "Quantidade de saída maior que a disponível"
            
            # Atualizar quantidade
            residue["quantity"] = residue.get("quantity", 0) - exit_qty
            residue["exitDate"] = datetime.now().strftime("%d/%m/%Y")
            residue["destination"] = destination
            
            if notes:
                residue["notes"] = notes
            
            # Atualizar resíduo
            success = self.update_residue(residue_id, residue)
            
            if success:
                # Registrar no histórico
                self._register_exit_history(residue, exit_qty, destination, notes)
                return True, f"Saída de {exit_qty} unidades registrada com sucesso"
            else:
                return False, "Erro ao atualizar resíduo"
        except Exception as e:
            error_msg = f"Erro ao registrar saída de resíduo: {str(e)}"
            print(error_msg)
            traceback.print_exc()
            return False, error_msg
    
    def _register_exit_history(self, residue, quantity, destination, notes=""):
        """Registra a saída no histórico"""
        try:
            # Criar registro de histórico
            exit_record = {
                "id": f"exit_{residue['id']}_{int(time.time())}",
                "residueId": residue.get("id"),
                "residueName": residue.get("name"),
                "quantity": quantity,
                "destination": destination,
                "notes": notes,
                "date": datetime.now().strftime("%d/%m/%Y"),
                "timestamp": time.time(),
                "type": residue.get("type")
            }
            
            # Salvar no histórico local
            cursor = self.db.conn.cursor()
            cursor.execute('''
            INSERT INTO residue_history (
                id, residueId, residueName, quantity, destination, 
                notes, date, timestamp, type
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                exit_record["id"], exit_record["residueId"], 
                exit_record["residueName"], exit_record["quantity"],
                exit_record["destination"], exit_record["notes"],
                exit_record["date"], exit_record["timestamp"],
                exit_record["type"]
            ))
            self.db.conn.commit()
            
            # Sincronizar com Firebase
            self._sync_with_firebase('residue_history', exit_record["id"], exit_record, 'add')
            
            # Criar notificação
            from services.notification_service import NotificationService
            notification_service = NotificationService(self.firebase, self.db)
            notification_service.create_notification(
                "RESIDUE_EXIT",
                f"Saída de {quantity} unidades de '{residue['name']}' registrada",
                residue["id"]
            )
            
            return True
        except Exception as e:
            print(f"Erro ao registrar histórico de saída: {e}")
            traceback.print_exc()
            return False
    
    def get_residue_history(self, residue_id=None, days=30):
        """Obtém o histórico de saídas de resíduos"""
        try:
            cursor = self.db.conn.cursor()
            
            if residue_id:
                # Histórico de um resíduo específico
                cursor.execute('''
                SELECT * FROM residue_history 
                WHERE residueId = ? 
                ORDER BY timestamp DESC
                ''', (residue_id,))
            else:
                # Histórico de todos os resíduos nos últimos X dias
                cutoff_time = time.time() - (days * 24 * 60 * 60)
                cursor.execute('''
                SELECT * FROM residue_history 
                WHERE timestamp >= ? 
                ORDER BY timestamp DESC
                ''', (cutoff_time,))
            
            results = cursor.fetchall()
            return self._convert_history_to_dict(results)
        except Exception as e:
            print(f"Erro ao buscar histórico de resíduos: {e}")
            traceback.print_exc()
            return []
    
    def _convert_history_to_dict(self, rows):
        """Converte resultados do histórico em dicionários"""
        history = []
        if not rows:
            return history
            
        for row in rows:
            try:
                record = {
                    "id": row[0],
                    "residueId": row[1],
                    "residueName": row[2],
                    "quantity": row[3],
                    "destination": row[4],
                    "notes": row[5],
                    "date": row[6],
                    "timestamp": row[7],
                    "type": row[8] if len(row) > 8 else ""
                }
                history.append(record)
            except Exception as e:
                print(f"Erro ao converter registro de histórico: {e}")
                traceback.print_exc()
                continue
        return history
    
    def get_residue_stats(self):
        """Obtém estatísticas sobre os resíduos"""
        try:
            stats = {
                "total_residues": 0,
                "total_quantity": 0,
                "by_type": {},
                "recent_exits": []
            }
            
            # Obter todos os resíduos
            residues = self.get_all_residues()
            
            # Calcular estatísticas
            stats["total_residues"] = len(residues)
            
            for residue in residues:
                # Somar quantidade total
                stats["total_quantity"] += residue.get("quantity", 0)
                
                # Agrupar por tipo
                residue_type = residue.get("type", "Não especificado")
                if residue_type not in stats["by_type"]:
                    stats["by_type"][residue_type] = {
                        "count": 0,
                        "quantity": 0
                    }
                
                stats["by_type"][residue_type]["count"] += 1
                stats["by_type"][residue_type]["quantity"] += residue.get("quantity", 0)
            
            # Obter saídas recentes (últimos 7 dias)
            stats["recent_exits"] = self.get_residue_history(days=7)
            
            return stats
        except Exception as e:
            print(f"Erro ao calcular estatísticas de resíduos: {e}")
            traceback.print_exc()
            return {
                "total_residues": 0,
                "total_quantity": 0,
                "by_type": {},
                "recent_exits": []
            }
    def identify_residue_group(self, residue_name):
        """Identifica o grupo de um resíduo com base no nome"""
        from services.group_service import GroupService
        group_service = GroupService(self.firebase, self.db)
        
        # Normalizar nome do resíduo (remover acentos, converter para minúsculas)
        import unicodedata
        import re
        
        def normalize_text(text):
            # Remover acentos e converter para minúsculas
            text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII').lower()
            # Remover caracteres especiais
            text = re.sub(r'[^a-z0-9\s]', '', text)
            return text
        
        normalized_name = normalize_text(residue_name)
        
        # Obter todos os grupos existentes
        all_groups = group_service.get_all_residue_groups()
        
        # Verificar se o nome do resíduo contém o nome de algum grupo
        for group in all_groups:
            group_name = normalize_text(group["name"])
            
            # Verificar se o nome do grupo está contido no nome do resíduo
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
            return group_service.get_or_create_residue_group(first_word)
        
        # Fallback: grupo "Outros"
        return group_service.get_or_create_residue_group("Outros")

    def delete_residue(self, residue_id):
        """Exclui um resíduo com tratamento de erros e sincronização"""
        try:
            print(f"Iniciando exclusão do resíduo com ID: {residue_id}")
            
            # Buscar resíduo antes de excluir para ter os dados para sincronização
            cursor = self.db.conn.cursor()
            cursor.execute('SELECT * FROM residues WHERE id = ?', (residue_id,))
            residue_data = cursor.fetchone()
            
            if not residue_data:
                print(f"Resíduo com ID {residue_id} não encontrado")
                return False
            
            # Excluir diretamente do banco de dados
            cursor.execute('DELETE FROM residues WHERE id = ?', (residue_id,))
            rows_affected = cursor.rowcount
            self.db.conn.commit()
            print(f"Resíduo com ID {residue_id} excluído localmente. Linhas afetadas: {rows_affected}")
            
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
            
            print(f"Exclusão do resíduo com ID {residue_id} concluída com sucesso")
            return True
        except Exception as e:
            print(f"Erro ao excluir resíduo: {e}")
            import traceback
            traceback.print_exc()
            try:
                self.db.conn.rollback()
            except:
                pass
            return False
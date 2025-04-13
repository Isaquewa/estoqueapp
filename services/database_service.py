import sqlite3
import json
from datetime import datetime
import os
import threading
import time
import traceback

class DatabaseService:
    """Serviço para gerenciamento do banco de dados local"""
    
    def __init__(self):
        # Garantir que o diretório data existe
        os.makedirs("data", exist_ok=True)
        
        # Usar um local thread para armazenar conexões específicas de thread
        self.thread_local = threading.local()
        
        # Inicializar a conexão para a thread atual
        try:
            conn = self._get_connection()
            print(f"Conexão com banco de dados local inicializada: {conn is not None}")
            
            # Criar tabelas
            self.create_tables()
            print("Tabelas do banco de dados local criadas/verificadas com sucesso")
            
            # Criar tabela de sincronização
            self._create_sync_table()
            print("Tabela de sincronização criada/verificada com sucesso")
            
            # Migrar dados antigos
            self.migrate_legacy_data()
        except Exception as e:
            print(f"Erro ao inicializar banco de dados local: {e}")
            # Tentar recuperar o banco de dados
            self._recover_database()
    
    def _get_connection(self):
        """Obtém uma conexão para a thread atual"""
        if not hasattr(self.thread_local, "conn") or self.thread_local.conn is None:
            try:
                self.thread_local.conn = sqlite3.connect('data/local_storage.db')
                # Habilitar suporte a chaves estrangeiras
                self.thread_local.conn.execute("PRAGMA foreign_keys = ON")
                # Configurar timeout para evitar bloqueios
                self.thread_local.conn.execute("PRAGMA busy_timeout = 5000")
                # Configurar modo de sincronização para melhorar desempenho
                self.thread_local.conn.execute("PRAGMA synchronous = NORMAL")
                # Configurar modo de journal para melhorar desempenho
                self.thread_local.conn.execute("PRAGMA journal_mode = WAL")
            except sqlite3.Error as e:
                print(f"Erro SQLite ao conectar: {e}")
                return None
            except Exception as e:
                print(f"Erro geral ao conectar: {e}")
                traceback.print_exc()
                return None
        return self.thread_local.conn
    
    @property
    def conn(self):
        """Propriedade para acessar a conexão da thread atual"""
        connection = self._get_connection()
        if connection is None:
            # Tentar reconectar
            time.sleep(0.5)  # Pequeno delay antes de tentar novamente
            connection = self._get_connection()
            if connection is None:
                # Se ainda falhar, tentar recuperar o banco de dados
                self._recover_database()
                connection = self._get_connection()
        return connection
    
    def create_tables(self):
        """Cria as tabelas necessárias se não existirem"""
        try:
            cursor = self.conn.cursor()
            
            # Tabela de grupos de produtos
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS product_groups (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                icon TEXT,
                color TEXT,
                created_at TEXT,
                last_updated TEXT
            )
            ''')
            
            # Tabela de grupos de resíduos
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS residue_groups (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                icon TEXT,
                color TEXT,
                created_at TEXT,
                last_updated TEXT
            )
            ''')
            
             # Tabela de produtos
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                lot TEXT NOT NULL,
                expiry TEXT NOT NULL,
                entryDate TEXT NOT NULL,
                fabDate TEXT,
                exitDate TEXT,
                weeklyUsage TEXT,
                lastUpdateDate TEXT NOT NULL,
                category TEXT,
                location TEXT,
                group_id TEXT,
                manufacturer TEXT
            )
            ''')
            
            # Verificar se a tabela de produtos existe e tem todas as colunas necessárias
            cursor.execute("PRAGMA table_info(products)")
            columns = [info[1] for info in cursor.fetchall()]
            
            # Adicionar colunas faltantes se necessário
            if "manufacturer" not in columns:
                try:
                    cursor.execute("ALTER TABLE products ADD COLUMN manufacturer TEXT")
                    print("Coluna 'manufacturer' adicionada à tabela products")
                except:
                    print("Não foi possível adicionar a coluna 'manufacturer'")
            
            if "group_id" not in columns:
                try:
                    cursor.execute("ALTER TABLE products ADD COLUMN group_id TEXT")
                    print("Coluna 'group_id' adicionada à tabela products")
                except:
                    print("Não foi possível adicionar a coluna 'group_id'")
            else:
                print("ERRO: Tabela 'products' não foi criada!")
            
             # Tabela de resíduos
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS residues (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                entryDate TEXT NOT NULL,
                exitDate TEXT,
                destination TEXT,
                notes TEXT,
                group_id TEXT,
                group_name TEXT,
                FOREIGN KEY (group_id) REFERENCES residue_groups (id) ON DELETE SET NULL
            )
            ''')
            
             # Verificar se a tabela de resíduos existe
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='residues'")
            if cursor.fetchone():
                print("Tabela 'residues' existe")
                # Verificar se tem dados
                cursor.execute("SELECT COUNT(*) FROM residues")
                count = cursor.fetchone()[0]
                print(f"Tabela 'residues' contém {count} registros")
                
                # Verificar se a tabela tem as colunas necessárias
                cursor.execute("PRAGMA table_info(residues)")
                columns = [info[1] for info in cursor.fetchall()]
                print(f"Colunas na tabela 'residues': {columns}")
                
                # Adicionar colunas faltantes se necessário
                if "destination" not in columns:
                    try:
                        cursor.execute("ALTER TABLE residues ADD COLUMN destination TEXT")
                        print("Coluna 'destination' adicionada à tabela residues")
                    except:
                        print("Não foi possível adicionar a coluna 'destination'")
                        
                if "notes" not in columns:
                    try:
                        cursor.execute("ALTER TABLE residues ADD COLUMN notes TEXT")
                        print("Coluna 'notes' adicionada à tabela residues")
                    except:
                        print("Não foi possível adicionar a coluna 'notes'")
                        
                if "group_id" not in columns:
                    try:
                        cursor.execute("ALTER TABLE residues ADD COLUMN group_id TEXT REFERENCES residue_groups(id) ON DELETE SET NULL")
                        print("Coluna 'group_id' adicionada à tabela residues")
                    except:
                        print("Não foi possível adicionar a coluna 'group_id'")
                        
                if "group_name" not in columns:
                    try:
                        cursor.execute("ALTER TABLE residues ADD COLUMN group_name TEXT")
                        print("Coluna 'group_name' adicionada à tabela residues")
                    except:
                        print("Não foi possível adicionar a coluna 'group_name'")
            else:
                print("ERRO: Tabela 'residues' não foi criada!")
            
            # Tabela de notificações
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                message TEXT NOT NULL,
                date TEXT NOT NULL,
                read INTEGER NOT NULL DEFAULT 0,
                productId TEXT
            )
            ''')
            
            # Tabela de configurações
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                id TEXT PRIMARY KEY,
                settings_data TEXT NOT NULL
            )
            ''')
            
            # Tabela de uso semanal
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS weekly_usage (
                id TEXT PRIMARY KEY,
                productId TEXT NOT NULL,
                week_start TEXT NOT NULL,
                usage_data TEXT NOT NULL,
                FOREIGN KEY (productId) REFERENCES products (id)
            )
            ''')
            
            # Tabela de histórico de resíduos
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS residue_history (
                id TEXT PRIMARY KEY,
                residueId TEXT,
                residueName TEXT,
                quantity INTEGER,
                destination TEXT,
                notes TEXT,
                date TEXT,
                timestamp REAL,
                type TEXT
            )
            ''')
            
            # Tabela de histórico de produtos
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS product_history (
                id TEXT PRIMARY KEY,
                productId TEXT,
                productName TEXT,
                quantity INTEGER,
                reason TEXT,
                date TEXT,
                timestamp REAL,
                type TEXT
            )
            ''')
            
            # Tabela de configuração do dashboard
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS dashboard_config (
                id TEXT PRIMARY KEY,
                config_data TEXT NOT NULL
            )
            ''')

            self.conn.commit()
            print("Todas as tabelas criadas/verificadas com sucesso")
            return True
        except Exception as e:
            print(f"ERRO ao criar tabelas: {e}")
            import traceback
            traceback.print_exc()
            return False
        
    def migrate_legacy_data(self):
        """Migra dados antigos para o novo formato"""
        try:
            print("Iniciando migração de dados antigos...")
            cursor = self.conn.cursor()
            
            # Migrar produtos antigos
            cursor.execute("SELECT * FROM products")
            old_products = cursor.fetchall()
            
            for product in old_products:
                try:
                    # Verificar se o produto tem o formato esperado
                    if len(product) < 10:
                        continue
                    
                    product_id = product[0]
                    product_name = product[1]
                    
                    # Verificar se o produto tem todos os campos necessários
                    cursor.execute("""
                    UPDATE products SET 
                        weeklyUsage = ?, 
                        lastUpdateDate = ?
                    WHERE id = ? AND (weeklyUsage IS NULL OR lastUpdateDate IS NULL)
                    """, (
                        json.dumps([0] * 7),
                        datetime.now().strftime("%d/%m/%Y"),
                        product_id
                    ))
                    
                    # Tentar extrair e associar grupo
                    from services.group_service import GroupService
                    group_service = GroupService(None, self)
                    group_name = group_service.extract_group_name(product_name)
                    
                    if group_name:
                        group = group_service.get_or_create_product_group(group_name)
                        
                        # Associar produto ao grupo
                        cursor.execute("""
                        UPDATE products SET 
                            group_id = ?
                        WHERE id = ? AND (group_id IS NULL)
                        """, (
                            group["id"],
                            product_id
                        ))
                    
                    print(f"Produto {product_id} migrado")
                except Exception as e:
                    print(f"Erro ao migrar produto: {e}")
            
            # Migrar resíduos antigos
            cursor.execute("SELECT * FROM residues")
            old_residues = cursor.fetchall()
            
            for residue in old_residues:
                try:
                    # Verificar se o resíduo tem o formato esperado
                    if len(residue) < 6:
                        continue
                    
                    residue_id = residue[0]
                    residue_name = residue[1]
                    residue_type = residue[2]
                    
                    # Verificar se o resíduo tem todos os campos necessários
                    cursor.execute("""
                    UPDATE residues SET 
                        destination = ?, 
                        notes = ?
                    WHERE id = ? AND (destination IS NULL OR notes IS NULL)
                    """, (
                        "",
                        "",
                        residue_id
                    ))
                    
                    # Tentar extrair e associar grupo
                    from services.group_service import GroupService
                    group_service = GroupService(None, self)
                    
                    # Usar o tipo como grupo, ou extrair do nome
                    group_name = residue_type if residue_type else group_service.extract_residue_group_name(residue_name)
                    
                    if group_name:
                        group = group_service.get_or_create_residue_group(group_name)
                        
                        # Associar resíduo ao grupo
                        cursor.execute("""
                        UPDATE residues SET 
                            group_id = ?
                        WHERE id = ? AND (group_id IS NULL)
                        """, (
                            group["id"],
                            residue_id
                        ))
                    
                    print(f"Resíduo {residue_id} migrado")
                except Exception as e:
                    print(f"Erro ao migrar resíduo: {e}")
            
            self.conn.commit()
            print("Migração de dados concluída")
            return True
        except Exception as e:
            print(f"Erro durante migração de dados: {e}")
            import traceback
            traceback.print_exc()
            return False   
        
    def _create_sync_table(self):
        """Cria a tabela de controle de sincronização"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS sync_operations (
                id TEXT PRIMARY KEY,
                operation_type TEXT NOT NULL,
                collection TEXT NOT NULL,
                document_id TEXT NOT NULL,
                data TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                synced INTEGER NOT NULL DEFAULT 0
            )
            ''')
            self.conn.commit()
            print("Tabela de sincronização criada/verificada com sucesso")
            return True
        except Exception as e:
            print(f"Erro ao criar tabela de sincronização: {e}")
            return False
    
    def add_sync_operation(self, operation_type, collection, document_id, data):
        """Adiciona uma operação à fila de sincronização"""
        try:
            operation_id = f"{collection}_{document_id}_{int(time.time())}"
            cursor = self.conn.cursor()
            cursor.execute('''
            INSERT INTO sync_operations (id, operation_type, collection, document_id, data, timestamp, synced)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                operation_id,
                operation_type,
                collection,
                document_id,
                json.dumps(data),
                datetime.now().isoformat(),
                0
            ))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Erro ao adicionar operação de sincronização: {e}")
            traceback.print_exc()
            return False
    
    def get_pending_sync_operations(self):
        """Retorna operações pendentes de sincronização"""
        try:
            cursor = self.conn.cursor()
            
            # Verificar se a tabela sync_operations existe
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sync_operations'")
            if not cursor.fetchone():
                print("Tabela sync_operations não existe, criando...")
                self._create_sync_table()
                return []  # Retorna lista vazia pois a tabela acabou de ser criada
            
            # Buscar operações pendentes
            cursor.execute('''
            SELECT * FROM sync_operations WHERE synced = 0 ORDER BY timestamp
            ''')
            operations = []
            for row in cursor.fetchall():
                operations.append({
                    'id': row[0],
                    'operation_type': row[1],
                    'collection': row[2],
                    'document_id': row[3],
                    'data': json.loads(row[4]),
                    'timestamp': row[5],
                    'synced': bool(row[6])
                })
            return operations
        except Exception as e:
            print(f"Erro ao buscar operações pendentes: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def mark_sync_operation_completed(self, operation_id):
        """Marca uma operação como sincronizada"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
            UPDATE sync_operations SET synced = 1 WHERE id = ?
            ''', (operation_id,))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Erro ao marcar operação como sincronizada: {e}")
            return False
    
    def execute_query(self, query, params=None):
        """Executa uma consulta SQL com tratamento de erros"""
        try:
            cursor = self.conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.conn.commit()
            return cursor
        except sqlite3.Error as e:
            print(f"Erro SQLite ao executar consulta: {e}")
            print(f"Query: {query}")
            print(f"Params: {params}")
            self.conn.rollback()
            return None
        except Exception as e:
            print(f"Erro geral ao executar consulta: {e}")
            traceback.print_exc()
            self.conn.rollback()
            return None
    
    def _recover_database(self):
        """Tenta recuperar o banco de dados em caso de corrupção"""
        try:
            print("Tentando recuperar banco de dados...")
            # Fechar conexão atual se existir
            if hasattr(self.thread_local, "conn") and self.thread_local.conn is not None:
                try:
                    self.thread_local.conn.close()
                except:
                    pass
                self.thread_local.conn = None
            
            # Criar backup do banco atual
            db_path = 'data/local_storage.db'
            if os.path.exists(db_path):
                backup_path = f'data/local_storage_backup_{int(time.time())}.db'
                try:
                    os.rename(db_path, backup_path)
                    print(f"Backup criado: {backup_path}")
                except:
                    print("Não foi possível criar backup, tentando remover arquivo corrompido")
                    try:
                        os.remove(db_path)
                        print("Arquivo de banco de dados removido")
                    except:
                        print("Não foi possível remover arquivo de banco de dados")
            
            # Tentar criar novo banco de dados
            self._get_connection()
            self.create_tables()
            self._create_sync_table()
            print("Banco de dados recuperado com sucesso")
            
            # Tentar restaurar dados do backup
            self._restore_from_backup(backup_path)
            
            return True
        except Exception as e:
            print(f"Falha ao recuperar banco de dados: {e}")
            traceback.print_exc()
            return False
    
    def _restore_from_backup(self, backup_path):
        """Tenta restaurar dados do backup"""
        if not os.path.exists(backup_path):
            print("Nenhum backup encontrado para restauração")
            return False
            
        try:
            print(f"Tentando restaurar dados do backup: {backup_path}")
            # Conectar ao backup
            backup_conn = sqlite3.connect(backup_path)
            backup_cursor = backup_conn.cursor()
            
            # Verificar tabelas no backup
            backup_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in backup_cursor.fetchall()]
            
            # Excluir tabelas de sistema
            tables = [t for t in tables if not t.startswith('sqlite_')]
            
            # Restaurar dados tabela por tabela
            for table in tables:
                try:
                    print(f"Restaurando tabela: {table}")
                    # Obter dados da tabela de backup
                    backup_cursor.execute(f"SELECT * FROM {table}")
                    rows = backup_cursor.fetchall()
                    
                    if not rows:
                        print(f"Tabela {table} vazia no backup")
                        continue
                    
                    # Obter nomes de colunas
                    backup_cursor.execute(f"PRAGMA table_info({table})")
                    columns = [col[1] for col in backup_cursor.fetchall()]
                    
                    # Criar placeholders para a inserção
                    placeholders = ', '.join(['?' for _ in columns])
                    columns_str = ', '.join(columns)
                    
                    # Inserir dados na nova tabela
                    cursor = self.conn.cursor()
                    for row in rows:
                        try:
                            cursor.execute(f"INSERT OR IGNORE INTO {table} ({columns_str}) VALUES ({placeholders})", row)
                        except Exception as e:
                            print(f"Erro ao restaurar linha: {e}")
                            continue
                    
                    self.conn.commit()
                    print(f"Tabela {table} restaurada com {len(rows)} registros")
                except Exception as e:
                    print(f"Erro ao restaurar tabela {table}: {e}")
                    continue
            
            backup_conn.close()
            print("Restauração de backup concluída")
            return True
        except Exception as e:
            print(f"Erro ao restaurar do backup: {e}")
            traceback.print_exc()
            return False
    
    def verify_database_integrity(self):
        """Verifica a integridade do banco de dados"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()
            if result and result[0] == 'ok':
                print("Verificação de integridade do banco de dados: OK")
                return True
            else:
                print(f"Verificação de integridade do banco de dados falhou: {result}")
                # Tentar recuperar automaticamente
                self._recover_database()
                return False
        except Exception as e:
            print(f"Erro ao verificar integridade do banco de dados: {e}")
            traceback.print_exc()
            return False
    
    def backup_database(self, backup_path=None):
        """Cria um backup do banco de dados"""
        if not backup_path:
            backup_path = f'data/backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
        
        try:
            # Garantir que o diretório existe
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            
            # Verificar se o banco de dados existe
            if not os.path.exists('data/local_storage.db'):
                print("Banco de dados não encontrado para backup")
                return False
                
            # Criar uma nova conexão para o backup
            source = sqlite3.connect('data/local_storage.db')
            destination = sqlite3.connect(backup_path)
            
            # Copiar o banco de dados
            source.backup(destination)
            
            # Fechar conexões
            source.close()
            destination.close()
            
            print(f"Backup criado com sucesso: {backup_path}")
            return True
        except Exception as e:
            print(f"Erro ao criar backup: {e}")
            traceback.print_exc()
            return False
    
    def close(self):
        """Fecha a conexão com o banco de dados para a thread atual"""
        if hasattr(self.thread_local, "conn") and self.thread_local.conn is not None:
            try:
                self.thread_local.conn.close()
                self.thread_local.conn = None
                print("Conexão com banco de dados fechada")
            except Exception as e:
                print(f"Erro ao fechar conexão: {e}")
    
    def __del__(self):
        """Garante que a conexão seja fechada quando o objeto é destruído"""
        self.close()
    
    def update_database_schema(self):
        """Atualiza o esquema do banco de dados para a versão mais recente"""
        try:
            cursor = self.conn.cursor()
            
            # Verificar e adicionar a coluna exit_type à tabela product_history
            cursor.execute("PRAGMA table_info(product_history)")
            columns = cursor.fetchall()
            column_names = [column[1] for column in columns]
            
            if "exit_type" not in column_names:
                print("Atualizando esquema: Adicionando coluna exit_type à tabela product_history")
                cursor.execute("ALTER TABLE product_history ADD COLUMN exit_type TEXT DEFAULT 'venda'")
                self.conn.commit()
                print("Esquema atualizado com sucesso")
            
            # Adicione aqui outras atualizações de esquema conforme necessário
            
            return True
        except Exception as e:
            print(f"Erro ao atualizar esquema do banco de dados: {e}")
            import traceback
            traceback.print_exc()
            return False

    def verify_products_table(self):
        """Verifica e corrige a estrutura da tabela de produtos"""
        try:
            cursor = self.conn.cursor()
            
            # Verificar se a tabela existe
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='products'")
            if not cursor.fetchone():
                print("Tabela de produtos não existe, criando...")
                cursor.execute('''
                CREATE TABLE products (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    quantity INTEGER DEFAULT 0,
                    lot TEXT,
                    expiry TEXT,
                    entryDate TEXT,
                    fabDate TEXT,
                    exitDate TEXT,
                    weeklyUsage TEXT,
                    lastUpdateDate TEXT,
                    category TEXT,
                    location TEXT,
                    group_id TEXT,
                    manufacturer TEXT
                )
                ''')
                self.conn.commit()
                print("Tabela de produtos criada com sucesso")
            
            # Verificar se todas as colunas existem
            cursor.execute("PRAGMA table_info(products)")
            columns = cursor.fetchall()
            column_names = [column[1] for column in columns]
            
            required_columns = [
                "id", "name", "quantity", "lot", "expiry", "entryDate", 
                "fabDate", "exitDate", "weeklyUsage", "lastUpdateDate",
                "category", "location", "group_id", "manufacturer"
            ]
            
            for column in required_columns:
                if column not in column_names:
                    print(f"Adicionando coluna {column} à tabela products")
                    cursor.execute(f"ALTER TABLE products ADD COLUMN {column} TEXT")
                    self.conn.commit()
            
            return True
        except Exception as e:
            print(f"Erro ao verificar tabela de produtos: {e}")
            import traceback
            traceback.print_exc()
            return False

    def verify_product_history_table(self):
        """Verifica e corrige a estrutura da tabela de histórico de produtos"""
        try:
            cursor = self.conn.cursor()
            
            # Verificar se a tabela existe
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='product_history'")
            if not cursor.fetchone():
                print("Tabela de histórico de produtos não existe, criando...")
                cursor.execute('''
                CREATE TABLE product_history (
                    id TEXT PRIMARY KEY,
                    productId TEXT,
                    productName TEXT,
                    quantity INTEGER,
                    reason TEXT,
                    date TEXT,
                    timestamp REAL,
                    type TEXT,
                    exit_type TEXT DEFAULT 'venda'
                )
                ''')
                self.conn.commit()
                print("Tabela de histórico de produtos criada com sucesso")
            
            # Verificar se a coluna exit_type existe
            cursor.execute("PRAGMA table_info(product_history)")
            columns = cursor.fetchall()
            column_names = [column[1] for column in columns]
            
            if "exit_type" not in column_names:
                print("Adicionando coluna exit_type à tabela product_history")
                cursor.execute("ALTER TABLE product_history ADD COLUMN exit_type TEXT DEFAULT 'venda'")
                self.conn.commit()
                print("Coluna exit_type adicionada com sucesso")
            
            return True
        except Exception as e:
            print(f"Erro ao verificar tabela de histórico de produtos: {e}")
            import traceback
            traceback.print_exc()
            return False
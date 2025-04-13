import flet as ft
from datetime import datetime

class AddGroupScreen:
    def __init__(self, data, navigation):
        self.data = data
        self.navigation = navigation
        self.is_product_group = True  # Por padrão, assume que é um grupo de produtos
    
    def set_group_type(self, is_product_group=True):
        """Define o tipo de grupo a ser adicionado"""
        self.is_product_group = is_product_group
    
    def build(self):
        name_field = ft.TextField(
            label="Nome do Grupo",
            border_radius=8,
        )
        
        description_field = ft.TextField(
            label="Descrição",
            border_radius=8,
            multiline=True,
            min_lines=2,
            max_lines=4,
        )
        
        # Lista de ícones disponíveis
        available_icons = [
            "INVENTORY_2_ROUNDED", "DELETE_OUTLINE", "CATEGORY", "FOLDER", 
            "LABEL", "TAG", "BOOKMARK", "STAR", "FAVORITE", "SHOPPING_CART",
            "LOCAL_SHIPPING", "STORE", "SCIENCE", "BIOTECH", "CONSTRUCTION",
            "HARDWARE", "KITCHEN", "MEDICAL_SERVICES", "AGRICULTURE"
        ]
        
        # Dropdown para seleção de ícone
        icon_dropdown = ft.Dropdown(
            label="Ícone",
            value="INVENTORY_2_ROUNDED" if self.is_product_group else "DELETE_OUTLINE",
            options=[
                ft.dropdown.Option(
                    text=icon_name,
                    key=icon_name
                ) for icon_name in available_icons
            ],
            border_radius=8,
        )
        
        # Lista de cores disponíveis
        available_colors = [
            "blue", "red", "green", "purple", "orange", 
            "teal", "pink", "amber", "indigo", "cyan"
        ]
        
        # Dropdown para seleção de cor
        color_dropdown = ft.Dropdown(
            label="Cor",
            value="blue" if self.is_product_group else "purple",
            options=[
                ft.dropdown.Option(
                    text=color.capitalize(),
                    key=color
                ) for color in available_colors
            ],
            border_radius=8,
        )
        
        def add_group(_):
            if not name_field.value:
                self.navigation.show_snack_bar(
                    "O nome do grupo é obrigatório",
                    ft.colors.RED_500
                )
                return
            
            # Preparar dados do novo grupo
            now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            group_id = f"{'group' if self.is_product_group else 'resgroup'}_{int(datetime.now().timestamp())}"
            
            new_group = {
                "id": group_id,
                "name": name_field.value,
                "description": description_field.value,
                "icon": icon_dropdown.value,
                "color": color_dropdown.value,
                "created_at": now,
                "last_updated": now
            }
            
            # Adicionar grupo usando o serviço apropriado
            from services.group_service import GroupService
            group_service = GroupService(self.data.firebase, self.data.db)
            
            # Salvar no banco de dados local
            cursor = self.data.db.conn.cursor()
            
            table = "product_groups" if self.is_product_group else "residue_groups"
            
            try:
                cursor.execute(f'''
                INSERT INTO {table} (id, name, description, icon, color, created_at, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    new_group["id"], 
                    new_group["name"], 
                    new_group["description"],
                    new_group["icon"],
                    new_group["color"],
                    new_group["created_at"],
                    new_group["last_updated"]
                ))
                
                self.data.db.conn.commit()
                
                # Salvar no Firebase se estiver online
                if self.data.firebase.online_mode:
                    try:
                        collection = "product_groups" if self.is_product_group else "residue_groups"
                        self.data.firebase.db.collection(collection).document(group_id).set(new_group)
                    except Exception as e:
                        print(f"Erro ao salvar grupo no Firebase: {e}")
                        # Adicionar à fila de sincronização
                        self.data.db.add_sync_operation('add', collection, group_id, new_group)
                else:
                    # Adicionar à fila de sincronização
                    collection = "product_groups" if self.is_product_group else "residue_groups"
                    self.data.db.add_sync_operation('add', collection, group_id, new_group)
                
                self.data.refresh_data()
                self.navigation.show_snack_bar("Grupo criado com sucesso!")
                self.navigation.go_back()
            except Exception as e:
                print(f"Erro ao criar grupo: {e}")
                self.data.db.conn.rollback()
                self.navigation.show_snack_bar(
                    "Erro ao criar grupo",
                    ft.colors.RED_500
                )
        
        group_type_text = "Produtos" if self.is_product_group else "Resíduos"
        
        return ft.Container(
            content=ft.Column(
                controls=[
                    # Cabeçalho
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.IconButton(
                                    icon=ft.icons.ARROW_BACK,
                                    on_click=lambda _: self.navigation.go_back()
                                ),
                                ft.Text(f"Novo Grupo de {group_type_text}", size=20, weight="bold"),
                            ],
                            alignment=ft.MainAxisAlignment.START,
                        ),
                        padding=10,
                    ),
                    
                    # Formulário
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                name_field,
                                description_field,
                                icon_dropdown,
                                color_dropdown,
                                
                                # Visualização do ícone e cor selecionados
                                ft.Container(
                                    content=ft.Row(
                                        controls=[
                                            ft.Text("Visualização:"),
                                            ft.Icon(
                                                name=getattr(ft.icons, icon_dropdown.value),
                                                color=getattr(ft.colors, f"{color_dropdown.value.upper()}_500"),
                                                size=24,
                                            ),
                                        ],
                                        spacing=10,
                                        alignment=ft.MainAxisAlignment.CENTER,
                                    ),
                                    padding=10,
                                ),
                            ],
                            spacing=10,
                            scroll=ft.ScrollMode.AUTO,
                        ),
                        padding=20,
                    ),
                    
                    # Botões
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.ElevatedButton(
                                    "Cancelar",
                                    on_click=lambda _: self.navigation.go_back(),
                                    style=ft.ButtonStyle(
                                        color=ft.colors.BLACK,
                                        bgcolor=ft.colors.GREY_300,
                                    ),
                                ),
                                ft.ElevatedButton(
                                    "Criar Grupo",
                                    on_click=add_group,
                                    style=ft.ButtonStyle(
                                        color=ft.colors.WHITE,
                                        bgcolor=ft.colors.BLUE_500,
                                    ),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.END,
                            spacing=10,
                        ),
                        padding=20,
                    ),
                ],
                spacing=0,
                expand=True,
            ),
            expand=True,
        )
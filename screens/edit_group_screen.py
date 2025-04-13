import flet as ft
from datetime import datetime

class EditGroupScreen:
    def __init__(self, data, navigation):
        self.data = data
        self.navigation = navigation
        self.group = None
        self.is_product_group = True
    
    def set_group(self, group, is_product_group=True):
        """Define o grupo a ser editado"""
        self.group = group
        self.is_product_group = is_product_group
    
    def build(self):
        if not self.group:
            return ft.Container(
                content=ft.Text("Grupo não encontrado"),
                alignment=ft.alignment.center,
                padding=20
            )
        
        name_field = ft.TextField(
            label="Nome do Grupo",
            value=self.group["name"],
            border_radius=8,
        )
        
        description_field = ft.TextField(
            label="Descrição",
            value=self.group.get("description", ""),
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
            value=self.group.get("icon", "INVENTORY_2_ROUNDED"),
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
            value=self.group.get("color", "blue"),
            options=[
                ft.dropdown.Option(
                    text=color.capitalize(),
                    key=color
                ) for color in available_colors
            ],
            border_radius=8,
        )
        
        def update_group(_):
            if not name_field.value:
                self.navigation.show_snack_bar(
                    "O nome do grupo é obrigatório",
                    ft.colors.RED_500
                )
                return
            
            # Preparar dados atualizados do grupo
            updated_group = {
                "id": self.group["id"],
                "name": name_field.value,
                "description": description_field.value,
                "icon": icon_dropdown.value,
                "color": color_dropdown.value,
                "created_at": self.group.get("created_at", datetime.now().strftime("%d/%m/%Y %H:%M:%S")),
                "last_updated": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            }
            
            # Atualizar grupo usando o serviço apropriado
            from services.group_service import GroupService
            group_service = GroupService(self.data.firebase, self.data.db)
            
            success = group_service.update_group(
                self.group["id"], 
                updated_group, 
                is_residue=not self.is_product_group
            )
            
            if success:
                self.data.refresh_data()
                self.navigation.show_snack_bar("Grupo atualizado com sucesso!")
                self.navigation.go_back()
            else:
                self.navigation.show_snack_bar(
                    "Erro ao atualizar grupo",
                    ft.colors.RED_500
                )
        
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
                                ft.Text("Editar Grupo", size=20, weight="bold"),
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
                                    "Salvar",
                                    on_click=update_group,
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
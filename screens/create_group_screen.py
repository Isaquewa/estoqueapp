import flet as ft
import uuid

class CreateGroupScreen:
    """Tela para criar um novo grupo de produtos ou resíduos"""
    
    def __init__(self, data, navigation, group_type):
        self.data = data
        self.navigation = navigation
        self.group_type = group_type  # "product" ou "residue"
        
        # Inicializar campos de edição
        self.name_field = ft.TextField(
            label="Nome do Grupo",
            hint_text="Ex: Café, Açúcar, Farinha..."
        )
        
        # Seleção de ícone
        self.icon_dropdown = ft.Dropdown(
            label="Ícone",
            width=200,
            options=[
                ft.dropdown.Option(key="INVENTORY_2_ROUNDED", text="Inventário"),
                ft.dropdown.Option(key="SHOPPING_CART", text="Carrinho"),
                ft.dropdown.Option(key="CATEGORY", text="Categoria"),
                ft.dropdown.Option(key="STORE", text="Loja"),
                ft.dropdown.Option(key="LOCAL_SHIPPING", text="Transporte"),
                ft.dropdown.Option(key="DELETE_OUTLINE", text="Lixeira"),
                ft.dropdown.Option(key="RECYCLING", text="Reciclagem"),
                ft.dropdown.Option(key="ECO", text="Ecologia"),
                ft.dropdown.Option(key="WATER_DROP", text="Água"),
                ft.dropdown.Option(key="SCIENCE", text="Ciência"),
                ft.dropdown.Option(key="FACTORY", text="Fábrica"),
                ft.dropdown.Option(key="RESTAURANT", text="Restaurante"),
                ft.dropdown.Option(key="FASTFOOD", text="Fast Food"),
                ft.dropdown.Option(key="KITCHEN", text="Cozinha"),
                ft.dropdown.Option(key="BAKERY_DINING", text="Padaria"),
                ft.dropdown.Option(key="LIQUOR", text="Bebidas"),
                ft.dropdown.Option(key="COFFEE", text="Café"),
                ft.dropdown.Option(key="EGG", text="Ovo"),
                ft.dropdown.Option(key="COOKIE", text="Biscoito"),
                ft.dropdown.Option(key="CAKE", text="Bolo"),
                ft.dropdown.Option(key="ICECREAM", text="Sorvete"),
                ft.dropdown.Option(key="RICE_BOWL", text="Arroz"),
                ft.dropdown.Option(key="SET_MEAL", text="Refeição"),
            ],
            value="INVENTORY_2_ROUNDED" if group_type == "product" else "DELETE_OUTLINE"
        )
        
        # Seleção de cor
        self.color_dropdown = ft.Dropdown(
            label="Cor",
            width=200,
            options=[
                ft.dropdown.Option(key="BLUE_500", text="Azul"),
                ft.dropdown.Option(key="RED_500", text="Vermelho"),
                ft.dropdown.Option(key="GREEN_500", text="Verde"),
                ft.dropdown.Option(key="PURPLE_500", text="Roxo"),
                ft.dropdown.Option(key="ORANGE_500", text="Laranja"),
                ft.dropdown.Option(key="AMBER_500", text="Âmbar"),
                ft.dropdown.Option(key="TEAL_500", text="Turquesa"),
                ft.dropdown.Option(key="PINK_500", text="Rosa"),
                ft.dropdown.Option(key="INDIGO_500", text="Índigo"),
                ft.dropdown.Option(key="LIME_500", text="Lima"),
                ft.dropdown.Option(key="BROWN_500", text="Marrom"),
                ft.dropdown.Option(key="GREY_500", text="Cinza"),
            ],
            value="BLUE_500" if group_type == "product" else "PURPLE_500"
        )
        
        # Descrição do grupo
        self.description_field = ft.TextField(
            label="Descrição (opcional)",
            hint_text="Descrição do grupo",
            multiline=True,
            min_lines=2,
            max_lines=4
        )
    
    def build(self):
        # Título da tela
        title = "Criar Grupo de Produtos" if self.group_type == "product" else "Criar Grupo de Resíduos"
        
        # Botão para salvar
        save_button = ft.ElevatedButton(
            text="Salvar",
            icon=ft.icons.SAVE,
            on_click=lambda _: self._save_group()
        )
        
        # Botão para voltar
        back_button = ft.TextButton(
            text="Voltar",
            icon=ft.icons.ARROW_BACK,
            on_click=lambda _: self.navigation.go_back()
        )
        
        # Layout principal
        return ft.Column([
            # Barra de título
            ft.Container(
                content=ft.Row([
                    back_button,
                    ft.Text(title, size=18, weight="bold"),
                ], alignment=ft.MainAxisAlignment.START),
                padding=10
            ),
            
            # Formulário de criação
            ft.Container(
                content=ft.Column([
                    # Nome do grupo
                    self.name_field,
                    
                    # Dropdowns
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Aparência", size=14, weight="bold"),
                            self.icon_dropdown,
                            self.color_dropdown,
                        ]),
                        margin=ft.margin.only(top=10, bottom=10)
                    ),
                    
                    # Descrição
                    self.description_field,
                    
                    # Botão de salvar
                    ft.Container(
                        content=save_button,
                        margin=ft.margin.only(top=20),
                        alignment=ft.alignment.center
                    )
                ]),
                padding=20,
                expand=True
            )
        ])
    
    def _save_group(self):
        """Salva o novo grupo"""
        try:
            # Validar campos
            if not self.name_field.value:
                self.navigation.show_snack_bar("Nome do grupo é obrigatório", is_error=True)
                return
            
            # Criar ID único para o grupo
            group_id = f"{self.group_type}_{uuid.uuid4().hex[:8]}"
            
            # Criar objeto do grupo
            group = {
                "id": group_id,
                "name": self.name_field.value,
                "icon": self.icon_dropdown.value,
                "color": self.color_dropdown.value,
                "description": self.description_field.value,
                "created_at": self.data.firebase.server_timestamp()
            }
            
            # Salvar grupo no banco de dados
            from services.group_service import GroupService
            group_service = GroupService(self.data.firebase, self.data.db)
            
            if self.group_type == "product":
                success = group_service.create_product_group(group)
            else:
                success = group_service.create_residue_group(group)
            
            if success:
                # Adicionar grupo ao dashboard
                from services.card_config_service import CardConfigService
                card_config_service = CardConfigService(self.data.firebase, self.data.db)
                
                if self.group_type == "product":
                    card_config_service.add_product_group_to_dashboard(group)
                else:
                    card_config_service.add_residue_group_to_dashboard(group)
                
                # Mostrar mensagem de sucesso
                self.navigation.show_snack_bar(f"Grupo '{self.name_field.value}' criado com sucesso")
                
                # Voltar para o dashboard
                self.navigation.go_to_dashboard()
            else:
                # Mostrar mensagem de erro
                self.navigation.show_snack_bar("Erro ao criar grupo", is_error=True)
        except Exception as e:
            print(f"Erro ao criar grupo: {e}")
            self.navigation.show_snack_bar(f"Erro: {str(e)}", is_error=True)
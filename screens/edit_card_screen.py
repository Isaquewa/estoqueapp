import flet as ft

class EditCardScreen:
    """Tela para editar configurações de um card do dashboard"""
    
    def __init__(self, data, navigation, card_type, card_data):
        self.data = data
        self.navigation = navigation
        self.card_type = card_type  # "product_group" ou "residue_group"
        self.card_data = card_data
        self.group_id = card_data.get("id", "")
        
        # Inicializar campos de edição
        self.title_field = ft.TextField(
            label="Título do Card",
            value=card_data.get("name", ""),
            hint_text="Nome exibido no card",
            read_only=True  # O título original não pode ser alterado
        )
        
        # Obter configuração atual do card
        from services.card_config_service import CardConfigService
        self.card_config_service = CardConfigService(self.data.firebase, self.data.db)
        
        if card_type == "product_group":
            self.config = self.card_config_service.get_product_group_config(self.group_id)
        else:
            self.config = self.card_config_service.get_residue_group_config(self.group_id)
        
        # Campos para configurações visuais
        self.custom_title_field = ft.TextField(
            label="Título Personalizado",
            value=self.config.get("custom_title", ""),
            hint_text="Deixe em branco para usar o nome original"
        )
        
        self.show_quantity_switch = ft.Switch(
            label="Mostrar Quantidade",
            value=self.config.get("show_quantity", True)
        )
        
        self.show_details_switch = ft.Switch(
            label="Mostrar Detalhes",
            value=self.config.get("show_details", True)
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
            value=self.config.get("icon", "INVENTORY_2_ROUNDED" if card_type == "product_group" else "DELETE_OUTLINE")
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
            value=self.config.get("color", "BLUE_500" if card_type == "product_group" else "PURPLE_500")
        )
        
        # Seleção de prioridade
        self.priority_dropdown = ft.Dropdown(
            label="Prioridade",
            width=200,
            options=[
                ft.dropdown.Option(key="low", text="Baixa"),
                ft.dropdown.Option(key="normal", text="Normal"),
                ft.dropdown.Option(key="high", text="Alta"),
            ],
            value=self.config.get("priority", "normal")
        )
    
    def build(self):
        # Título da tela
        title = "Editar Card de Produto" if self.card_type == "product_group" else "Editar Card de Resíduo"
        
        # Botão para salvar
        save_button = ft.ElevatedButton(
            text="Salvar",
            icon=ft.icons.SAVE,
            on_click=lambda _: self._save_card_config()
        )
        
        # Botão para remover do dashboard
        remove_button = ft.OutlinedButton(
            text="Remover do Dashboard",
            icon=ft.icons.DELETE_OUTLINE,
            on_click=lambda _: self._remove_from_dashboard()
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
            
            # Formulário de edição
            ft.Container(
                content=ft.Column([
                    # Título original (não editável)
                    self.title_field,
                    
                    # Título personalizado
                    self.custom_title_field,
                    
                    # Switches
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Opções de Exibição", size=14, weight="bold"),
                            self.show_quantity_switch,
                            self.show_details_switch,
                        ]),
                        margin=ft.margin.only(top=10, bottom=10)
                    ),
                    
                    # Dropdowns
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Aparência", size=14, weight="bold"),
                            self.icon_dropdown,
                            self.color_dropdown,
                            self.priority_dropdown,
                        ]),
                        margin=ft.margin.only(top=10, bottom=10)
                    ),
                    
                    # Botões
                    ft.Container(
                        content=ft.Row([
                            save_button,
                            remove_button,
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        margin=ft.margin.only(top=20)
                    )
                ]),
                padding=20,
                expand=True
            )
        ])
    
    def _save_card_config(self):
        """Salva as configurações do card"""
        try:
            # Criar objeto de configuração
            config = {
                "custom_title": self.custom_title_field.value,
                "show_quantity": self.show_quantity_switch.value,
                "show_details": self.show_details_switch.value,
                "icon": self.icon_dropdown.value,
                "color": self.color_dropdown.value,
                "priority": self.priority_dropdown.value,
                "bgcolor": "#FFFFFF"  # Valor padrão
            }
            
            # Salvar configuração
            success = False
            if self.card_type == "product_group":
                success = self.card_config_service.save_product_group_config(self.group_id, config)
            else:
                success = self.card_config_service.save_residue_group_config(self.group_id, config)
            
            if success:
                # Mostrar mensagem de sucesso
                self.navigation.show_snack_bar("Configurações salvas com sucesso")
                # Voltar para o dashboard
                self.navigation.go_back()
            else:
                # Mostrar mensagem de erro
                self.navigation.show_snack_bar("Erro ao salvar configurações", is_error=True)
        except Exception as e:
            print(f"Erro ao salvar configurações do card: {e}")
            self.navigation.show_snack_bar(f"Erro: {str(e)}", is_error=True)
    
    def _remove_from_dashboard(self):
        """Remove o card do dashboard"""
        try:
            success = False
            if self.card_type == "product_group":
                success = self.card_config_service.remove_product_group_from_dashboard(self.group_id)
            else:
                success = self.card_config_service.remove_residue_group_from_dashboard(self.group_id)
            
            if success:
                # Mostrar mensagem de sucesso
                self.navigation.show_snack_bar("Card removido do dashboard")
                # Voltar para o dashboard
                self.navigation.go_back()
            else:
                # Mostrar mensagem de erro
                self.navigation.show_snack_bar("Erro ao remover card", is_error=True)
        except Exception as e:
            print(f"Erro ao remover card do dashboard: {e}")
            self.navigation.show_snack_bar(f"Erro: {str(e)}", is_error=True)
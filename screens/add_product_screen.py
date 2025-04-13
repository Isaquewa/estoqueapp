import flet as ft
from datetime import datetime

class AddProductScreen:
    def __init__(self, data, navigation):
        self.data = data
        self.navigation = navigation
    
    def build(self):
        # Campos do formulário
        name_field = ft.TextField(
            label="Nome do Produto",
            value=self.data.new_product.get("name", ""),
            on_change=lambda e: self.data.update_new_product("name", e.control.value),
            border_radius=8,
        )
        
        quantity_field = ft.TextField(
            label="Quantidade",
            value=str(self.data.new_product.get("quantity", "")),
            on_change=lambda e: self.data.update_new_product("quantity", e.control.value),
            keyboard_type=ft.KeyboardType.NUMBER,
            border_radius=8,
        )
        
        lot_field = ft.TextField(
            label="Lote",
            value=self.data.new_product.get("lot", ""),
            on_change=lambda e: self.data.update_new_product("lot", e.control.value),
            border_radius=8,
        )
        
        expiry_field = ft.TextField(
            label="Data de Validade (DD/MM/AAAA)",
            value=self.data.new_product.get("expiry", ""),
            on_change=lambda e: self.data.update_new_product("expiry", e.control.value),
            border_radius=8,
        )
        
        fab_date_field = ft.TextField(
            label="Data de Fabricação (DD/MM/AAAA)",
            value=self.data.new_product.get("fabDate", ""),
            on_change=lambda e: self.data.update_new_product("fabDate", e.control.value),
            border_radius=8,
        )
        
        manufacturer_field = ft.TextField(
            label="Fabricante",
            value=self.data.new_product.get("manufacturer", ""),
            on_change=lambda e: self.data.update_new_product("manufacturer", e.control.value),
            border_radius=8,
        )
        
        def add_product(_):
            if not all([
                name_field.value, 
                quantity_field.value, 
                lot_field.value, 
                expiry_field.value
            ]):
                self.navigation.show_snack_bar(
                    "Preencha todos os campos obrigatórios",
                    ft.colors.RED_500
                )
                return
            
            # Adicionar produto
            success = self.data.add_product()
            
            if success:
                self.navigation.show_snack_bar("Produto adicionado com sucesso!")
                self.navigation.go_back()
            else:
                self.navigation.show_snack_bar(
                    "Erro ao adicionar produto. Verifique os dados.",
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
                                ft.Text("Adicionar Produto", size=20, weight="bold"),
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
                                quantity_field,
                                lot_field,
                                expiry_field,
                                fab_date_field,
                                manufacturer_field,
                                ft.Text(
                                    "* Campos obrigatórios: Nome, Quantidade, Lote e Data de Validade",
                                    size=12,
                                    color=ft.colors.GREY_500,
                                    italic=True
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
                                    "Adicionar",
                                    on_click=add_product,
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
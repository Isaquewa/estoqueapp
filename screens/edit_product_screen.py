import flet as ft
from datetime import datetime

class EditProductScreen:
    def __init__(self, data, navigation):
        self.data = data
        self.navigation = navigation
        self.product = None
    
    def set_product(self, product):
        """Define o produto a ser editado"""
        self.product = product
    
    def build(self):
        if not self.product:
            return ft.Container(
                content=ft.Text("Produto não encontrado"),
                alignment=ft.alignment.center,
                padding=20
            )
        
        name_field = ft.TextField(
            label="Nome do Produto",
            value=self.product["name"],
            border_radius=8,
        )
        
        quantity_field = ft.TextField(
            label="Quantidade",
            value=str(self.product["quantity"]),
            keyboard_type=ft.KeyboardType.NUMBER,
            border_radius=8,
        )
        
        lot_field = ft.TextField(
            label="Lote",
            value=self.product["lot"],
            border_radius=8,
        )
        
        expiry_field = ft.TextField(
            label="Data de Validade (DD/MM/AAAA)",
            value=self.product["expiry"],
            border_radius=8,
        )
        
        fab_date_field = ft.TextField(
            label="Data de Fabricação (DD/MM/AAAA)",
            value=self.product["fabDate"],
            border_radius=8,
        )
        
        manufacturer_field = ft.TextField(
            label="Fabricante",
            value=self.product.get("manufacturer", ""),
            border_radius=8,
        )
        
        group_info = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.icons.FOLDER, color=ft.colors.BLUE_500),
                    ft.Text(f"Grupo: {self.product.get('group_name', 'Não categorizado')}"),
                ],
                spacing=10,
            ),
            padding=10,
            border_radius=8,
            bgcolor=ft.colors.BLUE_50,
        )
        
        def update_product(_):
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
            
            updated_product = {
                "id": self.product["id"],
                "name": name_field.value,
                "quantity": int(quantity_field.value),
                "lot": lot_field.value,
                "expiry": expiry_field.value,
                "fabDate": fab_date_field.value,
                "manufacturer": manufacturer_field.value,
                "entryDate": self.product["entryDate"],
                "exitDate": self.product["exitDate"],
                "weeklyUsage": self.product["weeklyUsage"],
                "lastUpdateDate": datetime.now().strftime("%d/%m/%Y"),
                "group_id": self.product.get("group_id", ""),
                "group_name": self.product.get("group_name", "")
            }
            
            self.data.product_service.update_product(self.product["id"], updated_product)
            self.data.refresh_data()
            
            self.navigation.show_snack_bar("Produto atualizado com sucesso!")
            self.navigation.go_back()
        
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
                                ft.Text("Editar Produto", size=20, weight="bold"),
                            ],
                            alignment=ft.MainAxisAlignment.START,
                        ),
                        padding=10,
                    ),
                    
                    # Grupo do produto
                    group_info,
                    
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
                                    on_click=update_product,
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
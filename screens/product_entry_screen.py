import flet as ft
from datetime import datetime

class ProductEntryScreen:
    def __init__(self, data, navigation):
        self.data = data
        self.navigation = navigation
        self.product = None
        self.entry_quantity = ""
        self.entry_lot = ""
        self.entry_expiry = ""
        self.entry_notes = ""
    
    def set_product(self, product):
        """Define o produto para registrar entrada"""
        self.product = product
    
    def build(self):
        if not self.product:
            return ft.Container(
                content=ft.Text("Produto não encontrado"),
                alignment=ft.alignment.center,
                padding=20
            )
        
        # Campos do formulário
        quantity_field = ft.TextField(
            label="Quantidade de Entrada",
            value=self.entry_quantity,
            keyboard_type=ft.KeyboardType.NUMBER,
            on_change=self._update_entry_quantity,
            border_radius=8,
        )
        
        lot_field = ft.TextField(
            label="Lote",
            value=self.entry_lot,
            on_change=self._update_entry_lot,
            border_radius=8,
        )
        
        expiry_field = ft.TextField(
            label="Data de Validade (DD/MM/AAAA)",
            value=self.entry_expiry,
            on_change=self._update_entry_expiry,
            border_radius=8,
        )
        
        notes_field = ft.TextField(
            label="Observações",
            value=self.entry_notes,
            on_change=self._update_entry_notes,
            border_radius=8,
            multiline=True,
            min_lines=2,
            max_lines=4,
        )
        
        # Informações do produto
        product_info = ft.Column(
            [
                ft.Text(self.product["name"], size=18, weight="bold"),
                ft.Text(
                    f"Quantidade atual: {self.product['quantity']} unidades",
                    size=14,
                    color=ft.colors.BLUE_500,
                ),
                ft.Text(
                    f"Lote atual: {self.product.get('lot', 'N/A')} • Validade: {self.product.get('expiry', 'N/A')}",
                    size=14,
                ),
            ],
            spacing=5,
        )
        
        def register_entry(_):
            """Registra a entrada do produto"""
            if not self.entry_quantity:
                self.navigation.show_snack_bar(
                    "Informe a quantidade de entrada",
                    ft.colors.RED_500
                )
                return
            
            try:
                entry_qty = int(self.entry_quantity)
                if entry_qty <= 0:
                    self.navigation.show_snack_bar(
                        "A quantidade deve ser maior que zero",
                        ft.colors.RED_500
                    )
                    return
                
                # Validar data de validade
                if self.entry_expiry:
                    try:
                        datetime.strptime(self.entry_expiry, "%d/%m/%Y")
                    except ValueError:
                        self.navigation.show_snack_bar(
                            "Formato de data inválido. Use DD/MM/AAAA",
                            ft.colors.RED_500
                        )
                        return
                
                # Registrar entrada
                success, message = self.data.product_service.register_product_entry(
                    self.product["id"],
                    entry_qty,
                    self.entry_lot,
                    self.entry_expiry,
                    self.entry_notes
                )
                
                if success:
                    self.navigation.show_snack_bar(message)
                    self.data.refresh_data()
                    self.navigation.go_back()
                else:
                    self.navigation.show_snack_bar(
                        message,
                        ft.colors.RED_500
                    )
            except ValueError:
                self.navigation.show_snack_bar(
                    "Quantidade inválida. Digite um número inteiro.",
                    ft.colors.RED_500
                )
        
        return ft.Container(
            content=ft.Column(
                [
                    # Cabeçalho
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.IconButton(
                                    icon=ft.icons.ARROW_BACK,
                                    on_click=lambda _: self.navigation.go_back(),
                                ),
                                ft.Text("Registrar Entrada de Produto", size=20, weight="bold"),
                            ],
                            alignment=ft.MainAxisAlignment.START,
                        ),
                        padding=10,
                    ),
                    
                    # Informações do produto
                    ft.Container(
                        content=product_info,
                        padding=20,
                        border_radius=10,
                        bgcolor=ft.colors.WHITE,
                        border=ft.border.all(1, ft.colors.GREY_300),
                        margin=ft.margin.only(left=20, right=20, bottom=20),
                    ),
                    
                    # Formulário
                    ft.Container(
                        content=ft.Column(
                            [
                                quantity_field,
                                lot_field,
                                expiry_field,
                                notes_field,
                            ],
                            spacing=10,
                        ),
                        padding=20,
                    ),
                    
                    # Botões
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.ElevatedButton(
                                    "Cancelar",
                                    on_click=lambda _: self.navigation.go_back(),
                                    style=ft.ButtonStyle(
                                        color=ft.colors.BLACK,
                                        bgcolor=ft.colors.GREY_300,
                                    ),
                                ),
                                ft.ElevatedButton(
                                    "Registrar Entrada",
                                    on_click=register_entry,
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
    
    def _update_entry_quantity(self, e):
        """Atualiza a quantidade de entrada"""
        self.entry_quantity = e.control.value
    
    def _update_entry_lot(self, e):
        """Atualiza o lote da entrada"""
        self.entry_lot = e.control.value
    
    def _update_entry_expiry(self, e):
        """Atualiza a data de validade da entrada"""
        self.entry_expiry = e.control.value
    
    def _update_entry_notes(self, e):
        """Atualiza as observações da entrada"""
        self.entry_notes = e.control.value
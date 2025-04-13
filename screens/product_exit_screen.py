import flet as ft
from datetime import datetime

class ProductExitScreen:
    def __init__(self, data, navigation):
        self.data = data
        self.navigation = navigation
        self.product = None
        self.exit_quantity = ""
        self.exit_reason = ""
    
    def set_product(self, product):
        """Define o produto para registrar saída"""
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
            label="Quantidade de Saída",
            value=self.exit_quantity,
            keyboard_type=ft.KeyboardType.NUMBER,
            on_change=self._update_exit_quantity,
            border_radius=8,
        )
        
        reason_field = ft.TextField(
            label="Motivo da Saída",
            value=self.exit_reason,
            on_change=self._update_exit_reason,
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
                    f"Lote: {self.product.get('lot', 'N/A')} • Validade: {self.product.get('expiry', 'N/A')}",
                    size=14,
                ),
            ],
            spacing=5,
        )
        
        def register_exit(_):
            """Registra a saída do produto"""
            if not self.exit_quantity:
                self.navigation.show_snack_bar(
                    "Informe a quantidade de saída",
                    ft.colors.RED_500
                )
                return
            
            try:
                exit_qty = int(self.exit_quantity)
                if exit_qty <= 0:
                    self.navigation.show_snack_bar(
                        "A quantidade deve ser maior que zero",
                        ft.colors.RED_500
                    )
                    return
                
                if exit_qty > self.product["quantity"]:
                    self.navigation.show_snack_bar(
                        "Quantidade de saída maior que o estoque disponível",
                        ft.colors.RED_500
                    )
                    return
                
                # Registrar saída
                success, message = self.data.product_service.register_product_exit(
                    self.product["id"],
                    exit_qty,
                    self.exit_reason or "Saída de estoque"
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
                                ft.Text("Registrar Saída de Produto", size=20, weight="bold"),
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
                                reason_field,
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
                                    "Registrar Saída",
                                    on_click=register_exit,
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
    
    def _update_exit_quantity(self, e):
        """Atualiza a quantidade de saída"""
        self.exit_quantity = e.control.value
    
    def _update_exit_reason(self, e):
        """Atualiza o motivo da saída"""
        self.exit_reason = e.control.value
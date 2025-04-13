import flet as ft
from datetime import datetime

class AddResidueScreen:
    def __init__(self, data, navigation):
        self.data = data
        self.navigation = navigation
        # Inicializar variáveis para novo tipo
        self.new_type_name = ""
        self.new_type_color = "purple"
        self.new_type_icon = "DELETE_OUTLINE"
    
    def build(self):
        # Campos do formulário
        name_field = ft.TextField(
            label="Nome do Resíduo",
            value=self.data.new_residue.get("name", ""),
            on_change=lambda e: self.data.update_new_residue("name", e.control.value),
            border_radius=8,
        )
        
        quantity_field = ft.TextField(
            label="Quantidade",
            value=str(self.data.new_residue.get("quantity", "")),
            on_change=lambda e: self.data.update_new_residue("quantity", e.control.value),
            keyboard_type=ft.KeyboardType.NUMBER,
            border_radius=8,
        )
        
        destination_field = ft.TextField(
            label="Destino",
            value=self.data.new_residue.get("destination", ""),
            on_change=lambda e: self.data.update_new_residue("destination", e.control.value),
            border_radius=8,
        )
        
        notes_field = ft.TextField(
            label="Observações",
            value=self.data.new_residue.get("notes", ""),
            on_change=lambda e: self.data.update_new_residue("notes", e.control.value),
            border_radius=8,
            multiline=True,
            min_lines=2,
            max_lines=4,
        )
        
        # Botão de adicionar
        def add_residue(_):
            # Definir data de entrada como data atual
            current_date = datetime.now().strftime("%d/%m/%Y")
            self.data.update_new_residue("entryDate", current_date)
            
            # Validar campos obrigatórios
            if not name_field.value:
                self.navigation.show_snack_bar("Nome do resíduo é obrigatório", ft.colors.RED_500)
                return
            
            # Verificar quantidade
            if not quantity_field.value:
                self.navigation.show_snack_bar("Quantidade é obrigatória", ft.colors.RED_500)
                return
            
            try:
                quantity = int(quantity_field.value)
                if quantity <= 0:
                    self.navigation.show_snack_bar("Quantidade deve ser maior que zero", ft.colors.RED_500)
                    return
            except ValueError:
                self.navigation.show_snack_bar("Quantidade deve ser um número inteiro", ft.colors.RED_500)
                return
            
            # Identificar grupo automaticamente com base no nome
            from services.residue_service import ResidueService
            residue_service = ResidueService(self.data.firebase, self.data.db)
            
            # Criar dados do resíduo
            residue_data = {
                "name": name_field.value,
                "quantity": int(quantity_field.value),
                "destination": destination_field.value,
                "notes": notes_field.value,
                "entryDate": current_date
            }
            
            # Tentar adicionar resíduo
            try:
                success = residue_service.add_residue(residue_data)
                
                if success:
                    self.navigation.show_snack_bar("Resíduo adicionado com sucesso!", ft.colors.GREEN_500)
                    self.data.refresh_data()  # Atualizar dados
                    self.navigation.go_back()
                else:
                    self.navigation.show_snack_bar(
                        "Erro ao adicionar resíduo. Verifique os dados e tente novamente.",
                        ft.colors.RED_500
                    )
            except Exception as e:
                self.navigation.show_snack_bar(
                    f"Erro ao adicionar resíduo: {str(e)}",
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
                                ft.Text("Adicionar Resíduo", size=20, weight="bold"),
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
                                destination_field,
                                notes_field,
                                ft.Text(
                                    "* Campos obrigatórios: Nome e Quantidade",
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
                                    on_click=add_residue,
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
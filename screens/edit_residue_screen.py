import flet as ft
from datetime import datetime

class EditResidueScreen:
    def __init__(self, data, navigation):
        self.data = data
        self.navigation = navigation
        self.residue = None
    
    def set_residue(self, residue):
        """Define o resíduo a ser editado"""
        self.residue = residue
    
    def build(self):
        if not self.residue:
            return ft.Container(
                content=ft.Text("Resíduo não encontrado"),
                alignment=ft.alignment.center,
                padding=20
            )
        
        # Obter tipos de resíduos para o dropdown
        from services.group_service import GroupService
        group_service = GroupService(self.data.firebase, self.data.db)
        residue_groups = group_service.get_all_residue_groups()
        
        # Criar opções para o dropdown
        type_options = [ft.dropdown.Option("", "Selecione um tipo")]
        for group in residue_groups:
            type_options.append(ft.dropdown.Option(group["name"], group["name"]))
        
        # Adicionar opção para criar novo tipo
        type_options.append(ft.dropdown.Option("__new__", "Adicionar novo tipo..."))
        
        name_field = ft.TextField(
            label="Nome do Resíduo",
            value=self.residue["name"],
            border_radius=8,
        )
        
        # Dropdown para tipo de resíduo
        type_dropdown = ft.Dropdown(
            label="Tipo de Resíduo",
            options=type_options,
            value=self.residue["type"],
            border_radius=8,
        )
        
        # Campo para novo tipo (inicialmente oculto)
        new_type_field = ft.TextField(
            label="Novo Tipo de Resíduo",
            value="",
            border_radius=8,
            visible=False,
        )
        
        # Função para lidar com a mudança no dropdown de tipo
        def on_type_change(e):
            selected_value = e.control.value
            
            # Se selecionar "Adicionar novo tipo...", mostrar campo de novo tipo
            if selected_value == "__new__":
                new_type_field.visible = True
            else:
                new_type_field.visible = False
            
            # Atualizar a página
            self.navigation.page.update()
        
        # Atribuir a função ao dropdown
        type_dropdown.on_change = on_type_change
        
        quantity_field = ft.TextField(
            label="Quantidade",
            value=str(self.residue["quantity"]),
            keyboard_type=ft.KeyboardType.NUMBER,
            border_radius=8,
        )
        
        destination_field = ft.TextField(
            label="Destino",
            value=self.residue.get("destination", ""),
            border_radius=8,
        )
        
        def update_residue(_):
            if not all([
                name_field.value, 
                (type_dropdown.value and type_dropdown.value != "__new__") or (type_dropdown.value == "__new__" and new_type_field.value), 
                quantity_field.value
            ]):
                self.navigation.show_snack_bar(
                    "Preencha todos os campos obrigatórios",
                    ft.colors.RED_500
                )
                return
            
            # Se o tipo não estiver preenchido, usar o grupo selecionado
            residue_type = type_dropdown.value
            if residue_type == "__new__" and new_type_field.value:
                residue_type = new_type_field.value
            
            updated_residue = {
                "id": self.residue["id"],
                "name": name_field.value,
                "type": residue_type,
                "quantity": int(quantity_field.value),
                "entryDate": self.residue["entryDate"],
                "destination": destination_field.value,
                "exitDate": self.residue.get("exitDate", ""),
                "notes": self.residue.get("notes", "")
            }
            
            self.data.residue_service.update_residue(self.residue["id"], updated_residue)
            self.data.refresh_data()
            
            self.navigation.show_snack_bar("Resíduo atualizado com sucesso!")
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
                                ft.Text("Editar Resíduo", size=20, weight="bold"),
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
                                type_dropdown,
                                new_type_field,
                                quantity_field,
                                destination_field,
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
                                    on_click=update_residue,
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
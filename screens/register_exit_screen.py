import flet as ft
from datetime import datetime

class RegisterExitScreen:
    
    def __init__(self, data, navigation, item, item_type):
        self.data = data
        self.navigation = navigation
        
        # Garantir que estamos usando uma cópia do item
        import copy
        self.item = copy.deepcopy(item) if item else {}
        
        # Imprimir informações para depuração
        print(f"RegisterExitScreen inicializada com: {self.item.get('name')}, ID: {self.item.get('id')}, Tipo: {item_type}")
        
        self.item_type = item_type  # "product" ou "residue"
        
        # Definir cores e textos com base no tipo
        if self.item_type == "product":
            self.primary_color = "#4A6FFF"  # Azul para produtos
            self.title = f"Registrar Saída: {self.item.get('name')}"  # Incluir nome do produto no título
            self.icon = ft.icons.INVENTORY_2_ROUNDED
            self.quantity_label = "Estoque atual"
            self.reason_label = "Motivo da Saída"
        else:  # residue
            self.primary_color = "#6C5CE7"  # Roxo para resíduos
            self.title = f"Registrar Saída: {self.item.get('name')}"  # Incluir nome do resíduo no título
            self.icon = ft.icons.DELETE_OUTLINE
            self.quantity_label = "Quantidade atual"
            self.reason_label = "Destino"
    
    def build(self):
        # Verificar se temos um item válido
        if not self.item or not self.item.get("id"):
            print(f"ERRO: Item inválido na tela RegisterExitScreen: {self.item}")
            return ft.Container(
                content=ft.Column([
                    ft.Text("Erro: Item não encontrado", color="#FF6B6B", size=16),
                    ft.ElevatedButton("Voltar", on_click=lambda _: self.navigation.go_back())
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
                alignment=ft.alignment.center,
                expand=True
            )
        
        # Imprimir informações do item para depuração
        print(f"RegisterExitScreen.build: Renderizando tela para {self.item.get('name')}, ID: {self.item.get('id')}")
        # Cores modernas
        bg_color = "#F8F9FD"  # Fundo claro
        card_bg = "#FFFFFF"  # Branco para cards
        
        # Obter informações do item
        
        item_name = self.item.get("name", "Sem nome")
        item_quantity = self.item.get("quantity", "0")
        
        # Campos do formulário
        quantity_field = ft.TextField(
            label="Quantidade",
            keyboard_type=ft.KeyboardType.NUMBER,
            border_radius=8,
            value="1",
            filled=True,
            prefix_icon=ft.icons.NUMBERS,
            hint_text="Informe a quantidade",
            helper_text="Quantidade a ser retirada"
        )
        
        # Campo de tipo de saída (apenas para produtos)
        exit_type_dropdown = ft.Dropdown(
            label="Tipo de Saída",
            border_radius=8,
            filled=True,
            prefix_icon=ft.icons.CATEGORY,
            options=[
                ft.dropdown.Option("venda", "Venda"),
                ft.dropdown.Option("descarte", "Descarte"),
                ft.dropdown.Option("uso_semanal", "Uso Semanal (Atualiza o gráfico de uso)"),
            ],
            value="venda",  # Valor padrão
            visible=self.item_type == "product"
        )

        # Se o produto tiver um tipo de saída pré-selecionado, usar esse valor
        if self.item_type == "product" and "pre_selected_exit_type" in self.item:
            exit_type_dropdown.value = self.item["pre_selected_exit_type"]
            
            # Adicionar uma dica se o tipo for "uso_semanal"
            if self.item["pre_selected_exit_type"] == "uso_semanal":
                hint_text = ft.Text(
                    "Esta saída atualizará o gráfico de uso semanal",
                    color="#4A6FFF",
                    size=12,
                    italic=True
                )
        
        # Campo de motivo/destino
        reason_field = ft.TextField(
            label=self.reason_label,
            border_radius=8,
            multiline=True,
            min_lines=2,
            max_lines=4,
            filled=True,
            prefix_icon=ft.icons.DESCRIPTION if self.item_type == "product" else ft.icons.LOCATION_ON,
            hint_text=f"Informe o {self.reason_label.lower()}"
        )
        
        # Campo de observações (apenas para resíduos)
        notes_field = ft.TextField(
            label="Observações",
            border_radius=8,
            multiline=True,
            min_lines=2,
            max_lines=4,
            filled=True,
            prefix_icon=ft.icons.NOTES,
            hint_text="Observações adicionais (opcional)",
            visible=self.item_type == "residue"
        )
        
        # Texto de erro
        error_text = ft.Text(
            "",
            color="#FF6B6B",
            visible=False,
        )
        
        # Função para registrar a saída
        def register_exit(_):
            try:
                quantity = int(quantity_field.value)
                reason = reason_field.value
                
                if quantity <= 0:
                    error_text.value = "A quantidade deve ser maior que zero"
                    error_text.visible = True
                    self.navigation.page.update()
                    return
                
                if not reason:
                    error_text.value = f"Informe o {self.reason_label.lower()}"
                    error_text.visible = True
                    self.navigation.page.update()
                    return
                
                # Registrar saída com base no tipo
                if self.item_type == "product":
                    # Obter o tipo de saída selecionado
                    exit_type = exit_type_dropdown.value
                    
                    print(f"Registrando saída de produto: {self.item.get('name')}, ID: {self.item.get('id')}, Quantidade: {quantity}, Tipo: {exit_type}")
                    
                    # Verificar se o produto tem um ID válido
                    product_id = self.item.get("id")
                    if not product_id:
                        error_text.value = "ID do produto inválido"
                        error_text.visible = True
                        self.navigation.page.update()
                        return
                    
                    # Registrar saída de produto com o tipo selecionado
                    success, message = self.data.product_service.register_product_exit(
                        product_id, quantity, reason, exit_type
                    )
                    
                    print(f"Resultado do registro de saída: {success}, Mensagem: {message}")
                else:
                    # Registrar saída de resíduo
                    notes = notes_field.value
                    success, message = self.data.residue_service.register_residue_exit(
                        self.item["id"], quantity, reason, notes
                    )
                
                if success:
                    # Atualizar dados
                    self.data.refresh_data()
                    
                    # Mostrar mensagem de sucesso
                    self.navigation.show_snack_bar(message, "#2ED573")
                    
                    # Atualizar a tela de uso semanal se o tipo de saída for "uso_semanal"
                    if self.item_type == "product" and exit_type == "uso_semanal":
                        # Verificar se a tela de uso semanal está aberta
                        if hasattr(self.navigation, "current_screen") and self.navigation.current_screen == "weekly_usage":
                            # Atualizar a tela de uso semanal
                            self.navigation.refresh_weekly_usage()
                    
                    # Voltar para a tela anterior
                    self.navigation.go_back()
                
                else:
                    self.navigation.show_snack_bar(message, "#FF6B6B")
                    error_text.value = message
                    error_text.visible = True
                    self.navigation.page.update()
                
            except ValueError:
                error_text.value = "Quantidade inválida. Digite um número inteiro."
                error_text.visible = True
                self.navigation.page.update()
            except Exception as e:
                error_text.value = f"Erro: {str(e)}"
                error_text.visible = True
                self.navigation.page.update()
                print(f"Erro ao registrar saída: {e}")
                import traceback
                traceback.print_exc()
        
        # Layout principal
        return ft.Container(
            content=ft.Column([
                # Barra superior com título e botão de voltar
                ft.Container(
                    content=ft.Row([
                        ft.IconButton(
                            icon=ft.icons.ARROW_BACK,
                            icon_color="#505050",
                            on_click=lambda _: self.navigation.go_back()
                        ),
                        ft.Text(
                            self.title,
                            size=20,
                            weight="bold",
                            color="#505050"
                        ),
                    ], alignment=ft.MainAxisAlignment.START, spacing=10),
                    padding=10,
                    bgcolor=card_bg,
                    shadow=ft.BoxShadow(
                        spread_radius=0.1,
                        blur_radius=4,
                        color=ft.colors.with_opacity(0.08, "#000000")
                    ),
                ),
                
                # Conteúdo principal com scroll
                ft.Container(
                    content=ft.Column([
                        # Informações do item
                        ft.Container(
                            content=ft.Column([
                                ft.Text(
                                    item_name,
                                    size=18,
                                    weight="bold",
                                    color="#303030"
                                ),
                                ft.Container(
                                    content=ft.Row([
                                        ft.Icon(self.icon, color=self.primary_color, size=20),
                                        ft.Text(
                                            f"{self.quantity_label}: {item_quantity} unidades", 
                                            weight="w500",
                                            color="#505050"
                                        ),
                                    ], spacing=10),
                                    padding=10,
                                    border_radius=8,
                                    bgcolor=ft.colors.with_opacity(0.05, self.primary_color),
                                    margin=ft.margin.only(top=10, bottom=20)
                                ),
                            ]),
                            padding=20,
                            bgcolor=card_bg,
                            border_radius=12,
                            shadow=ft.BoxShadow(
                                spread_radius=0.1,
                                blur_radius=4,
                                color=ft.colors.with_opacity(0.08, "#000000")
                            ),
                            margin=ft.margin.only(bottom=20)
                        ),
                        
                        # Formulário de saída
                        ft.Container(
                            content=ft.Column([
                                ft.Text(
                                    "Informações da Saída",
                                    size=16,
                                    weight="bold",
                                    color="#303030"
                                ),
                                quantity_field,
                                exit_type_dropdown,  # Novo campo para tipo de saída
                                reason_field,
                                notes_field,
                                error_text,
                                
                                # Botões de ação
                                ft.Row([
                                    ft.OutlinedButton(
                                        "Cancelar",
                                        style=ft.ButtonStyle(
                                            color="#909090",
                                            shape=ft.RoundedRectangleBorder(radius=8)
                                        ),
                                        on_click=lambda _: self.navigation.go_back()
                                    ),
                                    ft.FilledButton(
                                        "Confirmar Saída",
                                        style=ft.ButtonStyle(
                                            bgcolor=self.primary_color,
                                            color="#FFFFFF",
                                            shape=ft.RoundedRectangleBorder(radius=8)
                                        ),
                                        on_click=register_exit
                                    ),
                                ], alignment=ft.MainAxisAlignment.END, spacing=10),
                            ], spacing=20),
                            padding=20,
                            bgcolor=card_bg,
                            border_radius=12,
                            shadow=ft.BoxShadow(
                                spread_radius=0.1,
                                blur_radius=4,
                                color=ft.colors.with_opacity(0.08, "#000000")
                            ),
                        ),
                    ], spacing=0, scroll=ft.ScrollMode.AUTO),
                    padding=20,
                    expand=True,
                ),
            ]),
            bgcolor=bg_color,
            expand=True,
        )
    
    def go_to_register_exit(self, item, item_type):
        """Navega para a tela de registro de saída"""
        # Criar uma cópia profunda do item para evitar referências compartilhadas
        import copy
        item_copy = copy.deepcopy(item) if item else {}
        
        print(f"Navegando para registro de saída: {item_copy.get('name')}, ID: {item_copy.get('id')}, Tipo: {item_type}")
        
        # Criar a tela com a cópia do item
        screen = RegisterExitScreen(self.data, self, item_copy, item_type)
        
        # Navegar para a tela
        self.navigate_to(screen)
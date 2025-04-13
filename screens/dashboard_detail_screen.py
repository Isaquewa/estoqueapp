import flet as ft
from datetime import datetime

class DashboardDetailScreen:
    def __init__(self, data, navigation):
        self.data = data
        self.navigation = navigation
        self.detail_type = None
        self.items = []
        self.title = "Detalhes"
    
    def set_data(self, detail_type, items, title=None):
        """Define os dados a serem exibidos"""
        try:
            print(f"set_data: tipo={detail_type}, título={title}")
            
            self.detail_type = detail_type
            self.title = title or self._get_default_title()
            
            # Inicializar items como lista vazia para evitar erros
            self.items = []
            
            # Se items for None, manter lista vazia
            if items is None:
                print("set_data: items é None, mantendo lista vazia")
                return
            
            # Se for um grupo de produtos, buscar os produtos do grupo
            if detail_type == "productGroup" and isinstance(items, dict) and "id" in items:
                group_id = items["id"]
                print(f"set_data: buscando produtos do grupo {group_id}")
                
                try:
                    products = self.data.group_service.get_products_in_group(group_id)
                    
                    # Verificar se a lista de produtos é válida
                    if isinstance(products, list):
                        self.items = products
                        print(f"set_data: {len(products)} produtos encontrados no grupo {group_id}")
                    else:
                        print(f"set_data: formato inválido retornado por get_products_in_group: {type(products)}")
                except Exception as e:
                    print(f"set_data: erro ao buscar produtos do grupo {group_id}: {e}")
                    import traceback
                    traceback.print_exc()
            
            # Se for um grupo de resíduos, buscar os resíduos do grupo
            elif detail_type == "residueGroup" and isinstance(items, dict) and "id" in items:
                group_id = items["id"]
                print(f"set_data: buscando resíduos do grupo {group_id}")
                
                try:
                    residues = self.data.group_service.get_residues_in_group(group_id)
                    
                    # Verificar se a lista de resíduos é válida
                    if isinstance(residues, list):
                        self.items = residues
                        print(f"set_data: {len(residues)} resíduos encontrados no grupo {group_id}")
                    else:
                        print(f"set_data: formato inválido retornado por get_residues_in_group: {type(residues)}")
                except Exception as e:
                    print(f"set_data: erro ao buscar resíduos do grupo {group_id}: {e}")
                    import traceback
                    traceback.print_exc()
            
            # Para outros tipos, usar items diretamente
            elif isinstance(items, list):
                self.items = items
                print(f"set_data: usando lista de {len(items)} itens diretamente")
            else:
                print(f"set_data: formato de items não reconhecido: {type(items)}")
                # Converter para lista se não for uma lista
                self.items = [items] if items else []
        
        except Exception as e:
            print(f"ERRO em set_data: {e}")
            import traceback
            traceback.print_exc()
            self.items = []
    
    def _get_default_title(self):
        """Retorna um título padrão com base no tipo de detalhe"""
        titles = {
            "lowStock": "Produtos com Estoque Baixo",
            "expiring": "Produtos Próximos ao Vencimento",
            "recentResidues": "Resíduos Recentes",
            "allStock": "Todos os Produtos",
            "allResidues": "Todos os Resíduos",
            "productGroup": "Grupo de Produtos",
            "residueGroup": "Grupo de Resíduos",
            "alerts": "Alertas Ativos"
        }
        return titles.get(self.detail_type, "Detalhes")
    
    def build(self):
        try:
            if not self.detail_type or not self.items:
                return ft.Container(
                    content=ft.Text("Nenhum item para exibir"),
                    alignment=ft.alignment.center,
                    padding=20
                )
            
            print(f"Construindo tela de detalhes: tipo={self.detail_type}, itens={len(self.items)}")
            
            # Cabeçalho
            header = ft.Container(
                content=ft.Row(
                    controls=[
                        ft.IconButton(
                            icon=ft.icons.ARROW_BACK,
                            on_click=lambda _: self.navigation.go_back()
                        ),
                        ft.Text(self.title, size=20, weight="bold"),
                        ft.Text(f"{len(self.items)} itens", size=14, color=ft.colors.GREY_700),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    spacing=10,
                ),
                padding=10,
            )
            
            # Determinar se são produtos ou resíduos
            is_product = self.detail_type in ["lowStock", "expiring", "allStock", "productGroup", "alerts"]
            
            # Criar lista de itens
            items_list_items = []
            
            if self.items:
                for item in self.items:
                    try:
                        # Verificar se o item é um dicionário antes de processá-lo
                        if isinstance(item, dict):
                            if is_product:
                                items_list_items.append(self._build_product_item(item))
                            else:
                                items_list_items.append(self._build_residue_item(item))
                        else:
                            # Se não for um dicionário, criar um item de erro
                            items_list_items.append(
                                ft.Container(
                                    content=ft.Text(f"Erro: item inválido ({type(item).__name__})", color=ft.colors.RED),
                                    padding=10,
                                    border=ft.border.all(1, ft.colors.RED_200),
                                    border_radius=8,
                                    margin=5
                                )
                            )
                    except Exception as e:
                        print(f"Erro ao construir item: {e}")
                        items_list_items.append(
                            ft.Container(
                                content=ft.Text(f"Erro ao construir item: {str(e)}", color=ft.colors.RED),
                                padding=10,
                                border=ft.border.all(1, ft.colors.RED_200),
                                border_radius=8,
                                margin=5
                            )
                        )
            
            # Se não houver itens, mostrar mensagem
            if not items_list_items:
                items_list_items.append(
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Icon(
                                    ft.icons.INVENTORY_2_OUTLINED if is_product else ft.icons.DELETE_OUTLINE, 
                                    size=50, 
                                    color=ft.colors.GREY_400
                                ),
                                ft.Text(
                                    "Nenhum item encontrado",
                                    size=16,
                                    color=ft.colors.GREY_500
                                ),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=10,
                        ),
                        alignment=ft.alignment.center,
                        padding=20,
                        expand=True,
                    )
                )
            
            # Criar ListView com os itens
            items_list = ft.ListView(
                controls=items_list_items,
                spacing=10,
                padding=10,
                expand=True,
            )
            
            # Layout principal
            return ft.Container(
                content=ft.Column(
                    controls=[
                        header,
                        items_list,
                    ],
                    spacing=0,
                    expand=True,
                ),
                expand=True,
            )
        except Exception as e:
            import traceback
            print(f"ERRO ao construir tela de detalhes: {e}")
            traceback.print_exc()
            
            # Retornar um container de erro em vez de None
            return ft.Container(
                content=ft.Column([
                    ft.Text("Erro ao carregar detalhes", size=16, color=ft.colors.RED_500, weight="bold"),
                    ft.Text(f"Detalhes: {str(e)}", size=12, color=ft.colors.GREY_700),
                    ft.ElevatedButton("Voltar", on_click=lambda _: self.navigation.go_back())
                ], spacing=10, alignment=ft.MainAxisAlignment.CENTER),
                alignment=ft.alignment.center,
                padding=20
        )
    
    def _build_product_item(self, product):
        """Constrói um item de produto para a lista"""
        # Verificar se product é um dicionário
        if not isinstance(product, dict):
            return ft.Container(
                content=ft.Text(f"Erro: item inválido ({type(product).__name__})", color=ft.colors.RED),
                padding=10,
                border=ft.border.all(1, ft.colors.RED_200),
                border_radius=8,
                margin=5
            )
        
        # Verificar se o produto está com estoque baixo
        is_low_stock = product in self.data.low_stock_products
        
        # Verificar se o produto está próximo ao vencimento
        is_expiring = product in self.data.expiring_products
        
        # Definir cor de fundo com base no status
        bg_color = ft.colors.WHITE
        if is_low_stock and is_expiring:
            bg_color = ft.colors.with_opacity(0.2, ft.colors.RED_100)
        elif is_low_stock:
            bg_color = ft.colors.with_opacity(0.2, ft.colors.RED_50)
        elif is_expiring:
            bg_color = ft.colors.with_opacity(0.2, ft.colors.ORANGE_50)
        
        # Criar item de produto
        return ft.Container(
            content=ft.Row(
                controls=[
                    # Informações do produto
                    ft.Column(
                        controls=[
                            ft.Text(product.get("name", "Sem nome"), size=16, weight="w500"),
                            ft.Text(
                                f"Quantidade: {product.get('quantity', 0)} • Lote: {product.get('lot', 'N/A')}",
                                size=12,
                                color=ft.colors.GREY_700,
                            ),
                            ft.Text(
                                f"Validade: {product.get('expiry', 'N/A')} • Entrada: {product.get('entryDate', 'N/A')}",
                                size=12,
                                color=ft.colors.GREY_700,
                            ),
                        ],
                        spacing=5,
                        expand=True,
                    ),
                    # Botões de ação
                    ft.Row(
                        controls=[
                            ft.IconButton(
                                icon=ft.icons.EXIT_TO_APP,
                                icon_color=ft.colors.ORANGE_500,
                                icon_size=20,
                                tooltip="Registrar Saída",
                                on_click=lambda _, p=product: self._register_product_exit(p),
                            ),
                            ft.IconButton(
                                icon=ft.icons.TRENDING_UP,
                                icon_color=ft.colors.GREEN_500,
                                icon_size=20,
                                tooltip="Uso Semanal",
                                on_click=lambda _, p=product: self.navigation.go_to_weekly_usage(p),
                            ),
                            ft.IconButton(
                                icon=ft.icons.EDIT_OUTLINED,
                                icon_color=ft.colors.BLUE_500,
                                icon_size=20,
                                tooltip="Editar",
                                on_click=lambda _, p=product: self.navigation.go_to_edit_product(p),
                            ),
                            ft.IconButton(
                                icon=ft.icons.DELETE_OUTLINE,
                                icon_color=ft.colors.RED_500,
                                icon_size=20,
                                tooltip="Excluir",
                                on_click=lambda _, p=product: self._confirm_delete_product(p),
                            ),
                        ],
                        spacing=0,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=10,
            border_radius=8,
            bgcolor=bg_color,
            border=ft.border.all(1, ft.colors.GREY_300),
            on_click=lambda _, p=product: self.navigation.select_product(p),
        )
    
    def _build_residue_item(self, residue):
        """Constrói um item de resíduo para a lista"""
        # Formatar data
        entry_date = residue.get("entryDate", "N/A")
        exit_date = residue.get("exitDate", "")
        
        # Criar item de resíduo
        return ft.Container(
            content=ft.Row(
                controls=[
                    # Informações do resíduo
                    ft.Column(
                        controls=[
                            ft.Text(residue["name"], size=16, weight="w500"),
                            ft.Text(
                                f"Quantidade: {residue['quantity']} • Tipo: {residue.get('type', 'N/A')}",
                                size=12,
                                color=ft.colors.GREY_700,
                            ),
                            ft.Text(
                                f"Entrada: {entry_date} • Saída: {exit_date if exit_date else 'Pendente'}",
                                size=12,
                                color=ft.colors.GREY_700,
                            ),
                        ],
                        spacing=5,
                        expand=True,
                    ),
                    # Botões de ação
                    ft.Row(
                        controls=[
                            ft.IconButton(
                                icon=ft.icons.EXIT_TO_APP,
                                icon_color=ft.colors.ORANGE_500,
                                icon_size=20,
                                tooltip="Registrar Saída",
                                on_click=lambda _, r=residue: self._register_residue_exit(r),
                            ),
                            ft.IconButton(
                                icon=ft.icons.EDIT_OUTLINED,
                                icon_color=ft.colors.BLUE_500,
                                icon_size=20,
                                tooltip="Editar",
                                on_click=lambda _, r=residue: self.navigation.go_to_edit_residue(r),
                            ),
                            ft.IconButton(
                                icon=ft.icons.DELETE_OUTLINE,
                                icon_color=ft.colors.RED_500,
                                icon_size=20,
                                tooltip="Excluir",
                                on_click=lambda _, r=residue: self._confirm_delete_residue(r),
                            ),
                        ],
                        spacing=0,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=10,
            border_radius=8,
            bgcolor=ft.colors.WHITE,
            border=ft.border.all(1, ft.colors.GREY_300),
            on_click=lambda _, r=residue: self.navigation.select_residue(r),
        )
    
    def _register_product_exit(self, product):
        """Abre diálogo para registrar saída de produto"""
        def close_dialog():
            self.navigation.page.dialog.open = False
            self.navigation.page.update()
        
        def confirm_exit(_):
            try:
                quantity = int(quantity_field.value)
                reason = reason_field.value
                
                if quantity <= 0:
                    error_text.value = "A quantidade deve ser maior que zero"
                    error_text.visible = True
                    self.navigation.page.update()
                    return
                
                if not reason:
                    error_text.value = "Informe o motivo da saída"
                    error_text.visible = True
                    self.navigation.page.update()
                    return
                
                # Registrar saída
                success, message = self.data.product_service.register_product_exit(
                    product["id"], quantity, reason
                )
                
                close_dialog()
                
                if success:
                    self.navigation.show_snack_bar(message, ft.colors.GREEN_500)
                    # Atualizar dados
                    self.data.refresh_data()
                    self.navigation.update_view()
                else:
                    self.navigation.show_snack_bar(message, ft.colors.RED_500)
                
            except ValueError:
                error_text.value = "Quantidade inválida. Digite um número inteiro."
                error_text.visible = True
                self.navigation.page.update()
        
        # Campos do diálogo
        quantity_field = ft.TextField(
            label="Quantidade",
            keyboard_type=ft.KeyboardType.NUMBER,
            border_radius=8,
            value="1",
        )
        
        reason_field = ft.TextField(
            label="Motivo da Saída",
            border_radius=8,
        )
        
        error_text = ft.Text(
            "",
            color=ft.colors.RED_500,
            visible=False,
        )
        
        # Criar diálogo
        dialog = ft.AlertDialog(
            title=ft.Text(f"Registrar Saída - {product['name']}"),
            content=ft.Column(
                controls=[
                    ft.Text(f"Quantidade atual: {product['quantity']} unidades"),
                    quantity_field,
                    reason_field,
                    error_text,
                ],
                spacing=10,
                width=400,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: close_dialog()),
                ft.ElevatedButton(
                    "Confirmar",
                    on_click=confirm_exit,
                    style=ft.ButtonStyle(
                        color=ft.colors.WHITE,
                        bgcolor=ft.colors.BLUE_500,
                    ),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        # Mostrar diálogo
        self.navigation.page.dialog = dialog
        self.navigation.page.dialog.open = True
        self.navigation.page.update()
    
    def _register_residue_exit(self, residue):
        """Abre diálogo para registrar saída de resíduo"""
        def close_dialog():
            self.navigation.page.dialog.open = False
            self.navigation.page.update()
        
        def confirm_exit(_):
            try:
                quantity = int(quantity_field.value)
                destination = destination_field.value
                notes = notes_field.value
                
                if quantity <= 0:
                    error_text.value = "A quantidade deve ser maior que zero"
                    error_text.visible = True
                    self.navigation.page.update()
                    return
                
                if not destination:
                    error_text.value = "Informe o destino do resíduo"
                    error_text.visible = True
                    self.navigation.page.update()
                    return
                
                # Registrar saída
                success, message = self.data.residue_service.register_residue_exit(
                    residue["id"], quantity, destination, notes
                )
                
                close_dialog()
                
                if success:
                    self.navigation.show_snack_bar(message, ft.colors.GREEN_500)
                    # Atualizar dados
                    self.data.refresh_data()
                    self.navigation.update_view()
                else:
                    self.navigation.show_snack_bar(message, ft.colors.RED_500)
                
            except ValueError:
                error_text.value = "Quantidade inválida. Digite um número inteiro."
                error_text.visible = True
                self.navigation.page.update()
        
        # Campos do diálogo
        quantity_field = ft.TextField(
            label="Quantidade",
            keyboard_type=ft.KeyboardType.NUMBER,
            border_radius=8,
            value="1",
        )
        
        destination_field = ft.TextField(
            label="Destino",
            border_radius=8,
        )
        
        notes_field = ft.TextField(
            label="Observações",
            border_radius=8,
            multiline=True,
            min_lines=2,
            max_lines=4,
        )
        
        error_text = ft.Text(
            "",
            color=ft.colors.RED_500,
            visible=False,
        )
        
        # Criar diálogo
        dialog = ft.AlertDialog(
            title=ft.Text(f"Registrar Saída - {residue['name']}"),
            content=ft.Column(
                controls=[
                    ft.Text(f"Quantidade atual: {residue['quantity']} unidades"),
                    quantity_field,
                    destination_field,
                    notes_field,
                    error_text,
                ],
                spacing=10,
                width=400,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: close_dialog()),
                ft.ElevatedButton(
                    "Confirmar",
                    on_click=confirm_exit,
                    style=ft.ButtonStyle(
                        color=ft.colors.WHITE,
                        bgcolor=ft.colors.BLUE_500,
                    ),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        # Mostrar diálogo
        self.navigation.page.dialog = dialog
        self.navigation.page.dialog.open = True
        self.navigation.page.update()
    
    def _confirm_delete_product(self, product):
        """Navega para a tela de confirmação de exclusão de produto"""
        self.navigation.go_to_confirm_delete("product", product)
    
    def _confirm_delete_residue(self, residue):
        """Navega para a tela de confirmação de exclusão de resíduo"""
        self.navigation.go_to_confirm_delete("residue", residue)
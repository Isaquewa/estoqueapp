import flet as ft

class StockScreen:
    def __init__(self, data, navigation):
        self.data = data
        self.navigation = navigation
        self.search_text = ""
        self.view_mode = "groups"  # Padrão: visualização por grupos
    
    def build(self):
        # Cores modernas
        primary_color = "#4A6FFF"  # Azul moderno
        secondary_color = "#6C5CE7"  # Roxo moderno
        accent_color = "#00D2D3"  # Turquesa
        warning_color = "#FFA502"  # Laranja
        danger_color = "#FF6B6B"  # Vermelho suave
        success_color = "#2ED573"  # Verde
        bg_color = "#F8F9FD"  # Fundo claro
        card_bg = "#FFFFFF"  # Branco para cards
        
        # Certifique-se de que os dados estão carregados
        if not hasattr(self.data, 'stock_products'):
            return ft.Container(
                content=ft.Text("Carregando dados de estoque..."),
                alignment=ft.alignment.center,
                padding=20
            )
        
        # Barra de pesquisa e botão de adicionar
        search_field = ft.TextField(
            hint_text="Pesquisar produtos ou grupos...",
            prefix_icon=ft.icons.SEARCH,
            on_change=self._on_search_change,
            border_radius=20,
            filled=True,
            bgcolor=card_bg,
            expand=True,
            border_color=ft.colors.with_opacity(0.1, primary_color),
            height=48
        )
        
        add_button = ft.IconButton(
            icon=ft.icons.ADD_CIRCLE,
            icon_color=primary_color,
            icon_size=30,
            tooltip="Adicionar Produto",
            on_click=lambda _: self.navigation.go_to_add_product()
        )
        
        # Toggle para alternar entre visualização de grupos e lista completa
        view_toggle = ft.SegmentedButton(
            selected={0} if self.view_mode == "groups" else {1},
            segments=[
                ft.Segment(value=0, label=ft.Text("Grupos"), icon=ft.Icon(ft.icons.FOLDER)),
                ft.Segment(value=1, label=ft.Text("Lista Completa"), icon=ft.Icon(ft.icons.LIST)),
            ],
            on_change=lambda e: self._toggle_view(next(iter(e.control.selected)))
        )
        
        # Estatísticas rápidas em formato de cards modernos
        stats_row = ft.Container(
            content=ft.ResponsiveRow([
                ft.Column([
                    self._build_stat_card(
                        "Total de Produtos", 
                        len(self.data.stock_products), 
                        ft.icons.INVENTORY_2_ROUNDED, 
                        primary_color
                    )
                ], col={"xs": 4, "sm": 4, "md": 4, "lg": 4, "xl": 4}),
                ft.Column([
                    self._build_stat_card(
                        "Estoque Baixo", 
                        len(self.data.low_stock_products), 
                        ft.icons.WARNING_ROUNDED, 
                        danger_color
                    )
                ], col={"xs": 4, "sm": 4, "md": 4, "lg": 4, "xl": 4}),
                ft.Column([
                    self._build_stat_card(
                        "Próx. Vencimento", 
                        len(self.data.expiring_products), 
                        ft.icons.CALENDAR_TODAY_ROUNDED, 
                        warning_color
                    )
                ], col={"xs": 4, "sm": 4, "md": 4, "lg": 4, "xl": 4}),
            ]),
            padding=10,
        )
        
        # Conteúdo principal (grupos ou lista completa)
        if self.view_mode == "groups":
            main_content = self._build_groups_view(primary_color, card_bg)
        else:
            main_content = self._build_full_list_view(primary_color, card_bg, warning_color, danger_color)
        
        # Layout principal com scroll
        return ft.Container(
            content=ft.Column(
                controls=[
                    # Barra de pesquisa e botão de adicionar (fixos no topo)
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                search_field,
                                add_button,
                            ],
                            spacing=10,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        padding=ft.padding.only(left=10, right=10, top=10, bottom=5),
                    ),
                    # Toggle de visualização (fixo no topo)
                    ft.Container(
                        content=view_toggle,
                        alignment=ft.alignment.center,
                        padding=ft.padding.only(bottom=5),
                    ),
                    # Conteúdo rolável (estatísticas e lista principal)
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                # Estatísticas rápidas
                                ft.Container(
                                    content=stats_row,
                                    padding=10,
                                    bgcolor=card_bg,
                                    border_radius=12,
                                    shadow=ft.BoxShadow(
                                        spread_radius=0.1,
                                        blur_radius=4,
                                        color=ft.colors.with_opacity(0.08, "#000000")
                                    ),
                                    margin=ft.margin.only(left=10, right=10, top=5, bottom=10)
                                ),
                                # Lista de grupos ou produtos
                                main_content,
                            ],
                            spacing=0,
                            scroll=ft.ScrollMode.AUTO,  # Adiciona scroll automático
                        ),
                        expand=True,  # Permite que este container ocupe todo o espaço disponível
                    ),
                ],
                spacing=0,
                expand=True,
            ),
            bgcolor=bg_color,
            expand=True,
        )
    
    def _toggle_view(self, selected):
        """Alterna entre visualização por grupos e lista completa"""
        print(f"Toggle view chamado com valor: {selected}")  # Debug
        
        # Verificar o tipo de 'selected' e converter se necessário
        if isinstance(selected, set):
            selected = next(iter(selected))
        
        # Converter para inteiro se for string
        if isinstance(selected, str):
            try:
                selected = int(selected)
            except ValueError:
                pass
        
        # Definir o modo de visualização com base no valor selecionado
        self.view_mode = "groups" if selected == 0 else "list"
        print(f"Modo de visualização alterado para: {self.view_mode}")  # Debug
        
        # Atualizar a interface
        self.navigation.update_view()
    
    def _build_groups_view(self, primary_color, card_bg):
        """Constrói a visualização por grupos com layout responsivo"""
        # Obter grupos de produtos
        from services.group_service import GroupService
        group_service = GroupService(self.data.firebase, self.data.db)
        groups = group_service.get_all_product_groups()
        
        # Filtrar grupos com base na pesquisa
        if self.search_text:
            search_lower = self.search_text.lower()
            groups = [
                group for group in groups
                if search_lower in group["name"].lower() or 
                   search_lower in group.get("description", "").lower()
            ]
        
        # Criar lista de grupos com layout responsivo
        if groups:
            groups_grid = ft.ResponsiveRow(
                controls=[
                    ft.Column([
                        self._build_group_item(group, primary_color, card_bg)
                    ], col={"xs": 12, "sm": 6, "md": 4, "lg": 4, "xl": 3})
                    for group in groups
                ],
                spacing=10,
                run_spacing=10
            )
            
            return ft.Container(
                content=groups_grid,
                padding=10,
                expand=True
            )
        else:
            return ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(ft.icons.FOLDER_OUTLINED, size=50, color="#CCCCCC"),
                        ft.Text("Nenhum grupo encontrado", size=16, color="#909090"),
                        ft.ElevatedButton(
                            "Criar Grupo",
                            icon=ft.icons.CREATE_NEW_FOLDER,
                            on_click=lambda _: self.navigation.go_to_add_group(),
                            style=ft.ButtonStyle(
                                bgcolor=primary_color,
                                color=card_bg
                            )
                        )
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=15,
                ),
                alignment=ft.alignment.center,
                padding=20,
                expand=True,
            )
    
    def _build_group_item(self, group, primary_color, card_bg):
        """Constrói um item de grupo para a lista com design moderno"""
        # Obter ícone e cor do grupo
        icon_name = getattr(ft.icons, group.get("icon", "FOLDER"))
        color_name = group.get("color", "blue").upper()
        color = getattr(ft.colors, f"{color_name}_500", primary_color)
        
        # Obter produtos do grupo usando GroupService
        from services.group_service import GroupService
        group_service = GroupService(self.data.firebase, self.data.db)
        group_id = group.get("id", "")
        group_products = group_service.get_products_in_group(group_id)
        
        # Calcular quantidade total
        total_quantity = 0
        for product in group_products:
            try:
                if 'quantity' in product and product['quantity'] is not None:
                    total_quantity += int(product['quantity'])
            except (ValueError, TypeError):
                print(f"Erro ao converter quantidade do produto {product.get('name')}: {product.get('quantity')}")
        
        # Número real de produtos no grupo
        actual_product_count = len(group_products)
        
        # Calcular produtos com estoque baixo
        low_stock_count = 0
        for product in group_products:
            try:
                quantity = int(product.get('quantity', 0))
                min_stock = int(product.get('minStock', 0) or 0)
                if min_stock > 0 and quantity <= min_stock:
                    low_stock_count += 1
            except (ValueError, TypeError):
                pass
        
        # Para depuração
        print(f"Grupo: {group.get('name')}, ID: {group_id}, Produtos: {actual_product_count}, Total: {total_quantity}")
        
        return ft.Container(
            content=ft.Column([
                # Cabeçalho do card
                ft.Row([
                    ft.Container(
                        content=ft.Icon(icon_name, color="#FFFFFF", size=18),
                        padding=8,
                        border_radius=8,
                        bgcolor=color
                    ),
                    ft.Text(group["name"], size=16, weight="w600", color="#303030", expand=True),
                    # Botão de excluir
                    ft.IconButton(
                        icon=ft.icons.DELETE_OUTLINE,
                        icon_color="#FF6B6B",
                        icon_size=20,
                        tooltip="Excluir Grupo",
                        on_click=lambda _, g=group: self._confirm_delete_group(g),
                    ),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                # Estatísticas do grupo
                ft.Container(
                    content=ft.Row([
                        # Quantidade de produtos
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Produtos", size=11, color="#707070"),
                                ft.Text(f"{actual_product_count}", size=16, weight="bold", color=color),
                            ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            expand=True,
                            padding=8,
                            border_radius=6,
                            bgcolor=ft.colors.with_opacity(0.05, color)
                        ),
                        # Quantidade total
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Quantidade", size=11, color="#707070"),
                                ft.Text(f"{total_quantity}", size=16, weight="bold", color=color),
                            ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            expand=True,
                            padding=8,
                            border_radius=6,
                            bgcolor=ft.colors.with_opacity(0.05, color)
                        ),
                        # Estoque baixo
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Estoque Baixo", size=11, color="#707070"),
                                ft.Text(f"{low_stock_count}", size=16, weight="bold", 
                                       color="#FF6B6B" if low_stock_count > 0 else "#909090"),
                            ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            expand=True,
                            padding=8,
                            border_radius=6,
                            bgcolor="#FFF0F0" if low_stock_count > 0 else "#F5F5F5"
                        ),
                    ], spacing=8),
                    margin=ft.margin.only(top=10, bottom=10)
                ),
                
                # Botão para ver detalhes
                ft.Container(
                    content=ft.Row([
                        ft.Text("Ver detalhes", size=12, color=color, weight="w500"),
                        ft.Icon(ft.icons.ARROW_FORWARD, size=14, color=color)
                    ], spacing=4, alignment=ft.MainAxisAlignment.CENTER),
                    padding=ft.padding.only(top=8, bottom=8),
                    border_radius=6,
                    bgcolor=ft.colors.with_opacity(0.05, color),
                    alignment=ft.alignment.center,
                    ink=True
                )
            ], spacing=0),
            padding=15,
            border_radius=12,
            bgcolor=card_bg,
            border=ft.border.all(1, ft.colors.GREY_300),
            shadow=ft.BoxShadow(
                spread_radius=0.1,
                blur_radius=4,
                color=ft.colors.with_opacity(0.08, "#000000")
            ),
            on_click=lambda _, g=group: self.navigation.go_to_group_detail(g, True),
        )
    
    def _build_full_list_view(self, primary_color, card_bg, warning_color, danger_color):
        """Constrói a visualização de lista completa com layout responsivo"""
        # Filtrar produtos com base na pesquisa
        filtered_products = self._filter_products()
        
        # Criar lista de produtos com layout responsivo
        if filtered_products:
            products_grid = ft.ResponsiveRow(
                controls=[
                    ft.Column([
                        self._build_product_item(product, primary_color, card_bg, warning_color, danger_color)
                    ], col={"xs": 12, "sm": 6, "md": 4, "lg": 4, "xl": 3})
                    for product in filtered_products
                ],
                spacing=10,
                run_spacing=10
            )
            
            return ft.Container(
                content=products_grid,
                padding=10,
                expand=True
            )
        else:
            return ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(ft.icons.INVENTORY_2_OUTLINED, size=50, color="#CCCCCC"),
                        ft.Text("Nenhum produto encontrado", size=16, color="#909090"),
                        ft.ElevatedButton(
                            "Adicionar Produto",
                            icon=ft.icons.ADD_CIRCLE_OUTLINE,
                            on_click=lambda _: self.navigation.go_to_add_product(),
                            style=ft.ButtonStyle(
                                bgcolor=primary_color,
                                color=card_bg
                            )
                        )
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=15,
                ),
                alignment=ft.alignment.center,
                padding=20,
                expand=True,
            )
    
    def _build_stat_card(self, title, value, icon, color):
        """Cria um card de estatística moderno"""
        return ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Icon(icon, color="#FFFFFF", size=18),
                    padding=8,
                    border_radius=8,
                    bgcolor=color
                ),
                ft.Text(title, size=12, color="#707070", weight="w500"),
                ft.Text(str(value), size=20, weight="bold", color=color),
            ], spacing=5, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=15,
            border_radius=10,
            bgcolor="#FFFFFF",
            shadow=ft.BoxShadow(
                spread_radius=0.1,
                blur_radius=4,
                color=ft.colors.with_opacity(0.08, "#000000")
            ),
            expand=True,
            alignment=ft.alignment.center
        )
    
    def _filter_products(self):
        if not self.search_text:
            return self.data.stock_products
        
        search_lower = self.search_text.lower()
        return [
            product for product in self.data.stock_products
            if search_lower in product["name"].lower() or 
               search_lower in product.get("category", "").lower() or
               search_lower in product.get("location", "").lower() or
               search_lower in product.get("group_name", "").lower()
        ]
    
    def _on_search_change(self, e):
        self.search_text = e.control.value
        self.navigation.update_view()
    
    def _build_product_item(self, product, primary_color, card_bg, warning_color, danger_color):
        """Constrói um item de produto com design moderno"""
        # Verificar se o produto está com estoque baixo
        is_low_stock = product in self.data.low_stock_products
        
        # Verificar se o produto está próximo ao vencimento
        is_expiring = product in self.data.expiring_products
        
        # Obter informações do produto
        product_name = product.get("name", "Sem nome")
        product_quantity = product.get("quantity", "0")
        product_lot = product.get("lot", "N/A")
        product_expiry = product.get("expiry", "N/A")
        product_group = product.get("group_name", "Sem grupo")
        product_location = product.get("location", "N/A")
        
        # Calcular uso semanal total
        weekly_usage = product.get("weeklyUsage", [0] * 7)
        weekly_usage_total = 0
        
        # Garantir que weekly_usage seja uma lista
        if not isinstance(weekly_usage, list):
            weekly_usage = [0] * 7
        
        # Calcular o total
        for usage in weekly_usage:
            try:
                if isinstance(usage, str) and usage.isdigit():
                    weekly_usage_total += int(usage)
                elif isinstance(usage, (int, float)):
                    weekly_usage_total += usage
            except (ValueError, TypeError):
                continue
        
        # Calcular dias até o vencimento
        days_left = None
        if product_expiry != "N/A":
            from datetime import datetime
            try:
                expiry_date = datetime.strptime(product_expiry, "%d/%m/%Y")
                days_left = (expiry_date - datetime.now()).days
            except Exception:
                days_left = None
        
        # Definir cores e status baseados nas condições
        status_color = "#909090"  # Cinza padrão
        status_bg = "#F5F5F5"
        status_text = "Normal"
        
        if is_low_stock and is_expiring:
            status_color = "#FF6B6B"  # Vermelho
            status_bg = "#FFF0F0"
            status_text = "Crítico"
        elif is_low_stock:
            status_color = "#FF6B6B"  # Vermelho
            status_bg = "#FFF0F0"
            status_text = "Estoque Baixo"
        elif is_expiring:
            status_color = "#FFA502"  # Laranja
            status_bg = "#FFF8E1"
            status_text = "Próx. Vencimento"
        
        return ft.Container(
            content=ft.Column([
                # Cabeçalho com nome e status
                ft.Row([
                    ft.Column([
                        ft.Text(product_name, size=16, weight="w600", color="#303030"),
                        ft.Container(
                            content=ft.Text(status_text, size=10, weight="bold", color=status_color),
                            padding=ft.padding.only(left=6, right=6, top=2, bottom=2),
                            border_radius=4,
                            bgcolor=status_bg,
                        )
                    ], spacing=4, expand=True),
                    
                    # Menu de ações
                    ft.PopupMenuButton(
                        icon=ft.icons.MORE_VERT,
                        icon_color="#707070",
                        items=[
                            ft.PopupMenuItem(
                                text="Editar",
                                icon=ft.icons.EDIT_OUTLINED,
                                on_click=lambda _, p=product: self.navigation.go_to_edit_product(p)
                            ),
                            ft.PopupMenuItem(
                                text="Registrar Saída",
                                icon=ft.icons.EXIT_TO_APP,
                                on_click=lambda _, p=product: self._register_product_exit(p)
                            ),
                            ft.PopupMenuItem(
                                text="Uso Semanal",
                                icon=ft.icons.TRENDING_UP,
                                on_click=lambda _, p=product: self.navigation.go_to_weekly_usage(p)
                            ),
                            ft.PopupMenuItem(
                                text="Excluir",
                                icon=ft.icons.DELETE_OUTLINE,
                                on_click=lambda _, p=product: self._confirm_delete_product(p)
                            ),
                        ]
                    )
                ]),
                
                # Informações principais
                ft.Container(
                    content=ft.Row([
                        # Quantidade
                        ft.Container(
                            content=ft.Column([
                            ft.Text("Quantidade", size=11, color="#707070"),
                            ft.Text(f"{product_quantity}", size=16, weight="bold", 
                                   color="#FF6B6B" if is_low_stock else primary_color),
                        ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        expand=True,
                        padding=8,
                        border_radius=6,
                        bgcolor=ft.colors.with_opacity(0.05, "#FF6B6B" if is_low_stock else primary_color)
                    ),
                    # Lote
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Lote", size=11, color="#707070"),
                            ft.Text(f"{product_lot}", size=16, weight="w500", color="#505050"),
                        ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        expand=True,
                        padding=8,
                        border_radius=6,
                        bgcolor="#F5F5F5"
                    ),
                    # Validade
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Validade", size=11, color="#707070"),
                            ft.Row([
                                ft.Text(f"{product_expiry}", size=14, weight="w500", 
                                       color="#FF6B6B" if is_expiring else "#505050"),
                                ft.Container(
                                    content=ft.Text(f"{days_left}d", size=10, color="#FFFFFF"),
                                    padding=ft.padding.only(left=4, right=4, top=1, bottom=1),
                                    border_radius=4,
                                    bgcolor="#FF6B6B" if days_left and days_left <= 7 else "#FFA502" if days_left and days_left <= 30 else "#909090",
                                    visible=days_left is not None
                                )
                            ], spacing=4, alignment=ft.MainAxisAlignment.CENTER)
                        ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        expand=True,
                        padding=8,
                        border_radius=6,
                        bgcolor=ft.colors.with_opacity(0.05, "#FF6B6B" if is_expiring else "#909090")
                    ),
                ], spacing=8),
                margin=ft.margin.only(top=10, bottom=10)
            ),
            
            # Informações adicionais
            ft.Row([
                ft.Row([
                    ft.Icon(ft.icons.FOLDER_OUTLINED, size=14, color="#707070"),
                    ft.Text(f"Grupo: {product_group}", size=12, color="#707070"),
                ], spacing=4),
                ft.Row([
                    ft.Icon(ft.icons.TRENDING_UP, size=14, color="#707070"),
                    ft.Text(f"Uso semanal: {weekly_usage_total}", size=12, color="#707070"),
                ], spacing=4),
            ], spacing=10, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            
            # Botões de ação rápida
            ft.Container(
                content=ft.Row([
                    ft.OutlinedButton(
                        "Editar",
                        icon=ft.icons.EDIT_OUTLINED,
                        style=ft.ButtonStyle(
                            color=primary_color,
                            shape=ft.RoundedRectangleBorder(radius=8)
                        ),
                        on_click=lambda _, p=product: self.navigation.go_to_edit_product(p),
                    ),
                    ft.FilledButton(
                        "Registrar Saída",
                        icon=ft.icons.EXIT_TO_APP,
                        style=ft.ButtonStyle(
                            bgcolor=primary_color,
                            color="#FFFFFF",
                            shape=ft.RoundedRectangleBorder(radius=8)
                        ),
                        on_click=lambda _, p=product: self._register_product_exit(p),
                    ),
                ], spacing=8, alignment=ft.MainAxisAlignment.END),
                margin=ft.margin.only(top=10)
            )
        ], spacing=0),
        padding=15,
        border_radius=12,
        bgcolor=card_bg,
        border=ft.border.all(1, ft.colors.with_opacity(0.1, status_color)),
        shadow=ft.BoxShadow(
            spread_radius=0.1,
            blur_radius=4,
            color=ft.colors.with_opacity(0.08, "#000000")
        ),
        on_click=lambda _, p=product: self.navigation.select_product(p),
    )
    
    def _register_product_exit(self, product):
        """Navega para a tela de registro de saída de produto"""
        print(f"StockScreen: Solicitando registro de saída para produto: {product.get('name')}, ID: {product.get('id')}")
        
        # Criar uma cópia do produto para evitar referências compartilhadas
        product_copy = product.copy()
        
        # Navegar para a tela de registro de saída
        self.navigation.go_to_register_exit(product_copy, "product")
        
    def _confirm_delete_group(self, group):
        print(f"StockScreen: Solicitando confirmação para excluir o grupo: {group['name']}")
        # Criar uma cópia do grupo para não modificar o original
        group_copy = group.copy()
        # Definir tipo de grupo explicitamente
        group_copy["group_type"] = "product"
        self.navigation.go_to_confirm_delete("group", group_copy)
    
    def _confirm_delete_product(self, product):
        """Navega para a tela de confirmação de exclusão de produto"""
        print(f"StockScreen: Solicitando confirmação para excluir o produto: {product['name']}")
        self.navigation.go_to_confirm_delete("product", product)
            
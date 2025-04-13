import flet as ft
from datetime import datetime

from screens.register_exit_screen import RegisterExitScreen

class GroupDetailScreen:
    def __init__(self, data, navigation):
        self.data = data
        self.navigation = navigation
        self.group = None
        self.is_product_group = True  # True para produtos, False para resíduos
    
    def set_group(self, group, is_product_group=True):
        """Define o grupo a ser exibido"""
        self.group = group
        self.is_product_group = is_product_group
    
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
        
        if not self.group:
            return ft.Container(
                content=ft.Column([
                    ft.Icon(ft.icons.ERROR_OUTLINE, size=50, color="#CCCCCC"),
                    ft.Text("Grupo não encontrado", size=18, color="#909090"),
                    ft.ElevatedButton(
                        "Voltar",
                        icon=ft.icons.ARROW_BACK,
                        on_click=lambda _: self.navigation.go_back(),
                        style=ft.ButtonStyle(
                            bgcolor=primary_color,
                            color=card_bg
                        )
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15),
                alignment=ft.alignment.center,
                padding=20,
                bgcolor=bg_color,
                expand=True
            )
        
        # Obter itens do grupo
        from services.group_service import GroupService
        group_service = GroupService(self.data.firebase, self.data.db)
        
        if self.is_product_group:
            items = group_service.get_products_in_group(self.group["id"])
        else:
            items = group_service.get_residues_in_group(self.group["id"])  
        
        # Cabeçalho
        icon_name = getattr(ft.icons, self.group.get("icon", "FOLDER"), ft.icons.FOLDER)
        color_name = self.group.get("color", "blue").upper()
        color = getattr(ft.colors, f"{color_name}_500", ft.colors.BLUE_500)
        
        # Calcular estatísticas do grupo
        total_quantity = 0
        low_stock_count = 0
        expiring_count = 0
        
        if self.is_product_group:
            for item in items:
                try:
                    # Quantidade total
                    quantity = int(item.get('quantity', 0))
                    total_quantity += quantity
                    
                    # Verificar produtos com estoque baixo
                    min_stock = int(item.get('minStock', 0) or 0)
                    if min_stock > 0 and quantity <= min_stock:
                        low_stock_count += 1
                    
                    # Verificar produtos próximos ao vencimento
                    if item in self.data.expiring_products:
                        expiring_count += 1
                        
                except (ValueError, TypeError):
                    pass
        else:
            # Para resíduos, apenas somamos a quantidade
            for item in items:
                try:
                    quantity = int(item.get('quantity', 0))
                    total_quantity += quantity
                except (ValueError, TypeError):
                    pass
        
        header = ft.Container(
            content=ft.Column([
                # Linha superior com botão de voltar, ícone e nome do grupo
                ft.Row(
                    controls=[
                        ft.IconButton(
                            icon=ft.icons.ARROW_BACK,
                            icon_color="#505050",
                            on_click=lambda _: self.navigation.go_back()
                        ),
                        ft.Container(
                            content=ft.Icon(icon_name, color="#FFFFFF", size=20),
                            padding=8,
                            border_radius=8,
                            bgcolor=color
                        ),
                        ft.Text(self.group["name"], size=20, weight="bold", color="#303030"),
                        ft.Container(width=0, expand=True),
                        ft.IconButton(
                            icon=ft.icons.EDIT,
                            tooltip="Editar Grupo",
                            icon_color="#505050",
                            on_click=lambda _: self._edit_group()
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    spacing=10,
                ),
                
                # Descrição do grupo
                ft.Container(
                    content=ft.Text(
                        self.group.get("description", "Sem descrição"),
                        size=14,
                        color="#707070"
                    ),
                    margin=ft.margin.only(left=10, right=10, top=5, bottom=10),
                    visible=bool(self.group.get("description"))
                ),
                
                # Estatísticas do grupo
                ft.Container(
                    content=ft.ResponsiveRow([
                        # Total de itens
                        ft.Column([
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("Total de Itens", size=12, color="#707070"),
                                    ft.Text(f"{len(items)}", size=18, weight="bold", color=color),
                                ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                                padding=10,
                                border_radius=8,
                                bgcolor=ft.colors.with_opacity(0.05, color),
                                expand=True
                            )
                        ], col={"xs": 4, "sm": 4, "md": 4, "lg": 4, "xl": 4}),
                        
                        # Quantidade total
                        ft.Column([
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("Quantidade", size=12, color="#707070"),
                                    ft.Text(f"{total_quantity}", size=18, weight="bold", color=color),
                                ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                                padding=10,
                                border_radius=8,
                                bgcolor=ft.colors.with_opacity(0.05, color),
                                expand=True
                            )
                        ], col={"xs": 4, "sm": 4, "md": 4, "lg": 4, "xl": 4}),
                        
                        # Estoque baixo ou outro indicador relevante
                        ft.Column([
                            ft.Container(
                                content=ft.Column([
                                    ft.Text(
                                        "Estoque Baixo" if self.is_product_group else "Disponíveis",
                                        size=12,
                                        color="#707070"
                                    ),
                                    ft.Text(
                                        f"{low_stock_count}" if self.is_product_group else f"{total_quantity}",
                                        size=18,
                                        weight="bold",
                                        color=danger_color if self.is_product_group and low_stock_count > 0 else success_color
                                    ),
                                ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                                padding=10,
                                border_radius=8,
                                bgcolor=ft.colors.with_opacity(0.05, danger_color if self.is_product_group and low_stock_count > 0 else success_color),
                                expand=True
                            )
                        ], col={"xs": 4, "sm": 4, "md": 4, "lg": 4, "xl": 4}),
                    ], spacing=10),
                    margin=ft.margin.only(bottom=15)
                ),
                
                # Barra de pesquisa e filtros
                ft.Container(
                    content=ft.Row([
                        ft.TextField(
                            hint_text=f"Pesquisar {'produtos' if self.is_product_group else 'resíduos'}...",
                            prefix_icon=ft.icons.SEARCH,
                            border_radius=20,
                            filled=True,
                            bgcolor=card_bg,
                            expand=True,
                            border_color=ft.colors.with_opacity(0.1, color),
                            height=40
                        ),
                        ft.IconButton(
                            icon=ft.icons.FILTER_LIST,
                            tooltip="Filtrar",
                            icon_color=color
                        ),
                        ft.IconButton(
                            icon=ft.icons.ADD_CIRCLE,
                            tooltip=f"Adicionar {'Produto' if self.is_product_group else 'Resíduo'}",
                            icon_color=color,
                            icon_size=30,
                            on_click=lambda _: self.navigation.go_to_add_product() if self.is_product_group else self.navigation.go_to_add_residue()
                        )
                    ], spacing=8),
                    margin=ft.margin.only(bottom=10)
                ),
                
                # Título da lista
                ft.Container(
                    content=ft.Row([
                        ft.Icon(
                            ft.icons.INVENTORY_2_OUTLINED if self.is_product_group else ft.icons.DELETE_OUTLINE,
                            color=color,
                            size=16
                        ),
                        ft.Text(
                            f"Lista de {'Produtos' if self.is_product_group else 'Resíduos'}",
                            size=14,
                            weight="bold",
                            color="#505050"
                        ),
                        ft.Container(
                            content=ft.Text(f"{len(items)}", size=12, color="#FFFFFF"),
                            padding=ft.padding.only(left=8, right=8, top=2, bottom=2),
                            border_radius=10,
                            bgcolor=color
                        )
                    ], spacing=8),
                    margin=ft.margin.only(bottom=10, left=5)
                )
            ]),
            padding=15,
            bgcolor=card_bg,
            border_radius=12,
            shadow=ft.BoxShadow(
                spread_radius=0.1,
                blur_radius=4,
                color=ft.colors.with_opacity(0.08, "#000000")
            ),
            margin=ft.margin.only(bottom=10)
        )
        
        # Lista de itens
        items_list_items = []
        
        if items:
            for item in items:
                if self.is_product_group:
                    items_list_items.append(self._build_product_item(item, color, warning_color, danger_color))
                else:
                    items_list_items.append(self._build_residue_item(item, color))
        else:
            items_list_items.append(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Icon(
                                ft.icons.INVENTORY_2_OUTLINED if self.is_product_group else ft.icons.DELETE_OUTLINE, 
                                size=50, 
                                color="#CCCCCC"
                            ),
                            ft.Text(
                                f"Nenhum {'produto' if self.is_product_group else 'resíduo'} encontrado neste grupo",
                                size=16,
                                color="#909090"
                            ),
                            ft.ElevatedButton(
                                f"Adicionar {'Produto' if self.is_product_group else 'Resíduo'}",
                                icon=ft.icons.ADD_CIRCLE_OUTLINE,
                                on_click=lambda _: self.navigation.go_to_add_product() if self.is_product_group else self.navigation.go_to_add_residue(),
                                style=ft.ButtonStyle(
                                    bgcolor=color,
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
            )
        
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
                scroll=ft.ScrollMode.AUTO,  # Adiciona scroll para a tela inteira
            ),
            bgcolor=bg_color,
            padding=10,
            expand=True,
        )
    
    def _build_product_item(self, product, primary_color, warning_color, danger_color):
        """Constrói um item de produto para a lista com design moderno"""
        # Verificar se o produto está com estoque baixo
        is_low_stock = product in self.data.low_stock_products
        
        # Verificar se o produto está próximo ao vencimento
        is_expiring = product in self.data.expiring_products
        
        # Obter informações do produto
        product_name = product.get("name", "Sem nome")
        product_quantity = product.get("quantity", "0")
        product_lot = product.get("lot", "N/A")
        product_expiry = product.get("expiry", "N/A")
        product_entry_date = product.get("entryDate", "N/A")
        
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
        border_color = ft.colors.GREY_300
        
        if is_low_stock and is_expiring:
            status_color = danger_color
            status_bg = ft.colors.with_opacity(0.1, danger_color)
            border_color = ft.colors.with_opacity(0.5, danger_color)
        elif is_low_stock:
            status_color = danger_color
            status_bg = ft.colors.with_opacity(0.05, danger_color)
            border_color = ft.colors.with_opacity(0.3, danger_color)
        elif is_expiring:
            status_color = warning_color
            status_color = warning_color
            status_bg = ft.colors.with_opacity(0.05, warning_color)
            border_color = ft.colors.with_opacity(0.3, warning_color)
        
        return ft.Container(
            content=ft.Column([
                # Linha principal com nome e status
                ft.Row([
                    # Coluna com nome e informações básicas
                    ft.Column([
                        ft.Text(product_name, size=16, weight="w600", color="#303030"),
                        ft.Row([
                            ft.Container(
                                content=ft.Text(
                                    "Estoque Baixo" if is_low_stock else "Próx. Vencimento" if is_expiring else "Normal",
                                    size=10,
                                    weight="bold",
                                    color=status_color
                                ),
                                padding=ft.padding.only(left=6, right=6, top=2, bottom=2),
                                border_radius=4,
                                bgcolor=status_bg,
                                visible=is_low_stock or is_expiring
                            ),
                            ft.Container(
                                content=ft.Text(f"{days_left} dias", size=10, color="#FFFFFF"),
                                padding=ft.padding.only(left=6, right=6, top=2, bottom=2),
                                border_radius=4,
                                bgcolor=danger_color if days_left and days_left <= 7 else warning_color,
                                visible=days_left is not None and days_left <= 30
                            )
                        ], spacing=8)
                    ], spacing=4, expand=True),
                    
                    # Quantidade destacada
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Quantidade", size=10, color="#707070"),
                            ft.Text(
                                f"{product_quantity}",
                                size=18,
                                weight="bold",
                                color=danger_color if is_low_stock else primary_color
                            )
                        ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        padding=ft.padding.only(left=10, right=10, top=5, bottom=5),
                        border_radius=6,
                        bgcolor=ft.colors.with_opacity(0.05, danger_color if is_low_stock else primary_color)
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                # Informações adicionais
                ft.Container(
                    content=ft.Row([
                        # Lote
                        ft.Row([
                            ft.Icon(ft.icons.INVENTORY_2_OUTLINED, size=14, color="#707070"),
                            ft.Text(f"Lote: {product_lot}", size=12, color="#707070"),
                        ], spacing=4),
                        # Validade
                        ft.Row([
                            ft.Icon(ft.icons.CALENDAR_TODAY_OUTLINED, size=14, color="#707070"),
                            ft.Text(
                                f"Validade: {product_expiry}",
                                size=12,
                                color=danger_color if is_expiring else "#707070"
                            ),
                        ], spacing=4),
                        # Uso semanal
                        ft.Row([
                            ft.Icon(ft.icons.TRENDING_UP, size=14, color="#707070"),
                            ft.Text(f"Uso: {weekly_usage_total}/sem", size=12, color="#707070"),
                        ], spacing=4),
                    ], spacing=12, wrap=True),
                    margin=ft.margin.only(top=8, bottom=8)
                ),
                
                # Botões de ação
                ft.Row([
                    # Botão de saída
                    ft.OutlinedButton(
                        "Saída",
                        icon=ft.icons.EXIT_TO_APP,
                        style=ft.ButtonStyle(
                            color=warning_color,
                            shape=ft.RoundedRectangleBorder(radius=8)
                        ),
                        on_click=lambda _, p=product: self._register_product_exit(p),
                    ),
                    # Botão de uso semanal
                    ft.OutlinedButton(
                        "Uso Semanal",
                        icon=ft.icons.TRENDING_UP,
                        style=ft.ButtonStyle(
                            color=primary_color,
                            shape=ft.RoundedRectangleBorder(radius=8)
                        ),
                        on_click=lambda _, p=product: self.navigation.go_to_weekly_usage(p),
                    ),
                    # Menu de mais opções
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
                                text="Excluir",
                                icon=ft.icons.DELETE_OUTLINE,
                                on_click=lambda _, p=product: self._confirm_delete_product(p)
                            ),
                        ]
                    )
                ], spacing=8, alignment=ft.MainAxisAlignment.END)
            ], spacing=0),
            padding=15,
            border_radius=12,
            bgcolor="#FFFFFF",
            border=ft.border.all(1, border_color),
            shadow=ft.BoxShadow(
                spread_radius=0.1,
                blur_radius=4,
                color=ft.colors.with_opacity(0.08, "#000000")
            ),
            margin=ft.margin.only(bottom=8),
            on_click=lambda _, p=product: self.navigation.select_product(p),
        )
    
    def _build_residue_item(self, residue, primary_color):
        """Constrói um item de resíduo para a lista com design moderno"""
        # Obter informações do resíduo
        residue_name = residue.get("name", "Sem nome")
        residue_quantity = residue.get("quantity", "0")
        residue_type = residue.get("type", "N/A")
        residue_entry_date = residue.get("entryDate", "N/A")
        residue_destination = residue.get("destination", "N/A")
        residue_exit_date = residue.get("exitDate", "")
        
        # Status do resíduo
        has_exit = bool(residue_exit_date)
        status_text = "Saída Registrada" if has_exit else "Disponível"
        status_color = "#909090" if has_exit else "#2ED573"
        
        return ft.Container(
            content=ft.Column([
                # Linha principal com nome e status
                ft.Row([
                    # Coluna com nome e informações básicas
                    ft.Column([
                        ft.Text(residue_name, size=16, weight="w600", color="#303030"),
                        ft.Row([
                            ft.Container(
                                content=ft.Text(
                                    status_text,
                                    size=10,
                                    weight="bold",
                                    color=status_color
                                ),
                                padding=ft.padding.only(left=6, right=6, top=2, bottom=2),
                                border_radius=4,
                                bgcolor=ft.colors.with_opacity(0.1, status_color)
                            ),
                            ft.Text(f"Tipo: {residue_type}", size=12, color="#707070")
                        ], spacing=8)
                    ], spacing=4, expand=True),
                    
                    # Quantidade destacada
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Quantidade", size=10, color="#707070"),
                            ft.Text(
                                f"{residue_quantity}",
                                size=18,
                                weight="bold",
                                color=primary_color
                            )
                        ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        padding=ft.padding.only(left=10, right=10, top=5, bottom=5),
                        border_radius=6,
                        bgcolor=ft.colors.with_opacity(0.05, primary_color)
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                # Informações adicionais
                ft.Container(
                    content=ft.Row([
                        # Data de entrada
                        ft.Row([
                            ft.Icon(ft.icons.DATE_RANGE_OUTLINED, size=14, color="#707070"),
                            ft.Text(f"Entrada: {residue_entry_date}", size=12, color="#707070"),
                        ], spacing=4),
                        # Destino
                        ft.Row([
                            ft.Icon(ft.icons.LOCATION_ON_OUTLINED, size=14, color="#707070"),
                            ft.Text(f"Destino: {residue_destination}", size=12, color="#707070"),
                        ], spacing=4),
                        # Data de saída (se houver)
                        ft.Row([
                            ft.Icon(ft.icons.EXIT_TO_APP, size=14, color="#707070"),
                            ft.Text(f"Saída: {residue_exit_date if residue_exit_date else 'Não registrada'}", size=12, color="#707070"),
                        ], spacing=4, visible=has_exit),
                    ], spacing=12, wrap=True),
                    margin=ft.margin.only(top=8, bottom=8)
                ),
                
                # Botões de ação
                ft.Row([
                    # Botão de saída
                    ft.OutlinedButton(
                        "Registrar Saída",
                        icon=ft.icons.EXIT_TO_APP,
                        style=ft.ButtonStyle(
                            color=primary_color,
                            shape=ft.RoundedRectangleBorder(radius=8)
                        ),
                        on_click=lambda _, r=residue: self._register_residue_exit(r),
                        disabled=has_exit
                    ),
                    # Menu de mais opções
                    ft.PopupMenuButton(
                        icon=ft.icons.MORE_VERT,
                        icon_color="#707070",
                        items=[
                            ft.PopupMenuItem(
                                text="Editar",
                                icon=ft.icons.EDIT_OUTLINED,
                                on_click=lambda _, r=residue: self.navigation.go_to_edit_residue(r)
                            ),
                            ft.PopupMenuItem(
                                text="Excluir",
                                icon=ft.icons.DELETE_OUTLINE,
                                on_click=lambda _, r=residue: self.navigation.go_to_confirm_delete("residue", r)
                            ),
                        ]
                    )
                ], spacing=8, alignment=ft.MainAxisAlignment.END)
            ], spacing=0),
            padding=15,
            border_radius=12,
            bgcolor="#FFFFFF",
            border=ft.border.all(1, ft.colors.GREY_300),
            shadow=ft.BoxShadow(
                spread_radius=0.1,
                blur_radius=4,
                color=ft.colors.with_opacity(0.08, "#000000")
            ),
            margin=ft.margin.only(bottom=8),
            on_click=lambda _, r=residue: self.navigation.select_residue(r),
        )
    
    def _edit_group(self):
        """Abre diálogo para editar o grupo"""
        def close_dialog():
            self.navigation.page.dialog.open = False
            self.navigation.page.update()
        
        def save_group(_):
            # Atualizar dados do grupo
            updated_group = self.group.copy()
            updated_group["name"] = name_field.value
            updated_group["description"] = description_field.value
            updated_group["icon"] = icon_dropdown.value
            updated_group["color"] = color_dropdown.value
            
            # Salvar grupo
            from services.group_service import GroupService
            group_service = GroupService(self.data.firebase, self.data.db)
            success = group_service.update_group(
                self.group["id"], 
                updated_group, 
                not self.is_product_group
            )
            
            if success:
                # Atualizar grupo local
                self.group = updated_group
                
                # Fechar diálogo e atualizar interface
                close_dialog()
                self.navigation.update_view()
                self.navigation.show_snack_bar("Grupo atualizado com sucesso!", "#2ED573")
            else:
                # Mostrar erro
                error_text.value = "Erro ao atualizar grupo. Tente novamente."
                error_text.visible = True
                self.navigation.page.update()
        
        # Campos do diálogo
        name_field = ft.TextField(
            label="Nome do Grupo",
            value=self.group["name"],
            border_radius=8,
            filled=True,
            prefix_icon=ft.icons.FOLDER
        )
        
        description_field = ft.TextField(
            label="Descrição",
            value=self.group.get("description", ""),
            border_radius=8,
            multiline=True,
            min_lines=2,
            max_lines=4,
            filled=True,
            prefix_icon=ft.icons.DESCRIPTION
        )
        
        # Opções de cores
        color_options = [
            ft.dropdown.Option("blue", "Azul"),
            ft.dropdown.Option("red", "Vermelho"),
            ft.dropdown.Option("green", "Verde"),
            ft.dropdown.Option("orange", "Laranja"),
            ft.dropdown.Option("purple", "Roxo"),
            ft.dropdown.Option("teal", "Turquesa"),
            ft.dropdown.Option("amber", "Âmbar"),
            ft.dropdown.Option("indigo", "Índigo"),
        ]
        
        color_dropdown = ft.Dropdown(
            label="Cor do Grupo",
            options=color_options,
            value=self.group.get("color", "blue"),
            border_radius=8,
            filled=True,
            prefix_icon=ft.icons.COLOR_LENS
        )
        
        # Opções de ícones
        icon_options = [
            ft.dropdown.Option("FOLDER", "Pasta"),
            ft.dropdown.Option("INVENTORY_2_ROUNDED", "Estoque"),
            ft.dropdown.Option("DELETE_OUTLINE", "Resíduo"),
            ft.dropdown.Option("CATEGORY", "Categoria"),
            ft.dropdown.Option("LABEL", "Etiqueta"),
            ft.dropdown.Option("BOOKMARK", "Marcador"),
            ft.dropdown.Option("STAR", "Estrela"),
        ]
        
        icon_dropdown = ft.Dropdown(
            label="Ícone do Grupo",
            options=icon_options,
            value=self.group.get("icon", "FOLDER"),
            border_radius=8,
            filled=True,
            prefix_icon=ft.icons.EMOJI_SYMBOLS
        )
        
        error_text = ft.Text(
            "",
            color="#FF6B6B",
            visible=False,
        )
        
        # Criar diálogo
        dialog = ft.AlertDialog(
            title=ft.Text(f"Editar Grupo - {self.group['name']}", weight="bold"),
            content=ft.Column(
                controls=[
                    name_field,
                    description_field,
                    color_dropdown,
                    icon_dropdown,
                    error_text,
                ],
                spacing=15,
                width=400,
            ),
            actions=[
                ft.TextButton(
                    "Cancelar", 
                    on_click=lambda _: close_dialog(),
                    style=ft.ButtonStyle(color="#909090")
                ),
                ft.FilledButton(
                    "Salvar",
                    on_click=save_group,
                    style=ft.ButtonStyle(
                        color="#FFFFFF",
                        bgcolor="#4A6FFF",
                    ),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            shape=ft.RoundedRectangleBorder(radius=12)
        )
        
        # Mostrar diálogo
        self.navigation.page.dialog = dialog
        self.navigation.page.dialog.open = True
        self.navigation.page.update()
    
    def _register_product_exit(self, product):
        """Navega para a tela de registro de saída de produto"""
        product_id = product.get("id")
        
        if not product_id:
            print("ERRO: Produto sem ID")
            return
        
        print(f"GroupDetailScreen: Solicitando registro de saída para produto ID: {product_id}")
        
        # Buscar o produto diretamente do banco de dados
        cursor = self.data.db.conn.cursor()
        cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
        product_data = cursor.fetchone()
        
        if not product_data:
            print(f"ERRO: Produto com ID {product_id} não encontrado no banco de dados")
            return
        
        # Converter para dicionário
        product_fresh = self.data.product_service._convert_to_dict([product_data])[0]
        
        print(f"Produto obtido do banco de dados: {product_fresh.get('name')}")
        
        # Criar a tela com o produto fresco do banco de dados
        register_exit_screen = RegisterExitScreen(self.data, self.navigation, product_fresh, "product")
        
        # Adicionar a tela como uma nova view
        self.navigation.page.views.append(
            ft.View(
                route=f"/register_exit/product/{product_id}",
                controls=[register_exit_screen.build()]
            )
        )
        self.navigation.page.go(f"/register_exit/product/{product_id}")
        self.navigation.page.update()
    
    def _register_residue_exit(self, residue):
        """Navega para a tela de registro de saída de resíduo"""
        self.navigation.go_to_register_exit(residue, "residue")
    
    def _confirm_delete_product(self, product):
        """Navega para a tela de confirmação de exclusão de produto"""
        self.navigation.go_to_confirm_delete("product", product)
    
    def _show_product_details(self, product):
        """Exibe um diálogo com detalhes completos do produto"""
        def close_dialog():
            self.navigation.page.dialog.open = False
            self.navigation.page.update()
        
        # Preparar dados de uso semanal
        weekly_usage = product.get("weeklyUsage", [0] * 7)
        if not isinstance(weekly_usage, list):
            weekly_usage = [0] * 7

        while len(weekly_usage) < 7:
            weekly_usage.append(0)

        weekly_usage = weekly_usage[:7]

        days = ["Domingo", "Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado"]
        weekly_usage_total = sum([int(u) if isinstance(u, str) and u.isdigit() else u if isinstance(u, (int, float)) else 0 for u in weekly_usage])

        # Obter informações do produto
        product_name = product.get("name", "Sem nome")
        product_quantity = product.get("quantity", "0")
        product_lot = product.get("lot", "N/A")
        product_expiry = product.get("expiry", "N/A")
        product_group = product.get("group_name", "Sem grupo")
        product_location = product.get("location", "N/A")
        product_category = product.get("category", "N/A")
        product_description = product.get("description", "Sem descrição")
        product_min_stock = product.get("minStock", "0")
        product_entry_date = product.get("entryDate", "N/A")
        
        # Verificar se o produto está com estoque baixo
        is_low_stock = product in self.data.low_stock_products
        
        # Verificar se o produto está próximo ao vencimento
        is_expiring = product in self.data.expiring_products
        
        # Calcular dias até o vencimento
        days_left = None
        if product_expiry != "N/A":
            from datetime import datetime
            try:
                expiry_date = datetime.strptime(product_expiry, "%d/%m/%Y")
                days_left = (expiry_date - datetime.now()).days
            except Exception:
                days_left = None
        
        # Criar diálogo
        dialog = ft.AlertDialog(
            title=ft.Text(product_name, weight="bold", size=18),
            content=ft.Column(
                controls=[
                    # Status do produto
                    ft.Container(
                        content=ft.Row([
                            ft.Container(
                                content=ft.Text("Estoque Baixo", size=12, weight="bold", color="#FFFFFF"),
                                padding=ft.padding.only(left=8, right=8, top=4, bottom=4),
                                border_radius=4,
                                bgcolor="#FF6B6B",
                                visible=is_low_stock
                            ),
                            ft.Container(
                                content=ft.Text("Próximo ao Vencimento", size=12, weight="bold", color="#FFFFFF"),
                                padding=ft.padding.only(left=8, right=8, top=4, bottom=4),
                                border_radius=4,
                                bgcolor="#FFA502",
                                visible=is_expiring
                            ),
                        ], spacing=8, wrap=True),
                        margin=ft.margin.only(bottom=15),
                        visible=is_low_stock or is_expiring
                    ),
                    
                    # Informações principais
                    ft.ResponsiveRow([
                        # Quantidade
                        ft.Column([
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("Quantidade", size=12, color="#707070"),
                                    ft.Row([
                                        ft.Text(f"{product_quantity}", size=18, weight="bold", 
                                            color="#FF6B6B" if is_low_stock else "#4A6FFF"),
                                        ft.Text("un", size=12, color="#707070"),
                                    ], spacing=4)
                                ], spacing=4),
                                padding=10,
                                border_radius=8,
                                bgcolor=ft.colors.with_opacity(0.05, "#FF6B6B" if is_low_stock else "#4A6FFF")
                            )
                        ], col={"xs": 6, "sm": 6, "md": 4, "lg": 4, "xl": 4}),
                        
                        # Estoque mínimo
                        ft.Column([
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("Estoque Mínimo", size=12, color="#707070"),
                                    ft.Row([
                                        ft.Text(f"{product_min_stock}", size=18, weight="bold", color="#505050"),
                                        ft.Text("un", size=12, color="#707070"),
                                    ], spacing=4)
                                ], spacing=4),
                                padding=10,
                                border_radius=8,
                                bgcolor="#F5F5F5"
                            )
                        ], col={"xs": 6, "sm": 6, "md": 4, "lg": 4, "xl": 4}),
                        
                        # Validade
                        ft.Column([
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("Validade", size=12, color="#707070"),
                                    ft.Row([
                                        ft.Text(f"{product_expiry}", size=18, weight="bold", 
                                            color="#FF6B6B" if is_expiring else "#505050"),
                                        ft.Container(
                                            content=ft.Text(f"{days_left}d", size=10, color="#FFFFFF"),
                                            padding=ft.padding.only(left=4, right=4, top=1, bottom=1),
                                            border_radius=4,
                                            bgcolor="#FF6B6B" if days_left and days_left <= 7 else "#FFA502" if days_left and days_left <= 30 else "#909090",
                                            visible=days_left is not None
                                        )
                                    ], spacing=4)
                                ], spacing=4),
                                padding=10,
                                border_radius=8,
                                bgcolor=ft.colors.with_opacity(0.05, "#FF6B6B" if is_expiring else "#909090")
                            )
                        ], col={"xs": 12, "sm": 12, "md": 4, "lg": 4, "xl": 4}),
                    ], spacing=10),
                    
                    # Informações secundárias
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.icons.FOLDER_OUTLINED, size=16, color="#707070"),
                                ft.Text("Grupo:", size=14, color="#707070", weight="w500"),
                                ft.Text(product_group, size=14, color="#505050", expand=True),
                            ], spacing=8),
                            ft.Row([
                                ft.Icon(ft.icons.LOCATION_ON_OUTLINED, size=16, color="#707070"),
                                ft.Text("Local:", size=14, color="#707070", weight="w500"),
                                ft.Text(product_location, size=14, color="#505050", expand=True),
                            ], spacing=8),
                            ft.Row([
                                ft.Icon(ft.icons.CATEGORY_OUTLINED, size=16, color="#707070"),
                                ft.Text("Categoria:", size=14, color="#707070", weight="w500"),
                                ft.Text(product_category, size=14, color="#505050", expand=True),
                            ], spacing=8),
                            ft.Row([
                                ft.Icon(ft.icons.INVENTORY_2_OUTLINED, size=16, color="#707070"),
                                ft.Text("Lote:", size=14, color="#707070", weight="w500"),
                                ft.Text(product_lot, size=14, color="#505050", expand=True),
                            ], spacing=8),
                            ft.Row([
                                ft.Icon(ft.icons.DATE_RANGE_OUTLINED, size=16, color="#707070"),
                                ft.Text("Data de Entrada:", size=14, color="#707070", weight="w500"),
                                ft.Text(product_entry_date, size=14, color="#505050", expand=True),
                            ], spacing=8),
                        ], spacing=12),
                        padding=15,
                        border_radius=8,
                        bgcolor="#F8F9FD",
                        margin=ft.margin.only(top=15, bottom=15)
                    ),
                    
                    # Seção de uso semanal
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Uso Semanal", size=14, color="#707070", weight="w500"),
                            ft.Row([
                                ft.Text(f"Total: {weekly_usage_total} unidades", size=14, weight="bold", color="#4A6FFF"),
                                ft.Text(f"Média: {round(weekly_usage_total/7, 1)} por dia", size=14, color="#707070"),
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            
                            # Gráfico simples de uso diário
                            ft.Container(
                                content=ft.Row([
                                    ft.Column([
                                        ft.Container(
                                            content=ft.Text(str(weekly_usage[i]), size=12, color="#FFFFFF"),
                                            padding=5,
                                            bgcolor="#4A6FFF",
                                            border_radius=4,
                                            alignment=ft.alignment.center,
                                            height=max(20, min(100, 20 + (weekly_usage[i] / (max(weekly_usage) if max(weekly_usage) > 0 else 1)) * 80)),
                                        ),
                                        ft.Text(days[i][:3], size=10, color="#707070"),
                                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5)
                                    for i in range(7)
                                ], spacing=5, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                margin=ft.margin.only(top=10, bottom=10),
                            ),
                            
                            ft.OutlinedButton(
                                "Editar Uso Semanal",
                                icon=ft.icons.EDIT_CALENDAR,
                                on_click=lambda _, p=product: (close_dialog(), self.navigation.go_to_weekly_usage(p)),
                                style=ft.ButtonStyle(color="#4A6FFF")
                            ),
                        ], spacing=10),
                        padding=15,
                        border_radius=8,
                        bgcolor="#F8F9FD",
                        margin=ft.margin.only(top=15, bottom=15)
                    ),
                    
                    # Descrição
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Descrição", size=14, color="#707070", weight="w500"),
                            ft.Text(product_description, size=14, color="#505050"),
                        ], spacing=8),
                        padding=15,
                        border_radius=8,
                        bgcolor="#F8F9FD",
                        visible=product_description != "Sem descrição"
                    ),
                ],
                spacing=10,
                width=500,
                scroll=ft.ScrollMode.AUTO,  # Adiciona scroll para conteúdos grandes
            ),
            actions=[
                ft.OutlinedButton(
                    "Fechar", 
                    on_click=lambda _: close_dialog(),
                    style=ft.ButtonStyle(color="#909090")
                ),
                ft.OutlinedButton(
                    "Editar",
                    icon=ft.icons.EDIT_OUTLINED,
                    on_click=lambda _, p=product: (close_dialog(), self.navigation.go_to_edit_product(p)),
                    style=ft.ButtonStyle(color="#4A6FFF")
                ),
                ft.FilledButton(
                    "Registrar Saída",
                    icon=ft.icons.EXIT_TO_APP,
                    on_click=lambda _, p=product: (close_dialog(), self._register_product_exit(p)),
                    style=ft.ButtonStyle(bgcolor="#4A6FFF", color="#FFFFFF")
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            shape=ft.RoundedRectangleBorder(radius=12)
        )
        
        # Mostrar diálogo
        self.navigation.page.dialog = dialog
        self.navigation.page.dialog.open = True
        self.navigation.page.update()
    
    def _show_residue_details(self, residue):
        """Exibe um diálogo com detalhes completos do resíduo"""
        def close_dialog():
            self.navigation.page.dialog.open = False
            self.navigation.page.update()
        
        # Obter informações do resíduo
        residue_name = residue.get("name", "Sem nome")
        residue_quantity = residue.get("quantity", "0")
        residue_type = residue.get("type", "N/A")
        residue_entry_date = residue.get("entryDate", "N/A")
        residue_destination = residue.get("destination", "N/A")
        residue_exit_date = residue.get("exitDate", "")
        residue_group = residue.get("group_name", "Sem grupo")
        residue_notes = residue.get("notes", "Sem observações")
        residue_unit_price = residue.get("unitPrice", "0")
        
        # Status do resíduo
        has_exit = bool(residue_exit_date)
        status_text = "Saída Registrada" if has_exit else "Disponível"
        status_color = "#909090" if has_exit else "#2ED573"
        
        # Calcular valor total
        try:
            total_value = float(residue_quantity) * float(residue_unit_price or 0)
        except (ValueError, TypeError):
            total_value = 0
        
        # Criar diálogo
        dialog = ft.AlertDialog(
            title=ft.Text(residue_name, weight="bold", size=18),
            content=ft.Column(
                controls=[
                    # Status do resíduo
                    ft.Container(
                        content=ft.Row([
                            ft.Container(
                                content=ft.Text(status_text, size=12, weight="bold", color="#FFFFFF"),
                                padding=ft.padding.only(left=8, right=8, top=4, bottom=4),
                                border_radius=4,
                                bgcolor=status_color
                            ),
                            ft.Text(f"Tipo: {residue_type}", size=14, color="#707070")
                        ], spacing=8),
                        margin=ft.margin.only(bottom=15)
                    ),
                    
                    # Informações principais
                    ft.ResponsiveRow([
                        # Quantidade
                        ft.Column([
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("Quantidade", size=12, color="#707070"),
                                    ft.Row([
                                        ft.Text(f"{residue_quantity}", size=18, weight="bold", color="#6C5CE7"),
                                        ft.Text("un", size=12, color="#707070"),
                                    ], spacing=4)
                                ], spacing=4),
                                padding=10,
                                border_radius=8,
                                bgcolor=ft.colors.with_opacity(0.05, "#6C5CE7")
                            )
                        ], col={"xs": 6, "sm": 6, "md": 4, "lg": 4, "xl": 4}),
                        
                        # Preço unitário
                        ft.Column([
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("Preço Unitário", size=12, color="#707070"),
                                    ft.Row([
                                        ft.Text(f"R$ {residue_unit_price or '0,00'}", size=18, weight="bold", color="#2ED573"),
                                    ], spacing=4)
                                ], spacing=4),
                                padding=10,
                                border_radius=8,
                                bgcolor=ft.colors.with_opacity(0.05, "#2ED573")
                            )
                        ], col={"xs": 6, "sm": 6, "md": 4, "lg": 4, "xl": 4}),
                        
                        # Valor total
                        ft.Column([
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("Valor Total", size=12, color="#707070"),
                                    ft.Row([
                                        ft.Text(f"R$ {total_value:.2f}".replace('.', ','), size=18, weight="bold", color="#2ED573"),
                                    ], spacing=4)
                                ], spacing=4),
                                padding=10,
                                border_radius=8,
                                bgcolor=ft.colors.with_opacity(0.05, "#2ED573")
                            )
                        ], col={"xs": 12, "sm": 12, "md": 4, "lg": 4, "xl": 4}),
                    ], spacing=10),
                    
                    # Informações secundárias
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.icons.FOLDER_OUTLINED, size=16, color="#707070"),
                                ft.Text("Grupo:", size=14, color="#707070", weight="w500"),
                                ft.Text(residue_group, size=14, color="#505050", expand=True),
                            ], spacing=8),
                            ft.Row([
                                ft.Icon(ft.icons.DATE_RANGE_OUTLINED, size=16, color="#707070"),
                                ft.Text("Data de Entrada:", size=14, color="#707070", weight="w500"),
                                ft.Text(residue_entry_date, size=14, color="#505050", expand=True),
                            ], spacing=8),
                            ft.Row([
                                ft.Icon(ft.icons.LOCATION_ON_OUTLINED, size=16, color="#707070"),
                                ft.Text("Destino:", size=14, color="#707070", weight="w500"),
                                ft.Text(residue_destination, size=14, color="#505050", expand=True),
                            ], spacing=8),
                            ft.Row([
                                ft.Icon(ft.icons.EXIT_TO_APP, size=16, color="#707070"),
                                ft.Text("Data de Saída:", size=14, color="#707070", weight="w500"),
                                ft.Text(residue_exit_date if residue_exit_date else "Não registrada", size=14, color="#505050", expand=True),
                            ], spacing=8, visible=has_exit),
                        ], spacing=12),
                        padding=15,
                        border_radius=8,
                        bgcolor="#F8F9FD",
                        margin=ft.margin.only(top=15, bottom=15)
                    ),
                    
                    # Observações
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Observações", size=14, color="#707070", weight="w500"),
                            ft.Text(residue_notes, size=14, color="#505050"),
                        ], spacing=8),
                        padding=15,
                        border_radius=8,
                        bgcolor="#F8F9FD",
                        visible=residue_notes != "Sem observações"
                    ),
                ],
                spacing=10,
                width=500,
                scroll=ft.ScrollMode.AUTO,  # Adiciona scroll para conteúdos grandes
            ),
            actions=[
                ft.OutlinedButton(
                    "Fechar", 
                    on_click=lambda _: close_dialog(),
                    style=ft.ButtonStyle(color="#909090")
                ),
                ft.OutlinedButton(
                    "Editar",
                    icon=ft.icons.EDIT_OUTLINED,
                    on_click=lambda _, r=residue: (close_dialog(), self.navigation.go_to_edit_residue(r)),
                    style=ft.ButtonStyle(color="#6C5CE7")
                ),
                ft.FilledButton(
                    "Registrar Saída",
                    icon=ft.icons.EXIT_TO_APP,
                    on_click=lambda _, r=residue: (close_dialog(), self._register_residue_exit(r)),
                    style=ft.ButtonStyle(bgcolor="#6C5CE7", color="#FFFFFF"),
                    disabled=has_exit
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            shape=ft.RoundedRectangleBorder(radius=12)
        )
        
        # Mostrar diálogo
        self.navigation.page.dialog = dialog
        self.navigation.page.dialog.open = True
        self.navigation.page.update()
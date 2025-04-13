import flet as ft

class GroupsScreen:
    def __init__(self, data, navigation):
        self.data = data
        self.navigation = navigation
        self.search_text = ""
        self.show_product_groups = True  # Por padrão, mostra grupos de produtos
    
    def build(self):
        # Obter grupos
        from services.group_service import GroupService
        group_service = GroupService(self.data.firebase, self.data.db)
        
        if self.show_product_groups:
            groups = group_service.get_all_product_groups()
            title = "Grupos de Produtos"
            add_tooltip = "Adicionar Grupo de Produtos"
        else:
            groups = group_service.get_all_residue_groups()
            title = "Grupos de Resíduos"
            add_tooltip = "Adicionar Grupo de Resíduos"
        
        # Filtrar grupos com base na pesquisa
        if self.search_text:
            search_lower = self.search_text.lower()
            groups = [
                group for group in groups
                if search_lower in group["name"].lower() or 
                   search_lower in group.get("description", "").lower()
            ]
        
        # Barra de pesquisa e botão de adicionar
        search_field = ft.TextField(
            hint_text="Pesquisar grupos...",
            prefix_icon=ft.icons.SEARCH,
            on_change=self._on_search_change,
            border_radius=20,
            filled=True,
            bgcolor=ft.colors.WHITE,
            expand=True,
        )
        
        add_button = ft.IconButton(
            icon=ft.icons.ADD_CIRCLE,
            icon_color=ft.colors.BLUE_500,
            icon_size=30,
            tooltip=add_tooltip,
            on_click=lambda _: self.navigation.go_to_add_group(self.show_product_groups)
        )
        
        # Botão para alternar entre grupos de produtos e resíduos
        toggle_button = ft.ElevatedButton(
            "Ver Grupos de Resíduos" if self.show_product_groups else "Ver Grupos de Produtos",
            on_click=self._toggle_group_type,
            style=ft.ButtonStyle(
                color=ft.colors.WHITE,
                bgcolor=ft.colors.PURPLE_500 if self.show_product_groups else ft.colors.BLUE_500,
            ),
        )
        
        # Criar lista de grupos
        groups_list_items = []
        
        if groups:
            for group in groups:
                groups_list_items.append(self._build_group_item(group))
        else:
            groups_list_items.append(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Icon(ft.icons.FOLDER_OUTLINED, size=50, color=ft.colors.GREY_400),
                            ft.Text("Nenhum grupo encontrado", size=16, color=ft.colors.GREY_500),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10,
                    ),
                    alignment=ft.alignment.center,
                    padding=20,
                    expand=True,
                )
            )
        
        groups_list = ft.ListView(
            controls=groups_list_items,
            spacing=10,
            padding=10,
            expand=True,
        )
        
        # Layout principal
        return ft.Container(
            content=ft.Column(
                controls=[
                    # Cabeçalho
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Text(title, size=20, weight="bold"),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        padding=10,
                    ),
                    
                    # Barra de pesquisa e botão de adicionar
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                search_field,
                                add_button,
                            ],
                            spacing=10,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        padding=ft.padding.only(left=10, right=10, top=5, bottom=5),
                    ),
                    
                    # Botão para alternar tipo de grupo
                    ft.Container(
                        content=toggle_button,
                        alignment=ft.alignment.center,
                        padding=ft.padding.only(bottom=10),
                    ),
                    
                    # Lista de grupos
                    groups_list,
                ],
                spacing=0,
                expand=True,
            ),
            expand=True,
        )
    
    def _build_group_item(self, group):
        """Constrói um item de grupo para a lista"""
        # Obter ícone e cor
        icon_name = getattr(ft.icons, group.get("icon", "FOLDER"))
        color_name = group.get("color", "blue").upper()
        color = getattr(ft.colors, f"{color_name}_500")
        
        # Contar itens no grupo
        item_count = self._count_items_in_group(group["id"])
        
        return ft.Container(
            content=ft.Row(
                controls=[
                    # Ícone do grupo
                    ft.Container(
                        content=ft.Icon(
                            icon_name,
                            color=color,
                            size=30,
                        ),
                        padding=10,
                    ),
                    
                    # Informações do grupo
                    ft.Column(
                        controls=[
                            ft.Text(group["name"], size=16, weight="w500"),
                            ft.Text(
                                group.get("description", "") or f"{item_count} itens neste grupo",
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
                                icon=ft.icons.EDIT_OUTLINED,
                                icon_color=ft.colors.BLUE_500,
                                icon_size=20,
                                tooltip="Editar",
                                on_click=lambda _, g=group: self.navigation.go_to_edit_group(g, self.show_product_groups),
                            ),
                            ft.IconButton(
                                icon=ft.icons.DELETE_OUTLINE,
                                icon_color=ft.colors.RED_500,
                                icon_size=20,
                                tooltip="Excluir",
                                # Modificar para usar a tela de confirmação genérica
                                on_click=lambda _, g=group: self.navigation.go_to_confirm_delete(
                                    "group", 
                                    {**g, "type": "product" if self.show_product_groups else "residue"}
                                ),
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
            on_click=lambda _, g=group: self.navigation.go_to_group_detail(g, self.show_product_groups),
        )
    
    def _on_search_change(self, e):
        """Atualiza o texto de pesquisa e a visualização"""
        self.search_text = e.control.value
        self.navigation.update_view()
    
    def _toggle_group_type(self, e):
        """Alterna entre grupos de produtos e resíduos"""
        self.show_product_groups = not self.show_product_groups
        self.navigation.update_view()
    
    def _count_items_in_group(self, group_id):
        """Conta quantos itens existem em um grupo"""
        if self.show_product_groups:
            return len([p for p in self.data.stock_products if p.get("group_id") == group_id])
        else:
            return len([r for r in self.data.residues if r.get("group_id") == group_id])
    
   
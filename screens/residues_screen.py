import flet as ft
from datetime import datetime

class ResiduesScreen:
    def __init__(self, data, navigation):
        self.data = data
        self.navigation = navigation
        self.search_text = ""
        self.view_mode = "groups"  # Padrão: visualização por grupos
    
    def build(self):
        # Cores modernas
        primary_color = "#6C5CE7"  # Roxo moderno (cor principal para resíduos)
        secondary_color = "#4A6FFF"  # Azul moderno
        accent_color = "#00D2D3"  # Turquesa
        warning_color = "#FFA502"  # Laranja
        danger_color = "#FF6B6B"  # Vermelho suave
        success_color = "#2ED573"  # Verde
        bg_color = "#F8F9FD"  # Fundo claro
        card_bg = "#FFFFFF"  # Branco para cards
        
        # Verificar se os dados estão carregados
        if not hasattr(self.data, 'residues'):
            return ft.Container(
                content=ft.Text("Carregando dados de resíduos..."),
                alignment=ft.alignment.center,
                padding=20
            )
        
        # Barra de pesquisa e botão de adicionar
        search_field = ft.TextField(
            hint_text="Pesquisar resíduos ou grupos...",
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
            tooltip="Adicionar Resíduo",
            on_click=lambda _: self.navigation.go_to_add_residue()
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
        
        # Estatísticas rápidas
        total_residues = len(self.data.residues)
        total_quantity = sum(int(r.get("quantity", 0)) for r in self.data.residues)
        
        # Estatísticas rápidas em formato de cards modernos
        stats_row = ft.Container(
            content=ft.ResponsiveRow([
                ft.Column([
                    self._build_stat_card(
                        "Total de Resíduos", 
                        total_residues, 
                        ft.icons.DELETE_OUTLINE, 
                        primary_color
                    )
                ], col={"xs": 4, "sm": 4, "md": 4, "lg": 4, "xl": 4}),
                ft.Column([
                    self._build_stat_card(
                        "Quantidade Total", 
                        total_quantity, 
                        ft.icons.INVENTORY_2_ROUNDED, 
                        secondary_color
                    )
                ], col={"xs": 4, "sm": 4, "md": 4, "lg": 4, "xl": 4}),
                ft.Column([
                    self._build_stat_card(
                        "Média por Tipo", 
                        round(total_quantity / total_residues, 1) if total_residues > 0 else 0, 
                        ft.icons.ANALYTICS_ROUNDED, 
                        success_color
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
                                # Lista de grupos ou resíduos
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
        print(f"ResiduesScreen._toggle_view chamado com valor: {selected}")  # Debug
        
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
        # Obter grupos de resíduos
        from services.group_service import GroupService
        group_service = GroupService(self.data.firebase, self.data.db)
        groups = group_service.get_all_residue_groups()
        
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
                            on_click=lambda _: self.navigation.go_to_add_group(is_product_group=False),
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
        icon_name = getattr(ft.icons, group.get("icon", "DELETE_OUTLINE"))
        color_name = group.get("color", "purple").upper()
        color = getattr(ft.colors, f"{color_name}_500", primary_color)
        
        # Obter resíduos do grupo usando GroupService
        from services.group_service import GroupService
        group_service = GroupService(self.data.firebase, self.data.db)
        group_id = group.get("id", "")
        group_residues = group_service.get_residues_in_group(group_id)
        
        # Calcular quantidade total
        total_quantity = 0
        for residue in group_residues:
            try:
                if 'quantity' in residue and residue['quantity'] is not None:
                    total_quantity += int(residue['quantity'])
            except (ValueError, TypeError):
                print(f"Erro ao converter quantidade do resíduo {residue.get('name')}: {residue.get('quantity')}")
        
        # Número real de resíduos no grupo
        actual_residue_count = len(group_residues)
        
        # Para depuração
        print(f"Grupo: {group.get('name')}, ID: {group_id}, Resíduos: {actual_residue_count}, Total: {total_quantity}")
        
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
                    # Botão de editar
                    ft.IconButton(
                        icon=ft.icons.EDIT,
                        icon_color="#707070",
                        icon_size=20,
                        tooltip="Editar Grupo",
                        on_click=lambda _, g=group: self._edit_group(g),
                    ),
                    # Botão de excluir
                    ft.IconButton(
                        icon=ft.icons.DELETE_OUTLINE,
                        icon_color="#FF6B6B",
                        icon_size=20,
                        tooltip="Excluir Grupo",
                        on_click=lambda _, g=group: self._confirm_delete_group(g),
                    ),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                # Descrição do grupo (se houver)
                ft.Container(
                    content=ft.Text(
                        group.get("description", ""),
                        size=12,
                        color="#707070"
                    ),
                    margin=ft.margin.only(top=5, bottom=10),
                    visible=bool(group.get("description"))
                ),
                
                # Estatísticas do grupo
                ft.Container(
                    content=ft.Row([
                        # Quantidade de resíduos
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Resíduos", size=11, color="#707070"),
                                ft.Text(f"{actual_residue_count}", size=16, weight="bold", color=color),
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
                        # Disponíveis
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Disponíveis", size=11, color="#707070"),
                                ft.Text(f"{total_quantity}", size=16, weight="bold", color="#2ED573"),
                            ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            expand=True,
                            padding=8,
                            border_radius=6,
                            bgcolor=ft.colors.with_opacity(0.05, "#2ED573")
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
            on_click=lambda _, g=group: self.navigation.go_to_group_detail(g, False),
        )
    
    def _build_full_list_view(self, primary_color, card_bg, warning_color, danger_color):
        """Constrói a visualização de lista completa com layout responsivo"""
        # Filtrar resíduos com base na pesquisa
        filtered_residues = self._filter_residues()
        
        # Criar lista de resíduos com layout responsivo
        if filtered_residues:
            residues_grid = ft.ResponsiveRow(
                controls=[
                    ft.Column([
                        self._build_residue_item(residue, primary_color, card_bg)
                    ], col={"xs": 12, "sm": 6, "md": 4, "lg": 4, "xl": 3})
                    for residue in filtered_residues
                ],
                spacing=10,
                run_spacing=10
            )
            
            return ft.Container(
                content=residues_grid,
                padding=10,
                expand=True
            )
        else:
            return ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(ft.icons.DELETE_OUTLINE, size=50, color="#CCCCCC"),
                        ft.Text("Nenhum resíduo encontrado", size=16, color="#909090"),
                        ft.ElevatedButton(
                            "Adicionar Resíduo",
                            icon=ft.icons.ADD_CIRCLE_OUTLINE,
                            on_click=lambda _: self.navigation.go_to_add_residue(),
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
    
    def _filter_residues(self):
        if not self.search_text:
            return self.data.residues
        
        search_lower = self.search_text.lower()
        return [
            residue for residue in self.data.residues
            if search_lower in residue["name"].lower() or 
               search_lower in residue.get("type", "").lower() or
               search_lower in residue.get("destination", "").lower() or
               search_lower in residue.get("group_name", "").lower()
        ]
    
    def _on_search_change(self, e):
        self.search_text = e.control.value
        self.navigation.update_view()
    
    def _build_residue_item(self, residue, primary_color, card_bg):
        """Constrói um item de resíduo com design moderno"""
        # Obter informações do resíduo
        residue_name = residue.get("name", "Sem nome")
        residue_quantity = residue.get("quantity", "0")
        residue_type = residue.get("type", "N/A")
        residue_entry_date = residue.get("entryDate", "N/A")
        residue_destination = residue.get("destination", "N/A")
        residue_exit_date = residue.get("exitDate", "")
        residue_group = residue.get("group_name", "Sem grupo")
        
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
                            ft.Text(f"Saída: {residue_exit_date if residue_exit_date else 'Não registrada'}", 
                                   size=12, color="#707070"),
                        ], spacing=4, visible=has_exit),
                    ], spacing=12, wrap=True),
                    margin=ft.margin.only(top=8, bottom=8)
                ),
                
                # Grupo
                ft.Row([
                    ft.Icon(ft.icons.FOLDER_OUTLINED, size=14, color="#707070"),
                    ft.Text(f"Grupo: {residue_group}", size=12, color="#707070"),
                ], spacing=4),
                
                # Botões de ação
                ft.Container(
                    content=ft.Row([
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
                                    on_click=lambda _, r=residue: self._confirm_delete_residue(r)
                                ),
                            ]
                        )
                    ], spacing=8, alignment=ft.MainAxisAlignment.END),
                    margin=ft.margin.only(top=10)
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
            margin=ft.margin.only(bottom=8),
            on_click=lambda _, r=residue: self.navigation.select_residue(r),
        )
    
    def _register_residue_exit(self, residue):
        """Navega para a tela de registro de saída de resíduo"""
        self.navigation.go_to_register_exit(residue, "residue")
    
    def _edit_group(self, group):
        """Abre diálogo para editar o grupo"""
        def close_dialog():
            self.navigation.page.dialog.open = False
            self.navigation.page.update()
        
        def save_group(_):
            try:
                # Atualizar grupo
                updated_group = group.copy()
                updated_group["name"] = name_field.value
                updated_group["description"] = description_field.value
                
                # Selecionar cor e ícone
                updated_group["color"] = color_dropdown.value.lower()
                updated_group["icon"] = icon_dropdown.value
                
                # Salvar grupo
                from services.group_service import GroupService
                group_service = GroupService(self.data.firebase, self.data.db)
                success = group_service.update_group(group["id"], updated_group, is_residue=True)
                
                close_dialog()
                
                if success:
                    self.navigation.show_snack_bar("Grupo atualizado com sucesso!", "#2ED573")
                    # Atualizar dados
                    self.data.refresh_data()
                    self.navigation.update_view()
                else:
                    self.navigation.show_snack_bar("Erro ao atualizar grupo", "#FF6B6B")
                
            except Exception as e:
                self.navigation.show_snack_bar(f"Erro: {str(e)}", "#FF6B6B")
        
        # Campos do diálogo
        name_field = ft.TextField(
            label="Nome do Grupo",
            value=group.get("name", ""),
            border_radius=8,
            filled=True,
            prefix_icon=ft.icons.FOLDER
        )
        
        description_field = ft.TextField(
            label="Descrição",
            value=group.get("description", ""),
            border_radius=8,
            multiline=True,
            min_lines=2,
            max_lines=4,
            filled=True,
            prefix_icon=ft.icons.DESCRIPTION
        )
        
        # Dropdown para cor
        color_options = [
            ft.dropdown.Option("purple", "Roxo"),
            ft.dropdown.Option("blue", "Azul"),
            ft.dropdown.Option("green", "Verde"),
            ft.dropdown.Option("red", "Vermelho"),
            ft.dropdown.Option("orange", "Laranja"),
            ft.dropdown.Option("teal", "Turquesa"),
            ft.dropdown.Option("amber", "Âmbar"),
            ft.dropdown.Option("pink", "Rosa"),
        ]
        
        color_dropdown = ft.Dropdown(
            label="Cor",
            options=color_options,
            value=group.get("color", "purple").lower(),
            border_radius=8,
            filled=True,
            prefix_icon=ft.icons.COLOR_LENS
        )
        
        # Dropdown para ícone
        icon_options = [
            ft.dropdown.Option("DELETE_OUTLINE", "Resíduo"),
            ft.dropdown.Option("RECYCLING", "Reciclagem"),
            ft.dropdown.Option("INVENTORY_2_ROUNDED", "Estoque"),
            ft.dropdown.Option("SCIENCE", "Laboratório"),
            ft.dropdown.Option("CATEGORY", "Categoria"),
            ft.dropdown.Option("FOLDER", "Pasta"),
        ]
        
        icon_dropdown = ft.Dropdown(
            label="Ícone",
            options=icon_options,
            value=group.get("icon", "DELETE_OUTLINE"),
            border_radius=8,
            filled=True,
            prefix_icon=ft.icons.EMOJI_SYMBOLS
        )
        
        # Criar diálogo
        dialog = ft.AlertDialog(
            title=ft.Text(f"Editar Grupo - {group.get('name', '')}", weight="bold"),
            content=ft.Column(
                controls=[
                    name_field,
                    description_field,
                    color_dropdown,
                    icon_dropdown,
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
                        bgcolor="#6C5CE7",
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
    
    def _confirm_delete_residue(self, residue):
        """Navega para a tela de confirmação de exclusão de resíduo"""
        print(f"Solicitando confirmação para excluir o resíduo: {residue['name']}")
        self.navigation.go_to_confirm_delete("residue", residue)

    def _confirm_delete_group(self, group):
        print(f"Solicitando confirmação para excluir o grupo: {group['name']}")
        # Criar uma cópia do grupo para não modificar o original
        group_copy = group.copy()
        # Definir tipo de grupo explicitamente
        group_copy["group_type"] = "residue"
        self.navigation.go_to_confirm_delete("group", group_copy)
    
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
            total_value_formatted = f"R$ {total_value:.2f}".replace('.', ',')
        except (ValueError, TypeError):
            total_value_formatted = "R$ 0,00"
        
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
                        
                        # Preço unitário (se houver)
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
                        ], col={"xs": 6, "sm": 6, "md": 4, "lg": 4, "xl": 4}, visible=bool(residue_unit_price)),
                        
                        # Valor total (se houver preço unitário)
                        ft.Column([
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("Valor Total", size=12, color="#707070"),
                                    ft.Row([
                                        ft.Text(total_value_formatted, size=18, weight="bold", color="#2ED573"),
                                    ], spacing=4)
                                ], spacing=4),
                                padding=10,
                                border_radius=8,
                                bgcolor=ft.colors.with_opacity(0.05, "#2ED573")
                            )
                        ], col={"xs": 12, "sm": 12, "md": 4, "lg": 4, "xl": 4}, visible=bool(residue_unit_price)),
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
import flet as ft
import traceback

class SelectGroupScreen:
    def __init__(self, data, navigation, group_type, all_groups, card_id=None):
        self.data = data
        self.navigation = navigation
        self.group_type = group_type  # "product" ou "residue"
        self.all_groups = all_groups
        self.card_id = card_id  # ID do card sendo editado, ou None para novo card
        self.title = "Selecionar Grupo de Produtos" if group_type == "product" else "Selecionar Grupo de Resíduos"
        
    def build(self):
        # Obter serviço de configuração de cards
        from services.card_config_service import CardConfigService
        self.card_config_service = CardConfigService(self.data.firebase, self.data.db)
        
        # Obter IDs de grupos já no dashboard
        if self.group_type == "product":
            self.dashboard_group_ids = self.card_config_service.get_dashboard_product_group_ids()
            # Garantir que estamos usando os grupos de produtos
            self.all_groups = self.data.product_groups
        else:
            self.dashboard_group_ids = self.card_config_service.get_dashboard_residue_group_ids()
            # Garantir que estamos usando os grupos de resíduos
            self.all_groups = self.data.residue_groups
        
        # Imprimir para debug
        print(f"Tipo de grupo: {self.group_type}")
        print(f"Total de grupos disponíveis: {len(self.all_groups)}")
        print(f"Grupos no dashboard: {self.dashboard_group_ids}")
        
        # Filtrar grupos que não estão no dashboard (exceto o que está sendo editado)
        available_groups = []
        for group in self.all_groups:
            # Se estamos editando um card, incluir o grupo atual e excluir outros já no dashboard
            if self.card_id:
                if group["id"] == self.card_id or group["id"] not in self.dashboard_group_ids:
                    available_groups.append(group)
            # Se estamos adicionando um novo card, excluir todos os grupos já no dashboard
            else:
                if group["id"] not in self.dashboard_group_ids:
                    available_groups.append(group)
        
        # Imprimir para debug
        print(f"Grupos disponíveis para seleção: {len(available_groups)}")
        for g in available_groups:
            print(f"  - {g.get('name', 'Sem nome')} (ID: {g.get('id', 'Sem ID')})")
        
        # Construir a interface
        return ft.Container(
            content=ft.Column([
                # Cabeçalho
                ft.Container(
                    content=ft.Row([
                        ft.IconButton(
                            icon=ft.icons.ARROW_BACK,
                            on_click=lambda _: self.navigation.go_back()
                        ),
                        ft.Text(self.title, size=20, weight="bold"),
                    ]),
                    padding=10
                ),
                
                # Mensagem explicativa
                ft.Container(
                    content=ft.Text(
                        "Selecione um grupo existente para adicionar ao dashboard:",
                        size=14
                    ),
                    padding=ft.padding.only(left=10, right=10, bottom=10)
                ),
                
                # Lista de grupos disponíveis
                ft.Container(
                    content=ft.Column([
                        self._build_group_item(group) for group in available_groups
                    ] if available_groups else [
                        ft.Container(
                            content=ft.Text(
                                "Nenhum grupo disponível. Todos os grupos já estão no dashboard ou não existem grupos cadastrados.",
                                size=14,
                                color=ft.colors.GREY_700,
                                text_align=ft.TextAlign.CENTER
                            ),
                            padding=20,
                            alignment=ft.alignment.center
                        )
                    ]),
                    padding=10,
                    expand=True
                ),
                
                # Botão para voltar
                ft.Container(
                    content=ft.ElevatedButton(
                        "Voltar",
                        on_click=lambda _: self.navigation.go_back(),
                        width=200
                    ),
                    padding=10,
                    alignment=ft.alignment.center
                )
            ]),
            expand=True
        )
    
    def _build_group_item(self, group):
        """Constrói um item de grupo na lista"""
        # Obter ícone e cor do grupo
        icon_name = group.get("icon", "INVENTORY_2_ROUNDED" if self.group_type == "product" else "DELETE_OUTLINE")
        color_name = group.get("color", "BLUE_500" if self.group_type == "product" else "PURPLE_500")
        
        # Converter para objetos flet
        icon = getattr(ft.icons, icon_name, ft.icons.INVENTORY_2_ROUNDED if self.group_type == "product" else ft.icons.DELETE_OUTLINE)
        color = getattr(ft.colors, color_name, ft.colors.BLUE_500 if self.group_type == "product" else ft.colors.PURPLE_500)
        
        # Verificar se o grupo já está no dashboard
        is_selected = group["id"] == self.card_id if self.card_id else False
        
        # Contar quantos itens estão neste grupo
        item_count = 0
        if self.group_type == "product":
            items = self.data.group_service.get_products_in_group(group["id"])
            item_count = len(items) if items else 0
        else:
            items = self.data.group_service.get_residues_in_group(group["id"])
            item_count = len(items) if items else 0
        
        return ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Icon(icon, size=24, color=color),
                    padding=10,
                    border_radius=30,
                    bgcolor=ft.colors.with_opacity(0.1, color)
                ),
                ft.Column([
                    ft.Text(group.get("name", ""), size=16, weight="bold"),
                    ft.Row([
                        ft.Text(
                            group.get("description", "") or f"Grupo de {'produtos' if self.group_type == 'product' else 'resíduos'}",
                            size=12,
                            color=ft.colors.GREY_700
                        ),
                        ft.Container(
                            content=ft.Text(
                                f"{item_count} {'produtos' if self.group_type == 'product' else 'resíduos'}",
                                size=12,
                                color=ft.colors.GREY_700
                            ),
                            padding=ft.padding.only(left=8, right=8, top=2, bottom=2),
                            border_radius=12,
                            bgcolor=ft.colors.GREY_100
                        )
                    ], spacing=8)
                ], spacing=2, expand=True),
                ft.ElevatedButton(
                    "Selecionar",
                    on_click=lambda _, g=group: self._add_group_to_dashboard(g),
                    bgcolor=ft.colors.GREEN_500 if is_selected else None,
                    color=ft.colors.WHITE if is_selected else None
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            border=ft.border.all(1, ft.colors.GREY_300),
            border_radius=8,
            padding=10,
            margin=ft.margin.only(bottom=10)
        )
    
    def _add_group_to_dashboard(self, group):
        """Adiciona o grupo selecionado ao dashboard"""
        try:
            # Se estamos editando um card existente, primeiro remover o grupo atual
            if self.card_id:
                if self.group_type == "product":
                    self.card_config_service.remove_product_group_from_dashboard(self.card_id)
                else:
                    self.card_config_service.remove_residue_group_from_dashboard(self.card_id)
            
            # Adicionar o novo grupo
            success = False
            if self.group_type == "product":
                success = self.card_config_service.add_product_group_to_dashboard(group)
            else:
                success = self.card_config_service.add_residue_group_to_dashboard(group)
            
            if success:
                # Mostrar mensagem de sucesso
                self.navigation.show_snack_bar(
                    f"Grupo '{group.get('name', '')}' adicionado ao dashboard",
                    color=ft.colors.GREEN_500
                )
                # Voltar para o dashboard
                self.navigation.go_back()
            else:
                # Mostrar mensagem de erro
                self.navigation.show_snack_bar(
                    "Erro ao adicionar grupo ao dashboard",
                    color=ft.colors.RED_500
                )
        except Exception as e:
            print(f"Erro ao adicionar grupo ao dashboard: {e}")
            traceback.print_exc()
            self.navigation.show_snack_bar(
                f"Erro: {str(e)}",
                color=ft.colors.RED_500
            )
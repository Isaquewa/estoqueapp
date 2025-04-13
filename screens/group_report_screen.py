import flet as ft
from datetime import datetime, timedelta

class GroupReportScreen:
    def __init__(self, data, navigation):
        self.data = data
        self.navigation = navigation
        self.selected_period = "30"  # Padrão: 30 dias
        self.search_text = ""
        self.show_details = False  # Controla se mostra detalhes expandidos
        self.group_type = "product"  # Padrão: grupos de produtos
    
    def build(self):
        # Obter grupos de produtos ou resíduos
        from services.group_service import GroupService
        group_service = GroupService(self.data.firebase, self.data.db)
        
        if self.group_type == "product":
            groups = group_service.get_all_product_groups()
        else:
            groups = group_service.get_all_residue_groups()
        
        # Filtrar grupos por texto de busca
        if self.search_text:
            search_lower = self.search_text.lower()
            groups = [
                group for group in groups
                if search_lower in group.get("name", "").lower() or
                   search_lower in group.get("description", "").lower()
            ]
        
        # Filtro de período
        period_dropdown = ft.Dropdown(
            options=[
                ft.dropdown.Option("7", "Últimos 7 dias"),
                ft.dropdown.Option("30", "Últimos 30 dias"),
                ft.dropdown.Option("90", "Últimos 90 dias"),
                ft.dropdown.Option("365", "Último ano"),
            ],
            value=self.selected_period,
            on_change=self._on_period_change,
            width=200,
        )
        
        # Filtro de tipo
        type_dropdown = ft.Dropdown(
            options=[
                ft.dropdown.Option("product", "Produtos"),
                ft.dropdown.Option("residue", "Resíduos"),
            ],
            value=self.group_type,
            on_change=self._on_type_change,
            width=150,
        )
        
        # Campo de busca
        search_field = ft.TextField(
            hint_text="Buscar por grupo...",
            value=self.search_text,
            on_change=self._on_search_change,
            prefix_icon=ft.icons.SEARCH,
            width=200,
        )
        
        # Botões de ação
        export_button = ft.ElevatedButton(
            "Exportar Relatório",
            icon=ft.icons.DOWNLOAD,
            on_click=self._export_report,
        )
        
        print_button = ft.ElevatedButton(
            "Imprimir",
            icon=ft.icons.PRINT,
            on_click=self._print_report,
        )
        
        details_button = ft.ElevatedButton(
        "Mostrar Detalhes" if not self.show_details else "Ocultar Detalhes",
        icon=ft.icons.DETAILS if not self.show_details else ft.icons.LIST,
        on_click=self._toggle_details,
        )
        
        # Construir cards de grupos
        group_cards = []
        
        for group in groups:
            # Obter itens deste grupo
            if self.group_type == "product":
                items = group_service.get_products_in_group(group["id"])
            else:
                items = group_service.get_residues_by_group(group["id"])
            
            if items:
                # Calcular estatísticas do grupo
                if self.group_type == "product":
                    # Estatísticas para produtos
                    total_quantity = sum(p.get("quantity", 0) for p in items)
                    total_value = sum(p.get("value", 0) * p.get("quantity", 0) for p in items)
                    expiring_count = len([p for p in items if p in self.data.expiring_products])
                    low_stock_count = len([p for p in items if p in self.data.low_stock_products])
                    
                    # Calcular uso no período selecionado
                    period_days = int(self.selected_period)
                    usage_data = self._calculate_group_usage(items, period_days)
                    
                    group_cards.append(
                        self._build_product_group_card(
                            group, items, total_quantity, total_value, 
                            expiring_count, low_stock_count, usage_data
                        )
                    )
                else:
                    # Estatísticas para resíduos
                    total_quantity = sum(r.get("quantity", 0) for r in items)
                    
                    # Calcular movimentação no período selecionado
                    period_days = int(self.selected_period)
                    movement_data = self._calculate_residue_movement(items, period_days)
                    
                    group_cards.append(
                        self._build_residue_group_card(
                            group, items, total_quantity, movement_data
                        )
                    )
        
        # Verificar se há grupos
        if not group_cards:
            group_cards.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.icons.CATEGORY_OUTLINED, size=40, color=ft.colors.GREY_400),
                        ft.Text(f"Nenhum grupo de {self.group_type} encontrado", 
                               size=14, color=ft.colors.GREY_700),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=20,
                    alignment=ft.alignment.center,
                )
            )
        
        # Estatísticas gerais
        stats_row = None
        if self.group_type == "product":
            total_products = sum(len(group_service.get_products_in_group(g["id"])) for g in groups)
            total_stock = sum(sum(p.get("quantity", 0) for p in group_service.get_products_in_group(g["id"])) for g in groups)
            total_groups = len(groups)
            
            stats_row = ft.Container(
                content=ft.Row([
                    self._build_stat_card(
                        "Total de Grupos", 
                        total_groups, 
                        ft.icons.CATEGORY, 
                        ft.colors.BLUE_500
                    ),
                    self._build_stat_card(
                        "Total de Produtos", 
                        total_products, 
                        ft.icons.INVENTORY_2_ROUNDED, 
                        ft.colors.GREEN_500
                    ),
                    self._build_stat_card(
                        "Estoque Total", 
                        total_stock, 
                        ft.icons.ANALYTICS_ROUNDED, 
                        ft.colors.PURPLE_500
                    ),
                ]),
                padding=10,
            )
        else:
            total_residues = sum(len(group_service.get_residues_by_group(g["id"])) for g in groups)
            total_quantity = sum(sum(r.get("quantity", 0) for r in group_service.get_residues_by_group(g["id"])) for g in groups)
            total_groups = len(groups)
            
            stats_row = ft.Container(
                content=ft.Row([
                    self._build_stat_card(
                        "Total de Grupos", 
                        total_groups, 
                        ft.icons.CATEGORY, 
                        ft.colors.BLUE_500
                    ),
                    self._build_stat_card(
                        "Total de Resíduos", 
                        total_residues, 
                        ft.icons.DELETE_OUTLINE, 
                        ft.colors.PURPLE_500
                    ),
                    self._build_stat_card(
                        "Quantidade Total", 
                        total_quantity, 
                        ft.icons.ANALYTICS_ROUNDED, 
                        ft.colors.GREEN_500
                    ),
                ]),
                padding=10,
            )
        
        return ft.Column(
            [
                # Cabeçalho
                ft.Container(
                    content=ft.Row(
                        [
                            ft.IconButton(
                                icon=ft.icons.ARROW_BACK,
                                on_click=lambda _: self.navigation.go_back(),
                            ),
                            ft.Text("Relatório por Grupos", size=20, weight="bold"),
                        ]
                    ),
                    padding=10,
                ),
                
                # Filtros e ações
                ft.Container(
                    content=ft.Column([
                        ft.Row(
                            [
                                ft.Text("Período:", size=14),
                                period_dropdown,
                                ft.Text("Tipo:", size=14),
                                type_dropdown,
                            ],
                            alignment=ft.MainAxisAlignment.START,
                            spacing=10,
                        ),
                        ft.Row(
                            [
                                search_field,
                                details_button,
                                export_button,
                                print_button,
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                    ], spacing=10),
                    padding=ft.padding.only(left=20, right=20, bottom=10),
                ),
                
                # Estatísticas gerais
                stats_row,
                
                # Lista de grupos
                ft.Container(
                    content=ft.Column(
                        group_cards,
                        spacing=15,
                        scroll=ft.ScrollMode.AUTO,
                    ),
                    padding=20,
                    expand=True,
                ),
            ],
            expand=True,
        )
    
    def _on_period_change(self, e):
        """Atualiza o período selecionado e reconstrói o relatório"""
        self.selected_period = e.control.value
        self.navigation.update_view()
    
    def _on_type_change(self, e):
        """Atualiza o tipo de grupo e reconstrói o relatório"""
        self.group_type = e.control.value
        self.navigation.update_view()
    
    def _on_search_change(self, e):
        """Atualiza o texto de busca"""
        self.search_text = e.control.value
        self.navigation.update_view()
    
    def _toggle_details(self, e):
        """Alterna a exibição de detalhes"""
        self.show_details = not self.show_details
        self.navigation.update_view()
    
    def _calculate_group_usage(self, products, period_days):
        """Calcula o uso de produtos de um grupo no período especificado"""
        try:
            # Obter histórico de movimentação
            history = self.data.get_product_movement_history(days=period_days)
            
            # Filtrar para produtos deste grupo
            product_ids = [p["id"] for p in products]
            group_history = [h for h in history if h["productId"] in product_ids]
            
            # Calcular uso total
            total_usage = sum(h["quantity"] for h in group_history if h["type"] == "exit")
            
            # Calcular uso médio diário
            avg_daily_usage = total_usage / period_days if period_days > 0 else 0
            
            # Calcular dias estimados até acabar o estoque
            total_quantity = sum(p.get("quantity", 0) for p in products)
            days_remaining = total_quantity / avg_daily_usage if avg_daily_usage > 0 else float('inf')
            
            return {
                "total_usage": total_usage,
                "avg_daily_usage": round(avg_daily_usage, 2),
                "days_remaining": round(days_remaining) if days_remaining != float('inf') else "∞"
            }
        except Exception as e:
            print(f"Erro ao calcular uso do grupo: {e}")
            import traceback
            traceback.print_exc()
            return {
                "total_usage": 0,
                "avg_daily_usage": 0,
                "days_remaining": "∞"
            }
    
    def _calculate_residue_movement(self, residues, period_days):
        """Calcula a movimentação de resíduos de um grupo no período especificado"""
        try:
            # Obter histórico de movimentação
            cursor = self.data.db.conn.cursor()
            
            # Calcular data limite
            cutoff_date = datetime.now() - timedelta(days=period_days)
            cutoff_timestamp = cutoff_date.timestamp()
            
            # Obter IDs dos resíduos
            residue_ids = [r["id"] for r in residues]
            residue_ids_str = ",".join(f"'{rid}'" for rid in residue_ids)
            
            # Consultar entradas
            cursor.execute(f'''
            SELECT SUM(quantity) FROM residue_history 
            WHERE type = 'entry' AND timestamp >= ? AND itemId IN ({residue_ids_str})
            ''', (cutoff_timestamp,))
            
            total_entries = cursor.fetchone()[0] or 0
            
            # Consultar saídas
            cursor.execute(f'''
            SELECT SUM(quantity) FROM residue_history 
            WHERE type = 'exit' AND timestamp >= ? AND itemId IN ({residue_ids_str})
            ''', (cutoff_timestamp,))
            
            total_exits = cursor.fetchone()[0] or 0
            
            return {
                "total_entries": total_entries,
                "total_exits": total_exits,
                "net_change": total_entries - total_exits
            }
        except Exception as e:
            print(f"Erro ao calcular movimentação de resíduos: {e}")
            import traceback
            traceback.print_exc()
            return {
                "total_entries": 0,
                "total_exits": 0,
                "net_change": 0
            }
    
    def _build_stat_card(self, title, value, icon, color):
        """Cria um card de estatística"""
        return ft.Container(
            content=ft.Row([
                ft.Icon(icon, color=color, size=24),
                ft.Column([
                    ft.Text(title, size=12, color=ft.colors.GREY_700),
                    ft.Text(str(value), size=18, weight="bold"),
                ], spacing=2),
            ], spacing=10),
            padding=15,
            border_radius=10,
            bgcolor=ft.colors.WHITE,
            expand=True,
        )
    
    def _build_product_group_card(self, group, products, total_quantity, total_value, 
                                expiring_count, low_stock_count, usage_data):
        """Constrói um card de relatório para um grupo de produtos"""
        # Criar gráfico de uso (simplificado para texto neste exemplo)
        usage_info = ft.Column(
            [
                ft.Text(f"Uso total no período: {usage_data['total_usage']} unidades", size=14),
                ft.Text(f"Uso médio diário: {usage_data['avg_daily_usage']} unidades", size=14),
                ft.Text(f"Dias estimados até acabar: {usage_data['days_remaining']}", size=14),
            ],
            spacing=5,
        )
        
        # Criar lista de produtos
        product_list = ft.Column(spacing=5)
        
        # Mostrar todos os produtos se detalhes estiverem ativados, senão apenas os 5 primeiros
        display_products = products if self.show_details else products[:5]
        
        for product in display_products:
            product_list.controls.append(
                ft.Text(
                    f"{product['name']} - {product.get('quantity', 0)} unidades - Validade: {product.get('expiry', 'N/A')}",
                    size=12,
                )
            )
        
        if len(products) > 5 and not self.show_details:
            product_list.controls.append(
                ft.Text(f"... e mais {len(products) - 5} produtos", size=12, italic=True)
            )
        
        return ft.Container(
            content=ft.Column(
                [
                    # Cabeçalho do grup
                    ft.Icon(
                        getattr(ft.icons, group.get("icon", "INVENTORY_2_ROUNDED")),
                        color=getattr(
                            ft.colors, 
                            f"{group.get('color', 'BLUE').upper().replace('_500', '')}_500",
                            ft.colors.BLUE_500  # Valor padrão caso a cor não exista
                        )
                    ),
                    
                    ft.Divider(),
                    
                    # Estatísticas principais
                    ft.Row(
                        [
                            ft.Column(
                                [
                                    ft.Text("Quantidade Total", size=14),
                                    ft.Text(f"{total_quantity}", size=18, weight="bold"),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            ft.VerticalDivider(width=1),
                            ft.Column(
                                [
                                    ft.Text("Próx. Vencimento", size=14),
                                    ft.Text(
                                        f"{expiring_count}",
                                        size=18,
                                        weight="bold",
                                        color=ft.colors.ORANGE_500 if expiring_count > 0 else None,
                                    ),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            ft.VerticalDivider(width=1),
                            ft.Column(
                                [
                                    ft.Text("Estoque Baixo", size=14),
                                    ft.Text(
                                        f"{low_stock_count}",
                                        size=18,
                                        weight="bold",
                                        color=ft.colors.RED_500 if low_stock_count > 0 else None,
                                    ),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_AROUND,
                    ),
                    
                    ft.Divider(),
                    
                    # Uso e tendências
                    ft.Text("Uso e Tendências", size=16, weight="bold"),
                    usage_info,
                    
                    ft.Divider(),
                    
                    # Lista de produtos
                    ft.Text("Produtos neste grupo:", size=16, weight="bold"),
                    product_list,
                    
                    # Botão para ver detalhes
                    ft.Container(
                        content=ft.ElevatedButton(
                            "Ver Detalhes Completos",
                            on_click=lambda _, g=group: self.navigation.go_to_group_detail(g, True),
                        ),
                        alignment=ft.alignment.center,
                        padding=ft.padding.only(top=10),
                    ),
                ],
                spacing=10,
            ),
            padding=20,
            border_radius=10,
            bgcolor=ft.colors.WHITE,
            border=ft.border.all(1, ft.colors.GREY_300),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=4,
                color=ft.colors.GREY_300,
            ),
        )
    
    def _build_residue_group_card(self, group, residues, total_quantity, movement_data):
        """Constrói um card de relatório para um grupo de resíduos"""
        # Criar informações de movimentação
        movement_info = ft.Column(
            [
                ft.Text(f"Entradas no período: {movement_data['total_entries']} unidades", size=14),
                ft.Text(f"Saídas no período: {movement_data['total_exits']} unidades", size=14),
                ft.Text(
                    f"Saldo no período: {movement_data['net_change']} unidades", 
                    size=14,
                    color=ft.colors.GREEN_500 if movement_data['net_change'] >= 0 else ft.colors.RED_500
                ),
            ],
            spacing=5,
        )
        
        # Criar lista de resíduos
        residue_list = ft.Column(spacing=5)
        
        # Mostrar todos os resíduos se detalhes estiverem ativados, senão apenas os 5 primeiros
        display_residues = residues if self.show_details else residues[:5]
        
        for residue in display_residues:
            residue_list.controls.append(
                ft.Text(
                    f"{residue['name']} - {residue.get('quantity', 0)} unidades - Tipo: {residue.get('type', 'N/A')}",
                    size=12,
                )
            )
        
        if len(residues) > 5 and not self.show_details:
            residue_list.controls.append(
                ft.Text(f"... e mais {len(residues) - 5} resíduos", size=12, italic=True)
            )
        
        return ft.Container(
            content=ft.Column(
                [
                    # Cabeçalho do grupo
                    ft.Row(
                        [
                            ft.Icon(getattr(ft.icons, group.get("icon", "DELETE_OUTLINE")), 
                                   color=getattr(ft.colors, f"{group.get('color', 'PURPLE').upper()}_500")),
                            ft.Text(group["name"], size=18, weight="bold"),
                            ft.Text(f"{len(residues)} resíduos", size=14),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    
                    ft.Divider(),
                    
                    # Estatísticas principais
                    ft.Row(
                        [
                            ft.Column(
                                [
                                    ft.Text("Quantidade Total", size=14),
                                    ft.Text(f"{total_quantity}", size=18, weight="bold"),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            ft.VerticalDivider(width=1),
                            ft.Column(
                                [
                                    ft.Text("Entradas", size=14),
                                    ft.Text(
                                        f"{movement_data['total_entries']}",
                                        size=18,
                                        weight="bold",
                                    ),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            ft.VerticalDivider(width=1),
                            ft.Column(
                                [
                                    ft.Text("Saídas", size=14),
                                    ft.Text(
                                        f"{movement_data['total_exits']}",
                                        size=18,
                                        weight="bold",
                                    ),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_AROUND,
                    ),
                    
                    ft.Divider(),
                    
                    # Movimentação
                    ft.Text("Movimentação no Período", size=16, weight="bold"),
                    movement_info,
                    
                    ft.Divider(),
                    
                    # Lista de resíduos
                    ft.Text("Resíduos neste grupo:", size=16, weight="bold"),
                    residue_list,
                    
                    # Botão para ver detalhes
                    ft.Container(
                        content=ft.ElevatedButton(
                            "Ver Detalhes Completos",
                            on_click=lambda _, g=group: self.navigation.go_to_group_detail(g, False),
                        ),
                        alignment=ft.alignment.center,
                        padding=ft.padding.only(top=10),
                    ),
                ],
                spacing=10,
            ),
            padding=20,
            border_radius=10,
            bgcolor=ft.colors.WHITE,
            border=ft.border.all(1, ft.colors.GREY_300),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=4,
                color=ft.colors.GREY_300,
            ),
        )
    
    def _export_report(self, e):
        """Exporta o relatório para um arquivo CSV"""
        try:
            import csv
            import os
            from datetime import datetime
            
            # Criar diretório de relatórios se não existir
            os.makedirs("reports", exist_ok=True)
            
            # Nome do arquivo com timestamp
            filename = f"reports/group_report_{self.group_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            # Obter dados para o relatório
            from services.group_service import GroupService
            group_service = GroupService(self.data.firebase, self.data.db)
            
            if self.group_type == "product":
                groups = group_service.get_all_product_groups()
            else:
                groups = group_service.get_all_residue_groups()
            
            # Filtrar grupos por texto de busca
            if self.search_text:
                search_lower = self.search_text.lower()
                groups = [
                    group for group in groups
                    if search_lower in group.get("name", "").lower() or
                       search_lower in group.get("description", "").lower()
                ]
            
            # Escrever arquivo CSV
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                if self.group_type == "product":
                    # Cabeçalho para produtos
                    writer.writerow([
                        "Grupo", "Total de Produtos", "Quantidade Total", "Valor Total",
                        "Produtos Vencendo", "Produtos com Estoque Baixo",
                        "Uso Total no Período", "Uso Médio Diário", "Dias Estimados Restantes"
                    ])
                    
                    # Dados de cada grupo
                    for group in groups:
                        products = group_service.get_products_by_group(group["id"])
                        
                        if products:
                            total_quantity = sum(p.get("quantity", 0) for p in products)
                            total_value = sum(p.get("value", 0) * p.get("quantity", 0) for p in products)
                            expiring_count = len([p for p in products if p in self.data.expiring_products])
                            low_stock_count = len([p for p in products if p in self.data.low_stock_products])
                            
                            period_days = int(self.selected_period)
                            usage_data = self._calculate_group_usage(products, period_days)
                            
                            writer.writerow([
                                group["name"],
                                len(products),
                                total_quantity,
                                f"{total_value:.2f}",
                                expiring_count,
                                low_stock_count,
                                usage_data["total_usage"],
                                usage_data["avg_daily_usage"],
                                usage_data["days_remaining"]
                            ])
                else:
                    # Cabeçalho para resíduos
                    writer.writerow([
                        "Grupo", "Total de Resíduos", "Quantidade Total",
                        "Entradas no Período", "Saídas no Período", "Saldo no Período"
                    ])
                    
                    # Dados de cada grupo
                    for group in groups:
                        residues = group_service.get_residues_by_group(group["id"])
                        
                        if residues:
                            total_quantity = sum(r.get("quantity", 0) for r in residues)
                            
                            period_days = int(self.selected_period)
                            movement_data = self._calculate_residue_movement(residues, period_days)
                            
                            writer.writerow([
                                group["name"],
                                len(residues),
                                total_quantity,
                                movement_data["total_entries"],
                                movement_data["total_exits"],
                                movement_data["net_change"]
                            ])
            
            self.navigation.show_snack_bar(f"Relatório exportado para {filename}")
        except Exception as e:
            print(f"Erro ao exportar relatório: {e}")
            import traceback
            traceback.print_exc()
            self.navigation.show_snack_bar(
                f"Erro ao exportar relatório: {str(e)}",
                ft.colors.RED_500
            )
    
    def _print_report(self, e):
        """Prepara o relatório para impressão"""
        try:
            import tempfile
            import webbrowser
            import os
            from datetime import datetime
            
            # Obter dados para o relatório
            from services.group_service import GroupService
            group_service = GroupService(self.data.firebase, self.data.db)
            
            if self.group_type == "product":
                groups = group_service.get_all_product_groups()
                report_title = "Relatório de Grupos de Produtos"
            else:
                groups = group_service.get_all_residue_groups()
                report_title = "Relatório de Grupos de Resíduos"
            
            # Filtrar grupos por texto de busca
            if self.search_text:
                search_lower = self.search_text.lower()
                groups = [
                    group for group in groups
                    if search_lower in group.get("name", "").lower() or
                       search_lower in group.get("description", "").lower()
                ]
            
            # Criar arquivo HTML temporário
            fd, path = tempfile.mkstemp(suffix='.html')
            
            with os.fdopen(fd, 'w') as tmp:
                # Escrever cabeçalho HTML
                tmp.write(f'''
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <title>{report_title}</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 20px; }}
                        .header {{ text-align: center; margin-bottom: 20px; }}
                        .group-card {{ border: 1px solid #ddd; padding: 15px; margin-bottom: 20px; border-radius: 5px; }}
                        .group-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }}
                        .group-stats {{ display: flex; justify-content: space-around; margin: 15px 0; }}
                        .stat-item {{ text-align: center; }}
                        .divider {{ border-top: 1px solid #ddd; margin: 10px 0; }}
                        .item-list {{ margin-top: 10px; }}
                        .footer {{ text-align: center; margin-top: 30px; font-size: 12px; color: #777; }}
                        @media print {{
                            .no-print {{ display: none; }}
                            button {{ display: none; }}
                        }}
                    </style>
                </head>
                <body>
                    <div class="header">
                        <h1>{report_title}</h1>
                        <p>Período: Últimos {self.selected_period} dias • Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
                        {f"<p>Filtro: {self.search_text}</p>" if self.search_text else ""}
                    </div>
                    
                    <div class="no-print">
                        <button onclick="window.print()">Imprimir</button>
                        <button onclick="window.close()">Fechar</button>
                    </div>
                ''')
                
                # Adicionar cards de grupos
                for group in groups:
                    if self.group_type == "product":
                        products = group_service.get_products_by_group(group["id"])
                        
                        if products:
                            total_quantity = sum(p.get("quantity", 0) for p in products)
                            total_value = sum(p.get("value", 0) * p.get("quantity", 0) for p in products)
                            expiring_count = len([p for p in products if p in self.data.expiring_products])
                            low_stock_count = len([p for p in products if p in self.data.low_stock_products])
                            
                            period_days = int(self.selected_period)
                            usage_data = self._calculate_group_usage(products, period_days)
                            
                            tmp.write(f'''
                            <div class="group-card">
                                <div class="group-header">
                                    <h2>{group["name"]}</h2>
                                    <span>{len(products)} produtos</span>
                                </div>
                                
                                <div class="group-stats">
                                    <div class="stat-item">
                                        <h3>Quantidade Total</h3>
                                        <p>{total_quantity}</p>
                                    </div>
                                    <div class="stat-item">
                                        <h3>Valor Total</h3>
                                        <p>R$ {total_value:.2f}</p>
                                    </div>
                                    <div class="stat-item">
                                        <h3>Próx. Vencimento</h3>
                                        <p>{expiring_count}</p>
                                    </div>
                                    <div class="stat-item">
                                        <h3>Estoque Baixo</h3>
                                        <p>{low_stock_count}</p>
                                    </div>
                                </div>
                                
                                <div class="divider"></div>
                                
                                <h3>Uso e Tendências</h3>
                                <p>Uso total no período: {usage_data["total_usage"]} unidades</p>
                                <p>Uso médio diário: {usage_data["avg_daily_usage"]} unidades</p>
                                <p>Dias estimados até acabar: {usage_data["days_remaining"]}</p>
                                
                                <div class="divider"></div>
                                
                                <h3>Produtos neste grupo:</h3>
                                <div class="item-list">
                            ''')
                            
                            # Adicionar lista de produtos
                            for product in products:
                                tmp.write(f'''
                                <p>{product["name"]} - {product.get("quantity", 0)} unidades - 
                                   Validade: {product.get("expiry", "N/A")}</p>
                                ''')
                            
                            tmp.write('</div></div>')  # Fechar div do grupo
                    else:
                        # Código para grupos de resíduos
                        residues = group_service.get_residues_by_group(group["id"])
                        
                        if residues:
                            total_quantity = sum(r.get("quantity", 0) for r in residues)
                            
                            period_days = int(self.selected_period)
                            movement_data = self._calculate_residue_movement(residues, period_days)
                            
                            tmp.write(f'''
                            <div class="group-card">
                                <div class="group-header">
                                    <h2>{group["name"]}</h2>
                                    <span>{len(residues)} resíduos</span>
                                </div>
                                
                                <div class="group-stats">
                                    <div class="stat-item">
                                        <h3>Quantidade Total</h3>
                                        <p>{total_quantity}</p>
                                    </div>
                                    <div class="stat-item">
                                        <h3>Entradas</h3>
                                        <p>{movement_data["total_entries"]}</p>
                                    </div>
                                    <div class="stat-item">
                                        <h3>Saídas</h3>
                                        <p>{movement_data["total_exits"]}</p>
                                    </div>
                                    <div class="stat-item">
                                        <h3>Saldo</h3>
                                        <p>{movement_data["net_change"]}</p>
                                    </div>
                                </div>
                                
                                <div class="divider"></div>
                                
                                <h3>Movimentação no Período</h3>
                                <p>Entradas no período: {movement_data["total_entries"]} unidades</p>
                                <p>Saídas no período: {movement_data["total_exits"]} unidades</p>
                                <p>Saldo no período: {movement_data["net_change"]} unidades</p>
                                
                                <div class="divider"></div>
                                
                                <h3>Resíduos neste grupo:</h3>
                                <div class="item-list">
                            ''')
                            
                            # Adicionar lista de resíduos
                            for residue in residues:
                                tmp.write(f'''
                                <p>{residue["name"]} - {residue.get("quantity", 0)} unidades - 
                                   Tipo: {residue.get("type", "N/A")}</p>
                                ''')
                            
                            tmp.write('</div></div>')  # Fechar div do grupo
                
                # Escrever rodapé HTML
                tmp.write(f'''
                    <div class="footer">
                        <p>Relatório gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
                    </div>
                </body>
                </html>
                ''')
            
            # Abrir o arquivo no navegador
            webbrowser.open('file://' + path)
            
            self.navigation.show_snack_bar(
                "Relatório aberto no navegador para impressão",
                ft.colors.GREEN_500
            )
        except Exception as e:
            print(f"Erro ao preparar relatório para impressão: {e}")
            import traceback
            traceback.print_exc()
            self.navigation.show_snack_bar(
                f"Erro ao preparar relatório: {str(e)}",
                ft.colors.RED_500
            )
    def set_group_type(self, group_type):
        """Define o tipo de grupo para o relatório (produto ou resíduo)"""
        self.group_type = group_type
        # Resetar o período selecionado para o padrão
        self.selected_period = "30"
        # Resetar a busca
        self.search_text = ""
        # Resetar a exibição de detalhes
        self.show_details = False
    
    def get_residues_by_group(self, group_id):
        """Obtém todos os resíduos de um grupo específico"""
        try:
            # Obter todos os resíduos
            residues = self.get_all_residues()
            
            # Filtrar por grupo
            return [r for r in residues if r.get("group_id") == group_id]
        except Exception as e:
            print(f"Erro ao obter resíduos do grupo {group_id}: {e}")
            import traceback
            traceback.print_exc()
            return []

    def get_all_residues(self):
        """Obtém todos os resíduos do banco de dados"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute('SELECT * FROM residues')
            
            residues = []
            for row in cursor.fetchall():
                residue = {
                    "id": row[0],
                    "name": row[1],
                    "type": row[2],
                    "quantity": row[3],
                    "entryDate": row[4],
                    "exitDate": row[5],
                    "destination": row[6],
                    "group_id": row[7],
                    "group_name": row[8],
                    "notes": row[9]
                }
                residues.append(residue)
            
            return residues
        except Exception as e:
            print(f"Erro ao obter todos os resíduos: {e}")
            import traceback
            traceback.print_exc()
            return []
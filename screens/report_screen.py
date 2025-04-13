import flet as ft
from datetime import datetime, timedelta

class ReportScreen:
    def __init__(self, data, navigation):
        self.data = data
        self.navigation = navigation

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
        
        # Corrigindo o cálculo do uso semanal para lidar com diferentes tipos de dados
        weekly_usage_total = 0
        for product in self.data.stock_products:
            weekly_usage = product.get("weeklyUsage", [0] * 7)
            
            # Verificar se weekly_usage é uma lista
            if not isinstance(weekly_usage, list):
                # Se não for uma lista, criar uma lista padrão
                weekly_usage = [0] * 7
            
            # Processar cada item na lista com tratamento de erro
            weekly_usage_sum = 0
            for usage in weekly_usage:
                try:
                    if isinstance(usage, str):
                        # Ignorar strings que não podem ser convertidas para números
                        if usage.isdigit():
                            weekly_usage_sum += int(usage)
                    else:
                        # Se já for um número, adicionar diretamente
                        weekly_usage_sum += usage if isinstance(usage, (int, float)) else 0
                except (ValueError, TypeError):
                    # Ignorar valores que causam erros
                    continue
            
            weekly_usage_total += weekly_usage_sum
        
        # Calcular estatísticas adicionais
        total_products = len(self.data.stock_products)
        total_residues = len(self.data.residues)
        total_alerts = len(self.data.low_stock_products) + len(self.data.expiring_products)
        
        # Calcular valor total do estoque (se disponível)
        total_stock_value = 0
        for product in self.data.stock_products:
            try:
                value = product.get("value", 0)
                quantity = product.get("quantity", 0)
                if value and quantity:
                    total_stock_value += float(value) * float(quantity)
            except (ValueError, TypeError):
                continue
        
        return ft.Container(
            content=ft.Column(
                controls=[
                    # Cabeçalho com título e data
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Row([
                                    ft.Icon(ft.icons.ANALYTICS_ROUNDED, size=24, color=primary_color),
                                    ft.Text("Relatórios e Análises", size=20, weight="bold", color="#303030"),
                                ], spacing=10),
                                ft.Container(
                                    content=ft.Row([
                                        ft.Icon(ft.icons.ACCESS_TIME, size=14, color="#707070"),
                                        ft.Text(
                                            f"Atualizado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
                                            size=12,
                                            color="#707070",
                                        ),
                                    ], spacing=5),
                                    padding=ft.padding.only(left=8, right=8, top=4, bottom=4),
                                    border_radius=8,
                                    bgcolor=ft.colors.with_opacity(0.05, primary_color)
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        padding=ft.padding.only(left=15, right=15, top=15, bottom=10),
                    ),
                    
                    # Resumo geral em cards modernos
                    ft.Container(
                        content=ft.ResponsiveRow(
                            [
                                ft.Column([
                                    self._build_summary_card(
                                        "Produtos em Estoque",
                                        total_products,
                                        ft.icons.INVENTORY_2,
                                        primary_color,
                                    )
                                ], col={"xs": 6, "sm": 6, "md": 3, "lg": 3, "xl": 3}),
                                
                                ft.Column([
                                    self._build_summary_card(
                                        "Resíduos Gerados",
                                        total_residues,
                                        ft.icons.DELETE_OUTLINE,
                                        secondary_color,
                                    )
                                ], col={"xs": 6, "sm": 6, "md": 3, "lg": 3, "xl": 3}),
                                
                                ft.Column([
                                    self._build_summary_card(
                                        "Alertas Ativos",
                                        total_alerts,
                                        ft.icons.WARNING_ROUNDED,
                                        danger_color,
                                    )
                                ], col={"xs": 6, "sm": 6, "md": 3, "lg": 3, "xl": 3}),
                                
                                ft.Column([
                                    self._build_summary_card(
                                        "Valor do Estoque",
                                        f"R$ {total_stock_value:.2f}".replace('.', ','),
                                        ft.icons.ATTACH_MONEY,
                                        success_color,
                                    )
                                ], col={"xs": 6, "sm": 6, "md": 3, "lg": 3, "xl": 3}),
                            ],
                            spacing=15,
                        ),
                        padding=15,
                    ),
                    
                    # Seções de relatórios
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Container(
                                    content=ft.Row([
                                        ft.Icon(ft.icons.ASSESSMENT, size=18, color=primary_color),
                                        ft.Text("Relatórios de Estoque", size=16, weight="bold", color="#303030"),
                                    ], spacing=10),
                                    margin=ft.margin.only(bottom=10, left=5)
                                ),
                                
                                ft.ResponsiveRow(
                                    [
                                        ft.Column([
                                            self._build_report_card(
                                                "Movimentação",
                                                "Entradas e saídas de produtos",
                                                ft.icons.SYNC_ALT,
                                                primary_color,
                                                lambda _: self._show_movement_report()
                                            )
                                        ], col={"xs": 12, "sm": 6, "md": 6, "lg": 6, "xl": 6}),
                                        
                                        ft.Column([
                                            self._build_report_card(
                                                "Produtos por Validade",
                                                "Análise de produtos por data de vencimento",
                                                ft.icons.EVENT_AVAILABLE,
                                                warning_color,
                                                lambda _: self._show_expiry_report()
                                            )
                                        ], col={"xs": 12, "sm": 6, "md": 6, "lg": 6, "xl": 6}),
                                    ],
                                    spacing=15,
                                ),
                                
                                ft.ResponsiveRow(
                                    [
                                        ft.Column([
                                            self._build_report_card(
                                                "Análise por Grupos",
                                                "Produtos e resíduos agrupados por categoria",
                                                ft.icons.CATEGORY,
                                                secondary_color,
                                                lambda _: self._show_group_report()
                                            )
                                        ], col={"xs": 12, "sm": 6, "md": 6, "lg": 6, "xl": 6}),
                                        
                                        ft.Column([
                                            self._build_report_card(
                                                "Entradas no Estoque",
                                                "Histórico de entradas de produtos e resíduos",
                                                ft.icons.INPUT,
                                                success_color,
                                                lambda _: self._show_entry_report()
                                            )
                                        ], col={"xs": 12, "sm": 6, "md": 6, "lg": 6, "xl": 6}),
                                    ],
                                    spacing=15,
                                ),
                            ],
                            spacing=15,
                        ),
                        padding=15,
                    ),
                    
                    # Uso semanal
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Container(
                                    content=ft.Row([
                                        ft.Icon(ft.icons.TRENDING_UP, size=18, color=primary_color),
                                        ft.Text("Uso Semanal de Produtos", size=16, weight="bold", color="#303030"),
                                    ], spacing=10),
                                    margin=ft.margin.only(bottom=10, left=5)
                                ),
                                
                                ft.Container(
                                    content=ft.Column(
                                        controls=[
                                            ft.Row([
                                                ft.Container(
                                                    content=ft.Column([
                                                        ft.Text("Total de Unidades Usadas", size=12, color="#707070"),
                                                        ft.Text(f"{weekly_usage_total}", size=24, weight="bold", color=primary_color),
                                                    ], spacing=5, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                                                    padding=15,
                                                    border_radius=10,
                                                    bgcolor=card_bg,
                                                    expand=True,
                                                    alignment=ft.alignment.center
                                                ),
                                                
                                                ft.Container(
                                                    content=ft.Column([
                                                        ft.Text("Média Diária", size=12, color="#707070"),
                                                        ft.Text(
                                                            f"{round(weekly_usage_total/7, 1)}" if weekly_usage_total > 0 else "0",
                                                            size=24, 
                                                            weight="bold", 
                                                            color=primary_color
                                                        ),
                                                    ], spacing=5, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                                                    padding=15,
                                                    border_radius=10,
                                                    bgcolor=card_bg,
                                                    expand=True,
                                                    alignment=ft.alignment.center
                                                ),
                                            ], spacing=15),
                                            
                                            ft.FilledButton(
                                                "Ver Detalhes de Uso Semanal",
                                                icon=ft.icons.ANALYTICS_OUTLINED,
                                                on_click=lambda _: self._show_weekly_usage_report(),
                                                style=ft.ButtonStyle(
                                                    color=card_bg,
                                                    bgcolor=primary_color,
                                                ),
                                                width=300,
                                            ),
                                        ],
                                        spacing=15,
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    ),
                                    padding=20,
                                    border_radius=12,
                                    bgcolor=ft.colors.with_opacity(0.05, primary_color),
                                    shadow=ft.BoxShadow(
                                        spread_radius=0.1,
                                        blur_radius=4,
                                        color=ft.colors.with_opacity(0.08, "#000000")
                                    ),
                                ),
                            ],
                            spacing=10,
                        ),
                        padding=15,
                    ),
                    
                    # Botões de exportação
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.OutlinedButton(
                                    "Exportar Todos os Dados",
                                    icon=ft.icons.DOWNLOAD,
                                    on_click=self._export_all_data,
                                    style=ft.ButtonStyle(
                                        color=primary_color,
                                        shape=ft.RoundedRectangleBorder(radius=8)
                                    ),
                                ),
                                ft.FilledButton(
                                    "Imprimir Relatório",
                                    icon=ft.icons.PRINT,
                                    on_click=self._print_report,
                                    style=ft.ButtonStyle(
                                        color=card_bg,
                                        bgcolor=primary_color,
                                        shape=ft.RoundedRectangleBorder(radius=8)
                                    ),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.END,
                            spacing=10,
                        ),
                        padding=15,
                    ),
                ],
                spacing=0,
                scroll=ft.ScrollMode.AUTO,
            ),
            bgcolor=bg_color,
            expand=True,
        )

    def _build_summary_card(self, title, value, icon, color):
        """Constrói um card de resumo para o dashboard com design moderno"""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Icon(icon, color="#FFFFFF", size=18),
                        padding=8,
                        border_radius=8,
                        bgcolor=color
                    ),
                    ft.Text(title, size=12, color="#707070", weight="w500"),
                    ft.Text(str(value), size=20, weight="bold", color=color),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5,
            ),
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
    
    def _build_report_card(self, title, description, icon, color, on_click):
        """Constrói um card para um tipo de relatório com design moderno"""
        return ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(icon, color="#FFFFFF", size=18),
                        padding=8,
                        border_radius=8,
                        bgcolor=color
                    ),
                    ft.Column(
                        [
                            ft.Text(title, size=16, weight="bold", color="#303030"),
                            ft.Text(description, size=12, color="#707070"),
                        ],
                        spacing=5,
                        expand=True,
                    ),
                    ft.Icon(ft.icons.ARROW_FORWARD_IOS, size=16, color=color),
                ],
                spacing=10,
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=15,
            border_radius=12,
            bgcolor="#FFFFFF",
            border=ft.border.all(1, ft.colors.GREY_300),
            shadow=ft.BoxShadow(
                spread_radius=0.1,
                blur_radius=4,
                color=ft.colors.with_opacity(0.08, "#000000")
            ),
            on_click=on_click,
            expand=True,
        )

    def _build_section(self, title, count, icon, color, unit_text, on_click):
        """Constrói uma seção de relatório com design moderno"""
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Icon(icon, color="#FFFFFF", size=18),
                                padding=8,
                                border_radius=8,
                                bgcolor=color
                            ),
                            ft.Text(title, size=16, weight="bold", color="#303030"),
                        ],
                        spacing=10,
                    ),
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Text(f"{count} {unit_text}", size=20, weight="bold", color=color),
                                ft.Row([
                                    ft.Text("Clique para ver detalhes", size=12, color="#707070"),
                                    ft.Icon(ft.icons.ARROW_FORWARD, size=14, color=color)
                                ], spacing=5, alignment=ft.MainAxisAlignment.CENTER),
                            ],
                            spacing=5,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        padding=15,
                        bgcolor="#FFFFFF",
                        border_radius=10,
                        shadow=ft.BoxShadow(
                            spread_radius=0.1,
                            blur_radius=4,
                            color=ft.colors.with_opacity(0.08, "#000000")
                        ),
                        on_click=on_click,
                        margin=ft.margin.only(top=10),
                    ),
                ],
                spacing=5,
            ),
            padding=15,
            bgcolor="#FFFFFF",
            border_radius=12,
            shadow=ft.BoxShadow(
                spread_radius=0.1,
                blur_radius=4,
                color=ft.colors.with_opacity(0.08, "#000000")
            ),
        )

    def _show_weekly_usage_report(self):
        """Navega para o relatório de uso semanal"""
        if self.data.stock_products:
            self.navigation.go_to_weekly_usage(self.data.stock_products[0])
        else:
            self.navigation.show_snack_bar(
                "Não há produtos em estoque para mostrar o uso semanal",
                "#FFA502"
            )

    def _show_alerts_report(self):
        """Mostra relatório de alertas (produtos com estoque baixo e próximos ao vencimento)"""
        alerts = self.data.low_stock_products + self.data.expiring_products
        self.navigation.go_to_dashboard_detail("alerts", alerts, "Alertas Ativos")
    
    def _show_movement_report(self):
        """Navega para o relatório de movimentação"""
        try:
            from screens.movement_report_screen import MovementReportScreen
            
            if not hasattr(self.navigation, 'movement_report_screen'):
                self.navigation.movement_report_screen = MovementReportScreen(self.data, self.navigation)
            
            self.navigation.previous_tab = self.navigation.current_tab
            self.navigation.previous_screen = self.navigation.current_screen
            
            self.navigation.current_screen = "movement_report"
            self.navigation.update_view()
        except ImportError:
            self.navigation.show_snack_bar(
                "Relatório de movimentação não disponível",
                "#FF6B6B"
            )
    
    def _show_entry_report(self):
        """Navega para o relatório de entradas"""
        try:
            from screens.entry_report_screen import EntryReportScreen
            
            if not hasattr(self.navigation, 'entry_report_screen'):
                self.navigation.entry_report_screen = EntryReportScreen(self.data, self.navigation)
            
            self.navigation.previous_tab = self.navigation.current_tab
            self.navigation.previous_screen = self.navigation.current_screen
            
            self.navigation.current_screen = "entry_report"
            self.navigation.update_view()
        except ImportError:
            self.navigation.show_snack_bar(
                "Relatório de entradas não disponível",
                "#FF6B6B"
            )
    
    def _show_expiry_report(self):
        """Navega para o relatório de validade"""
        try:
            from screens.expiry_report_screen import ExpiryReportScreen
            
            if not hasattr(self.navigation, 'expiry_report_screen'):
                self.navigation.expiry_report_screen = ExpiryReportScreen(self.data, self.navigation)
            
            self.navigation.previous_tab = self.navigation.current_tab
            self.navigation.previous_screen = self.navigation.current_screen
            
            self.navigation.current_screen = "expiry_report"
            self.navigation.update_view()
        except ImportError:
            self.navigation.show_snack_bar(
                "Relatório de validade não disponível",
                "#FF6B6B"
            )
    
    def _show_group_report(self):
        """Navega para o relatório por grupos"""
        try:
            from screens.group_report_screen import GroupReportScreen
            
            if not hasattr(self.navigation, 'group_report_screen'):
                self.navigation.group_report_screen = GroupReportScreen(self.data, self.navigation)
            
            self.navigation.previous_tab = self.navigation.current_tab
            self.navigation.previous_screen = self.navigation.current_screen
            
            self.navigation.current_screen = "group_report"
            self.navigation.update_view()
        except ImportError:
            self.navigation.show_snack_bar(
                "Relatório por grupos não disponível",
                "#FF6B6B"
            )
    
    def _export_all_data(self, e=None):
        """Exporta todos os dados do sistema"""
        try:
            import csv
            import os
            from datetime import datetime
            
            # Criar diretório de relatórios se não existir
            os.makedirs("reports", exist_ok=True)
            
            # Nome do arquivo com timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Exportar produtos
            products_filename = f"reports/produtos_{timestamp}.csv"
            with open(products_filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["ID", "Nome", "Quantidade", "Lote", "Validade", "Grupo", "Valor"])
                
                for product in self.data.stock_products:
                    writer.writerow([
                        product.get("id", ""),
                        product.get("name", ""),
                        product.get("quantity", 0),
                        product.get("lot", ""),
                        product.get("expiry", ""),
                        product.get("group_name", ""),
                        product.get("value", 0)
                    ])
            
            # Exportar resíduos
            residues_filename = f"reports/residuos_{timestamp}.csv"
            with open(residues_filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["ID", "Nome", "Quantidade", "Tipo", "Grupo", "Destino"])
                
                for residue in self.data.residues:
                    writer.writerow([
                        residue.get("id", ""),
                        residue.get("name", ""),
                        residue.get("quantity", 0),
                        residue.get("type", ""),
                        residue.get("group_name", ""),
                        residue.get("destination", "")
                    ])
            
            self.navigation.show_snack_bar(
                f"Dados exportados com sucesso para a pasta 'reports'",
                "#2ED573"
            )
        except Exception as e:
            print(f"Erro ao exportar dados: {e}")
            import traceback
            traceback.print_exc()
            self.navigation.show_snack_bar(
                f"Erro ao exportar dados: {str(e)}",
                "#FF6B6B"
            )
    
    def _print_report(self, e=None):
        """Prepara o relatório para impressão"""
        try:
            import tempfile
            import webbrowser
            import os
            
            # Criar arquivo HTML temporário
            fd, path = tempfile.mkstemp(suffix='.html')
            
            with os.fdopen(fd, 'w') as tmp:
                # Escrever cabeçalho HTML
                tmp.write(f'''
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <title>Relatório de Estoque e Resíduos</title>
                    <style>
                        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 20px; color: #303030; }}
                        .header {{ text-align: center; margin-bottom: 30px; padding-bottom: 20px; border-bottom: 1px solid #eee; }}
                        .section {{ margin-bottom: 30px; }}
                        .section-title {{ background-color: #f8f9fd; padding: 10px 15px; border-radius: 8px; font-size: 18px; color: #4A6FFF; }}
                        .card {{ border: 1px solid #eee; padding: 15px; margin-bottom: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }}
                        .footer {{ text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; font-size: 12px; color: #707070; }}
                        table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
                        th, td {{ border: 1px solid #eee; padding: 12px; text-align: left; }}
                        th {{ background-color: #f8f9fd; color: #4A6FFF; font-weight: 600; }}
                        tr:nth-child(even) {{ background-color: #f9f9f9; }}
                        .summary {{ display: flex; justify-content: space-between; margin-bottom: 30px; flex-wrap: wrap; }}
                        .summary-item {{ text-align: center; padding: 15px; border-radius: 8px; background-color: #fff; box-shadow: 0 2px 4px rgba(0,0,0,0.05); width: 22%; margin-bottom: 15px; }}
                        .summary-item h3 {{ color: #4A6FFF; margin-bottom: 5px; }}
                        .summary-item p {{ font-size: 24px; font-weight: bold; margin: 5px 0; }}
                        .alert {{ background-color: #fff0f0; color: #FF6B6B; }}
                        .expiring {{ background-color: #FFF8E1; color: #FFA502; }}
                        @media print {{
                            .no-print {{ display: none; }}
                            button {{ display: none; }}
                            body {{ font-size: 12px; }}
                            .summary-item {{ box-shadow: none; border: 1px solid #eee; }}
                            .card {{ box-shadow: none; }}
                        }}
                        @media (max-width: 768px) {{
                            .summary-item {{ width: 45%; }}
                        }}
                        @media (max-width: 480px) {{
                            .summary-item {{ width: 100%; }}
                        }}
                        .btn {{ display: inline-block; padding: 10px 15px; background-color: #4A6FFF; color: white; text-decoration: none; border-radius: 4px; margin-right: 10px; }}
                    </style>
                </head>
                <body>
                    <div class="header">
                        <h1>Relatório de Estoque e Resíduos</h1>
                        <p>Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
                    </div>
                    
                    <div class="no-print" style="margin-bottom: 20px; text-align: center;">
                        <button class="btn" onclick="window.print()">Imprimir Relatório</button>
                        <button class="btn" style="background-color: #6C5CE7;" onclick="window.close()">Fechar</button>
                    </div>
                    
                    <div class="summary">
                        <div class="summary-item">
                            <h3>Produtos</h3>
                            <p>{len(self.data.stock_products)}</p>
                        </div>
                        <div class="summary-item">
                            <h3>Resíduos</h3>
                            <p>{len(self.data.residues)}</p>
                        </div>
                        <div class="summary-item">
                            <h3>Alertas</h3>
                            <p>{len(self.data.low_stock_products) + len(self.data.expiring_products)}</p>
                        </div>
                        <div class="summary-item">
                            <h3>Uso Semanal</h3>
                            <p>{self._calculate_weekly_usage()}</p>
                        </div>
                    </div>
                    
                    <div class="section">
                        <h2 class="section-title">Produtos em Estoque</h2>
                        <table>
                            <tr>
                                <th>Nome</th>
                                <th>Quantidade</th>
                                <th>Lote</th>
                                <th>Validade</th>
                                <th>Grupo</th>
                                <th>Valor</th>
                            </tr>
                ''')
                
                # Adicionar produtos
                for product in self.data.stock_products:
                    is_low_stock = product in self.data.low_stock_products
                    is_expiring = product in self.data.expiring_products
                    row_class = "alert" if is_low_stock else "expiring" if is_expiring else ""
                    
                    tmp.write(f'''
                            <tr class="{row_class}">
                                <td>{product.get("name", "")}</td>
                                <td>{product.get("quantity", 0)}</td>
                                <td>{product.get("lot", "N/A")}</td>
                                <td>{product.get("expiry", "N/A")}</td>
                                <td>{product.get("group_name", "")}</td>
                                <td>R$ {float(product.get("value", 0)):.2f}</td>
                            </tr>
                    ''')
                
                tmp.write('''
                        </table>
                    </div>
                    
                    <div class="section">
                        <h2 class="section-title">Resíduos Gerados</h2>
                        <table>
                            <tr>
                                <th>Nome</th>
                                <th>Quantidade</th>
                                <th>Tipo</th>
                                <th>Destino</th>
                                <th>Grupo</th>
                                <th>Data de Entrada</th>
                            </tr>
                ''')
                
                # Adicionar resíduos
                for residue in self.data.residues:
                    tmp.write(f'''
                            <tr>
                                <td>{residue.get("name", "")}</td>
                                <td>{residue.get("quantity", 0)}</td>
                                <td>{residue.get("type", "N/A")}</td>
                                <td>{residue.get("destination", "N/A")}</td>
                                <td>{residue.get("group_name", "")}</td>
                                <td>{residue.get("entryDate", "N/A")}</td>
                            </tr>
                    ''')
                
                tmp.write('''
                        </table>
                    </div>
                    
                    <div class="section">
                        <h2 class="section-title">Alertas Ativos</h2>
                        <table>
                            <tr>
                                <th>Nome</th>
                                <th>Tipo de Alerta</th>
                                <th>Quantidade</th>
                                <th>Detalhes</th>
                            </tr>
                ''')
                
                # Adicionar alertas
                for product in self.data.low_stock_products:
                    tmp.write(f'''
                            <tr class="alert">
                                <td>{product.get("name", "")}</td>
                                <td>Estoque Baixo</td>
                                <td>{product.get("quantity", 0)}</td>
                                <td>Abaixo do mínimo recomendado ({product.get("minStock", "N/A")})</td>
                            </tr>
                    ''')
                
                for product in self.data.expiring_products:
                    tmp.write(f'''
                            <tr class="expiring">
                                <td>{product.get("name", "")}</td>
                                <td>Próximo ao Vencimento</td>
                                <td>{product.get("quantity", 0)}</td>
                                <td>Validade: {product.get("expiry", "N/A")}</td>
                            </tr>
                    ''')
                
                tmp.write('''
                        </table>
                    </div>
                    
                    <div class="section">
                        <h2 class="section-title">Uso Semanal de Produtos</h2>
                        <div class="card">
                            <p>Total de unidades usadas na semana: <strong>{}</strong></p>
                            <p>Média diária de uso: <strong>{}</strong></p>
                        </div>
                    </div>
                    
                    <div class="footer">
                        <p>Relatório gerado em {} pelo Sistema de Gestão de Estoque e Resíduos</p>
                    </div>
                </body>
                </html>
                '''.format(
                    self._calculate_weekly_usage(),
                    round(self._calculate_weekly_usage() / 7, 1),
                    datetime.now().strftime('%d/%m/%Y %H:%M')
                ))
            
            # Abrir o arquivo no navegador
            webbrowser.open('file://' + path)
            
            self.navigation.show_snack_bar(
                "Relatório aberto no navegador para impressão",
                "#2ED573"
            )
        except Exception as e:
            print(f"Erro ao preparar relatório para impressão: {e}")
            import traceback
            traceback.print_exc()
            self.navigation.show_snack_bar(
                f"Erro ao preparar relatório: {str(e)}",
                "#FF6B6B"
            )
    
    def _calculate_weekly_usage(self):
        """Calcula o uso semanal total com tratamento de erros"""
        weekly_usage_total = 0
        for product in self.data.stock_products:
            weekly_usage = product.get("weeklyUsage", [0] * 7)
            
            # Verificar se weekly_usage é uma lista
            if not isinstance(weekly_usage, list):
                weekly_usage = [0] * 7
            
            # Processar cada item na lista com tratamento de erro
            weekly_usage_sum = 0
            for usage in weekly_usage:
                try:
                    if isinstance(usage, str):
                        if usage.isdigit():
                            weekly_usage_sum += int(usage)
                    else:
                        weekly_usage_sum += usage if isinstance(usage, (int, float)) else 0
                except (ValueError, TypeError):
                    continue
            
            weekly_usage_total += weekly_usage_sum
        
        return weekly_usage_total
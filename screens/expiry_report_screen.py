import flet as ft
from datetime import datetime, timedelta

class ExpiryReportScreen:
    def __init__(self, data, navigation):
        self.data = data
        self.navigation = navigation
        self.filter_days = "30"  # Padrão: próximos 30 dias
        self.search_text = ""
        self.show_details = False  # Controla se mostra detalhes expandidos
    
    def build(self):
        # Filtro de período
        filter_dropdown = ft.Dropdown(
            options=[
                ft.dropdown.Option("7", "Próximos 7 dias"),
                ft.dropdown.Option("30", "Próximos 30 dias"),
                ft.dropdown.Option("90", "Próximos 90 dias"),
                ft.dropdown.Option("365", "Próximo ano"),
            ],
            value=self.filter_days,
            on_change=self._on_filter_change,
            width=200,
        )
        
        # Campo de busca
        search_field = ft.TextField(
            hint_text="Buscar por produto...",
            value=self.search_text,
            on_change=self._on_search_change,
            prefix_icon=ft.icons.SEARCH,
            width=200,
        )
        
        # Botões de ação
        export_button = ft.ElevatedButton(
            "Exportar",
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
        
        # Obter produtos que vencem no período selecionado
        days = int(self.filter_days)
        expiring_products = self.data.product_service.get_expiring_products(days)
        
        # Filtrar por texto de busca
        if self.search_text:
            search_lower = self.search_text.lower()
            expiring_products = [
                product for product in expiring_products
                if search_lower in product.get("name", "").lower() or
                   search_lower in product.get("lot", "").lower()
            ]
        
        # Agrupar por mês de vencimento
        expiry_groups = self._group_by_expiry_month(expiring_products)
        
        # Construir gráfico de distribuição
        expiry_chart = self._build_expiry_chart(expiry_groups)
        
        # Construir lista de produtos
        product_items = []
        
        # Ordenar produtos por data de validade (mais próximos primeiro)
        sorted_products = self._sort_by_expiry_date(expiring_products)
        
        for product in sorted_products:
            product_items.append(self._build_product_item(product))
        
        # Verificar se há produtos
        if not product_items:
            product_items.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.icons.EVENT_AVAILABLE, size=40, color=ft.colors.GREY_400),
                        ft.Text(f"Nenhum produto vence nos próximos {days} dias", 
                               size=14, color=ft.colors.GREY_700),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=20,
                    alignment=ft.alignment.center,
                )
            )
        
        # Estatísticas
        total_expiring = len(expiring_products)
        total_value = sum(p.get("value", 0) * p.get("quantity", 0) for p in expiring_products)
        
        # Calcular produtos críticos (vencendo em 7 dias ou menos)
        critical_products = [p for p in expiring_products if self._days_until_expiry(p) <= 7]
        
        stats_row = ft.Container(
            content=ft.Row([
                self._build_stat_card(
                    f"Vencendo em {days} dias", 
                    total_expiring, 
                    ft.icons.EVENT_AVAILABLE, 
                    ft.colors.ORANGE_500
                ),
                self._build_stat_card(
                    "Críticos (7 dias)", 
                    len(critical_products), 
                    ft.icons.WARNING_AMBER_ROUNDED, 
                    ft.colors.RED_500
                ),
                self._build_stat_card(
                    "Valor Total", 
                    f"R$ {total_value:.2f}".replace(".", ","), 
                    ft.icons.ATTACH_MONEY, 
                    ft.colors.GREEN_500
                ),
            ]),
            padding=10,
        )
        
        # Detalhes adicionais (se mostrar detalhes)
        details_section = None
        if self.show_details and expiring_products:
            details_section = self._build_details_section(expiring_products)
        
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
                            ft.Text("Análise de Validade", size=20, weight="bold"),
                        ]
                    ),
                    padding=10,
                ),
                
                # Filtro e estatísticas
                ft.Container(
                    content=ft.Column([
                        ft.Row(
                            [
                                ft.Text("Período:", size=16),
                                filter_dropdown,
                                search_field,
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        ft.Row(
                            [
                                ft.Text(
                                    f"{len(expiring_products)} produtos vencendo nos próximos {days} dias",
                                    size=16,
                                    weight="bold",
                                    color=ft.colors.ORANGE_500 if expiring_products else None,
                                ),
                                ft.Row([
                                    details_button,
                                    export_button,
                                    print_button,
                                ], spacing=10),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                    ], spacing=10),
                    padding=ft.padding.only(left=20, right=20, bottom=10),
                ),
                
                # Estatísticas
                stats_row,
                
                # Gráfico de distribuição
                ft.Container(
                    content=expiry_chart,
                    padding=ft.padding.only(left=20, right=20, bottom=20),
                ),
                
                # Detalhes adicionais (se mostrar detalhes)
                ft.Container(
                    content=details_section,
                    padding=ft.padding.only(left=20, right=20, bottom=10),
                    visible=self.show_details and details_section is not None,
                ),
                
                # Lista de produtos
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text("Produtos por Data de Validade", size=16, weight="bold"),
                            ft.Column(
                                product_items,
                                spacing=10,
                                scroll=ft.ScrollMode.AUTO,
                            ),
                        ],
                        spacing=10,
                    ),
                    padding=20,
                    expand=True,
                ),
            ],
            expand=True,
        )
    
    def _on_filter_change(self, e):
        """Atualiza o filtro de período e reconstrói a tela"""
        self.filter_days = e.control.value
        self.navigation.update_view()
    
    def _on_search_change(self, e):
        """Atualiza o texto de busca"""
        self.search_text = e.control.value
        self.navigation.update_view()
    
    def _toggle_details(self, e):
        """Alterna a exibição de detalhes"""
        self.show_details = not self.show_details
        self.navigation.update_view()
    
    def _group_by_expiry_month(self, products):
        """Agrupa produtos por mês de vencimento"""
        groups = {}
        
        for product in products:
            try:
                expiry_date = datetime.strptime(product["expiry"], "%d/%m/%Y")
                month_key = expiry_date.strftime("%m/%Y")
                month_name = expiry_date.strftime("%b/%Y")
                
                if month_key not in groups:
                    groups[month_key] = {
                        "name": month_name,
                        "count": 0,
                        "products": []
                    }
                
                groups[month_key]["count"] += 1
                groups[month_key]["products"].append(product)
            except:
                # Ignorar produtos com data inválida
                continue
        
        # Ordenar por mês
        sorted_groups = sorted(groups.items(), key=lambda x: datetime.strptime(x[0], "%m/%Y"))
        return [group for _, group in sorted_groups]
    
    def _build_expiry_chart(self, expiry_groups):
        """Constrói um gráfico simples de distribuição de validade"""
        if not expiry_groups:
            return ft.Container(
                content=ft.Text("Sem dados para exibir", size=14, color=ft.colors.GREY_700),
                alignment=ft.alignment.center,
                padding=20,
            )
        
        # Criar barras para cada mês
        chart_bars = []
        max_count = max(group["count"] for group in expiry_groups)
        
        for group in expiry_groups:
            # Calcular altura relativa da barra (máximo 100)
            height = (group["count"] / max_count) * 100 if max_count > 0 else 0
            
            chart_bars.append(
                ft.Column(
                    [
                        ft.Container(
                            content=ft.Text(str(group["count"]), size=12, color=ft.colors.WHITE),
                            bgcolor=ft.colors.ORANGE_500,
                            border_radius=ft.border_radius.only(top_left=5, top_right=5),
                            height=max(height, 20),
                            width=60,
                            alignment=ft.alignment.center,
                        ),
                        ft.Text(group["name"], size=12, text_align=ft.TextAlign.CENTER),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.END,
                )
            )
        
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("Distribuição de Produtos por Mês de Vencimento", 
                           size=16, weight="bold"),
                    ft.Container(
                        content=ft.Row(
                            chart_bars,
                            alignment=ft.MainAxisAlignment.SPACE_AROUND,
                        ),
                        height=150,
                        alignment=ft.alignment.bottom_center,
                    ),
                ],
                spacing=10,
            ),
            padding=10,
            border_radius=10,
            bgcolor=ft.colors.WHITE,
            border=ft.border.all(1, ft.colors.GREY_300),
        )
    
    def _build_details_section(self, products):
        """Constrói uma seção de detalhes adicionais"""
        # Agrupar por categoria ou grupo
        groups = {}
        for product in products:
            group_name = product.get("group_name", "Sem grupo")
            if group_name not in groups:
                groups[group_name] = []
            groups[group_name].append(product)
        
        # Criar gráfico de pizza (simplificado como barras horizontais)
        group_bars = []
        for group_name, group_products in groups.items():
            group_bars.append(
                ft.Row(
                    [
                        ft.Container(
                            width=len(group_products) * 5,  # 5px por produto
                            height=20,
                            bgcolor=ft.colors.BLUE_500,
                            border_radius=5,
                        ),
                        ft.Text(f"{group_name}: {len(group_products)}", size=14),
                    ],
                    spacing=10,
                    alignment=ft.MainAxisAlignment.START,
                )
            )
        
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("Análise por Grupos", size=16, weight="bold"),
                    ft.Column(group_bars, spacing=5),
                    ft.Divider(),
                    ft.Text("Recomendações:", size=16, weight="bold"),
                    ft.Text(
                        "• Produtos com validade próxima devem ser utilizados primeiro",
                        size=14,
                    ),
                    ft.Text(
                        "• Considere promoções para produtos com menos de 30 dias para vencer",
                        size=14,
                    ),
                    ft.Text(
                        f"• {len([p for p in products if self._days_until_expiry(p) <= 7])} produtos precisam de atenção imediata",
                        size=14,
                        color=ft.colors.RED_500,
                    ),
                ],
                spacing=10,
            ),
            padding=15,
            border_radius=10,
            bgcolor=ft.colors.WHITE,
            border=ft.border.all(1, ft.colors.GREY_300),
        )
    
    def _sort_by_expiry_date(self, products):
        """Ordena produtos por data de validade (mais próximos primeiro)"""
        def parse_date(date_str):
            try:
                return datetime.strptime(date_str, "%d/%m/%Y")
            except:
                return datetime(2099, 12, 31)
        
        return sorted(products, key=lambda p: parse_date(p.get("expiry", "31/12/2099")))
    
    def _days_until_expiry(self, product):
        """Calcula dias até o vencimento"""
        try:
            expiry_date = datetime.strptime(product["expiry"], "%d/%m/%Y")
            days = (expiry_date - datetime.now()).days
            return max(0, days)
        except:
            return 999  # Valor alto para produtos sem data válida
    
    def _build_stat_card(self, title, value, icon, color):
        """Constrói um card de estatística"""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(icon, color=color, size=24),
                            ft.Text(title, size=14),
                        ],
                        spacing=5,
                    ),
                    ft.Text(str(value), size=20, weight="bold"),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5,
            ),
            padding=15,
            border_radius=10,
            bgcolor=ft.colors.WHITE,
            border=ft.border.all(1, ft.colors.GREY_300),
            expand=True,
            alignment=ft.alignment.center,
        )
    
    def _build_product_item(self, product):
        """Constrói um item de produto para a lista"""
        # Calcular dias até o vencimento
        days_remaining = "N/A"
        try:
            expiry_date = datetime.strptime(product["expiry"], "%d/%m/%Y")
            days = (expiry_date - datetime.now()).days
            days_remaining = days
            
            # Definir cor com base nos dias restantes
            color = ft.colors.GREEN_500
            if days <= 7:
                color = ft.colors.RED_500
            elif days <= 30:
                color = ft.colors.ORANGE_500
            elif days <= 90:
                color = ft.colors.YELLOW_700
        except:
            color = ft.colors.GREY_500
        
        return ft.Container(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text(product["name"], size=16, weight="w500"),
                            ft.Text(
                                f"Lote: {product.get('lot', 'N/A')} • Quantidade: {product['quantity']}",
                                size=12,
                                color=ft.colors.GREY_700,
                            ),
                            ft.Text(
                                f"Grupo: {product.get('group_name', 'N/A')} • Valor: R$ {product.get('value', 0):.2f}".replace(".", ","),
                                size=12,
                                color=ft.colors.GREY_700,
                            ),
                        ],
                        spacing=5,
                        expand=True,
                    ),
                    ft.Column(
                        [
                            ft.Text("Validade", size=12, color=ft.colors.GREY_700),
                            ft.Text(
                                product.get("expiry", "N/A"),
                                size=14,
                                weight="bold",
                            ),
                            ft.Text(
                                f"{days_remaining} dias",
                                size=12,
                                color=color,
                                weight="bold",
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.END,
                        spacing=2,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=15,
            border_radius=10,
            bgcolor=ft.colors.WHITE,
            border=ft.border.all(1, ft.colors.GREY_300),
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
            filename = f"reports/expiry_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            # Obter dados para o relatório
            days = int(self.filter_days)
            expiring_products = self.data.product_service.get_expiring_products(days)
            
            # Filtrar por texto de busca
            if self.search_text:
                search_lower = self.search_text.lower()
                expiring_products = [
                    product for product in expiring_products
                    if search_lower in product.get("name", "").lower() or
                       search_lower in product.get("lot", "").lower()
                ]
            
            # Ordenar por data de validade
            sorted_products = self._sort_by_expiry_date(expiring_products)
            
            # Escrever arquivo CSV
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Cabeçalho
                writer.writerow([
                    "Nome", "Lote", "Quantidade", "Validade", "Dias Restantes", 
                    "Grupo", "Valor Unitário", "Valor Total"
                ])
                
                # Dados de cada produto
                for product in sorted_products:
                    # Calcular dias até o vencimento
                    days_remaining = "N/A"
                    try:
                        expiry_date = datetime.strptime(product["expiry"], "%d/%m/%Y")
                        days_remaining = (expiry_date - datetime.now()).days
                    except:
                        pass
                    
                    # Calcular valor total
                    value = product.get("value", 0)
                    quantity = product.get("quantity", 0)
                    total_value = value * quantity
                    
                    writer.writerow([
                        product.get("name", ""),
                        product.get("lot", "N/A"),
                        product.get("quantity", 0),
                        product.get("expiry", "N/A"),
                        days_remaining,
                        product.get("group_name", "N/A"),
                        f"{value:.2f}".replace(".", ","),
                        f"{total_value:.2f}".replace(".", ",")
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
            days = int(self.filter_days)
            expiring_products = self.data.product_service.get_expiring_products(days)
            
            # Filtrar por texto de busca
            if self.search_text:
                search_lower = self.search_text.lower()
                expiring_products = [
                    product for product in expiring_products
                    if search_lower in product.get("name", "").lower() or
                       search_lower in product.get("lot", "").lower()
                ]
            
            # Ordenar por data de validade
            sorted_products = self._sort_by_expiry_date(expiring_products)
            
            # Agrupar por mês
            expiry_groups = self._group_by_expiry_month(expiring_products)
            
            # Calcular estatísticas
            total_expiring = len(expiring_products)
            total_value = sum(p.get("value", 0) * p.get("quantity", 0) for p in expiring_products)
            critical_products = [p for p in expiring_products if self._days_until_expiry(p) <= 7]
            
            # Criar arquivo HTML temporário
            fd, path = tempfile.mkstemp(suffix='.html')
            
            with os.fdopen(fd, 'w') as tmp:
                # Escrever cabeçalho HTML
                tmp.write(f'''
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <title>Relatório de Validade</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 20px; }}
                        .header {{ text-align: center; margin-bottom: 20px; }}
                        .stats {{ display: flex; justify-content: space-between; margin-bottom: 20px; }}
                        .stat-card {{ border: 1px solid #ddd; padding: 10px; text-align: center; width: 30%; }}
                        .chart {{ margin: 20px 0; text-align: center; }}
                        .chart-bar {{ display: inline-block; margin: 0 5px; text-align: center; }}
                        .bar {{ background-color: #FF9800; border-radius: 5px 5px 0 0; }}
                        .product-item {{ border: 1px solid #ddd; padding: 10px; margin-bottom: 10px; }}
                        .critical {{ border-left: 5px solid #F44336; }}
                        .warning {{ border-left: 5px solid #FF9800; }}
                        .normal {{ border-left: 5px solid #4CAF50; }}
                        .footer {{ text-align: center; margin-top: 30px; font-size: 12px; color: #777; }}
                        @media print {{
                            .no-print {{ display: none; }}
                            button {{ display: none; }}
                        }}
                    </style>
                </head>
                <body>
                    <div class="header">
                        <h1>Relatório de Validade</h1>
                        <p>Período: Próximos {days} dias • Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
                        {f"<p>Filtro: {self.search_text}</p>" if self.search_text else ""}
                    </div>
                    
                    <div class="no-print">
                        <button onclick="window.print()">Imprimir</button>
                        <button onclick="window.close()">Fechar</button>
                    </div>
                    
                    <div class="stats">
                        <div class="stat-card">
                            <h3>Vencendo em {days} dias</h3>
                            <p>{total_expiring}</p>
                        </div>
                        <div class="stat-card">
                            <h3>Críticos (7 dias)</h3>
                            <p>{len(critical_products)}</p>
                        </div>
                        <div class="stat-card">
                            <h3>Valor Total</h3>
                            <p>R$ {total_value:.2f}</p>
                        </div>
                    </div>
                    
                    <div class="chart">
                        <h2>Distribuição por Mês de Vencimento</h2>
                ''')
                
                # Adicionar gráfico de barras
                max_count = max(group["count"] for group in expiry_groups) if expiry_groups else 0
                
                for group in expiry_groups:
                    # Calcular altura relativa da barra (máximo 100px)
                    height = int((group["count"] / max_count) * 100) if max_count > 0 else 0
                    
                    tmp.write(f'''
                    <div class="chart-bar">
                        <div class="bar" style="height: {max(height, 20)}px; width: 40px;">{group["count"]}</div>
                        <div>{group["name"]}</div>
                    </div>
                    ''')
                
                tmp.write('</div>')  # Fechar div do gráfico
                
                # Adicionar lista de produtos
                tmp.write('<h2>Produtos por Data de Validade</h2>')
                
                for product in sorted_products:
                    # Calcular dias até o vencimento
                    days_remaining = "N/A"
                    css_class = "normal"
                    
                    try:
                        expiry_date = datetime.strptime(product["expiry"], "%d/%m/%Y")
                        days = (expiry_date - datetime.now()).days
                        days_remaining = days
                        
                        if days <= 7:
                            css_class = "critical"
                        elif days <= 30:
                            css_class = "warning"
                    except:
                        pass
                    
                    # Calcular valor total
                    value = product.get("value", 0)
                    quantity = product.get("quantity", 0)
                    total_value = value * quantity
                    
                    tmp.write(f'''
                    <div class="product-item {css_class}">
                        <h3>{product.get("name", "")}</h3>
                        <p>Lote: {product.get("lot", "N/A")} • Quantidade: {product.get("quantity", 0)}</p>
                        <p>Validade: {product.get("expiry", "N/A")} • Dias restantes: {days_remaining}</p>
                        <p>Grupo: {product.get("group_name", "N/A")} • Valor total: R$ {total_value:.2f}</p>
                    </div>
                    ''')
                
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
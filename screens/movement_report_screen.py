import flet as ft
from datetime import datetime, timedelta

class MovementReportScreen:
    def __init__(self, data, navigation):
        self.data = data
        self.navigation = navigation
        self.selected_period = "30"  # Padrão: 30 dias
        self.selected_type = "all"   # Padrão: todos os tipos
        self.search_text = ""
        self.show_details = False    # Controla se mostra detalhes expandidos

    def build(self):
        # Obter histórico de movimentação
        period_days = int(self.selected_period)
        movement_history = self.data.get_product_movement_history(
            product_name=self.search_text if self.search_text else None,
            days=period_days
        )
        
        # Filtrar por tipo se necessário
        if self.selected_type != "all":
            movement_history = [m for m in movement_history if m["type"] == self.selected_type]
        
        # Filtros
        period_dropdown = ft.Dropdown(
            options=[
                ft.dropdown.Option("7", "Últimos 7 dias"),
                ft.dropdown.Option("30", "Últimos 30 dias"),
                ft.dropdown.Option("90", "Últimos 90 dias"),
                ft.dropdown.Option("365", "Último ano"),
            ],
            value=self.selected_period,
            on_change=self._on_period_change,
            width=150,
        )
        
        type_dropdown = ft.Dropdown(
            options=[
                ft.dropdown.Option("all", "Todos os tipos"),
                ft.dropdown.Option("entry", "Entradas"),
                ft.dropdown.Option("exit", "Saídas"),
                ft.dropdown.Option("adjustment", "Ajustes"),
            ],
            value=self.selected_type,
            on_change=self._on_type_change,
            width=150,
        )
        
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
        
        # Estatísticas resumidas
        total_entries = sum(m["quantity"] for m in movement_history if m["type"] == "entry")
        total_exits = sum(m["quantity"] for m in movement_history if m["type"] == "exit")
        net_change = total_entries - total_exits
        
        stats_row = ft.Row(
            [
                self._build_stat_card(
                    "Entradas Totais",
                    total_entries,
                    ft.icons.ADD_CIRCLE_OUTLINE,
                    ft.colors.GREEN_500
                ),
                self._build_stat_card(
                    "Saídas Totais",
                    total_exits,
                    ft.icons.REMOVE_CIRCLE_OUTLINE,
                    ft.colors.RED_500
                ),
                self._build_stat_card(
                    "Saldo Líquido",
                    net_change,
                    ft.icons.SYNC_ALT,
                    ft.colors.BLUE_500 if net_change >= 0 else ft.colors.RED_500
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        
        # Construir lista de movimentações
        movement_items = []
        
        # Agrupar por data para melhor visualização
        grouped_movements = self._group_by_date(movement_history)
        
        for date, movements in grouped_movements.items():
            # Adicionar cabeçalho da data
            movement_items.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Icon(ft.icons.CALENDAR_TODAY, size=20, color=ft.colors.BLUE_500),
                            ft.Text(
                                date,
                                size=16,
                                weight="bold",
                                color=ft.colors.BLUE_500,
                            ),
                            ft.Text(
                                f"({len(movements)} movimentações)",
                                size=12,
                                color=ft.colors.GREY_700,
                            ),
                        ],
                        spacing=10,
                    ),
                    padding=ft.padding.only(left=10, top=15, bottom=5),
                    margin=ft.margin.only(top=10),
                    border=ft.border.only(bottom=ft.BorderSide(1, ft.colors.BLUE_500)),
                )
            )
            
            # Adicionar movimentações do dia
            for movement in movements:
                movement_items.append(self._build_movement_item(movement))
        
        # Verificar se há movimentações
        if not movement_items:
            movement_items.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.icons.SYNC_ALT, size=40, color=ft.colors.GREY_400),
                        ft.Text("Nenhuma movimentação encontrada", 
                               size=14, color=ft.colors.GREY_700),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=20,
                    alignment=ft.alignment.center,
                )
            )
        
        # Gráfico de movimentação (se mostrar detalhes)
        movement_chart = None
        if self.show_details:
            movement_chart = self._build_movement_chart(movement_history)
        
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
                            ft.Text("Relatório de Movimentação", size=20, weight="bold"),
                        ]
                    ),
                    padding=10,
                ),
                
                # Filtros
                ft.Container(
                    content=ft.Column(
                        [
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
                        ],
                        spacing=10,
                    ),
                    padding=ft.padding.only(left=20, right=20, bottom=10),
                ),
                
                # Estatísticas
                ft.Container(
                    content=stats_row,
                    padding=ft.padding.only(left=20, right=20, bottom=10),
                ),
                
                # Gráfico (se mostrar detalhes)
                ft.Container(
                    content=movement_chart,
                    padding=ft.padding.only(left=20, right=20, bottom=10),
                    visible=self.show_details and movement_chart is not None,
                ),
                
                # Lista de movimentações
                ft.Container(
                    content=ft.Column(
                        movement_items,
                        spacing=10,
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
        """Atualiza o tipo selecionado e reconstrói o relatório"""
        self.selected_type = e.control.value
        self.navigation.update_view()
    
    def _on_search_change(self, e):
        """Atualiza o texto de busca e reconstrói o relatório"""
        self.search_text = e.control.value
        self.navigation.update_view()
    
    def _toggle_details(self, e):
        """Alterna a exibição de detalhes"""
        self.show_details = not self.show_details
        self.navigation.update_view()
    
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
    
    def _build_movement_item(self, movement):
        """Constrói um item de movimentação"""
        # Definir ícone e cor com base no tipo
        icon = ft.icons.ADD_CIRCLE_OUTLINE
        color = ft.colors.GREEN_500
        
        if movement["type"] == "exit":
            icon = ft.icons.REMOVE_CIRCLE_OUTLINE
            color = ft.colors.RED_500
        elif movement["type"] == "adjustment":
            icon = ft.icons.TUNE
            color = ft.colors.ORANGE_500
        
        # Formatar tipo para exibição
        type_text = "Entrada"
        if movement["type"] == "exit":
            type_text = "Saída"
        elif movement["type"] == "adjustment":
            type_text = "Ajuste"
        
        return ft.Container(
            content=ft.Row(
                [
                    ft.Icon(icon, color=color, size=24),
                    ft.Column(
                        [
                            ft.Text(movement["productName"], size=16, weight="bold"),
                            ft.Text(
                                f"Quantidade: {movement['quantity']} • Data: {movement['date']}",
                                size=12,
                                color=ft.colors.GREY_700,
                            ),
                            ft.Text(
                                f"Tipo: {type_text} • Motivo: {movement.get('reason', 'N/A')}",
                                size=12,
                                color=ft.colors.GREY_700,
                            ),
                        ],
                        spacing=5,
                        expand=True,
                    ),
                ],
                spacing=10,
            ),
            padding=15,
            border_radius=10,
            bgcolor=ft.colors.WHITE,
            border=ft.border.all(1, ft.colors.GREY_300),
        )
    
    def _group_by_date(self, movements):
        """Agrupa movimentações por data"""
        grouped = {}
        
        for movement in movements:
            date = movement.get("date", "Data desconhecida")
            
            if date not in grouped:
                grouped[date] = []
            
            grouped[date].append(movement)
        
        # Ordenar datas (mais recente primeiro)
        return dict(sorted(grouped.items(), key=lambda x: self._parse_date(x[0]), reverse=True))
    
    def _parse_date(self, date_str):
        """Converte string de data para objeto datetime"""
        try:
            return datetime.strptime(date_str, "%d/%m/%Y")
        except:
            return datetime.min
    
    def _build_movement_chart(self, movements):
        """Constrói um gráfico de movimentação"""
        # Se não houver movimentações suficientes, não mostrar gráfico
        if len(movements) < 2:
            return None
        
        # Agrupar por data e tipo
        entries_by_date = {}
        exits_by_date = {}
        
        # Obter datas únicas ordenadas
        all_dates = set()
        for movement in movements:
            date = movement.get("date", "")
            all_dates.add(date)
        
        # Ordenar datas
        sorted_dates = sorted(list(all_dates), key=lambda x: self._parse_date(x))
        
        # Limitar a 10 datas mais recentes para o gráfico não ficar muito grande
        if len(sorted_dates) > 10:
            sorted_dates = sorted_dates[-10:]
        
        # Inicializar contadores
        for date in sorted_dates:
            entries_by_date[date] = 0
            exits_by_date[date] = 0
        
        # Contar entradas e saídas por data
        for movement in movements:
            date = movement.get("date", "")
            if date in sorted_dates:
                if movement["type"] == "entry":
                    entries_by_date[date] += movement["quantity"]
                elif movement["type"] == "exit":
                    exits_by_date[date] += movement["quantity"]
        
        # Criar barras para o gráfico
        chart_bars = []
        
        # Encontrar o valor máximo para escala
        max_value = max(
            max(entries_by_date.values()) if entries_by_date else 0,
            max(exits_by_date.values()) if exits_by_date else 0
        )
        
        for date in sorted_dates:
            entry_value = entries_by_date[date]
            exit_value = exits_by_date[date]
            
            # Calcular alturas relativas (máximo 100)
            entry_height = (entry_value / max_value) * 100 if max_value > 0 else 0
            exit_height = (exit_value / max_value) * 100 if max_value > 0 else 0
            
            chart_bars.append(
                ft.Column(
                    [
                        ft.Container(
                            content=ft.Text(str(entry_value), size=10, color=ft.colors.WHITE),
                            bgcolor=ft.colors.GREEN_500,
                            border_radius=ft.border_radius.only(top_left=5, top_right=5),
                            height=max(entry_height, 20),
                            width=25,
                            alignment=ft.alignment.center,
                        ),
                        ft.Container(
                            content=ft.Text(str(exit_value), size=10, color=ft.colors.WHITE),
                            bgcolor=ft.colors.RED_500,
                            border_radius=ft.border_radius.only(top_left=5, top_right=5),
                            height=max(exit_height, 20),
                            width=25,
                            alignment=ft.alignment.center,
                            margin=ft.margin.only(top=5),
                        ),
                        ft.Text(date[-5:], size=10, text_align=ft.TextAlign.CENTER),  # Mostrar apenas MM/DD
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.END,
                )
            )
        
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("Movimentação por Data", size=16, weight="bold"),
                    ft.Row(
                        [
                            ft.Row([
                                ft.Container(width=15, height=15, bgcolor=ft.colors.GREEN_500),
                                ft.Text("Entradas", size=12),
                            ], spacing=5),
                            ft.Row([
                                ft.Container(width=15, height=15, bgcolor=ft.colors.RED_500),
                                ft.Text("Saídas", size=12),
                            ], spacing=5),
                        ],
                        spacing=20,
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    ft.Container(
                        content=ft.Row(
                            chart_bars,
                            alignment=ft.MainAxisAlignment.SPACE_AROUND,
                        ),
                        height=250,
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
    
    def _export_report(self, e):
        """Exporta o relatório para um arquivo CSV"""
        try:
            import csv
            import os
            from datetime import datetime
            
            # Criar diretório de relatórios se não existir
            os.makedirs("reports", exist_ok=True)
            
            # Nome do arquivo com timestamp
            filename = f"reports/movement_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            # Obter dados para o relatório
            period_days = int(self.selected_period)
            movement_history = self.data.get_product_movement_history(
                product_name=self.search_text if self.search_text else None,
                days=period_days
            )
            
            # Filtrar por tipo se necessário
            if self.selected_type != "all":
                movement_history = [m for m in movement_history if m["type"] == self.selected_type]
            
            # Escrever arquivo CSV
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Cabeçalho
                writer.writerow([
                    "Data", "Produto", "Quantidade", "Tipo", "Motivo", "ID"
                ])
                
                # Dados de cada movimentação
                for movement in movement_history:
                    # Formatar tipo para exibição
                    type_text = "Entrada"
                    if movement["type"] == "exit":
                        type_text = "Saída"
                    elif movement["type"] == "adjustment":
                        type_text = "Ajuste"
                    
                    writer.writerow([
                        movement["date"],
                        movement["productName"],
                        movement["quantity"],
                        type_text,
                        movement.get("reason", "N/A"),
                        movement["id"]
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
            period_days = int(self.selected_period)
            movement_history = self.data.get_product_movement_history(
                product_name=self.search_text if self.search_text else None,
                days=period_days
            )
            
            # Filtrar por tipo se necessário
            if self.selected_type != "all":
                movement_history = [m for m in movement_history if m["type"] == self.selected_type]
            
            # Agrupar por data
            grouped_movements = self._group_by_date(movement_history)
            
            # Calcular estatísticas
            total_entries = sum(m["quantity"] for m in movement_history if m["type"] == "entry")
            total_exits = sum(m["quantity"] for m in movement_history if m["type"] == "exit")
            net_change = total_entries - total_exits
            
            # Criar arquivo HTML temporário
            fd, path = tempfile.mkstemp(suffix='.html')
            
            with os.fdopen(fd, 'w') as tmp:
                # Escrever cabeçalho HTML
                tmp.write(f'''
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <title>Relatório de Movimentação</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 20px; }}
                        .header {{ text-align: center; margin-bottom: 20px; }}
                        .stats {{ display: flex; justify-content: space-between; margin-bottom: 20px; }}
                        .stat-card {{ border: 1px solid #ddd; padding: 10px; text-align: center; width: 30%; }}
                        .date-header {{ background-color: #f2f2f2; padding: 10px; margin-top: 20px; }}
                        .movement-item {{ border: 1px solid #ddd; padding: 10px; margin-bottom: 5px; }}
                        .entry {{ border-left: 5px solid #4CAF50; }}
                        .exit {{ border-left: 5px solid #F44336; }}
                        .adjustment {{ border-left: 5px solid #FF9800; }}
                        .footer {{ text-align: center; margin-top: 30px; font-size: 12px; color: #777; }}
                        @media print {{
                            .no-print {{ display: none; }}
                            button {{ display: none; }}
                        }}
                    </style>
                </head>
                <body>
                    <div class="header">
                        <h1>Relatório de Movimentação</h1>
                        <p>Período: Últimos {period_days} dias • Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
                        <p>Filtro: {self.selected_type.capitalize() if self.selected_type != "all" else "Todos os tipos"} 
                           {f"• Busca: {self.search_text}" if self.search_text else ""}</p>
                    </div>
                    
                    <div class="no-print">
                        <button onclick="window.print()">Imprimir</button>
                        <button onclick="window.close()">Fechar</button>
                    </div>
                    
                    <div class="stats">
                        <div class="stat-card">
                            <h3>Entradas Totais</h3>
                            <p>{total_entries}</p>
                        </div>
                        <div class="stat-card">
                            <h3>Saídas Totais</h3>
                            <p>{total_exits}</p>
                        </div>
                        <div class="stat-card">
                            <h3>Saldo Líquido</h3>
                            <p>{net_change}</p>
                        </div>
                    </div>
                ''')
                
                # Adicionar movimentações agrupadas por data
                for date, movements in grouped_movements.items():
                    tmp.write(f'''
                    <div class="date-header">
                        <h2>{date} ({len(movements)} movimentações)</h2>
                    </div>
                    ''')
                    
                    for movement in movements:
                        # Definir classe CSS com base no tipo
                        css_class = "entry"
                        type_text = "Entrada"
                        
                        if movement["type"] == "exit":
                            css_class = "exit"
                            type_text = "Saída"
                        elif movement["type"] == "adjustment":
                            css_class = "adjustment"
                            type_text = "Ajuste"
                        
                        tmp.write(f'''
                        <div class="movement-item {css_class}">
                            <h3>{movement["productName"]}</h3>
                            <p>Quantidade: {movement["quantity"]} • Tipo: {type_text}</p>
                            <p>Motivo: {movement.get("reason", "N/A")}</p>
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
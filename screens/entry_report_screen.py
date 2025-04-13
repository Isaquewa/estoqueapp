import flet as ft
from datetime import datetime, timedelta

class EntryReportScreen:
    def __init__(self, data, navigation):
        self.data = data
        self.navigation = navigation
        self.filter_days = "30"  # Padrão: últimos 30 dias
        self.filter_type = "all"  # Padrão: todos (produtos e resíduos)
        self.search_text = ""
        self.show_details = False  # Controla se mostra detalhes expandidos
    
    def build(self):
        # Filtros
        days_dropdown = ft.Dropdown(
            options=[
                ft.dropdown.Option("7", "Últimos 7 dias"),
                ft.dropdown.Option("30", "Últimos 30 dias"),
                ft.dropdown.Option("90", "Últimos 90 dias"),
                ft.dropdown.Option("365", "Último ano"),
            ],
            value=self.filter_days,
            on_change=self._on_days_filter_change,
            width=180,
        )
        
        type_dropdown = ft.Dropdown(
            options=[
                ft.dropdown.Option("all", "Todos"),
                ft.dropdown.Option("products", "Produtos"),
                ft.dropdown.Option("residues", "Resíduos"),
            ],
            value=self.filter_type,
            on_change=self._on_type_filter_change,
            width=150,
        )
        
        search_field = ft.TextField(
            hint_text="Buscar por nome...",
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
        
        # Obter dados de entradas
        days = int(self.filter_days)
        entries = self._get_entries(days, self.filter_type)
        
        # Filtrar por texto de busca
        if self.search_text:
            search_lower = self.search_text.lower()
            entries = [
                entry for entry in entries
                if search_lower in entry.get("name", "").lower()
            ]
        
        # Agrupar entradas por data
        grouped_entries = self._group_by_date(entries)
        
        # Construir lista de entradas
        entry_items = []
        
        if grouped_entries:
            for date, date_entries in grouped_entries.items():
                # Cabeçalho da data
                entry_items.append(
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
                                    f"({len(date_entries)} entradas)",
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
                
                # Entradas da data
                for entry in date_entries:
                    entry_items.append(self._build_entry_item(entry))
        else:
            entry_items.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Icon(ft.icons.INBOX, size=50, color=ft.colors.GREY_400),
                            ft.Text(f"Nenhuma entrada nos últimos {days} dias", 
                                   size=16, color=ft.colors.GREY_700),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10,
                    ),
                    padding=20,
                    alignment=ft.alignment.center,
                )
            )
        
        # Estatísticas
        total_entries = len(entries)
        total_quantity = sum(entry.get("quantity", 0) for entry in entries)
        
        stats_row = ft.Container(
            content=ft.Row(
                [
                    self._build_stat_card(
                        "Total de Entradas", 
                        total_entries, 
                        ft.icons.INPUT, 
                        ft.colors.BLUE_500
                    ),
                    self._build_stat_card(
                        "Quantidade Total", 
                        total_quantity, 
                        ft.icons.INVENTORY_2_ROUNDED, 
                        ft.colors.GREEN_500
                    ),
                    self._build_stat_card(
                        "Média por Entrada", 
                        round(total_quantity / total_entries, 1) if total_entries > 0 else 0, 
                        ft.icons.ANALYTICS_ROUNDED, 
                        ft.colors.PURPLE_500
                    ),
                ]
            ),
            padding=10,
        )
        
        # Gráfico de entradas (se mostrar detalhes)
        entry_chart = None
        if self.show_details and entries:
            entry_chart = self._build_entry_chart(entries)
        
        # Lista de entradas
        entries_list = ft.ListView(
            controls=entry_items,
            spacing=10,
            padding=10,
            expand=True,
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
                            ft.Text("Relatório de Entradas", size=20, weight="bold"),
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
                                    days_dropdown,
                                    ft.Text("Tipo:", size=14),
                                    type_dropdown,
                                ],
                                spacing=10,
                                alignment=ft.MainAxisAlignment.START,
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
                stats_row,
                
                # Gráfico (se mostrar detalhes)
                ft.Container(
                    content=entry_chart,
                    padding=ft.padding.only(left=20, right=20, bottom=10),
                    visible=self.show_details and entry_chart is not None,
                ),
                
                # Lista de entradas
                entries_list,
            ],
            expand=True,
        )
    
    def _on_days_filter_change(self, e):
        """Atualiza o filtro de dias"""
        self.filter_days = e.control.value
        self.navigation.update_view()
    
    def _on_type_filter_change(self, e):
        """Atualiza o filtro de tipo"""
        self.filter_type = e.control.value
        self.navigation.update_view()
    
    def _on_search_change(self, e):
        """Atualiza o texto de busca"""
        self.search_text = e.control.value
        self.navigation.update_view()
    
    def _toggle_details(self, e):
        """Alterna a exibição de detalhes"""
        self.show_details = not self.show_details
        self.navigation.update_view()
    
    def _get_entries(self, days, entry_type):
        """Obtém as entradas de acordo com os filtros"""
        entries = []
        
        # Calcular data limite
        cutoff_date = datetime.now() - timedelta(days=days)
        cutoff_timestamp = cutoff_date.timestamp()
        
        # Obter entradas de produtos
        if entry_type in ["all", "products"]:
            product_entries = self._get_product_entries(cutoff_timestamp)
            entries.extend(product_entries)
        
        # Obter entradas de resíduos
        if entry_type in ["all", "residues"]:
            residue_entries = self._get_residue_entries(cutoff_timestamp)
            entries.extend(residue_entries)
        
        # Ordenar por data (mais recente primeiro)
        entries.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
        
        return entries
    
    def _get_product_entries(self, cutoff_timestamp):
        """Obtém entradas de produtos"""
        try:
            cursor = self.data.db.conn.cursor()
            cursor.execute('''
            SELECT * FROM product_history 
            WHERE type = 'entry' AND timestamp >= ? 
            ORDER BY timestamp DESC
            ''', (cutoff_timestamp,))
            
            results = cursor.fetchall()
            entries = []
            
            for row in results:
                try:
                    entry = {
                        "id": row[0],
                        "itemId": row[1],
                        "name": row[2],
                        "quantity": row[3],
                        "reason": row[4],
                        "date": row[5],
                        "timestamp": row[6],
                        "type": "product",
                        "icon": ft.icons.INVENTORY_2_ROUNDED,
                        "color": ft.colors.BLUE_500
                    }
                    entries.append(entry)
                except Exception as e:
                    print(f"Erro ao processar entrada de produto: {e}")
                    continue
            
            return entries
        except Exception as e:
            print(f"Erro ao buscar entradas de produtos: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _get_residue_entries(self, cutoff_timestamp):
        """Obtém entradas de resíduos"""
        try:
            cursor = self.data.db.conn.cursor()
            cursor.execute('''
            SELECT * FROM residue_history 
            WHERE type = 'entry' AND timestamp >= ? 
            ORDER BY timestamp DESC
            ''', (cutoff_timestamp,))
            
            results = cursor.fetchall()
            entries = []
            
            for row in results:
                try:
                    entry = {
                        "id": row[0],
                        "itemId": row[1],
                        "name": row[2],
                        "quantity": row[3],
                        "reason": row[4],
                        "date": row[5],
                        "timestamp": row[6],
                        "type": "residue",
                        "icon": ft.icons.DELETE_OUTLINE,
                        "color": ft.colors.PURPLE_500
                    }
                    entries.append(entry)
                except Exception as e:
                    print(f"Erro ao processar entrada de resíduo: {e}")
                    continue
            
            return entries
        except Exception as e:
            print(f"Erro ao buscar entradas de resíduos: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _group_by_date(self, entries):
        """Agrupa entradas por data"""
        grouped = {}
        
        for entry in entries:
            date = entry.get("date", "Data desconhecida")
            
            if date not in grouped:
                grouped[date] = []
            
            grouped[date].append(entry)
        
        # Ordenar datas (mais recente primeiro)
        return dict(sorted(grouped.items(), key=lambda x: self._parse_date(x[0]), reverse=True))
    
    def _parse_date(self, date_str):
        """Converte string de data para objeto datetime"""
        try:
            return datetime.strptime(date_str, "%d/%m/%Y")
        except:
            return datetime.min
    
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
    
    def _build_entry_item(self, entry):
        """Cria um item de entrada para a lista"""
        # Obter ícone e cor com base no tipo
        icon = entry.get("icon", ft.icons.INPUT)
        color = entry.get("color", ft.colors.BLUE_500)
        
        return ft.Container(
            content=ft.Row(
                [
                    ft.Icon(icon, color=color, size=24),
                    ft.Column(
                        [
                            ft.Text(entry["name"], size=16, weight="w500"),
                            ft.Text(
                                f"Quantidade: {entry['quantity']} • {entry.get('reason', 'Entrada no estoque')}",
                                size=12,
                                color=ft.colors.GREY_700,
                            ),
                        ],
                        spacing=5,
                        expand=True,
                    ),
                    ft.Text(
                        entry["date"],
                        size=14,
                        color=ft.colors.GREY_700,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=10,
            border_radius=8,
            bgcolor=ft.colors.WHITE,
            border=ft.border.all(1, ft.colors.GREY_300),
        )
    
    def _build_entry_chart(self, entries):
        """Constrói um gráfico de entradas por tipo e data"""
        # Agrupar entradas por data e tipo
        product_entries_by_date = {}
        residue_entries_by_date = {}
        
        # Obter datas únicas ordenadas
        all_dates = set()
        for entry in entries:
            date = entry.get("date", "")
            all_dates.add(date)
        
        # Ordenar datas
        sorted_dates = sorted(list(all_dates), key=lambda x: self._parse_date(x))
        
        # Limitar a 10 datas mais recentes para o gráfico não ficar muito grande
        if len(sorted_dates) > 10:
            sorted_dates = sorted_dates[-10:]
        
        # Inicializar contadores
        for date in sorted_dates:
            product_entries_by_date[date] = 0
            residue_entries_by_date[date] = 0
        
        # Contar entradas por data e tipo
        for entry in entries:
            date = entry.get("date", "")
            if date in sorted_dates:
                if entry.get("type") == "product":
                    product_entries_by_date[date] += entry.get("quantity", 0)
                else:
                    residue_entries_by_date[date] += entry.get("quantity", 0)
        
        # Criar barras para o gráfico
        chart_bars = []
        
        # Encontrar o valor máximo para escala
        max_value = max(
            max(product_entries_by_date.values()) if product_entries_by_date else 0,
            max(residue_entries_by_date.values()) if residue_entries_by_date else 0
        )
        
        for date in sorted_dates:
            product_value = product_entries_by_date[date]
            residue_value = residue_entries_by_date[date]
            
            # Calcular alturas relativas (máximo 100)
            product_height = (product_value / max_value) * 100 if max_value > 0 else 0
            residue_height = (residue_value / max_value) * 100 if max_value > 0 else 0
            
            chart_bars.append(
                ft.Column(
                    [
                        ft.Container(
                            content=ft.Text(str(product_value), size=10, color=ft.colors.WHITE),
                            bgcolor=ft.colors.BLUE_500,
                            border_radius=ft.border_radius.only(top_left=5, top_right=5),
                            height=max(product_height, 20),
                            width=25,
                            alignment=ft.alignment.center,
                        ),
                        ft.Container(
                            content=ft.Text(str(residue_value), size=10, color=ft.colors.WHITE),
                            bgcolor=ft.colors.PURPLE_500,
                            border_radius=ft.border_radius.only(top_left=5, top_right=5),
                            height=max(residue_height, 20),
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
                    ft.Text("Entradas por Data e Tipo", size=16, weight="bold"),
                    ft.Row(
                        [
                            ft.Row([
                                ft.Container(width=15, height=15, bgcolor=ft.colors.BLUE_500),
                                ft.Text("Produtos", size=12),
                            ], spacing=5),
                            ft.Row([
                                ft.Container(width=15, height=15, bgcolor=ft.colors.PURPLE_500),
                                ft.Text("Resíduos", size=12),
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
            filename = f"reports/entry_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            # Obter dados para o relatório
            days = int(self.filter_days)
            entries = self._get_entries(days, self.filter_type)
            
            # Filtrar por texto de busca
            if self.search_text:
                search_lower = self.search_text.lower()
                entries = [
                    entry for entry in entries
                    if search_lower in entry.get("name", "").lower()
                ]
            
            # Escrever arquivo CSV
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Cabeçalho
                writer.writerow([
                    "Data", "Nome", "Quantidade", "Tipo", "Motivo", "ID"
                ])
                
                # Dados de cada entrada
                for entry in entries:
                    writer.writerow([
                        entry.get("date", ""),
                        entry.get("name", ""),
                        entry.get("quantity", 0),
                        "Produto" if entry.get("type") == "product" else "Resíduo",
                        entry.get("reason", ""),
                        entry.get("id", "")
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
            entries = self._get_entries(days, self.filter_type)
            
            # Filtrar por texto de busca
            if self.search_text:
                search_lower = self.search_text.lower()
                entries = [
                    entry for entry in entries
                    if search_lower in entry.get("name", "").lower()
                ]
            
            # Agrupar por data
            grouped_entries = self._group_by_date(entries)
            
            # Calcular estatísticas
            total_entries = len(entries)
            total_quantity = sum(entry.get("quantity", 0) for entry in entries)
            avg_per_entry = round(total_quantity / total_entries, 1) if total_entries > 0 else 0
            
            # Criar arquivo HTML temporário
            fd, path = tempfile.mkstemp(suffix='.html')
            
            with os.fdopen(fd, 'w') as tmp:
                # Escrever cabeçalho HTML
                tmp.write(f'''
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <title>Relatório de Entradas</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 20px; }}
                        .header {{ text-align: center; margin-bottom: 20px; }}
                        .stats {{ display: flex; justify-content: space-between; margin-bottom: 20px; }}
                        .stat-card {{ border: 1px solid #ddd; padding: 10px; text-align: center; width: 30%; }}
                        .date-header {{ background-color: #f2f2f2; padding: 10px; margin-top: 20px; }}
                        .entry-item {{ border: 1px solid #ddd; padding: 10px; margin-bottom: 5px; }}
                        .product {{ border-left: 5px solid #2196F3; }}
                        .residue {{ border-left: 5px solid #9C27B0; }}
                        .footer {{ text-align: center; margin-top: 30px; font-size: 12px; color: #777; }}
                        @media print {{
                            .no-print {{ display: none; }}
                            button {{ display: none; }}
                        }}
                    </style>
                </head>
                <body>
                    <div class="header">
                        <h1>Relatório de Entradas</h1>
                        <p>Período: Últimos {days} dias • Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
                        <p>Tipo: {self.filter_type.capitalize() if self.filter_type != "all" else "Todos"} 
                           {f"• Busca: {self.search_text}" if self.search_text else ""}</p>
                    </div>
                    
                    <div class="no-print">
                        <button onclick="window.print()">Imprimir</button>
                        <button onclick="window.close()">Fechar</button>
                    </div>
                    
                    <div class="stats">
                        <div class="stat-card">
                            <h3>Total de Entradas</h3>
                            <p>{total_entries}</p>
                        </div>
                        <div class="stat-card">
                            <h3>Quantidade Total</h3>
                            <p>{total_quantity}</p>
                        </div>
                        <div class="stat-card">
                            <h3>Média por Entrada</h3>
                            <p>{avg_per_entry}</p>
                        </div>
                    </div>
                ''')
                
                # Adicionar entradas agrupadas por data
                for date, date_entries in grouped_entries.items():
                    tmp.write(f'''
                    <div class="date-header">
                        <h2>{date} ({len(date_entries)} entradas)</h2>
                    </div>
                    ''')
                    
                    for entry in date_entries:
                        # Definir classe CSS com base no tipo
                        css_class = "product" if entry.get("type") == "product" else "residue"
                        type_text = "Produto" if entry.get("type") == "product" else "Resíduo"
                        
                        tmp.write(f'''
                        <div class="entry-item {css_class}">
                            <h3>{entry.get("name", "")}</h3>
                            <p>Quantidade: {entry.get("quantity", 0)} • Tipo: {type_text}</p>
                            <p>Motivo: {entry.get("reason", "Entrada no estoque")}</p>
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
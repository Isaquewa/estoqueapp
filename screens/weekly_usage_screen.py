import json
import flet as ft
from datetime import datetime, timedelta

class WeeklyUsageScreen:
    def __init__(self, data, navigation):
        self.data = data
        self.navigation = navigation
        self.product = None  # Inicializa o produto como None
    
    def set_product(self, product):
        """Define o produto para o uso semanal e carrega dados atualizados"""
        # Armazenar o ID do produto
        self.product_id = product["id"]
        
        # Buscar dados atualizados do banco de dados
        try:
            cursor = self.data.db.conn.cursor()
            cursor.execute('SELECT * FROM products WHERE id = ?', (self.product_id,))
            product_data = cursor.fetchone()
            
            if product_data:
                # Converter para dicionário usando o método do serviço de produtos
                self.product = self.data.product_service._convert_to_dict([product_data])[0]
                print(f"Produto carregado do banco de dados: {self.product['name']}")
                print(f"Uso semanal: {self.product.get('weeklyUsage', [])}")
            else:
                # Se não encontrar no banco de dados, usar o produto fornecido
                self.product = product
                print(f"Produto não encontrado no banco de dados, usando dados fornecidos")
        except Exception as e:
            print(f"Erro ao carregar produto do banco de dados: {e}")
            # Em caso de erro, usar o produto fornecido
            self.product = product
    
    def build(self):
        """Constrói a tela de uso semanal"""
        # Cores modernas
        primary_color = "#4A6FFF"  # Azul moderno
        secondary_color = "#6C5CE7"  # Roxo moderno
        accent_color = "#00D2D3"  # Turquesa
        warning_color = "#FFA502"  # Laranja
        danger_color = "#FF6B6B"  # Vermelho suave
        success_color = "#2ED573"  # Verde
        bg_color = "#F8F9FD"  # Fundo claro
        card_bg = "#FFFFFF"  # Branco para cards
        
        if not self.product:
            return ft.Container(
                content=ft.Column([
                    ft.Icon(ft.icons.ERROR_OUTLINE, size=50, color="#CCCCCC"),
                    ft.Text("Produto não encontrado", size=18, color="#909090"),
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
                expand=True
            )
        
        # Recarregar dados do produto para garantir que estão atualizados
        try:
            cursor = self.data.db.conn.cursor()
            cursor.execute('SELECT * FROM products WHERE id = ?', (self.product["id"],))
            product_data = cursor.fetchone()
            
            if product_data:
                # Atualizar o produto com dados frescos do banco de dados
                self.product = self.data.product_service._convert_to_dict([product_data])[0]
                print(f"Produto recarregado do banco de dados para exibição")
                print(f"Uso semanal atualizado: {self.product.get('weeklyUsage', [])}")
        except Exception as e:
            print(f"Erro ao recarregar produto: {e}")
        
        # Verificar e preparar os dados de uso semanal
        weekly_usage = self.product.get("weeklyUsage", [0] * 7)
        
        # Garantir que weekly_usage seja uma lista
        if not isinstance(weekly_usage, list):
            try:
                weekly_usage = json.loads(weekly_usage)
                print(f"Convertido weekly_usage de JSON para lista: {weekly_usage}")
            except Exception as e:
                print(f"Erro ao converter weekly_usage: {e}")
                weekly_usage = [0] * 7
    
        # Garantir que a lista tenha 7 elementos
        while len(weekly_usage) < 7:
            weekly_usage.append(0)
        
        # Limitar a 7 elementos se tiver mais
        weekly_usage = weekly_usage[:7]
        
        # Garantir que todos os elementos sejam números
        for i in range(7):
            try:
                if isinstance(weekly_usage[i], str) and weekly_usage[i].isdigit():
                    weekly_usage[i] = int(weekly_usage[i])
                elif not isinstance(weekly_usage[i], (int, float)):
                    weekly_usage[i] = 0
            except (ValueError, TypeError):
                weekly_usage[i] = 0
        
        # Calcular estatísticas
        total_usage = sum(weekly_usage)
        avg_daily = round(total_usage / 7, 1) if total_usage > 0 else 0
        max_usage = max(weekly_usage) if weekly_usage else 0
        
        # Obter o dia atual da semana (0 = domingo, 6 = sábado)
        current_day = datetime.now().weekday()
        # Converter para formato onde 0 = domingo, 6 = sábado
        current_day_index = (current_day + 1) % 7
        
        # Criar campos de entrada para cada dia
        usage_fields = []
        days = ["Domingo", "Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado"]
        
        for i, day in enumerate(days):
            # Destacar o dia atual
            is_current_day = i == current_day_index
            
            usage_fields.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text(
                            day, 
                            size=14, 
                            weight="bold" if is_current_day else "normal",
                            color=primary_color if is_current_day else "#505050"
                        ),
                        ft.TextField(
                            value=str(weekly_usage[i]),
                            keyboard_type=ft.KeyboardType.NUMBER,
                            border_radius=8,
                            filled=True,
                            text_align=ft.TextAlign.CENTER,
                            content_padding=10,
                            bgcolor=ft.colors.with_opacity(0.05, primary_color) if is_current_day else None,
                            border_color=primary_color if is_current_day else None,
                        ),
                    ], spacing=5, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=5,
                )
            )
        
        def save_weekly_usage(_):
            try:
                # Obter os valores dos campos
                usage_data = []
                
                # Iterar sobre os campos de forma mais segura
                for i, field_container in enumerate(usage_fields):
                    try:
                        # Verificar se o container tem o conteúdo esperado
                        if hasattr(field_container, 'content') and hasattr(field_container.content, 'controls'):
                            # Procurar o TextField nos controles
                            for control in field_container.content.controls:
                                if isinstance(control, ft.TextField):
                                    # Encontrou o TextField
                                    value = control.value or "0"
                                    usage_data.append(int(value))
                                    print(f"Campo {i}: valor = {value}")
                                    break
                            else:
                                # Se não encontrou o TextField, tenta acessar diretamente
                                if len(field_container.content.controls) > 1:
                                    text_field = field_container.content.controls[1]
                                    if hasattr(text_field, 'value'):
                                        value = text_field.value or "0"
                                        usage_data.append(int(value))
                                        print(f"Campo {i} (acesso direto): valor = {value}")
                                    else:
                                        usage_data.append(0)
                                        print(f"Campo {i}: controle não tem atributo 'value'")
                                else:
                                    usage_data.append(0)
                                    print(f"Campo {i}: número insuficiente de controles")
                        else:
                            # Se a estrutura não é a esperada, adiciona 0
                            usage_data.append(0)
                            print(f"Campo {i}: estrutura inesperada")
                    except Exception as field_error:
                        print(f"Erro ao processar campo {i}: {field_error}")
                        usage_data.append(0)
                
                # Garantir que temos 7 valores
                while len(usage_data) < 7:
                    usage_data.append(0)
                
                # Limitar a 7 valores
                usage_data = usage_data[:7]
                
                print(f"Dados de uso coletados: {usage_data}")
                
                # Atualizar o produto diretamente no banco de dados
                try:
                    # Obter o produto atual do banco de dados
                    cursor = self.data.db.conn.cursor()
                    cursor.execute('SELECT * FROM products WHERE id = ?', (self.product["id"],))
                    product_data = cursor.fetchone()
                    
                    if not product_data:
                        raise Exception(f"Produto com ID {self.product['id']} não encontrado no banco de dados")
                    
                    # Atualizar o campo weeklyUsage diretamente
                    cursor.execute('''
                    UPDATE products SET 
                        weeklyUsage = ?,
                        lastUpdateDate = ?
                    WHERE id = ?
                    ''', (
                        json.dumps(usage_data),
                        datetime.now().strftime("%d/%m/%Y"),
                        self.product["id"]
                    ))
                    
                    # Commit da transação
                    self.data.db.conn.commit()
                    
                    print(f"Produto atualizado diretamente no banco de dados")
                    
                    # Adicionar à fila de sincronização
                    updated_product = self.product.copy()
                    updated_product["weeklyUsage"] = usage_data
                    updated_product["lastUpdateDate"] = datetime.now().strftime("%d/%m/%Y")
                    
                    self.data.db.add_sync_operation('update', 'products', self.product["id"], updated_product)
                    
                    # Forçar atualização dos dados em cache
                    self.data.refresh_data()
                    
                    # Mostrar mensagem de sucesso
                    self.navigation.show_snack_bar(
                        "Uso semanal atualizado com sucesso!",
                        "#2ED573"
                    )
                    
                    # Atualizar o produto na tela atual
                    self.product = updated_product
                    
                    # Atualizar a tela atual em vez de voltar
                    self.navigation.update_view()
                    
                except Exception as db_error:
                    print(f"Erro ao atualizar banco de dados: {db_error}")
                    import traceback
                    traceback.print_exc()
                    
                    self.navigation.show_snack_bar(
                        f"Erro ao atualizar banco de dados: {str(db_error)}",
                        "#FF6B6B"
                    )
            except Exception as e:
                # Mostrar mensagem de erro detalhada
                print(f"Erro ao salvar uso semanal: {e}")
                import traceback
                traceback.print_exc()
                
                self.navigation.show_snack_bar(
                    f"Erro: {str(e)}",
                    "#FF6B6B"
                )
           
        # Buscar histórico de saídas (apenas do tipo uso_semanal)
        exit_history = self._get_product_exit_history(self.product["id"])
        
        return ft.Container(
            content=ft.Column(
                controls=[
                    # Cabeçalho
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.IconButton(
                                    icon=ft.icons.ARROW_BACK,
                                    icon_color="#505050",
                                    on_click=lambda _: self.navigation.go_back()
                                ),
                                ft.Column([
                                    ft.Text(
                                        f"Uso Semanal", 
                                        size=20, 
                                        weight="bold",
                                        color="#303030"
                                    ),
                                    ft.Text(
                                        self.product['name'],
                                        size=14,
                                        color="#707070"
                                    ),
                                ], spacing=2),
                                ft.Container(expand=True, width=0),
                                ft.Container(
                                    content=ft.Text(
                                        f"Estoque: {self.product.get('quantity', '0')}",
                                        size=14,
                                        weight="bold",
                                        color="#FFFFFF"
                                    ),
                                    padding=ft.padding.only(left=12, right=12, top=6, bottom=6),
                                    border_radius=15,
                                    bgcolor=primary_color,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.START,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        padding=15,
                        bgcolor=card_bg,
                        border_radius=12,
                        shadow=ft.BoxShadow(
                            spread_radius=0.1,
                            blur_radius=4,
                            color=ft.colors.with_opacity(0.08, "#000000")
                        ),
                    ),
                    
                    # Estatísticas de uso
                    ft.Container(
                        content=ft.ResponsiveRow([
                            # Total de uso
                            ft.Column([
                                ft.Container(
                                    content=ft.Column([
                                        ft.Text("Total Semanal", size=12, color="#707070"),
                                        ft.Text(f"{total_usage}", size=20, weight="bold", color=primary_color),
                                    ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                                    padding=15,
                                    border_radius=10,
                                    bgcolor=card_bg,
                                    shadow=ft.BoxShadow(
                                        spread_radius=0.1,
                                        blur_radius=4,
                                        color=ft.colors.with_opacity(0.08, "#000000")
                                    ),
                                    expand=True,
                                )
                                ], col={"xs": 4, "sm": 4, "md": 4, "lg": 4, "xl": 4}),
                            
                            # Média diária
                            ft.Column([
                                ft.Container(
                                    content=ft.Column([
                                        ft.Text("Média Diária", size=12, color="#707070"),
                                        ft.Text(f"{avg_daily}", size=20, weight="bold", color=primary_color),
                                    ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                                    padding=15,
                                    border_radius=10,
                                    bgcolor=card_bg,
                                    shadow=ft.BoxShadow(
                                        spread_radius=0.1,
                                        blur_radius=4,
                                        color=ft.colors.with_opacity(0.08, "#000000")
                                    ),
                                    expand=True,
                                )
                            ], col={"xs": 4, "sm": 4, "md": 4, "lg": 4, "xl": 4}),
                            
                            # Dia de maior uso
                            ft.Column([
                                ft.Container(
                                    content=ft.Column([
                                        ft.Text("Maior Uso", size=12, color="#707070"),
                                        ft.Text(
                                            f"{max_usage} ({days[weekly_usage.index(max_usage)][:3]})" if max_usage > 0 else "0",
                                            size=20, 
                                            weight="bold", 
                                            color=primary_color
                                        ),
                                    ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                                    padding=15,
                                    border_radius=10,
                                    bgcolor=card_bg,
                                    shadow=ft.BoxShadow(
                                        spread_radius=0.1,
                                        blur_radius=4,
                                        color=ft.colors.with_opacity(0.08, "#000000")
                                    ),
                                    expand=True,
                                )
                            ], col={"xs": 4, "sm": 4, "md": 4, "lg": 4, "xl": 4}),
                        ]),
                        padding=15,
                    ),
                    
                    # Visualização gráfica
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.icons.BAR_CHART, size=18, color=primary_color),
                                ft.Text("Visualização Gráfica", size=16, weight="bold", color="#303030"),
                            ], spacing=10),
                            
                            # Gráfico de barras simples
                            ft.Container(
                                content=ft.Row([
                                    ft.Column([
                                        ft.Container(
                                            content=ft.Container(
                                                padding=5,
                                                content=ft.Text(
                                                    str(weekly_usage[i]), 
                                                    size=12, 
                                                    color="#FFFFFF", 
                                                    text_align=ft.TextAlign.CENTER
                                                ),
                                                bgcolor=primary_color if i != current_day_index else success_color,
                                                border_radius=ft.border_radius.only(
                                                    top_left=4, top_right=4
                                                ),
                                                alignment=ft.alignment.center,
                                            ),
                                            height=max(30, min(150, 30 + (weekly_usage[i] / (max_usage if max_usage > 0 else 1)) * 120)),
                                            alignment=ft.alignment.bottom_center,
                                        ),
                                        ft.Container(
                                            content=ft.Text(
                                                days[i][:3], 
                                                size=10, 
                                                color="#707070",
                                                text_align=ft.TextAlign.CENTER
                                            ),
                                            margin=ft.margin.only(top=5),
                                            width=40,
                                            alignment=ft.alignment.center,
                                        ),
                                    ], 
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    alignment=ft.MainAxisAlignment.END,
                                    spacing=0)
                                    for i in range(7)
                                ], 
                                spacing=5, 
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                vertical_alignment=ft.CrossAxisAlignment.END
                                ),
                                margin=ft.margin.only(top=15, bottom=15),
                                padding=15,
                                border_radius=10,
                                bgcolor=card_bg,
                                shadow=ft.BoxShadow(
                                    spread_radius=0.1,
                                    blur_radius=4,
                                    color=ft.colors.with_opacity(0.08, "#000000")
                                ),
                                height=220,
                            ),
                        ]),
                        padding=15,
                    ),
                    
                    # Formulário de edição
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.icons.EDIT, size=18, color=primary_color),
                                ft.Text("Editar Uso Semanal", size=16, weight="bold", color="#303030"),
                            ], spacing=10),
                            
                            ft.Text(
                                "Registre o consumo diário deste produto:",
                                size=14,
                                color="#707070",
                            ),
                            
                            # Campos de entrada em formato de grid
                            ft.ResponsiveRow([
                                ft.Column([field], col={"xs": 12, "sm": 6, "md": 3, "lg": 3, "xl": 3})
                                for field in usage_fields[:4]  # Primeiros 4 dias
                            ]),
                            
                            ft.ResponsiveRow([
                                ft.Column([field], col={"xs": 12, "sm": 6, "md": 4, "lg": 4, "xl": 4})
                                for field in usage_fields[4:]  # Últimos 3 dias
                            ]),
                            
                            # Botões de ação
                            ft.Container(
                                content=ft.Row(
                                    controls=[
                                        ft.OutlinedButton(
                                            "Cancelar",
                                            icon=ft.icons.CANCEL,
                                            on_click=lambda _: self.navigation.go_back(),
                                            style=ft.ButtonStyle(
                                                color="#909090",
                                                shape=ft.RoundedRectangleBorder(radius=8)
                                            ),
                                        ),
                                        ft.FilledButton(
                                            "Salvar",
                                            icon=ft.icons.SAVE,
                                            on_click=save_weekly_usage,
                                            style=ft.ButtonStyle(
                                                bgcolor=primary_color,
                                                color="#FFFFFF",
                                                shape=ft.RoundedRectangleBorder(radius=8)
                                            ),
                                        ),
                                    ],
                                    alignment=ft.MainAxisAlignment.END,
                                    spacing=10,
                                ),
                                margin=ft.margin.only(top=15),
                            ),
                        ]),
                        padding=15,
                        bgcolor=card_bg,
                        border_radius=12,
                        shadow=ft.BoxShadow(
                            spread_radius=0.1,
                            blur_radius=4,
                            color=ft.colors.with_opacity(0.08, "#000000")
                        ),
                    ),
                    
                    # Histórico de saídas
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.icons.HISTORY, size=18, color=primary_color),
                                ft.Text("Histórico de Saídas", size=16, weight="bold", color="#303030"),
                            ], spacing=10),
                            
                            # Lista de saídas recentes
                            ft.Container(
                                content=ft.Column(
                                    controls=[
                                        self._build_exit_history_item(exit, primary_color)
                                        for exit in exit_history
                                    ] if exit_history else [
                                        ft.Container(
                                            content=ft.Column([
                                                ft.Icon(ft.icons.INFO_OUTLINE, size=40, color="#CCCCCC"),
                                                ft.Text(
                                                    "Nenhuma saída registrada recentemente",
                                                    size=14,
                                                    color="#909090",
                                                    text_align=ft.TextAlign.CENTER
                                                ),
                                                ft.OutlinedButton(
                                                    "Registrar Saída",
                                                    icon=ft.icons.EXIT_TO_APP,
                                                    on_click=lambda _: self._register_product_exit(),
                                                    style=ft.ButtonStyle(
                                                        color=primary_color,
                                                        shape=ft.RoundedRectangleBorder(radius=8)
                                                    ),
                                                ),
                                            ], 
                                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                            spacing=10
                                            ),
                                            padding=30,
                                            alignment=ft.alignment.center,
                                        )
                                    ],
                                    spacing=8,
                                    scroll=ft.ScrollMode.AUTO,
                                ),
                                height=200,
                                border_radius=8,
                                bgcolor=ft.colors.with_opacity(0.03, "#000000"),
                                padding=10,
                            ),
                            
                            # Botão para registrar nova saída
                            ft.Container(
                                content=ft.FilledButton(
                                    "Registrar Nova Saída",
                                    icon=ft.icons.EXIT_TO_APP,
                                    on_click=lambda _: self._register_product_exit(),
                                    style=ft.ButtonStyle(
                                        bgcolor=warning_color,
                                        color="#FFFFFF",
                                        shape=ft.RoundedRectangleBorder(radius=8)
                                    ),
                                ),
                                alignment=ft.alignment.center,
                                margin=ft.margin.only(top=10),
                            ),
                        ]),
                        padding=15,
                        bgcolor=card_bg,
                        border_radius=12,
                        shadow=ft.BoxShadow(
                            spread_radius=0.1,
                            blur_radius=4,
                            color=ft.colors.with_opacity(0.08, "#000000")
                        ),
                        margin=ft.margin.only(top=15, bottom=15),
                    ),
                ],
                spacing=0,
                scroll=ft.ScrollMode.AUTO,
            ),
            padding=15,
            bgcolor=bg_color,
            expand=True,
        )
    
    def _build_exit_history_item(self, exit_data, primary_color):
        """Constrói um item para o histórico de saídas"""
        return ft.Container(
            content=ft.Row([
                # Data e hora
                ft.Container(
                    content=ft.Column([
                        ft.Text(
                            exit_data.get("date", "").split(" ")[0],  # Apenas a data
                            size=12,
                            weight="bold",
                            color="#FFFFFF",
                        ),
                        ft.Text(
                            exit_data.get("date", "").split(" ")[1] if " " in exit_data.get("date", "") else "",  # Apenas a hora
                            size=10,
                            color="#FFFFFF",
                        ),
                    ], 
                    spacing=2,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    padding=8,
                    border_radius=8,
                    bgcolor=primary_color,
                    width=70,
                ),
                
                # Informações da saída
                ft.Column([
                    ft.Text(
                        f"Quantidade: {exit_data.get('quantity', '0')} unidades",
                        size=14,
                        weight="bold",
                    ),
                    ft.Text(
                        f"Motivo: {exit_data.get('reason', 'N/A')}",
                        size=12,
                        color="#707070",
                    ),
                ], 
                spacing=2,
                expand=True
                ),
                
                # Dia da semana
                ft.Container(
                    content=ft.Text(
                        self._get_weekday_from_date(exit_data.get("date", "")),
                        size=12,
                        color="#707070",
                    ),
                    padding=ft.padding.only(left=8, right=8, top=4, bottom=4),
                    border_radius=4,
                    bgcolor=ft.colors.with_opacity(0.05, primary_color),
                ),
            ], 
            spacing=10,
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
            ),
            padding=10,
            border_radius=8,
            bgcolor="#FFFFFF",
            border=ft.border.all(1, ft.colors.GREY_200),
        )
    
    def _get_weekday_from_date(self, date_str):
        """Obtém o dia da semana a partir de uma string de data"""
        try:
            # Tenta converter a string para um objeto datetime
            date_obj = datetime.strptime(date_str.split(" ")[0], "%d/%m/%Y")
            
            # Obtém o dia da semana (0 = segunda, 6 = domingo)
            weekday = date_obj.weekday()
            
            # Lista de dias da semana
            days = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
            
            return days[weekday]
        except:
            return "N/A"
    
    def _get_product_exit_history(self, product_id, limit=5):
        """Obtém o histórico de saídas de um produto do tipo uso_semanal"""
        
        # Verificar se o serviço de produtos tem um método para isso
        if hasattr(self.data, 'product_service') and hasattr(self.data.product_service, 'get_product_exits'):
            return self.data.product_service.get_product_exits(product_id, limit, exit_type="uso_semanal")
        
        # Caso contrário, retornar dados simulados para demonstração
        today = datetime.now()
        
        # Criar algumas saídas simuladas nos últimos 7 dias
        exit_history = []
        for i in range(min(limit, 5)):
            date = today - timedelta(days=i)
            exit_history.append({
                "id": f"exit_{i}",
                "product_id": product_id,
                "quantity": 2 + i,  # Quantidade simulada
                "reason": f"Uso semanal",
                "date": date.strftime("%d/%m/%Y %H:%M"),
                "user": "Sistema",
                "exit_type": "uso_semanal"
            })
        
        return exit_history
    
    def _register_product_exit(self):
        """Abre diálogo para registrar saída de produto com tipo 'uso_semanal' pré-selecionado"""
        if not self.product:
            return
        
        # Criar uma cópia do produto com um campo adicional para indicar o tipo de saída pré-selecionado
        product_with_exit_type = self.product.copy()
        product_with_exit_type["pre_selected_exit_type"] = "uso_semanal"
        
        print(f"WeeklyUsageScreen: Solicitando registro de saída para produto: {self.product.get('name')}, ID: {self.product.get('id')}, Tipo pré-selecionado: uso_semanal")
        
        # Navegar para a tela de registro de saída
        self.navigation.go_to_register_exit(product_with_exit_type, "product")
    
    def refresh_weekly_usage(self):
        """Atualiza os dados de uso semanal após registrar uma saída"""
        if not self.product or not self.product.get("id"):
            return
        
        # Buscar dados atualizados do banco de dados
        try:
            cursor = self.data.db.conn.cursor()
            cursor.execute('SELECT * FROM products WHERE id = ?', (self.product["id"],))
            product_data = cursor.fetchone()
            
            if product_data:
                # Atualizar o produto com dados frescos do banco de dados
                self.product = self.data.product_service._convert_to_dict([product_data])[0]
                print(f"Produto recarregado do banco de dados após saída")
                print(f"Uso semanal atualizado: {self.product.get('weeklyUsage', [])}")
                
                # Atualizar a tela
                self.navigation.update_view()
            else:
                print(f"Produto não encontrado no banco de dados após saída")
        except Exception as e:
            print(f"Erro ao recarregar produto após saída: {e}")
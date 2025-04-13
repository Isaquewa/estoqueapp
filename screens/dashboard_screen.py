import flet as ft
from datetime import datetime, timedelta

class DashboardScreen:
    def __init__(self, data, navigation):
        self.data = data
        self.navigation = navigation
    
    def build(self):
        try:
            # Verificar se os dados estão disponíveis
            if not hasattr(self.data, 'stock_products') or not hasattr(self.data, 'residues'):
                return ft.Container(content=ft.Text("Carregando dados..."))
            
            current_date = datetime.now().strftime("%d/%m/%Y %H:%M")
            
            # Obter dados com segurança
            stock_products = getattr(self.data, 'stock_products', []) or []
            residues = getattr(self.data, 'residues', []) or []
            expiring_products = getattr(self.data, 'expiring_products', []) or []
            notifications = getattr(self.data, 'notifications', []) or []
            
            # Debug para verificar os dados
            print(f"Dashboard - Total de produtos: {len(stock_products)}")
            print(f"Dashboard - Total de resíduos: {len(residues)}")
            print(f"Dashboard - Produtos expirando: {len(expiring_products)}")
            
            # Obter grupos configurados para o dashboard
            from services.card_config_service import CardConfigService
            from services.group_service import GroupService
            
            card_config_service = CardConfigService(self.data.firebase, self.data.db)
            group_service = GroupService(self.data.firebase, self.data.db)
            
            # Obter IDs dos grupos configurados para o dashboard
            product_group_ids = card_config_service.get_dashboard_product_group_ids()
            residue_group_ids = card_config_service.get_dashboard_residue_group_ids()
            
            # Obter informações dos grupos
            product_groups = group_service.get_all_product_groups()
            residue_groups = group_service.get_all_residue_groups()
            
            # Mapear grupos por ID para acesso rápido
            product_groups_map = {g["id"]: g for g in product_groups}
            residue_groups_map = {g["id"]: g for g in residue_groups}
            
            # Preparar dados dos grupos de produtos para o dashboard
            dashboard_product_groups = {}
            for group_id in product_group_ids:
                if group_id in product_groups_map:
                    group = product_groups_map[group_id]
                    dashboard_product_groups[group_id] = {
                        "name": group.get("name", ""),
                        "quantity": 0,  # Inicializar com zero
                        "products": [],
                        "group_id": group_id,
                        "group_data": group
                    }

            # Adicionar logs para depuração
            print(f"Grupos de produtos inicializados: {len(dashboard_product_groups)}")
            for group_id, group_data in dashboard_product_groups.items():
                print(f"Grupo {group_id}: {group_data['name']}")

            # Preencher dados dos produtos nos grupos
            for product in stock_products:
                group_id = product.get("group_id", "")
                if group_id in dashboard_product_groups:
                    # Adicionar produto ao grupo
                    dashboard_product_groups[group_id]["products"].append(product)
                    try:
                        # Converter para inteiro antes de somar
                        product_quantity = int(product.get("quantity", 0))
                        dashboard_product_groups[group_id]["quantity"] += product_quantity
                        print(f"Adicionado produto {product.get('name')} ao grupo {group_id}. Quantidade: {product_quantity}")
                    except (ValueError, TypeError):
                        print(f"Erro ao converter quantidade do produto {product.get('name')}: {product.get('quantity')}")
                elif group_id:  # Se o produto tem um grupo_id, mas o grupo não está no dashboard
                    print(f"Produto {product.get('name')} tem grupo_id {group_id}, mas este grupo não está configurado para o dashboard")

            # Verificar os dados finais dos grupos
            for group_id, group_data in dashboard_product_groups.items():
                products = group_data.get("products", [])
                total_quantity = group_data.get("quantity", 0)
                print(f"Verificação final - Grupo {group_id}: {len(products)} produtos, quantidade total: {total_quantity}")
                
                # Verificar cada produto no grupo
                for product in products:
                    print(f"  - Produto no grupo {group_id}: {product.get('name')}, Quantidade: {product.get('quantity')}")
            
            # Cálculo de uso semanal
            weekly_usage_total = 0
            for p in stock_products:
                try:
                    usage = p.get("weeklyUsage", [0] * 7)
                    if isinstance(usage, list):
                        weekly_usage_total += sum(usage)
                except Exception as e:
                    print(f"Erro ao calcular uso semanal: {e}")
            
            # Estatísticas gerais - Garantir que são números inteiros
            total_stock_quantity = 0
            for p in stock_products:
                try:
                    total_stock_quantity += int(p.get("quantity", 0))
                except (ValueError, TypeError):
                    pass
                    
            total_residue_quantity = 0
            for r in residues:
                try:
                    total_residue_quantity += int(r.get("quantity", 0))
                except (ValueError, TypeError):
                    pass

            dashboard_residue_groups = {}
            for group_id in residue_group_ids:
                if group_id in residue_groups_map:
                    group = residue_groups_map[group_id]
                    dashboard_residue_groups[group_id] = {
                        "name": group.get("name", ""),
                        "quantity": 0,  # Inicializar com zero
                        "residues": [],
                        "group_id": group_id,
                        "group_data": group
                    }

            # Preencher dados dos resíduos nos grupos
            for residue in residues:
                group_id = residue.get("group_id", "")
                if group_id in dashboard_residue_groups:
                    # Adicionar resíduo ao grupo
                    dashboard_residue_groups[group_id]["residues"].append(residue)
                    try:
                        # Converter para inteiro antes de somar
                        residue_quantity = int(residue.get("quantity", 0))
                        dashboard_residue_groups[group_id]["quantity"] += residue_quantity
                    except (ValueError, TypeError):
                        print(f"Erro ao converter quantidade do resíduo {residue.get('name')}: {residue.get('quantity')}")
                        pass

            
            print(f"Dashboard - Total estoque: {total_stock_quantity}")
            print(f"Dashboard - Total resíduos: {total_residue_quantity}")
            print(f"Dashboard - Uso semanal: {weekly_usage_total}")
            
            # Construir o dashboard
            return self._build_dashboard(
                current_date,
                dashboard_product_groups,
                dashboard_residue_groups,
                weekly_usage_total,
                expiring_products,
                len(notifications),
                total_stock_quantity,
                total_residue_quantity,
                product_groups,
                residue_groups
            )
            
        except Exception as e:
            print(f"Erro ao construir dashboard: {e}")
            import traceback
            traceback.print_exc()
            return ft.Container(
                content=ft.Column([
                    ft.Text("Erro ao carregar o Dashboard", size=18, color=ft.colors.RED),
                    ft.Text(f"Detalhes: {str(e)}", size=12, color=ft.colors.GREY)
                ]),
                alignment=ft.alignment.center,
                padding=15
            )
    
    def _build_dashboard(self, current_date, product_groups, residue_groups, weekly_usage, 
                        expiring_products, notification_count, total_stock, total_residues,
                        all_product_groups, all_residue_groups):
        """Constrói o dashboard adaptado para mobile"""
        
        # Cores modernas
        primary_color = "#4A6FFF"  # Azul moderno
        secondary_color = "#6C5CE7"  # Roxo moderno
        accent_color = "#00D2D3"  # Turquesa
        warning_color = "#FFA502"  # Laranja
        danger_color = "#FF6B6B"  # Vermelho suave
        success_color = "#2ED573"  # Verde
        bg_color = "#F8F9FD"  # Fundo claro
        card_bg = "#FFFFFF"  # Branco para cards
        
        # Cabeçalho
        header = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("Dashboard", size=24, weight="bold", color=primary_color),
                    ft.Row([
                        ft.IconButton(
                            icon=ft.icons.NOTIFICATIONS,
                            icon_color=warning_color if notification_count > 0 else "#A0A0A0",
                            icon_size=22,
                            tooltip="Notificações",
                            on_click=lambda _: self.navigation.go_to_notifications(),
                            badge=notification_count if notification_count > 0 else None
                        ),
                        ft.IconButton(
                            icon=ft.icons.SETTINGS,
                            icon_color="#A0A0A0",
                            icon_size=22,
                            tooltip="Configurações",
                            on_click=lambda _: self.navigation.go_to_settings()
                        )
                    ], spacing=5)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.icons.ACCESS_TIME, size=14, color="#A0A0A0"),
                        ft.Text(f"Atualizado: {current_date}", size=12, color="#A0A0A0")
                    ], spacing=4),
                    border_radius=12,
                    padding=ft.padding.only(left=10, right=10, top=6, bottom=6),
                    bgcolor="#F0F3FA"
                )
            ], spacing=10),
            margin=ft.margin.only(bottom=15)
        )
        
        # Estatísticas gerais - Horizontalmente para economizar espaço
        stats_section = ft.Container(
            content=ft.Row([
                self._build_stat_box("Estoque", total_stock, "un", primary_color, ft.icons.INVENTORY),
                self._build_stat_box("Resíduos", total_residues, "un", secondary_color, ft.icons.DELETE),
                self._build_stat_box("Uso Diário", round(weekly_usage / 7, 1) if weekly_usage > 0 else 0, "un/dia", success_color, ft.icons.TRENDING_DOWN)
            ], spacing=10, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=15,
            margin=ft.margin.only(bottom=15),
            bgcolor=card_bg,
            border_radius=12,
            shadow=ft.BoxShadow(
                spread_radius=0.1,
                blur_radius=4,
                color=ft.colors.with_opacity(0.08, "#000000")
            )
        )
        
        # Produtos principais com layout responsivo
        products_grid = ft.ResponsiveRow([
            ft.Column([
                self._build_product_card(data["name"], data, primary_color, accent_color)
            ], col={"xs": 12, "sm": 4, "md": 4, "lg": 4, "xl": 4})
            for group_id, data in product_groups.items()
        ], spacing=10)
        
        products_section = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Row([
                        ft.Icon(ft.icons.INVENTORY_2_ROUNDED, color=primary_color, size=18),
                        ft.Text("Insumos Principais", weight="bold", size=16, color="#303030"),
                    ], spacing=8),
                    # Botão de adicionar grupo de produtos ao lado esquerdo do título
                    ft.IconButton(
                        icon=ft.icons.ADD_CIRCLE_OUTLINE,
                        icon_color=primary_color,
                        icon_size=22,
                        tooltip="Adicionar Grupo de Produtos",
                        on_click=lambda _: self._add_product_group_card(all_product_groups)
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),  # Alinha os elementos nas extremidades
                products_grid,
            ], spacing=12),
            bgcolor=card_bg,
            border_radius=12,
            padding=15,
            margin=ft.margin.only(bottom=15),
            shadow=ft.BoxShadow(
                spread_radius=0.1,
                blur_radius=4,
                color=ft.colors.with_opacity(0.08, "#000000")
            )
        )
        
        # Resíduos principais com layout responsivo
        residues_grid = ft.ResponsiveRow([
            ft.Column([
                self._build_residue_card(data["name"], data, secondary_color, accent_color)
            ], col={"xs": 12, "sm": 6, "md": 6, "lg": 6, "xl": 6})
            for group_id, data in residue_groups.items()
        ], spacing=10)
        
        residues_section = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Row([
                        ft.Icon(ft.icons.DELETE_OUTLINE, color=secondary_color, size=18),
                        ft.Text("Resíduos", weight="bold", size=16, color="#303030"),
                    ], spacing=8),
                    # Botão de adicionar grupo de resíduos ao lado esquerdo do título
                    ft.IconButton(
                        icon=ft.icons.ADD_CIRCLE_OUTLINE,
                        icon_color=secondary_color,
                        icon_size=22,
                        tooltip="Adicionar Grupo de Resíduos",
                        on_click=lambda _: self._add_residue_group_card(all_residue_groups)
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                residues_grid,
            ], spacing=12),
            bgcolor=card_bg,
            border_radius=12,
            padding=15,
            margin=ft.margin.only(bottom=15),
            shadow=ft.BoxShadow(
                spread_radius=0.1,
                blur_radius=4,
                color=ft.colors.with_opacity(0.08, "#000000")
            )
        )
        
        # Seção de produtos próximos ao vencimento
        expiry_section = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.icons.CALENDAR_TODAY_ROUNDED, color=danger_color, size=18),
                    ft.Text("Próximos ao Vencimento", weight="bold", size=16, color="#303030"),
                    ft.Container(
                        content=ft.Text(f"{len(expiring_products)}", size=12, weight="bold", color=danger_color),
                        bgcolor=ft.colors.with_opacity(0.15, danger_color),
                        padding=ft.padding.only(left=10, right=10, top=4, bottom=4),
                        border_radius=12
                    )
                ], spacing=8),
                
                # Lista de produtos próximos ao vencimento
                *[self._build_expiry_item(product, danger_color, warning_color) for product in expiring_products[:3]],
                
                # Botão para ver todos
                ft.Container(
                    content=ft.Text("Ver todos", 
                                size=13, 
                                weight="w500",
                                color=primary_color),
                    on_click=lambda _: self.navigation.go_to_dashboard_detail("expiring", expiring_products),
                    padding=10,
                    alignment=ft.alignment.center,
                    border_radius=8,
                    bgcolor=ft.colors.with_opacity(0.1, primary_color),
                    visible=len(expiring_products) > 3
                )
            ], spacing=12),
            bgcolor=card_bg,
            border_radius=12,
            padding=15,
            margin=ft.margin.only(bottom=15),
            shadow=ft.BoxShadow(
                spread_radius=0.1,
                blur_radius=4,
                color=ft.colors.with_opacity(0.08, "#000000")
            )
        )
        
        # Layout principal com ScrollView para garantir funcionamento em telas pequenas
        return ft.Container(
            content=ft.Column([
                header,
                ft.Container(
                    content=ft.Column([
                        stats_section,
                        products_section,
                        residues_section,
                        expiry_section,
                        #quick_actions,
                    ], spacing=0),
                    expand=True,
                )
            ], scroll=ft.ScrollMode.AUTO),
            padding=ft.padding.all(16),
            bgcolor=bg_color,
        )
   
    def _build_stat_box(self, title, value, unit, color, icon):
        """Cria uma caixa de estatística compacta"""
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(icon, size=16, color=color),
                    ft.Text(title, size=13, color="#505050", weight="w500"),
                ], spacing=6),
                ft.Row([
                    ft.Text(str(value), size=22, weight="bold", color=color),
                    ft.Text(unit, size=12, color="#707070", weight="w400"),
                ], spacing=4, alignment=ft.MainAxisAlignment.START),
            ], spacing=4, horizontal_alignment=ft.CrossAxisAlignment.START),
            expand=True,
            padding=10
        )
    
    def _build_product_card(self, product_name, data, primary_color, accent_color):
        """Cria um card para um grupo de produtos com conteúdo melhorado"""
        group_id = data.get("group_id", "")
        group_data = data.get("group_data", {})
        
        # Obter produtos do grupo
        from services.group_service import GroupService
        group_service = GroupService(self.data.firebase, self.data.db)
        products = group_service.get_products_in_group(group_id)
        
        # Calcular estatísticas importantes
        total_quantity = 0
        total_value = 0
        low_stock_count = 0
        
        for product in products:
            try:
                quantity = int(product.get('quantity', 0))
                total_quantity += quantity
                
                # Verificar produtos com estoque baixo
                min_stock = int(product.get('minStock', 0) or 0)
                if min_stock > 0 and quantity <= min_stock:
                    low_stock_count += 1
                    
            except (ValueError, TypeError):
                pass
        
        # Ordenar produtos por data de validade
        from datetime import datetime
        
        def parse_date(date_str):
            try:
                if not date_str:
                    return datetime.max
                return datetime.strptime(date_str, "%d/%m/%Y")
            except Exception:
                return datetime.max
        
        sorted_products = sorted(products, key=lambda p: parse_date(p.get("expiry", "")))
        expiring_soon = sorted_products[:3]
        
        # Obter configuração do card
        from services.card_config_service import CardConfigService
        card_config_service = CardConfigService(self.data.firebase, self.data.db)
        config = card_config_service.get_product_group_config(group_id)
        
        # Obter ícone e cor
        icon_name = group_data.get("icon", config.get("icon", "INVENTORY_2_ROUNDED"))
        icon = getattr(ft.icons, icon_name, ft.icons.INVENTORY_2_ROUNDED)
        color = primary_color
        
        # Configurações do card
        bgcolor = "#FFFFFF"
        custom_title = config.get("custom_title", "")
        priority = config.get("priority", "normal")
        
        # Definir borda baseada na prioridade
        border = None
        if priority == "high":
            border = ft.border.all(2, "#FF6B6B")
        elif priority == "low":
            border = ft.border.all(1, "#E0E0E0")
        else:
            border = ft.border.all(1, ft.colors.with_opacity(0.1, primary_color))
        
        # Usar título personalizado se disponível
        display_name = custom_title if custom_title else product_name
        
        # Criar o card com conteúdo melhorado
        return ft.Container(
            content=ft.Column([
                # Cabeçalho do card
                ft.Row([
                    ft.Container(
                        content=ft.Icon(icon, size=18, color="#FFFFFF"),
                        padding=8,
                        border_radius=8,
                        bgcolor=color
                    ),
                    ft.Column([
                        ft.Text(display_name, size=14, weight="w600", color="#303030"),
                    ], spacing=2, expand=True),
                    
                    # Botões de ação
                    ft.Row([
                        ft.IconButton(
                            icon=ft.icons.EDIT,
                            icon_size=16,
                            tooltip="Editar Card",
                            icon_color="#909090",
                            on_click=lambda e, gid=group_id, gn=product_name, ps=products: self._edit_product_card(gid, gn, ps)
                        ),
                        ft.IconButton(
                            icon=ft.icons.DELETE_OUTLINE,
                            icon_size=16,
                            tooltip="Remover Card",
                            icon_color="#FF6B6B",
                            on_click=lambda e, gid=group_id, gn=product_name: self._delete_dashboard_card("product", gid, gn)
                        )
                    ], spacing=0)
                ], spacing=10, alignment=ft.MainAxisAlignment.START),
                
                # Estatísticas principais em formato de grid
                ft.Container(
                    content=ft.Row([
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
                        # Estoque baixo
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Estoque Baixo", size=11, color="#707070"),
                                ft.Text(f"{low_stock_count}", size=16, weight="bold", 
                                    color="#FF6B6B" if low_stock_count > 0 else "#909090"),
                            ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            expand=True,
                            padding=8,
                            border_radius=6,
                            bgcolor="#FFF0F0" if low_stock_count > 0 else "#F5F5F5"
                        ),
                    ], spacing=8),
                    margin=ft.margin.only(top=10, bottom=10)
                ),
                
                # Produtos próximos ao vencimento
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row([
                                ft.Icon(ft.icons.WARNING_AMBER_ROUNDED, size=14, color="#FF9800"),
                                ft.Text("Próxi. ao vencimento", size=12, weight="w600", color="#FF9800"),
                            ], spacing=6),
                        ] + [
                            ft.Row([
                                ft.Container(
                                    content=ft.Text(
                                        f"{(parse_date(p.get('expiry', '')) - datetime.now()).days}",
                                        size=12, weight="bold", color="#FFFFFF"
                                    ),
                                    width=30, height=30,
                                    border_radius=18,
                                    bgcolor="#FF9800",
                                    alignment=ft.alignment.center
                                ),
                                ft.Text(
                                    f"{p.get('name', '')[:15]}...",
                                    size=12,
                                    color="#505050",
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                    expand=True
                                ),
                                ft.Text(
                                    f"{p.get('expiry', 'N/A')}",
                                    size=12,
                                    color="#707070",
                                ),
                                ft.Text(
                                    f"{p.get('quantity', 'N/A')} un",
                                    size=12,
                                    weight="w500",
                                    color="#505050",
                                ),
                            ], spacing=8, alignment=ft.MainAxisAlignment.SPACE_BETWEEN) 
                            for p in expiring_soon[:2]
                        ] if expiring_soon else [
                            ft.Text("Nenhum produto próximo ao vencimento", size=12, color="#909090")
                        ],
                        spacing=8
                    ),
                    padding=10,
                    border_radius=8,
                    bgcolor="#FFF8E1",
                    visible=len(products) > 0
                ),
                
                # Botão para ver detalhes
                ft.Container(
                    content=ft.Row([
                        ft.Text("Ver detalhes", size=12, color=primary_color, weight="w500"),
                        ft.Icon(ft.icons.ARROW_FORWARD, size=14, color=primary_color)
                    ], spacing=4, alignment=ft.MainAxisAlignment.CENTER),
                    margin=ft.margin.only(top=8),
                    padding=ft.padding.only(top=8, bottom=8),
                    border_radius=6,
                    bgcolor=ft.colors.with_opacity(0.05, primary_color),
                    alignment=ft.alignment.center,
                    ink=True
                )
            ], spacing=0),
            bgcolor=bgcolor,
            border_radius=12,
            border=border,
            padding=15,
            margin=ft.margin.only(bottom=8),
            shadow=ft.BoxShadow(
                spread_radius=0.1,
                blur_radius=4,
                color=ft.colors.with_opacity(0.08, "#000000")
            ),
            on_click=lambda _: self.navigation.go_to_dashboard_detail("productGroup", {"id": group_id, "name": product_name}, title=product_name)
        )

    def _build_residue_card(self, residue_name, data, secondary_color, accent_color):
        """Cria um card para um grupo de resíduos com conteúdo melhorado"""
        group_id = data.get("group_id", "")
        group_data = data.get("group_data", {})
        
        # Obter resíduos do grupo
        from services.group_service import GroupService
        group_service = GroupService(self.data.firebase, self.data.db)
        residues = group_service.get_residues_in_group(group_id)
        
        # Calcular estatísticas importantes
        total_quantity = 0
        total_value = 0
        
        for residue in residues:
            try:
                quantity = int(residue.get('quantity', 0))
                total_quantity += quantity
                
                # Calcular valor total (preço unitário * quantidade)
                unit_price = float(residue.get('unitPrice', 0) or 0)
                total_value += unit_price * quantity
                    
            except (ValueError, TypeError):
                pass
        
        # Ordenar resíduos por data de entrada (do mais recente ao mais antigo)
        from datetime import datetime
        
        def parse_date(date_str):
            try:
                if not date_str:
                    return datetime.min
                return datetime.strptime(date_str, "%d/%m/%Y")
            except Exception:
                return datetime.min
        
        sorted_residues = sorted(residues, key=lambda r: parse_date(r.get("entryDate", "")), reverse=True)
        recent_residues = sorted_residues[:3]
        
        # Obter configuração do card
        from services.card_config_service import CardConfigService
        card_config_service = CardConfigService(self.data.firebase, self.data.db)
        config = card_config_service.get_residue_group_config(group_id)
        
        # Obter ícone e cor
        icon_name = group_data.get("icon", config.get("icon", "DELETE_OUTLINE"))
        icon = getattr(ft.icons, icon_name, ft.icons.DELETE_OUTLINE)
        color = secondary_color
        
        # Configurações do card
        bgcolor = "#FFFFFF"
        custom_title = config.get("custom_title", "")
        priority = config.get("priority", "normal")
        
        # Definir borda baseada na prioridade
        border = None
        if priority == "high":
            border = ft.border.all(2, "#FF6B6B")
        elif priority == "low":
            border = ft.border.all(1, "#E0E0E0")
        else:
            border = ft.border.all(1, ft.colors.with_opacity(0.1, secondary_color))
        
        # Usar título personalizado se disponível
        display_name = custom_title if custom_title else residue_name
        
        # Criar o card com conteúdo melhorado
        return ft.Container(
            content=ft.Column([
                # Cabeçalho do card
                ft.Row([
                    ft.Container(
                        content=ft.Icon(icon, size=18, color="#FFFFFF"),
                        padding=8,
                        border_radius=8,
                        bgcolor=color
                    ),
                    ft.Column([
                        ft.Text(display_name, size=14, weight="w600", color="#303030"),
                    ], spacing=2, expand=True),
                    
                    # Botões de ação
                    ft.Row([
                        ft.IconButton(
                            icon=ft.icons.EDIT,
                            icon_size=16,
                            tooltip="Editar Card",
                            icon_color="#909090",
                            on_click=lambda e, gid=group_id, rn=residue_name, rs=residues: self._edit_residue_card(gid, rn, rs)
                        ),
                        ft.IconButton(
                            icon=ft.icons.DELETE_OUTLINE,
                            icon_size=16,
                            tooltip="Remover Card",
                            icon_color="#FF6B6B",
                            on_click=lambda e, gid=group_id, rn=residue_name: self._delete_dashboard_card("residue", gid, rn)
                        )
                    ], spacing=0)
                ], spacing=10, alignment=ft.MainAxisAlignment.START),
                
                # Estatísticas principais em formato de grid
                ft.Container(
                    content=ft.Row([
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
                        # Número de registros
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Registros", size=11, color="#707070"),
                                ft.Text(f"{len(residues)}", size=16, weight="bold", color="#505050"),
                            ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            expand=True,
                            padding=8,
                            border_radius=6,
                            bgcolor="#F5F5F5"
                        ),
                    ], spacing=8),
                    margin=ft.margin.only(top=10, bottom=10)
                ),
                
                # Registros recentes
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row([
                                ft.Icon(ft.icons.ACCESS_TIME, size=14, color=color),
                                ft.Text("Registros recentes", size=12, weight="w600", color=color),
                            ], spacing=6),
                        ] + [
                            ft.Row([
                                ft.Container(
                                    content=ft.Icon(ft.icons.CALENDAR_TODAY, size=12, color="#FFFFFF"),
                                    width=22, height=22,
                                    border_radius=11,
                                    bgcolor=color,
                                    alignment=ft.alignment.center
                                ),
                                ft.Text(
                                    f"{r.get('name', '')[:15]}...",
                                    size=12,
                                    color="#505050",
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                    expand=True
                                ),
                                ft.Text(
                                    f"{r.get('entryDate', 'N/A')}",
                                    size=12,
                                    color="#707070",
                                ),
                                ft.Text(
                                    f"{r.get('quantity', 'N/A')} un",
                                    size=12,
                                    weight="w500",
                                    color="#505050",
                                ),
                            ], spacing=8, alignment=ft.MainAxisAlignment.SPACE_BETWEEN) 
                            for r in recent_residues[:2]
                        ] if recent_residues else [
                            ft.Text("Nenhum registro recente", size=12, color="#909090")
                        ],
                        spacing=8
                    ),
                    padding=10,
                    border_radius=8,
                    bgcolor=ft.colors.with_opacity(0.08, color),
                    visible=len(residues) > 0
                ),
                
                # Botão para ver detalhes
                ft.Container(
                    content=ft.Row([
                        ft.Text("Ver detalhes", size=12, color=secondary_color, weight="w500"),
                        ft.Icon(ft.icons.ARROW_FORWARD, size=14, color=secondary_color)
                    ], spacing=4, alignment=ft.MainAxisAlignment.CENTER),
                    margin=ft.margin.only(top=8),
                    padding=ft.padding.only(top=8, bottom=8),
                    border_radius=6,
                    bgcolor=ft.colors.with_opacity(0.05, secondary_color),
                    alignment=ft.alignment.center,
                    ink=True
                )
            ], spacing=0),
            bgcolor=bgcolor,
            border_radius=12,
            border=border,
            padding=15,
            margin=ft.margin.only(bottom=8),
            shadow=ft.BoxShadow(
                spread_radius=0.1,
                blur_radius=4,
                color=ft.colors.with_opacity(0.08, "#000000")
            ),
            on_click=lambda _: self.navigation.go_to_dashboard_detail("residueGroup", {"id": group_id, "name": residue_name}, title=residue_name)
        )
    
    def _build_expiry_item(self, product, danger_color, warning_color):
        """Cria um item de produto próximo ao vencimento com informações mais detalhadas"""
        try:
            days_left = (self._parse_date(product.get("expiry", "")) - datetime.now()).days
            
            # Definir cores baseadas na urgência
            if days_left <= 3:
                bg_color = "#FF6B6B"  # Vermelho para muito urgente
                text_color = "#FFFFFF"
                status_text = "Crítico"
            elif days_left <= 7:
                bg_color = "#FFA502"  # Laranja para urgente
                text_color = "#FFFFFF"
                status_text = "Urgente"
            else:
                bg_color = "#FFD166"  # Amarelo para atenção
                text_color = "#505050"
                status_text = "Atenção"
            
            # Calcular valor do produto
            quantity = int(product.get("quantity", 0))
            unit_price = float(product.get("unitPrice", 0) or 0)
            total_value = quantity * unit_price
            
            # Obter grupo do produto
            group_name = product.get("group_name", "Sem grupo")
            
            return ft.Container(
                content=ft.Column([
                    # Linha principal com dias restantes e nome
                    ft.Row([
                        ft.Container(
                            content=ft.Column([
                                ft.Text(f"{days_left}", size=18, weight="bold", color=text_color),
                                ft.Text("dias", size=10, color=text_color),
                            ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            padding=10,
                            border_radius=10,
                            bgcolor=bg_color,
                            width=45,
                            height=45,
                            alignment=ft.alignment.center
                        ),
                        ft.Column([
                            ft.Text(product.get("name", ""), size=14, weight="w600", color="#303030"),
                            ft.Row([
                                ft.Container(
                                    content=ft.Text(status_text, size=10, weight="bold", color=text_color),
                                    padding=ft.padding.only(left=6, right=6, top=2, bottom=2),
                                    border_radius=4,
                                    bgcolor=bg_color,
                                ),
                                ft.Text(f"Vence: {product.get('expiry', '')}", size=12, color="#707070"),
                            ], spacing=8),
                        ], spacing=2, expand=True),
                    ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    
                    # Linha de informações adicionais
                    ft.Container(
                        content=ft.Row([
                            # Quantidade
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("Quantidade", size=10, color="#707070"),
                                    ft.Text(f"{quantity} un", size=12, weight="w500", color="#505050"),
                                ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                                expand=True,
                                padding=6,
                                border_radius=4,
                                bgcolor="#F5F5F5"
                            ),
                            # Valor
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("Valor", size=10, color="#707070"),
                                    ft.Text(f"R$ {total_value:.2f}".replace('.', ','), size=12, weight="w500", color="#4CAF50"),
                                ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                                expand=True,
                                padding=6,
                                border_radius=4,
                                bgcolor="#F0F8F0"
                            ),
                            # Grupo
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("Grupo", size=10, color="#707070"),
                                    ft.Text(group_name, size=12, weight="w500", color="#505050", 
                                        overflow=ft.TextOverflow.ELLIPSIS),
                                ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                                expand=True,
                                padding=6,
                                border_radius=4,
                                bgcolor="#F5F5F5"
                            ),
                        ], spacing=6),
                        margin=ft.margin.only(top=8)
                    )
                ], spacing=0),
                bgcolor=ft.colors.with_opacity(0.1, bg_color),
                border_radius=10,
                padding=12,
                margin=ft.margin.only(bottom=8),
                on_click=lambda _: self.navigation.go_to_edit_product(product),
                ink=True
            )
        except Exception as e:
            print(f"Erro ao construir item de vencimento: {e}")
            import traceback
            traceback.print_exc()
            return ft.Container(
                content=ft.Text(f"Erro ao exibir produto: {product.get('name', 'Desconhecido')}", size=12, color="#FF6B6B"),
                padding=10
            )


    def _edit_product_card(self, group_id, group_name, products):
        """Navega para a tela de edição de card de produto"""
        # Criar um objeto representando o grupo de produtos
        product_group = {
            "id": group_id,
            "name": group_name,
            "products": products
        }
        # Navegar para a tela de seleção de grupos existentes
        self.navigation.go_to_select_group_for_card("product", self.data.product_groups, card_id=group_id)

    def _edit_residue_card(self, group_id, residue_name, residues):
        """Navega para a tela de edição de card de resíduo"""
        # Criar um objeto representando o grupo de resíduos
        residue_group = {
            "id": group_id,
            "name": residue_name,
            "residues": residues
        }
        # Navegar para a tela de seleção de grupos existentes
        # Garantir que o tipo seja "residue"
        self.navigation.go_to_select_group_for_card("residue", self.data.residue_groups, card_id=group_id)    
    
    def _add_product_group_card(self, all_groups):
        """Adiciona um novo card de grupo de produtos ao dashboard"""
        # Navegar para a tela de seleção de grupo
        self.navigation.go_to_select_group_for_card("product", all_groups)
    
    def _add_residue_group_card(self, all_groups):
        """Adiciona um novo card de grupo de resíduos ao dashboard"""
        # Navegar para a tela de seleção de grupo
        self.navigation.go_to_select_group_for_card("residue", all_groups)
    
    def _parse_date(self, date_str):
        """Converte string de data para objeto datetime"""
        try:
            if not date_str:
                return datetime.now() + timedelta(days=365)  # Data futura distante
            
            # Adicionar log para verificar a conversão de data
            print(f"Convertendo data: '{date_str}'")
            date_obj = datetime.strptime(date_str, "%d/%m/%Y")
            print(f"Data convertida: {date_obj}")
            return date_obj
        except Exception as e:
            print(f"Erro ao converter data '{date_str}': {e}")
            import traceback
            traceback.print_exc()
            return datetime.now() + timedelta(days=365)  # Data futura distante em caso de erro
    
    def _delete_dashboard_card(self, card_type, group_id, group_name):
        """Exclui um card do dashboard imediatamente e mostra uma mensagem de confirmação"""
        try:
            # Usar o CardConfigService para remover o card do dashboard
            from services.card_config_service import CardConfigService
            card_config_service = CardConfigService(self.data.firebase, self.data.db)
            
            if card_type == "product":
                # Obter os IDs dos grupos de produtos atuais
                product_group_ids = card_config_service.get_dashboard_product_group_ids()
                # Remover o ID do grupo
                if group_id in product_group_ids:
                    product_group_ids.remove(group_id)
                    # Atualizar a configuração
                    card_config_service.save_dashboard_product_group_ids(product_group_ids)
                    print(f"Card de produto '{group_name}' removido com sucesso")
            
            elif card_type == "residue":
                # Obter os IDs dos grupos de resíduos atuais
                residue_group_ids = card_config_service.get_dashboard_residue_group_ids()
                # Remover o ID do grupo
                if group_id in residue_group_ids:
                    residue_group_ids.remove(group_id)
                    # Atualizar a configuração
                    card_config_service.save_dashboard_residue_group_ids(residue_group_ids)
                    print(f"Card de resíduo '{group_name}' removido com sucesso")
            
            # Mostrar mensagem de confirmação
            self.navigation.show_snack_bar(f"Card '{group_name}' removido com sucesso", "#2ED573")
            
            # Atualizar os dados
            if hasattr(self.data, 'refresh_data'):
                self.data.refresh_data()
            
            # Forçar atualização da página
            if hasattr(self.navigation, 'page'):
                self.navigation.page.update()
            elif hasattr(self.data, 'page'):
                self.data.page.update()
            
        except Exception as e:
            print(f"Erro ao excluir card: {e}")
            import traceback
            traceback.print_exc()
            
            # Mostrar mensagem de erro
            self.navigation.show_snack_bar(f"Erro ao excluir card: {str(e)}", "#FF6B6B")
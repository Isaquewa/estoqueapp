import flet as ft

from screens.register_exit_screen import RegisterExitScreen
from screens.weekly_usage_screen import WeeklyUsageScreen

class Navigation:
    def __init__(self, page, data):
        self.page = page
        self.data = data
        self.current_tab = 0
        self.current_screen = None
        self.selected_product = None
        self.selected_residue = None
        self.selected_item = None
        self.item_exit_type = None
        # Propriedades para tela de detalhes do dashboard
        self.detail_type = None
        self.detail_items = None
        self.detail_title = None
        # Propriedades para tela de confirmação de exclusão
        self.item_type_to_delete = None
        self.item_to_delete = None
    
    def change_tab(self, tab_index):
        """Muda para a aba especificada e limpa seleções"""
        self.current_tab = tab_index
        self.current_screen = None
        self.selected_product = None
        self.selected_residue = None
        self.update_view()
    
    def select_product(self, product):
        """Seleciona um produto"""
        self.selected_product = product
        self.update_view()
    
    def select_residue(self, residue):
        """Seleciona um resíduo"""
        self.selected_residue = residue
        self.update_view()
    
    def go_back(self):
        """Volta para a tela anterior"""
        if len(self.page.views) > 1:
            # Se estiver em uma view adicional, remover a view atual
            self.page.views.pop()
            self.page.update()
        else:
            # Se estiver na view principal, voltar para a tela principal da aba atual
            self.current_screen = None
            self.selected_product = None
            self.selected_residue = None
            self.detail_type = None
            self.detail_items = None
            self.detail_title = None
            self.update_view()
    
    def go_to_add_product(self):
        """Navega para a tela de adicionar produto"""
        self.current_screen = "add_product"
        self.update_view()
    
    def go_to_edit_product(self, product):
        """Navega para a tela de editar produto"""
        self.selected_product = product
        self.current_screen = "edit_product"
        self.update_view()
    
    def go_to_add_residue(self):
        """Navega para a tela de adicionar resíduo"""
        self.current_screen = "add_residue"
        self.update_view()
    
    def go_to_edit_residue(self, residue):
        """Navega para a tela de editar resíduo"""
        self.selected_residue = residue
        self.current_screen = "edit_residue"
        self.update_view()
    
    def go_to_weekly_usage(self, product):
        """Navega para a tela de uso semanal"""
        # Armazenar o produto selecionado
        self.selected_product = product
        
        # Criar uma nova instância da tela
        from screens.weekly_usage_screen import WeeklyUsageScreen
        self.weekly_usage_screen = WeeklyUsageScreen(self.data, self)
        
        self.previous_tab = self.current_tab
        self.previous_screen = self.current_screen
        
        self.current_screen = "weekly_usage"
        self.update_view()
        
    def show_dashboard_modal(self, modal_type, items):
        """Mostra o modal do dashboard com os itens especificados"""
        self.dashboard_modal.show(modal_type, items)

    def go_to_notifications(self):
        """Navega para a tela de notificações"""
        self.current_screen = "notifications"
        self.update_view()

    def go_to_settings(self):
        """Navega para a tela de configurações"""
        self.current_screen = "settings"
        self.update_view()
    
    def go_to_select_group_for_card(self, group_type, all_groups, card_id=None):
        """Navega para a tela de seleção de grupo para adicionar ao dashboard"""
        self.current_screen = "select_group_for_card"
        self.group_type = group_type
        
        # Garantir que estamos usando os grupos corretos
        if group_type == "product":
            self.all_groups = self.data.product_groups
        else:
            self.all_groups = self.data.residue_groups
            
        self.card_id = card_id
        self.update_view()

    def go_to_edit_card(self, card_type, card_data):
        """Navega para a tela de edição de card do dashboard"""
        from screens.edit_card_screen import EditCardScreen
        screen = EditCardScreen(self.data, self, card_type, card_data)
        self.page.views.append(
            ft.View(
                route=f"/edit_card/{card_type}/{card_data.get('id', '')}",
                controls=[screen.build()]
            )
        )
        self.page.update()

    def go_to_edit_group(self, group_type, group_data):
        """Navega para a tela de edição de grupo"""
        # Armazenar dados do grupo para edição
        self.current_screen = "edit_group"
        self.edit_group_type = group_type
        self.edit_group_data = group_data
        self.update_view()

    def go_to_create_product_group(self):
        """Navega para a tela de criação de grupo de produtos"""
        from screens.create_group_screen import CreateGroupScreen
        screen = CreateGroupScreen(self.data, self, "product")
        self.page.views.append(
            ft.View(
                route="/create_product_group",
                controls=[screen.build()]
            )
        )
        self.page.update()

    def go_to_create_residue_group(self):
        """Navega para a tela de criação de grupo de resíduos"""
        from screens.create_group_screen import CreateGroupScreen
        screen = CreateGroupScreen(self.data, self, "residue")
        self.page.views.append(
            ft.View(
                route="/create_residue_group",
                controls=[screen.build()]
            )
        )
        self.page.update()  
    
    def go_to_dashboard_detail(self, detail_type, items, title=None):
        """Navega para a tela de detalhes do dashboard"""
        self.detail_type = detail_type
        self.detail_items = items
        self.detail_title = title
        self.current_screen = "dashboard_detail"
        
        # Adicione logs para debug
        print(f"Navegando para detalhes: tipo={detail_type}, título={title}")
        if isinstance(items, dict) and "id" in items:
            print(f"ID do grupo: {items['id']}")
        elif isinstance(items, list):
            print(f"Número de itens: {len(items)}")
        
        self.update_view()

    def go_to_confirm_delete(self, item_type, item):
        """Navega para a tela de confirmação de exclusão"""
        self.current_screen = "confirm_delete"
        self.item_type_to_delete = item_type
        self.item_to_delete = item
        self.update_view()    
    
    def show_snack_bar(self, message, color=None):
        """Exibe uma mensagem na barra de notificações"""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=color or ft.colors.GREEN_500
        )
        self.page.snack_bar.open = True
        self.page.update()

    # Em navigation.py
    def go_to_group_detail(self, group, is_product_group=True):
        """Navega para a tela de detalhes do grupo"""
        self.current_screen = "group_detail"
        self.current_group = group
        self.is_product_group = is_product_group
        self.update_view() 

    def go_to_movement_report(self):
        """Navega para o relatório de movimentação"""
        self.previous_tab = self.current_tab
        self.previous_screen = self.current_screen
        self.current_screen = "movement_report"
        self.update_view()

    def go_to_entry_report(self):
        """Navega para o relatório de entradas"""
        self.previous_tab = self.current_tab
        self.previous_screen = self.current_screen
        self.current_screen = "entry_report"
        self.update_view()

    def go_to_expiry_report(self):
        """Navega para o relatório de validade"""
        self.previous_tab = self.current_tab
        self.previous_screen = self.current_screen
        self.current_screen = "expiry_report"
        self.update_view()

    def go_to_group_report(self):
        """Navega para o relatório por grupos"""
        self.previous_tab = self.current_tab
        self.previous_screen = self.current_screen
        self.current_screen = "group_report"
        self.update_view()  

    def go_to_register_exit(self, item, item_type):
        """Navega para a tela de registro de saída"""
        # Criar uma cópia profunda do item para evitar referências compartilhadas
        import copy
        item_copy = copy.deepcopy(item) if item else {}
        
        print(f"Navigation: Navegando para registro de saída: {item_copy.get('name')}, ID: {item_copy.get('id')}, Tipo: {item_type}")
        
        # Criar a tela com a cópia do item
        register_exit_screen = RegisterExitScreen(self.data, self, item_copy, item_type)
        
        # Adicionar a tela como uma nova view
        self.page.views.append(
            ft.View(
                route=f"/register_exit/{item_type}/{item_copy.get('id', '')}",
                controls=[register_exit_screen.build()]
            )
        )
        self.page.go(f"/register_exit/{item_type}/{item_copy.get('id', '')}")
        self.page.update()

    def update_view(self):
        """Atualiza a visualização atual (será substituído em main.py)"""
        print("Método update_view chamado na navegação")
        pass
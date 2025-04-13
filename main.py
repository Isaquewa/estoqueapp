import flet as ft


from screens.dashboard_screen import DashboardScreen
from screens.stock_screen import StockScreen
from screens.residues_screen import ResiduesScreen
from screens.report_screen import ReportScreen
from navigation import Navigation
from services.data_service import DataService
import threading
import time

# Importar todas as telas no início para evitar problemas de escopo
from screens.settings_screen import SettingsScreen
from screens.notifications_screen import NotificationsScreen
from screens.dashboard_detail_screen import DashboardDetailScreen
from screens.add_product_screen import AddProductScreen
from screens.group_detail_screen import GroupDetailScreen
from screens.confirm_delete_screen import ConfirmDeleteScreen
from screens.edit_product_screen import EditProductScreen
from screens.weekly_usage_screen import WeeklyUsageScreen
from screens.add_residue_screen import AddResidueScreen
from screens.edit_residue_screen import EditResidueScreen
from screens.select_group_screen import SelectGroupScreen

# Importar novas telas
from screens.product_entry_screen import ProductEntryScreen
from screens.residue_entry_screen import ResidueEntryScreen
from screens.residue_exit_screen import ResidueExitScreen
from screens.movement_report_screen import MovementReportScreen
from screens.expiry_report_screen import ExpiryReportScreen
from screens.entry_report_screen import EntryReportScreen
from screens.group_report_screen import GroupReportScreen
from screens.register_exit_screen import RegisterExitScreen


def main(page: ft.Page):
    # Configurações da página
    page.title = "Gestão de Estoque"
    page.padding = 0
    page.theme_mode = "light"
    page.window_width = 800
    page.window_height = 600
    
    # Inicializar serviços
    data = DataService()
    
    # Inicializar navegação
    navigation = Navigation(page, data)
    
    # IMPORTANTE: Adicionar referência da navegação ao serviço de dados
    data.navigation = navigation
    
    # Inicializar telas principais
    dashboard_screen = DashboardScreen(data, navigation)
    stock_screen = StockScreen(data, navigation)
    residues_screen = ResiduesScreen(data, navigation)
    report_screen = ReportScreen(data, navigation)
    
    # Definir conteúdo para abrigar a tela atual
    content = ft.Container(expand=True)
    
    # Definir barra de navegação
    navigation_bar = ft.NavigationBar(
        selected_index=0,
        destinations=[
            ft.NavigationBarDestination(
                icon=ft.icons.DASHBOARD_OUTLINED,
                selected_icon=ft.icons.DASHBOARD,
                label="Dashboard"
            ),
            ft.NavigationBarDestination(
                icon=ft.icons.INVENTORY_2_OUTLINED,
                selected_icon=ft.icons.INVENTORY_2,
                label="Estoque"
            ),
            ft.NavigationBarDestination(
                icon=ft.icons.DELETE_OUTLINE,
                selected_icon=ft.icons.DELETE,
                label="Resíduos"
            ),
            ft.NavigationBarDestination(
                icon=ft.icons.ANALYTICS_OUTLINED,
                selected_icon=ft.icons.ANALYTICS,
                label="Relatórios"
            )
        ],
        on_change=lambda e: change_tab(e)
    )
    
    # Criar um layout principal que nunca será limpo
    main_column = ft.Column(
        controls=[
            content,
            navigation_bar
        ],
        spacing=0,
        expand=True
    )
    
    # Adicionar o layout principal à página apenas uma vez
    page.add(main_column)
    
    # Função para alternar entre abas
    def change_tab(e):
        navigation.change_tab(e.control.selected_index)
        # Limpar qualquer tela específica ao mudar de aba
        navigation.current_screen = None
        navigation.selected_product = None
        navigation.selected_residue = None
        navigation.detail_type = None
        navigation.detail_items = None
        navigation.detail_title = None
        update_view()
    
    # Função para atualizar a tela
    def update_view():
        # Atualizar dados
        data.refresh_data()
        
        # Selecionar tela atual com base no índice da aba e no current_screen
        current_content = None
        
        print(f"Atualizando view: tab={navigation.current_tab}, screen={navigation.current_screen}")

        if navigation.current_tab == 0:  # Dashboard
            if navigation.current_screen == "settings":
                if not hasattr(navigation, 'settings_screen'):
                    navigation.settings_screen = SettingsScreen(data, navigation)
                current_content = navigation.settings_screen.build()
            elif navigation.current_screen == "notifications":
                if not hasattr(navigation, 'notifications_screen'):
                    navigation.notifications_screen = NotificationsScreen(data, navigation)
                current_content = navigation.notifications_screen.build()
            elif navigation.current_screen == "dashboard_detail":
                if not hasattr(navigation, 'dashboard_detail_screen'):
                    navigation.dashboard_detail_screen = DashboardDetailScreen(data, navigation)
                navigation.dashboard_detail_screen.set_data(
                    navigation.detail_type, 
                    navigation.detail_items, 
                    navigation.detail_title
                )
                current_content = navigation.dashboard_detail_screen.build()
            elif navigation.current_screen == "select_group_for_card":
                # Sempre criar uma nova instância para evitar problemas com estados antigos
                navigation.select_group_screen = SelectGroupScreen(
                    data, 
                    navigation, 
                    navigation.group_type, 
                    data.product_groups if navigation.group_type == "product" else data.residue_groups,
                    navigation.card_id
                )
                current_content = navigation.select_group_screen.build()
            else:
                current_content = dashboard_screen.build()
        elif navigation.current_tab == 1:  # Estoque
            if navigation.current_screen == "add_product":
                if not hasattr(navigation, 'add_product_screen'):
                    navigation.add_product_screen = AddProductScreen(data, navigation)
                current_content = navigation.add_product_screen.build()
            elif navigation.current_screen == "group_detail":
                if not hasattr(navigation, 'group_detail_screen'):
                    navigation.group_detail_screen = GroupDetailScreen(data, navigation)
                navigation.group_detail_screen.set_group(navigation.current_group, navigation.is_product_group)
                current_content = navigation.group_detail_screen.build()
            elif navigation.current_screen == "confirm_delete":
                if not hasattr(navigation, 'confirm_delete_screen'):
                    navigation.confirm_delete_screen = ConfirmDeleteScreen(data, navigation)
                navigation.confirm_delete_screen.set_item(
                    navigation.item_type_to_delete, 
                    navigation.item_to_delete
                )
                current_content = navigation.confirm_delete_screen.build()
            elif navigation.current_screen == "edit_product":
                if not hasattr(navigation, 'edit_product_screen'):
                    navigation.edit_product_screen = EditProductScreen(data, navigation)
                navigation.edit_product_screen.set_product(navigation.selected_product)
                current_content = navigation.edit_product_screen.build()
            elif navigation.current_screen == "weekly_usage":
                if not hasattr(navigation, 'weekly_usage_screen'):
                    navigation.weekly_usage_screen = WeeklyUsageScreen(data, navigation)
                navigation.weekly_usage_screen.set_product(navigation.selected_product)
                current_content = navigation.weekly_usage_screen.build()
            elif navigation.current_screen == "confirm_delete":
                if not hasattr(navigation, 'confirm_delete_screen'):
                    navigation.confirm_delete_screen = ConfirmDeleteScreen(data, navigation)
                navigation.confirm_delete_screen.set_item(
                    navigation.item_type_to_delete, 
                    navigation.item_to_delete
                )
                current_content = navigation.confirm_delete_screen.build()

            elif navigation.current_screen == "register_exit":
                if not hasattr(navigation, 'register_exit_screen'):
                    navigation.register_exit_screen = RegisterExitScreen(
                        data, 
                        navigation, 
                        navigation.selected_item,  # Item selecionado (produto ou resíduo)
                        navigation.item_exit_type  # Tipo do item ("product" ou "residue")
                    )
                current_content = navigation.register_exit_screen.build()

            else:
                current_content = stock_screen.build()
        elif navigation.current_tab == 2:  # Resíduos
            if navigation.current_screen == "add_residue":
                if not hasattr(navigation, 'add_residue_screen'):
                    navigation.add_residue_screen = AddResidueScreen(data, navigation)
                current_content = navigation.add_residue_screen.build()
            elif navigation.current_screen == "edit_residue":
                if not hasattr(navigation, 'edit_residue_screen'):
                    navigation.edit_residue_screen = EditResidueScreen(data, navigation)
                navigation.edit_residue_screen.set_residue(navigation.selected_residue)
                current_content = navigation.edit_residue_screen.build()
            elif navigation.current_screen == "confirm_delete":
                if not hasattr(navigation, 'confirm_delete_screen'):
                    navigation.confirm_delete_screen = ConfirmDeleteScreen(data, navigation)
                navigation.confirm_delete_screen.set_item(
                    navigation.item_type_to_delete, 
                    navigation.item_to_delete
                )
                current_content = navigation.confirm_delete_screen.build()
            elif navigation.current_screen == "group_detail":  # Adicionar este caso
                if not hasattr(navigation, 'group_detail_screen'):
                    navigation.group_detail_screen = GroupDetailScreen(data, navigation)
                navigation.group_detail_screen.set_group(navigation.current_group, navigation.is_product_group)
                current_content = navigation.group_detail_screen.build()
            else:
                current_content = residues_screen.build()
        
        elif navigation.current_tab == 3:  # Relatórios
            if navigation.current_screen == "movement_report":
                if not hasattr(navigation, 'movement_report_screen'):
                    from screens.movement_report_screen import MovementReportScreen
                    navigation.movement_report_screen = MovementReportScreen(data, navigation)
                current_content = navigation.movement_report_screen.build()
            elif navigation.current_screen == "entry_report":
                if not hasattr(navigation, 'entry_report_screen'):
                    from screens.entry_report_screen import EntryReportScreen
                    navigation.entry_report_screen = EntryReportScreen(data, navigation)
                current_content = navigation.entry_report_screen.build()
            elif navigation.current_screen == "product_exit":
                if not hasattr(navigation, 'product_exit_screen'):
                    from screens.product_exit_screen import ProductExitScreen
                    navigation.product_exit_screen = ProductExitScreen(data, navigation)
                current_content = navigation.product_exit_screen.build()
            elif navigation.current_screen == "expiry_report":
                if not hasattr(navigation, 'expiry_report_screen'):
                    from screens.expiry_report_screen import ExpiryReportScreen
                    navigation.expiry_report_screen = ExpiryReportScreen(data, navigation)
                current_content = navigation.expiry_report_screen.build()
            elif navigation.current_screen == "group_report":
                if not hasattr(navigation, 'group_report_screen'):
                    from screens.group_report_screen import GroupReportScreen
                    navigation.group_report_screen = GroupReportScreen(data, navigation)
                    navigation.group_report_screen.set_group_type(navigation.group_type)
                current_content = navigation.group_report_screen.build()
            elif navigation.current_screen == "product_entry":
                if not hasattr(navigation, 'product_entry_screen'):
                    navigation.product_entry_screen = ProductEntryScreen(data, navigation)
                navigation.product_entry_screen.set_product(navigation.selected_product)
                current_content = navigation.product_entry_screen.build()
            elif navigation.current_screen == "residue_entry":
                if not hasattr(navigation, 'residue_entry_screen'):
                    navigation.residue_entry_screen = ResidueEntryScreen(data, navigation)
                navigation.residue_entry_screen.set_residue(navigation.selected_residue)
                current_content = navigation.residue_entry_screen.build()
            elif navigation.current_screen == "residue_exit":
                if not hasattr(navigation, 'residue_exit_screen'):
                    navigation.residue_exit_screen = ResidueExitScreen(data, navigation)
                navigation.residue_exit_screen.set_residue(navigation.selected_residue)
                current_content = navigation.residue_exit_screen.build()

            # Adicionar suporte para dashboard_detail na aba de Relatórios
            elif navigation.current_screen == "dashboard_detail":
                if not hasattr(navigation, 'dashboard_detail_screen'):
                    navigation.dashboard_detail_screen = DashboardDetailScreen(data, navigation)
                navigation.dashboard_detail_screen.set_data(
                    navigation.detail_type, 
                    navigation.detail_items, 
                    navigation.detail_title
                )
                current_content = navigation.dashboard_detail_screen.build()
            else:
                current_content = report_screen.build()
        
         # Fallback para conteúdo vazio se build retornar None
        if current_content is None:
            print("ERRO: build() retornou None")
            current_content = ft.Container(
                content=ft.Text("Erro ao carregar conteúdo"),
                alignment=ft.alignment.center,
                padding=20
            )
        
        # Atualizar apenas o conteúdo, não a página inteira
        content.content = current_content
        page.update()
        print("View atualizada com sucesso")
    
    # Adicionar método update_view à navegação
    navigation.update_view = update_view
    
    # Carregar tela inicial (dashboard)
    update_view()
    
    # Função para atualização periódica
    def periodic_update():
        while True:
            time.sleep(60)  # Espera 60 segundos
            # Executar atualização na thread principal
            update_view()
            page.update()
    
    # Iniciar thread de atualização
    update_thread = threading.Thread(target=periodic_update, daemon=True)
    update_thread.start()

if __name__ == "__main__":
    ft.app(target=main)
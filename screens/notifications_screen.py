import flet as ft

class NotificationsScreen:
    def __init__(self, data, navigation):
        self.data = data
        self.navigation = navigation
    
    def build(self):
        notifications = self.data.notifications
        
        notification_list = ft.ListView(
            spacing=5,
            controls=[
                self._build_notification_item(notification)
                for notification in notifications
            ] if notifications else [
                ft.Container(
                    padding=10,
                    content=ft.Text("Nenhuma notificação", color=ft.colors.GREY_500)
                )
            ],
            expand=True,
        )
        
        return ft.Container(
            content=ft.Column(
                controls=[
                    # Cabeçalho
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.IconButton(
                                    icon=ft.icons.ARROW_BACK,
                                    on_click=lambda _: self.navigation.go_back()
                                ),
                                ft.Text("Notificações", size=20, weight="bold"),
                                ft.IconButton(
                                    icon=ft.icons.CHECK_CIRCLE_OUTLINE,
                                    tooltip="Marcar todas como lidas",
                                    on_click=lambda _: self._mark_all_as_read()
                                ) if notifications else None,
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        padding=10,
                    ),
                    
                    # Lista de notificações
                    notification_list,
                ],
                spacing=0,
                expand=True,
            ),
            expand=True,
        )
    
    def _build_notification_item(self, notification):
        icon_map = {
            "LOW_STOCK": ft.icons.WARNING_ROUNDED,
            "EXPIRY": ft.icons.CALENDAR_TODAY_ROUNDED,
            "RESIDUE": ft.icons.DELETE_ROUNDED,
            "PRODUCT_ADDED": ft.icons.INVENTORY_2_ROUNDED,
            "PRODUCT_DELETED": ft.icons.INVENTORY_2_ROUNDED,
            "RESIDUE_DELETED": ft.icons.DELETE_ROUNDED
        }
        
        color_map = {
            "LOW_STOCK": ft.colors.RED_500,
            "EXPIRY": ft.colors.ORANGE_500,
            "RESIDUE": ft.colors.PURPLE_500,
            "PRODUCT_ADDED": ft.colors.BLUE_500,
            "PRODUCT_DELETED": ft.colors.RED_500,
            "RESIDUE_DELETED": ft.colors.PURPLE_500
        }
        
        return ft.Container(
            padding=10,
            border_radius=8,
            bgcolor=color_map.get(notification["type"], ft.Colors.GREY_500).with_opacity(0.1),
            content=ft.Row(
                controls=[
                    ft.Icon(
                        icon_map.get(notification["type"], ft.icons.NOTIFICATIONS_ROUNDED),
                        color=color_map.get(notification["type"], ft.Colors.GREY_500),
                        size=20
                    ),
                    ft.Column(
                        controls=[
                            ft.Text(notification["message"], size=14),
                            ft.Text(notification["date"], size=12, color=ft.colors.GREY_500)
                        ],
                        spacing=5,
                        expand=True,
                    ),
                    ft.IconButton(
                        icon=ft.icons.CHECK_CIRCLE_OUTLINE_ROUNDED,
                        icon_color=ft.colors.GREEN_500,
                        icon_size=20,
                        on_click=lambda _, n=notification: self._mark_as_read(n["id"])
                    ) if not notification["read"] else None
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            )
        )
    
    def _mark_as_read(self, notification_id):
        """Marca uma notificação como lida"""
        self.data.notification_service.mark_as_read(notification_id)
        self.data.refresh_data()
        self.navigation.update_view()
    
    def _mark_all_as_read(self):
        """Marca todas as notificações como lidas"""
        for notification in self.data.notifications:
            if not notification["read"]:
                self.data.notification_service.mark_as_read(notification["id"])
        self.data.refresh_data()
        self.navigation.update_view()
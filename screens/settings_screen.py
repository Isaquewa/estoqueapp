import flet as ft

class SettingsScreen:
    def __init__(self, data, navigation):
        self.data = data
        self.navigation = navigation
        self.settings = None
        self.form_fields = {}
    
    def build(self):
        # Obter configurações atuais
        self.settings = self.data.settings
        
        # Criar campos do formulário
        self.form_fields = {
            "notifications_enabled": ft.Switch(
                label="Ativar notificações",
                value=self.settings["notifications"]["enabled"],
                on_change=lambda e: self._update_setting("notifications.enabled", e.control.value)
            ),
            
            "low_stock_threshold": ft.TextField(
                label="Limite de estoque baixo",
                value=str(self.settings["notifications"]["lowStockThreshold"]),
                keyboard_type=ft.KeyboardType.NUMBER,
                border_radius=8,
                on_change=lambda e: self._update_setting(
                    "notifications.lowStockThreshold", 
                    int(e.control.value) if e.control.value.isdigit() else 5
                )
            ),
            
            "expiry_warning_days": ft.TextField(
                label="Dias para alerta de vencimento",
                value=str(self.settings["notifications"]["expiryWarningDays"]),
                keyboard_type=ft.KeyboardType.NUMBER,
                border_radius=8,
                on_change=lambda e: self._update_setting(
                    "notifications.expiryWarningDays", 
                    int(e.control.value) if e.control.value.isdigit() else 30
                )
            ),
            
            "weekly_report_enabled": ft.Switch(
                label="Ativar relatório semanal",
                value=self.settings["weeklyReportEnabled"],
                on_change=lambda e: self._update_setting("weeklyReportEnabled", e.control.value)
            ),
            
            "backup_enabled": ft.Switch(
                label="Ativar backup automático",
                value=self.settings["backupEnabled"],
                on_change=lambda e: self._update_setting("backupEnabled", e.control.value)
            ),
        }
        
        # Adicionar campos de tema se existirem nas configurações
        if "theme" in self.settings:
            theme_options = [
                ft.dropdown.Option("light", "Claro"),
                ft.dropdown.Option("dark", "Escuro"),
                ft.dropdown.Option("system", "Sistema")
            ]
            
            self.form_fields["theme_mode"] = ft.Dropdown(
                label="Tema do aplicativo",
                value=self.settings["theme"].get("mode", "light"),
                options=theme_options,
                border_radius=8,
                on_change=lambda e: self._update_setting("theme.mode", e.control.value)
            )
            
            color_options = [
                ft.dropdown.Option("blue", "Azul"),
                ft.dropdown.Option("green", "Verde"),
                ft.dropdown.Option("purple", "Roxo"),
                ft.dropdown.Option("red", "Vermelho"),
                ft.dropdown.Option("amber", "Âmbar"),
                ft.dropdown.Option("cyan", "Ciano"),
                ft.dropdown.Option("indigo", "Índigo"),
                ft.dropdown.Option("teal", "Turquesa")
            ]
            
            self.form_fields["primary_color"] = ft.Dropdown(
                label="Cor primária",
                value=self.settings["theme"].get("primaryColor", "blue"),
                options=color_options,
                border_radius=8,
                on_change=lambda e: self._update_setting("theme.primaryColor", e.control.value)
            )
        
        # Layout da tela
        return ft.Container(
            content=ft.Column(
                controls=[
                    # Cabeçalho
                    self._build_header(),
                    
                    # Formulário
                    self._build_form(),
                    
                    # Botões
                    self._build_action_buttons(),
                ],
                spacing=0,
                expand=True,
            ),
            expand=True,
        )
    
    def _build_header(self):
        """Constrói o cabeçalho da tela"""
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.IconButton(
                        icon=ft.icons.ARROW_BACK,
                        on_click=lambda _: self.navigation.go_back()
                    ),
                    ft.Text("Configurações", size=20, weight="bold"),
                ],
                alignment=ft.MainAxisAlignment.START,
            ),
            padding=10,
        )
    
    def _build_form(self):
        """Constrói o formulário de configurações"""
        return ft.Container(
            content=ft.Column(
                controls=[
                    # Seção de notificações
                    ft.Text("Notificações", size=16, weight="bold"),
                    self.form_fields["notifications_enabled"],
                    self.form_fields["low_stock_threshold"],
                    self.form_fields["expiry_warning_days"],
                    
                    ft.Divider(),
                    
                    # Seção de relatórios
                    ft.Text("Relatórios", size=16, weight="bold"),
                    self.form_fields["weekly_report_enabled"],
                    
                    ft.Divider(),
                    
                    # Seção de backup
                    ft.Text("Backup", size=16, weight="bold"),
                    self.form_fields["backup_enabled"],
                    
                    # Seção de tema (se disponível)
                    *([
                        ft.Divider(),
                        ft.Text("Aparência", size=16, weight="bold"),
                        self.form_fields["theme_mode"],
                        self.form_fields["primary_color"],
                    ] if "theme_mode" in self.form_fields else []),
                ],
                spacing=10,
                scroll=ft.ScrollMode.AUTO,
            ),
            padding=20,
            expand=True,
        )
    
    def _build_action_buttons(self):
        """Constrói os botões de ação"""
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.ElevatedButton(
                        "Restaurar Padrões",
                        on_click=lambda _: self._reset_to_defaults(),
                        style=ft.ButtonStyle(
                            color=ft.colors.BLACK,
                            bgcolor=ft.colors.GREY_300,
                        ),
                    ),
                    ft.ElevatedButton(
                        "Salvar",
                        on_click=lambda _: self._save_settings(),
                        style=ft.ButtonStyle(
                            color=ft.colors.WHITE,
                            bgcolor=ft.colors.BLUE_500,
                        ),
                    ),
                ],
                alignment=ft.MainAxisAlignment.END,
                spacing=10,
            ),
            padding=20,
        )
    
    def _update_setting(self, path, value):
        """Atualiza uma configuração específica"""
        parts = path.split(".")
        current = self.settings
        
        for part in parts[:-1]:
            current = current[part]
        
        current[parts[-1]] = value
    
    def _save_settings(self):
        """Salva as configurações atualizadas"""
        # Validar configurações antes de salvar
        if self._validate_settings():
            success = self.data.update_settings(self.settings)
            
            if success:
                self.navigation.show_snack_bar(
                    "Configurações salvas com sucesso!",
                    ft.colors.GREEN_500
                )
                self.navigation.go_back()
            else:
                self.navigation.show_snack_bar(
                    "Erro ao salvar configurações. Tente novamente.",
                    ft.colors.RED_500
                )
        else:
            self.navigation.show_snack_bar(
                "Configurações inválidas. Verifique os valores.",
                ft.colors.RED_500
            )
    
    def _validate_settings(self):
        """Valida as configurações antes de salvar"""
        try:
            # Validar limite de estoque baixo
            low_stock = self.settings["notifications"]["lowStockThreshold"]
            if not isinstance(low_stock, int) or low_stock < 0:
                return False
            
            # Validar dias para alerta de vencimento
            expiry_days = self.settings["notifications"]["expiryWarningDays"]
            if not isinstance(expiry_days, int) or expiry_days < 0:
                return False
            
            return True
        except Exception as e:
            print(f"Erro ao validar configurações: {e}")
            return False
    
    def _reset_to_defaults(self):
        """Restaura as configurações para os valores padrão"""
        # Confirmar antes de restaurar
        def confirm_reset(e):
            if e.control.result:
                # Obter configurações padrão do serviço
                from services.settings_service import SettingsService
                settings_service = SettingsService(self.data.firebase, self.data.db)
                default_settings = settings_service.get_default_settings()
                
                # Atualizar configurações
                success = self.data.update_settings(default_settings)
                
                if success:
                    # Atualizar formulário
                    self.settings = default_settings
                    self.navigation.show_snack_bar(
                        "Configurações restauradas para os valores padrão",
                        ft.colors.GREEN_500
                    )
                    # Reconstruir a tela
                    self.navigation.update_view()
                else:
                    self.navigation.show_snack_bar(
                        "Erro ao restaurar configurações padrão",
                        ft.colors.RED_500
                    )
        
        # Mostrar diálogo de confirmação
        self.navigation.page.dialog = ft.AlertDialog(
            title=ft.Text("Restaurar configurações padrão?"),
            content=ft.Text("Isso irá substituir todas as suas configurações personalizadas. Esta ação não pode ser desfeita."),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: setattr(self.navigation.page.dialog, "open", False)),
                ft.TextButton("Restaurar", on_click=confirm_reset),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            on_dismiss=lambda e: print("Diálogo fechado")
        )
        
        self.navigation.page.dialog.open = True
        self.navigation.page.update()
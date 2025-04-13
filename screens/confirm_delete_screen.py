import flet as ft

class ConfirmDeleteScreen:
    def __init__(self, data, navigation):
        self.data = data
        self.navigation = navigation
        self.item_type = None
        self.item = None
    
    def set_item(self, item_type, item):
        """Define o item a ser excluído"""
        self.item_type = item_type
        self.item = item
    
    def build(self):
        if not self.item:
            return ft.Container(
                content=ft.Text("Nenhum item selecionado para exclusão"),
                alignment=ft.alignment.center,
                padding=20
            )
        
        # Determinar tipo de item e mensagem
        item_name = self.item.get("name", "Item")
        
        if self.item_type == "product":
            title = "Excluir Produto"
            message = f"Tem certeza que deseja excluir o produto '{item_name}'? Esta ação não pode ser desfeita."
            icon = ft.icons.INVENTORY_2_OUTLINED
            color = ft.colors.BLUE
        elif self.item_type == "residue":
            title = "Excluir Resíduo"
            message = f"Tem certeza que deseja excluir o resíduo '{item_name}'? Esta ação não pode ser desfeita."
            icon = ft.icons.DELETE_OUTLINE
            color = ft.colors.PURPLE
        elif self.item_type == "group":
            title = "Excluir Grupo"
            message = f"Tem certeza que deseja excluir o grupo '{item_name}'? Esta ação não pode ser desfeita."
            icon = ft.icons.FOLDER_DELETE
            color = ft.colors.ORANGE
            
            # Verificar se há itens no grupo
            from services.group_service import GroupService
            group_service = GroupService(self.data.firebase, self.data.db)
            
            # Verificar se é grupo de produtos ou resíduos
            is_product_group = self.item.get("group_type", "product") == "product"
            
            # Contar itens no grupo
            if is_product_group:
                items = group_service.get_products_in_group(self.item["id"])
                item_type_name = "produtos"
            else:
                items = group_service.get_residues_in_group(self.item["id"])
                item_type_name = "resíduos"
            
            if len(items) > 0:
                message = f"O grupo '{item_name}' contém {len(items)} {item_type_name}. Se excluir o grupo, esses itens perderão a associação com o grupo. Deseja continuar?"
        else:
            title = "Excluir Item"
            message = f"Tem certeza que deseja excluir '{item_name}'? Esta ação não pode ser desfeita."
            icon = ft.icons.DELETE_OUTLINE
            color = ft.colors.RED
        
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
                                ft.Text(title, size=20, weight="bold"),
                            ],
                            alignment=ft.MainAxisAlignment.START,
                        ),
                        padding=10,
                    ),
                    
                    # Conteúdo
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Icon(
                                    icon,
                                    size=64,
                                    color=color,
                                ),
                                ft.Text(
                                    message,
                                    size=16,
                                    text_align=ft.TextAlign.CENTER,
                                ),
                                
                                # Detalhes do item
                                ft.Container(
                                    content=self._build_item_details(),
                                    margin=ft.margin.only(top=20),
                                ),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=20,
                        ),
                        padding=20,
                        alignment=ft.alignment.center,
                    ),
                    
                    # Botões
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.ElevatedButton(
                                    "Cancelar",
                                    on_click=lambda _: self.navigation.go_back(),
                                    style=ft.ButtonStyle(
                                        color=ft.colors.BLACK,
                                        bgcolor=ft.colors.GREY_300,
                                    ),
                                ),
                                ft.ElevatedButton(
                                    "Excluir",
                                    on_click=self._confirm_delete,
                                    style=ft.ButtonStyle(
                                        color=ft.colors.WHITE,
                                        bgcolor=ft.colors.RED_500,
                                    ),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.END,
                            spacing=10,
                        ),
                        padding=20,
                    ),
                ],
                spacing=0,
                expand=True,
            ),
            expand=True,
        )
    
    def _build_item_details(self):
        """Constrói os detalhes do item a ser excluído"""
        details = []
        
        if self.item_type == "product":
            details = [
                self._build_detail_row("Nome", self.item.get("name", "N/A")),
                self._build_detail_row("Quantidade", str(self.item.get("quantity", "N/A"))),
                self._build_detail_row("Lote", self.item.get("lot", "N/A")),
                self._build_detail_row("Validade", self.item.get("expiry", "N/A")),
            ]
        elif self.item_type == "residue":
            details = [
                self._build_detail_row("Nome", self.item.get("name", "N/A")),
                self._build_detail_row("Tipo", self.item.get("type", "N/A")),
                self._build_detail_row("Quantidade", str(self.item.get("quantity", "N/A"))),
                self._build_detail_row("Data de Entrada", self.item.get("entryDate", "N/A")),
            ]
        elif self.item_type == "group":
            # Adicionar detalhes para grupos
            from services.group_service import GroupService
            group_service = GroupService(self.data.firebase, self.data.db)
            
            # Verificar se é grupo de produtos ou resíduos
            is_product_group = self.item.get("type", "product") == "product"
            
            # Contar itens no grupo
            if is_product_group:
                items = group_service.get_products_in_group(self.item["id"])
                item_type = "produtos"
            else:
                items = group_service.get_residues_in_group(self.item["id"])
                item_type = "resíduos"
            
            details = [
                self._build_detail_row("Nome", self.item.get("name", "N/A")),
                self._build_detail_row("Descrição", self.item.get("description", "N/A")),
                self._build_detail_row("Tipo", "Produtos" if is_product_group else "Resíduos"),
                self._build_detail_row("Itens associados", f"{len(items)} {item_type}"),
            ]
        
        return ft.Column(
            controls=details,
            spacing=8,
            horizontal_alignment=ft.CrossAxisAlignment.START,
        )

    def _build_detail_row(self, label, value):
        """Constrói uma linha de detalhe do item"""
        return ft.Row(
            controls=[
                ft.Text(f"{label}:", weight="bold", size=14),
                ft.Text(value, size=14),
            ],
            spacing=8,
        )   

    def _confirm_delete(self, _):
        """Confirma a exclusão do item"""
        success = False
        
        try:
            print(f"Confirmando exclusão de {self.item_type}: {self.item.get('name', 'Desconhecido')}")
            
            if self.item_type == "product":
                success = self.data.delete_product(self.item["id"])
            elif self.item_type == "residue":
                success = self.data.delete_residue(self.item["id"])
            elif self.item_type == "group":
                # Verificar se é grupo de produtos ou resíduos
                from services.group_service import GroupService
                group_service = GroupService(self.data.firebase, self.data.db)
                
                # Obter todos os grupos de resíduos
                residue_groups = group_service.get_all_residue_groups()
                residue_group_ids = [g["id"] for g in residue_groups]
                
                # Verificar se o ID do grupo está na lista de IDs de grupos de resíduos
                is_residue_group = self.item["id"] in residue_group_ids
                is_product_group = not is_residue_group
                
                print(f"ID do grupo: {self.item['id']}, is_residue_group: {is_residue_group}")
                
                # Obter itens do grupo
                if is_product_group:
                    items = group_service.get_products_in_group(self.item["id"])
                    print(f"Encontrados {len(items)} produtos no grupo")
                    
                    # MODIFICAÇÃO: Excluir todos os produtos do grupo
                    print(f"Excluindo {len(items)} produtos do grupo {self.item['name']}")
                    from services.product_service import ProductService
                    product_service = ProductService(self.data.firebase, self.data.db)
                    
                    for item in items:
                        try:
                            product_id = item["id"]
                            print(f"Excluindo produto {item['name']} (ID: {product_id})")
                            product_service.delete_product(product_id)
                        except Exception as e:
                            print(f"Erro ao excluir produto {item.get('name', 'desconhecido')}: {e}")
                else:
                    items = group_service.get_residues_in_group(self.item["id"])
                    print(f"Encontrados {len(items)} resíduos no grupo")
                    
                    # MODIFICAÇÃO: Excluir todos os resíduos do grupo
                    print(f"Excluindo {len(items)} resíduos do grupo {self.item['name']}")
                    from services.residue_service import ResidueService
                    residue_service = ResidueService(self.data.firebase, self.data.db)
                    
                    for item in items:
                        try:
                            residue_id = item["id"]
                            print(f"Excluindo resíduo {item['name']} (ID: {residue_id})")
                            residue_service.delete_residue(residue_id)
                        except Exception as e:
                            print(f"Erro ao excluir resíduo {item.get('name', 'desconhecido')}: {e}")
                
                # Excluir o grupo
                is_residue_group = not is_product_group
                print(f"Chamando delete_group com id: {self.item['id']}, is_residue: {is_residue_group}")
                success = self.data.delete_group(self.item["id"], is_product_group)  # Use o método do data_service
                print(f"Resultado da exclusão do grupo: {success}")
            
            if success:
                self.navigation.show_snack_bar(
                    f"{self.item_type.capitalize()} excluído com sucesso!",
                    ft.colors.GREEN_500
                )
                # Atualizar dados
                self.data.refresh_data()
                # Voltar para a tela anterior
                self.navigation.go_back()
                # Forçar atualização da interface
                self.navigation.update_view()
            else:
                self.navigation.show_snack_bar(
                    f"Erro ao excluir {self.item_type}. Tente novamente.",
                    ft.colors.RED_500
                )
        except Exception as e:
            print(f"Erro ao confirmar exclusão: {e}")
            import traceback
            traceback.print_exc()
            self.navigation.show_snack_bar(
                f"Erro ao excluir: {str(e)}",
                ft.colors.RED_500
            )
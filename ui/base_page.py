import flet as ft
from abc import abstractmethod

from models import User


class UserControl[UserType:User]:
    def __init__(self) -> None:
        self.authorized_user: UserType = None

    def get_user(self) -> UserType:
        return self.authorized_user

    def set_user(self, value: UserType) -> None:
        self.authorized_user = value

    def logout(self) -> None:
        self.authorized_user = None


class BasePage:
    def __init__(self, page: ft.Page, user_storage: UserControl):
        self.page = page
        self.user_storage = user_storage

    def handle_go_back(self):
        pass

    @abstractmethod
    async def render(self) -> ft.Control:
        raise NotImplemented

    def force_rerender(self) -> None:
        self.page.update(self.render())

    def create_error_message(self, description: str):
        def handle_decline_banner(_):
            self.page.banner.open = False
            self.page.update()

        banner = ft.Banner(
            bgcolor=ft.colors.RED_50,
            leading=ft.Icon(ft.icons.ERROR_OUTLINED, color=ft.colors.RED, size=40),
            content=ft.Text(
                description,
                color='black'
            ),
            actions=[
                ft.TextButton("Закрыть", on_click=handle_decline_banner),
            ],
        )
        self.page.banner = banner
        self.page.banner.open = True
        self.page.update()

    def create_success_message(self, description: str):
        def handle_decline_banner(_):
            self.page.banner.open = False
            self.page.update()

        banner = ft.Banner(
            bgcolor=ft.colors.GREEN_50,
            leading=ft.Icon(ft.icons.CHECK_OUTLINED, color=ft.colors.GREEN, size=40),
            content=ft.Text(
                description,
                color='black'
            ),
            actions=[
                ft.TextButton("Закрыть", on_click=handle_decline_banner),
            ],
        )
        self.page.banner = banner
        self.page.banner.open = True
        self.page.update()

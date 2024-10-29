import flet as ft

import settings
from ui.login_page import LoginPage
from ui.registration_page import RegistrationPage
from ui.appointments_page import AppointmentsPage
from ui.base_page import UserControl
from ui.diagnoses_page import DiagnosesPage
from ui.patients_page import PatientsPage


class Router:
    def __init__(self, page: ft.Page, initial_route: str = '/'):
        self.user_control = UserControl()

        self.routes = {
            '/': lambda: ft.Container(),
            '/login': lambda: settings.LOOP.run_until_complete(
                LoginPage(page, self.user_control).render()
            ),
            '/registration': lambda: settings.LOOP.run_until_complete(
                RegistrationPage(page, self.user_control).render()
            ),
            '/appointments': lambda: settings.LOOP.run_until_complete(
                AppointmentsPage(page, self.user_control).render()
            ),
            '/diagnoses': lambda: settings.LOOP.run_until_complete(
                DiagnosesPage(page, self.user_control).render()
            ),
            '/patients': lambda: settings.LOOP.run_until_complete(
                PatientsPage(page, self.user_control).render()
            )
        }
        self.page = page
        self.body = ft.Container(content=self.routes[initial_route]())

    def handle_switch_drawer(self, *_):
        self.page.drawer.open = not self.page.drawer.open
        self.page.update()

    def handle_route_change(self, route: ft.RouteChangeEvent) -> None:
        self.page.drawer = ft.NavigationDrawer(
            tile_padding=ft.Padding(top=20, bottom=20, left=0, right=0),
            controls=[
                ft.OutlinedButton(
                    text="Пациенты",
                    on_click=lambda *_: self.page.go('/patients')
                ),
                ft.OutlinedButton(
                    text="Диагнозы",
                    on_click=lambda *_: self.page.go('/diagnoses')
                ),
                ft.OutlinedButton(
                    text="Приемы",
                    on_click=lambda *_: self.page.go('/appointments')
                ),
                ft.OutlinedButton(
                    text="Выход",
                    style=ft.ButtonStyle(color=ft.colors.RED_50),
                    on_click=lambda *_: None
                )
            ]
        ) if self.user_control.get_user() else None
        self.page.appbar = ft.AppBar(
            title=ft.Text("Клиника Саныча"),
            center_title=True,
        )
        self.body.clean()
        new_content = self.routes[route.route]()
        if not new_content:
            return

        self.body.content = new_content
        self.body.update()

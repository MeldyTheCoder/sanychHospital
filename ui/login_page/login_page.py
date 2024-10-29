import flet as ft

import models
import serializers
from ui.components.flet_form import FletForm
from ui.base_page import BasePage


class LoginPage(BasePage):
    """
    Страница авторизации проекта
    """

    async def handle_form_submit(self, data):
        user = await models.User.objects.get_or_none(username=data.get('username'))
        if not user:
            return self.create_error_message(
                'Неверный логин или пароль',
            )

        self.user_storage.set_user(user)
        self.create_success_message('Вы успешно вошли!')
        self.page.route = '/patients'
        self.page.update()

    def handle_registration_button_click(self, *_):
        self.page.route = '/registration'
        self.page.update()

    async def render(self) -> ft.Control:
        return ft.Column(
            [
                ft.Text('Авторизация', size=25, text_align=ft.TextAlign.CENTER),
                ft.Divider(),
                ft.Row(
                    [
                        FletForm(
                            model=serializers.UserLoginModel,
                            handle_form_submit=self.handle_form_submit,
                            submit_button_text='Войти',
                            actions=[
                                ft.ElevatedButton('Регистрация', on_click=self.handle_registration_button_click)
                            ]
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )






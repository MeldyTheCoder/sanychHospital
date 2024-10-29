import flet as ft

import models
import serializers
from ui.components.flet_form import FletForm
from ui.base_page import BasePage


class RegistrationPage(BasePage):
    """
    Страница авторизации проекта
    """

    async def handle_form_submit(self, data):
        user = await models.User.objects.get_or_none(
            username=data.get('username'),
        )

        if user:
            return self.create_error_message(
                'Пользователь с указанными данными уже существует.',
            )

        created_user = await models.User.objects.create(
            **data,
        )
        self.user_storage.set_user(created_user)
        self.page.route = '/'
        self.page.update()
        self.create_success_message('Вы успешно зарегистрировались!')

    def handle_login_button_click(self, *_,):
        self.page.route = '/login'
        self.page.update()

    async def render(self) -> ft.Control:
        return ft.Column(
            [
                ft.Text('Регистрация', size=25, text_align=ft.TextAlign.CENTER),
                ft.Divider(),
                ft.Row(
                    [
                        FletForm(
                            model=serializers.UserRegistrationModel,
                            handle_form_submit=self.handle_form_submit,
                            submit_button_text='Зарегистрироваться',
                            actions=[
                                ft.ElevatedButton('Вход', on_click=self.handle_login_button_click)
                            ]
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )






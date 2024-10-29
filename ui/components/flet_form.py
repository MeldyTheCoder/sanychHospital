import asyncio
import typing

import flet as ft
import pydantic
import datetime

import pydantic_core

import settings


class FletForm(ft.UserControl):
    """
    Виджет формы, адаптирующийся почти под любую модель pydantic.
    """

    def __init__(
            self,
            model: pydantic.BaseModel,
            handle_form_submit: typing.Callable[[dict], typing.Any] = None,
            submit_button_text: str = 'Ввести',
            actions: list[ft.Control] = None,
            choices: dict[str, tuple[list[pydantic.BaseModel], typing.Callable[[pydantic.BaseModel], typing.Any]]] = None,
            initial_values: dict = None,
            **kwargs
    ):

        self.__model = model
        self.__handle_form_submit = handle_form_submit
        self.__submit_button_text = submit_button_text
        self.__actions = actions
        self.__choices = choices or []

        self.__values = {}
        self.__fields = {}
        self.__initial_values = initial_values or {}
        self.container = ft.Column()

        super().__init__(**kwargs)

    @staticmethod
    def get_keyboard_type(field_name: str, field: pydantic.fields.FieldInfo):
        if field_name == 'email':
            return ft.KeyboardType.EMAIL

        elif field_name.startswith('password'):
            return ft.KeyboardType.VISIBLE_PASSWORD

        elif field.annotation in [str, typing.Optional[str]]:
            return ft.KeyboardType.TEXT

        elif field.annotation in (int, float, typing.Optional[int], typing.Optional[float], typing.Union[int, float]):
            return ft.KeyboardType.NUMBER

        elif field.annotation == datetime.datetime:
            return ft.KeyboardType.DATETIME

        return None

    @staticmethod
    def get_error_for_field(errors: list, field_name: str):
        result = list(filter(
            lambda error: field_name in error['loc'],
            errors
        ))

        if not result:
            return None

        return result[0]

    def handle_field_errors(self, validation_error: pydantic.ValidationError):
        errors = validation_error.errors()

        for field_name, field in self.__fields.items():
            if not field.value and field.data.get('required'):
                field.error_text = 'Данное поле обязательно для заполнения.'
                continue

            error = self.get_error_for_field(errors, field_name)
            if not error:
                continue

            error_message = error.get('ctx', {}).get('error', None) or error.get('msg')
            if not error_message:
                continue

            message = str(error_message)
            field.error_text = message

        self.update()

    def clear_field_errors(self):
        for _, field in self.__fields.items():
            field.error_text = None

        self.update()

    def handle_field_change(self, e, field_name: str):
        self.__values[field_name] = e.control.value

        if e.control.error_text:
            e.control.error_text = ''
            self.update()

    def handle_form_submit(self, _):
        try:
            self.clear_field_errors()
            self.__model.model_validate(self.__values)

            if self.__handle_form_submit and not asyncio.iscoroutinefunction(self.__handle_form_submit):
                return self.__handle_form_submit(self.__values.copy())
            elif asyncio.iscoroutinefunction(self.__handle_form_submit):
                return settings.LOOP.run_until_complete(self.__handle_form_submit(self.__values.copy()))

        except pydantic.ValidationError as validation_error:
            self.handle_field_errors(validation_error)

    def build(self):
        fields = self.__model.__fields__

        if self.container.controls:
            self.container.controls = []

        for field_name, field in fields.items():
            keyboard_type = self.get_keyboard_type(field_name, field)
            if not keyboard_type:
                continue

            initial_value = self.__initial_values.get(field_name, '')
            if initial_value:
                self.__values[field_name] = initial_value
            else:
                default_value = field.get_default(call_default_factory=True)
                if not isinstance(default_value, pydantic_core.PydanticUndefinedType):
                    self.__values[field_name] = default_value
                else:
                    self.__values[field_name] = ''

            is_required = field.is_required()

            if self.__choices and self.__choices.get(field_name):
                choices = self.__choices[field_name]
                self.container.controls.append(
                    ft.Row([
                        field := ft.Dropdown(
                            suffix_text="*" if is_required else None,
                            suffix_style=ft.TextStyle(color='red'),
                            label=field.title,
                            value=self.__values[field_name],
                            tooltip=field.description,
                            on_change=lambda e, fn=field_name: self.handle_field_change(e, fn),
                            data={
                                'required': is_required
                            },
                            options=[
                                ft.dropdown.Option(
                                    key=getattr(option, 'id', index), text=choices[1](option),
                                ) for index, option in enumerate(choices[0])
                            ]
                        )
                    ])
                )
            else:
                self.container.controls.append(
                    ft.Row([
                        field := ft.TextField(
                            suffix_text='*' if is_required else None,
                            suffix_style=ft.TextStyle(color='red'),
                            label=field.title,
                            value=self.__values[field_name],
                            tooltip=field.description,
                            keyboard_type=keyboard_type,
                            on_change=lambda e, fn=field_name: self.handle_field_change(e, fn),
                            password=keyboard_type is ft.KeyboardType.VISIBLE_PASSWORD,
                            can_reveal_password=keyboard_type is ft.KeyboardType.VISIBLE_PASSWORD,
                            data={
                                'required': is_required
                            }
                        )
                    ])
                )

            self.__fields[field_name] = field

        if not self.__actions:
            self.__actions = []

        actions = ft.Row(
            controls=[
                ft.ElevatedButton(
                    text=self.__submit_button_text,
                    on_click=self.handle_form_submit
                ),
                *self.__actions
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )

        self.container.controls.append(actions)
        return self.container

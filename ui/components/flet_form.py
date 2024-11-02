import abc
import asyncio
import typing
from collections.abc import Callable

import flet as ft
import pydantic
import datetime

import pydantic_core
from pydantic._internal._model_construction import ModelMetaclass
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

        self.__subform_validated = {}

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

    def handle_field_errors(self, validation_error: pydantic.ValidationError, path: list[str] = None):
        errors = validation_error.errors()

        fields_controls = self.__fields if not path else self.get_attr_by_path(path, self.__fields)
        for field_name, field in fields_controls.items():
            if isinstance(field, dict):
                self.handle_field_errors(validation_error, [*(path or []), field_name])
                continue

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
        self.page.update()

    def clear_field_errors(self, fields: dict = None):
        fields = self.__fields if not fields else fields
        for _, field in fields.items():
            if isinstance(field, dict):
                self.clear_field_errors(field)
            else:
                field.error_text = None

        self.page.update()

    @staticmethod
    def set_attr_by_path[T:dict](path: list, data: T, value: typing.Any) -> T:
        prev_data = data
        last_index = len(path) - 1

        for index, line in enumerate(path):
            if not line:
                continue

            if not prev_data.get(line):
                prev_data[line] = {}

            if index == last_index:
                prev_data[line] = value
                break

            prev_data = prev_data.get(line)

        return data

    def handle_field_change(self, e, field_path: list):
        self.set_attr_by_path(
            field_path,
            self.__values,
            e.control.value,
        )

        if e.control.error_text:
            e.control.error_text = ''
            self.update()
            self.page.update()

    def handle_subform_submit(self, path: list[str], on_close: Callable[[], typing.Any]):
        model = self.get_attr_by_path(path, self.__model)
        values = self.get_attr_by_path(path, self.__values)
        fields = self.get_attr_by_path(path, self.__fields)

        try:
            self.clear_field_errors(fields)
            model.model_validate(values)
            self.set_attr_by_path(path, self.__subform_validated, True)
            on_close()
            self.update()
        except pydantic.ValidationError as validation_error:
            print(validation_error)
            self.handle_field_errors(validation_error, path=path)

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

    def get_attr_by_path(self, path: list, data: typing.Any):
        if not path:
            return None

        path_list = path.copy()
        path_line = path_list.pop(-1)

        if isinstance(data, dict):
            output = data.get(path_line, None)
        elif isinstance(data, ModelMetaclass):
            output = data.__dict__['__annotations__'].get(path_line, None)
        else:
            output = getattr(data, path_line)

        if not path_list:
            return output

        return self.get_attr_by_path(path_list, output)

    def handle_dialog_close(self, *_):
        self.page.close_dialog()
        self.page.update()

    def handle_open_alert_form_dialog(self, field: pydantic.fields.FieldInfo, path: list[str], form_content: ft.Control):
        def handle_dialog_close(*_):
            self.page.close(dialog)

        dialog = ft.AlertDialog(
            title=ft.Text(
                value=field.title
            ),
            modal=True,
            scrollable=True,
            content_padding=ft.Padding(top=20, bottom=20, left=20, right=20),
            content=ft.Container(
                width=315,
                content=form_content,
                alignment=ft.alignment.center,
            ),
            actions=[
                ft.FilledButton(
                    text="Сохранить",
                    on_click=lambda *_, p=path, on_close=handle_dialog_close: self.handle_subform_submit(path=p, on_close=on_close),
                ),
                ft.OutlinedButton(
                    text="Отмена",
                    style=ft.ButtonStyle(
                        color=ft.colors.RED,
                    ),
                    on_click=handle_dialog_close,
                )
            ]
        )

        self.page.open(dialog)
        self.page.update()

    def _build_fields(self, path: list = None):
        fields_list = self.__model.__fields__ if not path else self.get_attr_by_path(path, self.__model).__fields__
        container = ft.Column(scroll=ft.ScrollMode.ADAPTIVE)
        values = {}
        fields = {}

        for field_name, field in fields_list.items():
            field_path = (path or []) + [field_name]
            if type(field.annotation) == ModelMetaclass:
                model_fields, model_values, model_container = self._build_fields(
                    (path or []) + [field_name],
                )

                values[field_name] = model_values
                fields[field_name] = model_fields

                subfield_validated = self.get_attr_by_path(
                    field_path,
                    self.__subform_validated,
                )

                container.horizontal_alignment = ft.CrossAxisAlignment.CENTER
                container.controls.append(
                    ft.OutlinedButton(
                        text=field.title,
                        width=300,
                        height=50,
                        style=ft.ButtonStyle(
                            color=ft.colors.RED if not subfield_validated else ft.colors.GREEN,
                            shape=ft.RoundedRectangleBorder(radius=5),
                            side=ft.BorderSide(1, ft.colors.BLACK)
                        ),
                        on_click=lambda *_, content=model_container, f=field, path=field_path: self.handle_open_alert_form_dialog(f, path, content)
                    )
                )
                continue

            keyboard_type = self.get_keyboard_type(field_name, field)
            if not keyboard_type:
                continue

            initial_value = self.__initial_values.get(field_name, '')
            if initial_value:
                values[field_name] = initial_value
            else:
                default_value = field.get_default(call_default_factory=True)
                if not isinstance(default_value, pydantic_core.PydanticUndefinedType):
                    values[field_name] = default_value
                else:
                    values[field_name] = ''

            is_required = field.is_required()

            if self.__choices and self.__choices.get(field_name):
                choices = self.__choices[field_name]
                container.controls.append(
                    ft.Row([
                        field_control := ft.Dropdown(
                            suffix_text="*" if is_required else None,
                            suffix_style=ft.TextStyle(color='red'),
                            label=field.title,
                            value=values[field_name],
                            tooltip=field.description,
                            on_change=lambda e, fp=field_path: self.handle_field_change(e, fp),
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
                container.controls.append(
                    ft.Row([
                        field_control := ft.TextField(
                            suffix_text='*' if is_required else None,
                            suffix_style=ft.TextStyle(color='red'),
                            label=field.title,
                            value=values[field_name],
                            tooltip=field.description,
                            keyboard_type=keyboard_type,
                            on_change=lambda e, fp=field_path: self.handle_field_change(e, fp),
                            password=keyboard_type is ft.KeyboardType.VISIBLE_PASSWORD,
                            can_reveal_password=keyboard_type is ft.KeyboardType.VISIBLE_PASSWORD,
                            data={
                                'required': is_required
                            }
                        )
                    ])
                )

            fields[field_name] = field_control

        return fields, values, container

    def build(self):
        fields, values, container = self._build_fields()

        self.__values = values.copy()
        self.__fields = fields.copy()

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

        container.controls.append(actions)
        return container

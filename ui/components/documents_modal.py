from typing import Optional

import flet as ft

import models


description_font_style = ft.TextStyle(
    size=10,
    color=ft.colors.GREY,
)

value_font_style = ft.TextStyle(
    size=14,
)

def render_description_item(title: str, value: str):
    return ft.Column(
        spacing=2,
        controls=[
            ft.Text(
                value=title,
                style=description_font_style
            ),
            ft.Text(
                value=value,
                style=value_font_style,
                max_lines=3,
                no_wrap=False,
                overflow=ft.TextOverflow.ELLIPSIS,
            )
        ],
    )

def render_tab_container(content: ft.Control):
    return ft.Container(
        width=300,
        margin=ft.Margin(
            top=20,
            bottom=0,
            left=0,
            right=0,
        ),
        padding=ft.Padding(
            top=5,
            bottom=5,
            left=5,
            right=5,
        ),
        border_radius=10,
        alignment=ft.alignment.top_center,
        content=content,
    )

class DocumentsModal(ft.AlertDialog):
    def __init__(self, patient: models.Patient, **kwargs):
        super().__init__(**kwargs)

        patient_bio_container = ft.Column(
            width=300,
            controls=[
                ft.CircleAvatar(content=ft.Icon(ft.icons.PERSON_OUTLINED), width=80, height=80),
                ft.Text(
                    value=f"{patient.last_name} {patient.first_name} {patient.surname}",
                    style=ft.TextStyle(
                        size=16,
                    ),
                    no_wrap=False,
                )
            ],
            spacing=10,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
        )

        passport = patient.passport
        passport_content = ft.Column(
            height=200,
            width=300,
            spacing=20,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.SPACE_AROUND,
            controls=[
                ft.Column(
                    spacing=10,
                    alignment=ft.MainAxisAlignment.START,
                    controls=[
                        ft.Text(
                            value=f"{passport.serial} {passport.number}",
                            style=ft.TextStyle(
                                size=20,
                                weight=ft.FontWeight.W_500,
                            ),
                        ),
                        render_description_item(
                            title="Кем выдан",
                            value=passport.issued_by,
                        ),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.START,
                            controls=[
                                ft.Column(
                                    controls=[
                                        render_description_item(
                                            title="Дата выдачи",
                                            value=passport.issued_date.strftime('%d.%m.%Y')
                                        ),
                                        render_description_item(
                                            title="Код подразделения",
                                            value="000-000",
                                        ),
                                    ]
                                ),
                                ft.Column(
                                    [
                                        render_description_item(
                                            title="Дата рождения",
                                            value=passport.date_of_birth.strftime('%d.%m.%Y')
                                        ),
                                        render_description_item(
                                            title="Пол",
                                            value="Мужской" if passport.gender == models.Gender.MALE else "Женский",
                                        ),
                                    ]
                                ),
                            ],
                        ),
                        render_description_item(
                            title="Адрес регистрации",
                            value=passport.address,
                        ),
                    ]
                )
            ],
        )

        insurance = patient.insurance
        insurance_content = ft.Column(
            height=120,
            spacing=20,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.SPACE_AROUND,
            controls=[
                ft.Column(
                    spacing=10,
                    alignment=ft.MainAxisAlignment.START,
                    controls=[
                        ft.Text(
                            value=f"{insurance.number}",
                            style=ft.TextStyle(
                                size=20,
                            ),
                        ),
                        render_description_item(
                            title="Кем выдан",
                            value='ООО "РЕСО-Cтрахование"',
                        ),
                        ft.Row(
                            vertical_alignment=ft.CrossAxisAlignment.START,
                            controls=[
                                ft.Column(
                                    controls=[
                                        render_description_item(
                                            title="Дата выдачи",
                                            value=insurance.date_of_issue.strftime('%d.%m.%Y')
                                        ),
                                    ]
                                ),
                                ft.Column(
                                    [
                                        render_description_item(
                                            title="Дата окончания",
                                            value=insurance.date_expires.strftime('%d.%m.%Y')
                                        ),
                                    ]
                                )
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                    ]
                )
            ],
        )

        med_card = patient.med_card
        med_card_content = ft.Column(
            height=100,
            spacing=20,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.SPACE_AROUND,
            controls=[
                ft.Column(
                    spacing=10,
                    alignment=ft.MainAxisAlignment.START,
                    controls=[
                        ft.Text(
                            value=f"№{med_card.id}",
                            style=ft.TextStyle(
                                size=20,
                            ),
                        ),
                        render_description_item(
                            title="Кем выдан",
                            value='Аганов Арам Арамович - лор эндокринолог',
                        ),
                        ft.Row(
                            vertical_alignment=ft.CrossAxisAlignment.START,
                            controls=[
                                ft.Column(
                                    controls=[
                                        render_description_item(
                                            title="Дата выдачи",
                                            value=insurance.date_of_issue.strftime('%d.%m.%Y')
                                        ),
                                    ]
                                ),
                                ft.Column(
                                    [
                                        render_description_item(
                                            title="Дата окончания",
                                            value="не обозначена",
                                        ),
                                    ]
                                )
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                    ]
                )
            ],
        )

        self.title = None
        self.content = ft.Column(
            controls=[
                patient_bio_container,
                ft.Tabs(
                    height=550,
                    tabs=[
                        ft.Tab(
                            text="Паспорт",
                            content=render_tab_container(
                                passport_content
                            ),
                        ),
                        ft.Tab(
                            text="Страховка",
                            content=render_tab_container(
                                insurance_content
                            ),
                        ),
                        ft.Tab(
                            text="Мед. карта",
                            content=render_tab_container(
                                med_card_content,
                            )
                        )
                    ]
                )
            ],
            spacing=20,
        )
        self.actions = [
            ft.OutlinedButton(
                text="Закрыть",
                on_click=lambda *_: self.page.close(self),
            )
        ]
        self.actions_alignment = ft.MainAxisAlignment.END
        self.modal = True
import flet as ft

import models
import serializers
import settings
from ui.base_page import BasePage
from modules.diagnosis import create_diagnosis, get_diagnoses
from ui.components import PydanticTable, FletForm


class DiagnosesPage(BasePage):
    """
    Страница диагнозов
    """

    all_diagnoses: list[models.Diagnosis]

    async def handle_create_diagnosis_form_submit(self, data):
        diagnosis = await create_diagnosis(
            name=data['name']
        )
        self.create_success_message(
            f"Диагноз {diagnosis.name} успешно создан."
        )

        await self.refresh_data()
        self.page.go('/', skip_route_change_event=False)
        self.page.go('/diagnoses', skip_route_change_event=False)

    async def refresh_data(self):
        self.all_diagnoses = await get_diagnoses()

    async def delete_diagnosis(self, diagnosis: models.Diagnosis):
        await diagnosis.delete()
        self.page.go('/')
        self.page.go('/diagnoses')
        return self.create_success_message(f"Диагноз {diagnosis.name} успешно удален!")

    async def render(self) -> ft.Control:
        await self.refresh_data()

        all_diagnoses_table = PydanticTable(
            dataset=self.all_diagnoses,
            columns_by_keys={
                'id': 'ID',
                'name': 'Название',
            },
            actions=[
                ("Удалить", lambda record: settings.LOOP.run_until_complete(
                    self.delete_diagnosis(record)
                ))
            ]
        )

        create_diagnosis_form = FletForm(
            model=serializers.DiagnosisSerializer,
            handle_form_submit=self.handle_create_diagnosis_form_submit,
        )

        return ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=30,
            controls=[
                ft.Text(
                    "Диагнозы",
                    size=35,
                ),
                ft.Container(
                    alignment=ft.alignment.center,
                    content=ft.Tabs(
                        height=700,
                        tab_alignment=ft.TabAlignment.CENTER,
                        tabs=[
                            ft.Tab(
                                content=ft.Container(
                                    content=all_diagnoses_table,
                                    alignment=ft.alignment.top_center,
                                ),
                                text='Все диагнозы',
                                icon=ft.icons.LIST_OUTLINED,
                            ),
                            ft.Tab(
                                content=ft.Container(
                                    ft.Row(
                                        [
                                            create_diagnosis_form,
                                        ],
                                        alignment=ft.MainAxisAlignment.CENTER,
                                    ),
                                    margin=ft.Margin(top=20, bottom=0, left=0, right=0),
                                    alignment=ft.alignment.center,
                                ),
                                text='Создать диагноз',
                                icon=ft.icons.CREATE_OUTLINED,
                            )
                        ]
                    )
                )
            ]
        )

import datetime

import flet as ft

import models
import serializers
import settings
from ui.base_page import BasePage
from ui.components import PydanticTable, FletForm
from modules.patient import get_patients, create_patient
from modules.diagnosis import get_diagnoses


class PatientsPage(BasePage):
    patients: list[models.Patient]

    async def handle_create_patient_form_submit(self, data):
        patient = await create_patient(
            serializers.PatientFormSerializer(
                **data,
            )
        )
        self.create_success_message(
            f"Запись пациента {patient.patient.first_name} успешно создана."
        )

        await self.refresh_data()
        self.page.go('/', skip_route_change_event=False)
        self.page.go('/patients', skip_route_change_event=False)

    async def refresh_data(self):
        self.patients = await get_patients()

    async def handle_delete_patient(self, patient: models.Patient):
        await patient.delete()

        self.page.go('/')
        self.page.go('/patients')

        return self.create_success_message(
            f"Пациент {patient.first_name} {patient.last_name} успешно удален!"
        )

    async def render(self) -> ft.Control:
        await self.refresh_data()

        all_patients_table = PydanticTable(
            dataset=self.patients,
            columns_by_keys={
                'id': 'ID',
                'first_name': 'Имя',
                'last_name': 'Фамилия',
                'surname': 'Отчество',
                'passport': 'Паспорт',
                'insurance': 'Страховой полис',
                'med_card': 'Мед. карта',
                'phone_number': 'Номер тел.'
            },
            displays={
                'passport': lambda value: f"{value.serial} {value.number}",
                'insurance': lambda value: f'№{value.number} до {value.date_expires}',
                'med_card': lambda value: f"№{value.number}",
            },
            actions=[
                ("Госпитализация", lambda record: self.create_success_message(f'Госпитализация назначена для пациента {record.first_name}!')),
                ("Удалить", lambda record: settings.LOOP.run_until_complete(self.handle_delete_patient(record)))
            ]
        )

        create_patient_form = FletForm(
            model=serializers.PatientFormSerializer,
            handle_form_submit=self.handle_create_patient_form_submit,
        )

        return ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=30,
            controls=[
                ft.Text(
                    "Пациенты",
                    size=35,
                ),
                ft.Container(
                    alignment=ft.alignment.top_center,
                    content=ft.Tabs(
                        height=600,
                        tab_alignment=ft.TabAlignment.CENTER,
                        tabs=[
                            ft.Tab(
                                content=ft.Container(
                                    content=all_patients_table,
                                    alignment=ft.alignment.top_center,
                                ),
                                text='Все пациенты',
                                icon=ft.icons.BOOK_ONLINE_OUTLINED,
                            ),
                            ft.Tab(
                                content=ft.Container(
                                    ft.Row(
                                        [
                                            create_patient_form,
                                        ],
                                        alignment=ft.MainAxisAlignment.CENTER,
                                    ),
                                    margin=ft.Margin(top=20, bottom=0, left=0, right=0),
                                    alignment=ft.alignment.top_center,
                                ),
                                text='Добавить пациента',
                                icon=ft.icons.CREATE_OUTLINED,
                            )
                        ]
                    )
                )
            ]
        )



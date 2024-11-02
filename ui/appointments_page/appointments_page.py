import datetime

import flet as ft

import models
import serializers
from ui.base_page import BasePage
from ui.components import PydanticTable, FletForm

from modules.appointments import get_all_appointments, get_active_appointments, create_appointment, get_inactive_appointments
from modules.patient import get_patients
from modules.diagnosis import get_diagnoses


class AppointmentsPage(BasePage):
    all_appointments: list[models.Appointment]
    active_appointments: list[models.Appointment]
    inactive_appointments: list[models.Appointment]
    patients: list[models.Patient]
    diagnoses: list[models.Diagnosis]

    async def handle_create_appointment_form_submit(self, data):
        appointment = await create_appointment(
            serializers.AppointmentSerializer(
                patient_id=int(data['patient']),
                diagnosis_id=int(data['diagnosis']),
                date_to_come=datetime.datetime.strptime(data['date_to_come'], '%Y-%m-%dT%H:%M'),
            )
        )
        self.create_success_message(
            f"Запись пациента {appointment.patient.first_name} успешно создана."
        )

        await self.refresh_data()
        self.page.go('/', skip_route_change_event=False)
        self.page.go('/appointments', skip_route_change_event=False)

    async def refresh_data(self):
        self.all_appointments = await get_all_appointments()
        self.active_appointments = await get_active_appointments()
        self.inactive_appointments = await get_inactive_appointments()
        self.patients = await get_patients()
        self.diagnoses = await get_diagnoses()

    async def render(self) -> ft.Control:
        await self.refresh_data()

        all_appointments_table = PydanticTable(
            dataset=self.all_appointments,
            columns_by_keys={
                'id': 'ID',
                'patient': 'ФИО Пациента',
                'diagnosis': 'Диагноз',
                'date_created': 'Дата создания',
                'date_to_come': 'Дата приема',
                'status': 'Статус приема'
            },
            displays={
                'diagnosis': lambda value: value.name,
                'patient': lambda value: f'{value.last_name} {value.first_name} {value.surname}',
                'date_created': lambda value: value.strftime('%d.%m.%Y %H:%M'),
                'date_to_come': lambda value: value.strftime('%d.%m.%Y %H:%M'),
                'status': lambda value: value.value
            },
            actions=[
                ("Обновить", lambda: None),
                ("Удалить", lambda: None)
            ]
        )

        active_appointments_table = PydanticTable(
            dataset=self.active_appointments,
            columns_by_keys={
                'id': 'ID',
                'patient': 'ФИО Пациента',
                'diagnosis': 'Диагноз',
                'date_created': 'Дата создания',
                'date_to_come': 'Дата приема',
                'status': 'Статус приема'
            },
            displays={
                'diagnosis': lambda value: value.name,
                'patient': lambda value: f'{value.last_name} {value.first_name} {value.surname}',
                'date_created': lambda value: value.strftime('%d.%m.%Y %H:%M'),
                'date_to_come': lambda value: value.strftime('%d.%m.%Y %H:%M'),
                'status': lambda value: value.value
            },
            actions=[
                ("Обновить", lambda: None),
                ("Удалить", lambda: None)
            ]
        )

        inactive_appointments_table = PydanticTable(
            dataset=self.inactive_appointments,
            columns_by_keys={
                'id': 'ID',
                'patient': 'ФИО Пациента',
                'diagnosis': 'Диагноз',
                'date_created': 'Дата создания',
                'date_to_come': 'Дата приема',
                'status': 'Статус приема'
            },
            displays={
                'diagnosis': lambda value: value.name,
                'patient': lambda value: f'{value.last_name} {value.first_name} {value.surname}',
                'date_created': lambda value: value.strftime('%d.%m.%Y %H:%M'),
                'date_to_come': lambda value: value.strftime('%d.%m.%Y %H:%M'),
                'status': lambda value: value.value
            },
            actions=[
                ("Обновить", lambda: None),
                ("Удалить", lambda: None)
            ]
        )

        create_appointment_form = FletForm(
            model=serializers.AppointmentFormSerializer,
            choices={
                'diagnosis': (
                    self.diagnoses,
                    lambda diagnosis: diagnosis.name,
                ),
                'patient': (
                    self.patients,
                    lambda patient: f"{patient.last_name} {patient.first_name} {patient.surname}",
                )
            },
            handle_form_submit=self.handle_create_appointment_form_submit,
        )

        return ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=30,
            controls=[
                ft.Text(
                    "Приемы",
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
                                    content=active_appointments_table,
                                    alignment=ft.alignment.top_center,
                                ),
                                text='Активные приемы',
                                icon=ft.icons.BOOK_ONLINE_OUTLINED,
                            ),
                            ft.Tab(
                                content=ft.Container(
                                    content=all_appointments_table,
                                    alignment=ft.alignment.top_center,
                                ),
                                text='Все приемы',
                                icon=ft.icons.LIST_OUTLINED,
                            ),
                            ft.Tab(
                                content=ft.Container(
                                    content=inactive_appointments_table,
                                    alignment=ft.alignment.top_center,
                                ),
                                text='Завершенные приемы',
                                icon=ft.icons.CLOSE_OUTLINED,
                            ),
                            ft.Tab(
                                content=ft.Container(
                                    ft.Row(
                                        [
                                            create_appointment_form,
                                        ],
                                        alignment=ft.MainAxisAlignment.CENTER,
                                    ),
                                    margin=ft.Margin(top=20, bottom=0, left=0, right=0),
                                    alignment=ft.alignment.top_center,
                                ),
                                text='Создать прием',
                                icon=ft.icons.CREATE_OUTLINED,
                            )
                        ]
                    )
                )
            ]
        )



import datetime

import models
import serializers
from models import Appointment, AppointmentStatuses, Patient,  Diagnosis


async def create_diagnosis():
    pass


async def create_appointment(data: serializers.AppointmentSerializer) -> Appointment:
    diagnosis = await Diagnosis.objects.get_or_none(
        id=data.diagnosis_id,
    )

    patient = await Patient.objects.get(
        id=data.patient_id,
    )

    if not diagnosis:
        raise Exception('Запрашиваемый Вами диагноз не найден.')

    if not patient:
        raise Exception('Запрашиваемый Вами пациент не найден.')

    appointment = await Appointment.objects.create(
        diagnosis=diagnosis,
        patient=patient,
        date_to_come=data.date_to_come,
        status=AppointmentStatuses.IN_QUEUE,
    )

    return appointment


async def get_patient_active_appointments(patient: models.Patient) -> list[Appointment]:
    return await Appointment.objects.select_related(['diagnosis', 'patient']).filter(
        patient__id=patient.id,
        status__in=[
            AppointmentStatuses.IN_QUEUE,
            AppointmentStatuses.RECREATED,
        ]
    ).all()


async def get_all_appointments() -> list[Appointment]:
    return await Appointment.objects.select_related(['diagnosis', 'patient']).all()


async def get_active_appointments() -> list[Appointment]:
    return await Appointment.objects.select_related(['diagnosis', 'patient']).filter(
        status__in=[
            AppointmentStatuses.IN_QUEUE,
        ]
    ).all()


async def recreate_appointment(appointment: Appointment, date_to_come: datetime.datetime) -> Appointment:
    await appointment.update(
        status=AppointmentStatuses.RECREATED,
    )

    new_appointment = await Appointment.objects.create(
        patient=appointment.patient,
        date_to_come=date_to_come,
        diagnosis=appointment.diagnosis,
        status=AppointmentStatuses.IN_QUEUE,
    )

    return new_appointment


async def update_appointment_status(appointment: Appointment, status: AppointmentStatuses) -> Appointment:
    if appointment.status in [
        AppointmentStatuses.RECREATED,
        AppointmentStatuses.CANCELED,
        AppointmentStatuses.COMPLETED,
        AppointmentStatuses.NOT_CAME,
    ]:
        raise Exception(
            'Прием уже был закрыт/отменен/завершен, и редактировать его данные уже нельзя.'
        )

    await appointment.update(
        status=status
    )

    return appointment


async def get_inactive_appointments():
    return await Appointment.objects.filter(
        status__in=[
            AppointmentStatuses.CANCELED,
            AppointmentStatuses.NOT_CAME,
            AppointmentStatuses.COMPLETED,
            AppointmentStatuses.RECREATED,
        ]
    ).all()

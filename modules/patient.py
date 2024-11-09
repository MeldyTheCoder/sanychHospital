from datetime import datetime, date

import models
import serializers
import settings
from models import Patient, Passport, MedCard, Insurance


async def create_patient(patient_data: serializers.PatientFormSerializer | dict) -> Patient:
    """
    Метод для создания пациента в системе со всеми привязанными документами.
    :param patient_data: Данные пациента
    :return: сущность пациента
    """

    patient = await Patient.objects.get_or_none(
        first_name=patient_data.first_name,
        last_name=patient_data.last_name,
        surname=patient_data.surname,
        passport__serial=patient_data.passport.serial,
        passport__number=patient_data.passport.number,
    )

    if patient:
        raise Exception(
            'Пациент с такими данными уже существует.'
        )

    passport = await Passport.objects.create(
        serial=patient_data.passport.serial,
        number=patient_data.passport.number,
        issued_date=patient_data.passport.issued_date,
        date_of_birth=patient_data.passport.date_of_birth,
        gender=patient_data.passport.gender,
        issued_by=patient_data.passport.issued_by,
        address=patient_data.passport.address,
    )

    insurance, is_created = await Insurance.objects.get_or_create(
        number=patient_data.insurance.number,
        _defaults={
            'date_of_issue': patient_data.insurance.date_of_issue,
            'date_expires': patient_data.insurance.date_expires,
        }
    )

    if not is_created:
        raise Exception(
            "Пациент с таким страховым полисом уже сущесвует в базе."
        )

    elif insurance.date_expires < date.today():
        raise Exception(
            "Страховой полис клиента уже просрочен."
        )

    med_card = await MedCard.objects.create(
        date_of_issue=date.today()
    )

    patient = await Patient.objects.create(
        first_name=patient_data.first_name,
        last_name=patient_data.last_name,
        surname=patient_data.surname,
        phone_number=patient_data.phone_number,
        email=patient_data.email,
        insurance=insurance,
        passport=passport,
        med_card=med_card,
        photo_url='',
    )

    return patient


async def update_patient_bio(patient: models.Patient, data: serializers.PatientFormSerializer) -> Patient:
    patient_data_decoded = data.model_dump(
        exclude={
            'med_card__id',
            'med_card__date_of_issue'
            'passport__id',
            'insurance__id',
        },
        exclude_none=True,
        exclude_unset=True,
        exclude_defaults=True,
    )

    await patient.update(
        **patient_data_decoded
    )

    return patient


async def remove_patient(patient: models.Patient) -> bool:
    await patient.delete()
    return True


async def get_patients() -> list[Patient]:
    return await models.Patient.objects.select_related([
        'passport',
        'med_card',
        'insurance',
    ]).all()



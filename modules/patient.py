import models
import serializers
from models import Patient, Passport, MedCard, Insurance


async def create_patient(patient_data: serializers.PatientFormSerializer) -> Patient:
    """
    Метод для создания пациента в системе со всеми привязанными документами.
    :param patient_data: Данные пациента
    :return: сущность пациента
    """

    patient_data_decoded = patient_data.model_dump(
        exclude={
            'med_card',
            'passport',
            'insurance',
        }
    )

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
        **patient_data.passport.model_dump(),
    )

    insurance = await Insurance.objects.create(
        **patient_data.insurance.model_dump(),
    )

    med_card = await MedCard.objects.create()

    patient = await Patient.objects.create(
        **patient_data_decoded,
        insurance=insurance,
        passport=passport,
        med_card=med_card,
    )

    return patient


async def update_patient_bio(patient: models.Patient, data: serializers.PatientFormSerializer) -> Patient:
    patient_data_decoded = data.model_dump(
        exclude={
            'med_card__number',
            'med_card__id',
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



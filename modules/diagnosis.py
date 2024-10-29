from models import Diagnosis, Appointment


async def get_diagnoses() -> list[Diagnosis]:
    diagnoses = await Diagnosis.objects.all()
    # for diagnosis in diagnoses:
    #     setattr(diagnosis, 'appointments_count', await Appointment.objects.filter(diagnosis__id=diagnosis.id).count())
    return diagnoses


async def create_diagnosis(name: str) -> Diagnosis:
    diagnosis, is_created = await Diagnosis.objects.get_or_create(
        name=name
    )

    if not is_created:
        raise Exception("Данный диагноз уже существует в базе.")

    return diagnosis


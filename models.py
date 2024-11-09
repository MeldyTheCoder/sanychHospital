import enum
from datetime import datetime, date
import ormar
import sqlalchemy
import databases

import settings

engine = sqlalchemy.create_engine(settings.DATABASE_URL)
database = databases.Database(settings.DATABASE_URL)
metadata = sqlalchemy.MetaData(bind=engine)

ormar_config = ormar.OrmarConfig(
    metadata=metadata,
    database=database,
)

CYRILLIC_NAME_REGEX = '^[\p{InCyrillic}\s]+$'


def get_current_date() -> datetime:
    return datetime.now(tz=settings.TIMEZONE).now()


class Gender(enum.Enum):
    """
    Enum для перечисления и валидации пола.
    """

    MALE = 'male'
    FEMALE = 'female'


class AppointmentStatuses(enum.Enum):
    """
    Enum для перечисления и валидации статуса приема
    """

    IN_QUEUE = 1
    COMPLETED = 2
    CANCELED = 3
    NOT_CAME = 4
    RECREATED = 5


class User(ormar.Model):
    """
    Сущность пользователя в БД
    """

    ormar_config = ormar_config.copy(
        tablename='users'
    )

    id = ormar.Integer(
        autoincrement=True,
        primary_key=True,
        minimum=1,
    )

    username = ormar.String(
        unique=True,
        regex=r'^[\w.-]+$',
        max_length=12,
        nullable=False,
    )

    first_name = ormar.String(
        unique=False,
        min_length=2,
        max_length=12,
        nullable=False,
        regex=CYRILLIC_NAME_REGEX,
    )

    last_name = ormar.String(
        unique=False,
        min_length=2,
        max_length=12,
        regex=CYRILLIC_NAME_REGEX,
    )

    password = ormar.Text(
        encrypt_backend=ormar.EncryptBackends.HASH,
        encrypt_secret=settings.SECRET_KEY,
        nullable=False,
    )


class Passport(ormar.Model):
    """
    Сущность паспорта пациента
    """

    ormar_config = ormar_config.copy(
        tablename='passports',
    )

    id = ormar.Integer(
        primary_key=True,
        autoincrement=True,
        minimum=1,
    )

    serial = ormar.Integer(
        nullable=False,
        maximum=9999,
        minimum=1000,
    )

    number = ormar.Integer(
        nullable=False,
        maximum=999999,
        minimum=100000,
    )

    issued_by = ormar.String(
        max_length=50,
        nullable=False,
    )

    issued_date = ormar.Date(
        nullable=False,
    )

    date_of_birth = ormar.Date(
        nullable=False,
    )

    gender = ormar.Enum(
        enum_class=Gender,
        default=Gender.MALE,
        nullable=False,
    )

    address = ormar.Text(
        nullable=False,
    )


class MedCard(ormar.Model):
    """
    Сущность медицинской карты пациента
    """

    ormar_config = ormar_config.copy(
        tablename='medcards',
    )

    id = ormar.Integer(
        primary_key=True,
        autoincrement=True,
        nullable=False,
        minimum=1,
    )

    date_of_issue = ormar.Date(
        nullable=False,
        default=date.today(),
    )


class Insurance(ormar.Model):
    """
    Сущность страхового полиса пациента
    """

    ormar_config = ormar_config.copy(
        tablename='insurances',
    )

    id = ormar.Integer(
        primary_key=True,
        autoincrement=True,
        nullable=False,
        minimum=1,
    )

    number = ormar.Integer(
        unique=True,
        nullable=False,
    )

    date_of_issue = ormar.Date(
        nullable=False,
    )

    date_expires = ormar.Date(
        nullable=False,
    )


class Patient(ormar.Model):
    """
    Сущность пациента в БД
    """

    ormar_config = ormar_config.copy(
        tablename='patients',
    )

    id = ormar.Integer(
        primary_key=True,
        autoincrement=True,
        nullable=False,
        minimum=1,
    )

    photo_url = ormar.Text(
        nullable=True,
    )

    first_name = ormar.String(
        max_length=12,
        min_length=2,
        nullable=False,
        regex=CYRILLIC_NAME_REGEX,
    )

    last_name = ormar.String(
        max_length=12,
        min_length=2,
        nullable=False,
        regex=CYRILLIC_NAME_REGEX,
    )

    surname = ormar.String(
        max_length=12,
        nullable=True,
        regex=CYRILLIC_NAME_REGEX,
    )

    passport = ormar.ForeignKey(
        to=Passport,
        on_delete=ormar.ReferentialAction.CASCADE,
        on_update=ormar.ReferentialAction.CASCADE,
        nullable=False,
    )

    med_card = ormar.ForeignKey(
        to=MedCard,
        nullable=False,
        on_delete=ormar.ReferentialAction.CASCADE,
        on_update=ormar.ReferentialAction.CASCADE,
    )

    insurance = ormar.ForeignKey(
        to=Insurance,
        nullable=False,
        on_delete=ormar.ReferentialAction.CASCADE,
        on_update=ormar.ReferentialAction.CASCADE,
    )

    phone_number = ormar.Text(
        nullable=False,
    )

    email = ormar.String(
        nullable=False,
        regex=r"^\S+@\S+\.\S+$",
        unique=True,
        max_length=50,
    )


class Diagnosis(ormar.Model):
    """
    Сущность диагноза пациента
    """

    ormar_config = ormar_config.copy(
        tablename='diagnosis',
    )

    id = ormar.Integer(
        primary_key=True,
        autoincrement=True,
        nullable=False,
        minimum=1,
    )

    name = ormar.String(
        max_length=50,
        nullable=False,
        unique=True,
    )


class Appointment(ormar.Model):
    """
    Сущность пациента в БД
    """

    ormar_config = ormar_config.copy(
        tablename='appointments',
    )

    id = ormar.Integer(
        primary_key=True,
        autoincrement=True,
        nullable=False,
        minimum=1,
    )

    diagnosis = ormar.ForeignKey(
        to=Diagnosis,
        on_delete=ormar.ReferentialAction.CASCADE,
        on_update=ormar.ReferentialAction.CASCADE,
    )

    date_created = ormar.DateTime(
        default=get_current_date,
        nullable=False,
        timezone=True,
    )

    date_to_come = ormar.DateTime(
        nullable=False,
        timezone=True,
    )

    patient = ormar.ForeignKey(
        to=Patient,
        on_delete=ormar.ReferentialAction.CASCADE,
        on_update=ormar.ReferentialAction.CASCADE,
        nullable=False,
    )

    status = ormar.Enum(
        enum_class=AppointmentStatuses,
        default=AppointmentStatuses.IN_QUEUE,
    )


async def run_database():
    await database.connect()

metadata.create_all(bind=engine)
settings.LOOP.run_until_complete(run_database())

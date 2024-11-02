import datetime
import string

import pydantic

import models


class Base(pydantic.BaseModel):
    """
    Базовая модель pydantic
    """


class PassportFormSerializer(Base):
    serial: int = pydantic.Field(
        title="Серия паспорта"
    )
    number: int = pydantic.Field(
        title="Номер паспорта"
    )
    issued_by: str = pydantic.Field(
        title="Кем выдан"
    )
    issued_date: datetime.datetime = pydantic.Field(
        title="Дата выдачи"
    )
    date_of_birth: datetime.datetime = pydantic.Field(
        title="Дата рождения"
    )
    gender: bool = pydantic.Field(
        title="Пол"
    )
    address: str = pydantic.Field(
        title="Адрес проживания"
    )

class InsurancePolicyFormSerializer(Base):
    number: int = pydantic.Field(
        title="Номер страхового полиса"
    )

MedCardSerializer = models.MedCard.get_pydantic(
    exclude={
        'id'
    }
)


class PatientFormSerializer(Base):
    first_name: str = pydantic.Field(
        title='Имя',
    )
    last_name: str = pydantic.Field(
        title="Фамилия",
    )
    surname: str = pydantic.Field(
        title="Отчество",
    )
    phone_number: str = pydantic.Field(
        title="Номер телефона",
    )
    email: str = pydantic.Field(
        title="Эл. почта"
    )
    passport: PassportFormSerializer = pydantic.Field(
        title="Паспорт"
    )
    insurance: InsurancePolicyFormSerializer = pydantic.Field(
        title="Страховой полис"
    )


class DiagnosisSerializer(Base):
    name: str = pydantic.Field(
        title="Название диагноза",
    )


class AppointmentSerializer(Base):
    """
    Модель валидации приема
    """

    diagnosis_id: int
    date_to_come: datetime.datetime
    patient_id: int


class AppointmentFormSerializer(Base):
    """
    Модель создания приема
    """

    diagnosis: int = pydantic.Field(
        title="Диагноз",
    )
    date_to_come: datetime.datetime = pydantic.Field(
        title="Дата посещения"
    )
    patient: int = pydantic.Field(
        title="Пациент"
    )


class UserLoginModel(Base):
    username: str = pydantic.Field(
        title='Имя пользователя',
        pattern=r'^[\w.-]+$',
        min_length=1,
    )

    password: str = pydantic.Field(
        title='Пароль',
        min_length=1,
    )


class UserRegistrationModel(Base):
    username: str = pydantic.Field(
        title='Имя пользователя',
        pattern=r'^[\w.-]+$',
    )

    password: str = pydantic.Field(
        title='Пароль',
    )

    first_name: str = pydantic.Field(
        title='Имя',
    )

    last_name: str = pydantic.Field(
        title='Фамилия',
    )

    @pydantic.field_validator('password')
    def validate_password(cls, value: str):
        if not len(value) >= 8:
            raise ValueError(
                'Длина пароля должна составлять минимум 8 символов',
            )

        password_set = set(value)

        if not password_set & set(string.digits):
            raise ValueError(
                'Пароль должен содержать цифры.'
            )

        return value


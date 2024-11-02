import asyncio
from datetime import timedelta, timezone


# Путь подключения СУБД
DATABASE_URL = 'mysql://root:1234@127.0.0.1:3306/exam'

# Приватный ключ проекта для шифрования данных
SECRET_KEY = "3c6fa465-8f4e-4308-9f4c-8d5ddf9c95dc"

# Часовой пояс проекта
TIMEZONE = timezone(offset=timedelta(hours=3), name='МСК')


# Жизненный цикл проекта
LOOP = asyncio.get_event_loop()

<h3>Задание на должность Python junior разработчика (проект
DATAPK)</h3>



Необходимо разработать back-end, реализующий следующее REST API:

<b>GET /convert?from=RUR&to=USD&amount=42</b>

Перевести amount из валюты from в валюту to
Ответ в Json

<b>POST /database?merge=1</b>

Установить данные по валютам

Если merge == 0, то старые данные инвалидируются

Если merge == 1, то новые данные перетирают старые, но старые все еще акутальны, если не
перетерты

Ответ в Json

<b>Оформление решения:</b>

• Решение необходимо предоставить в виде git репозитория.

• Язык реализации Python 3.7 или выше.

• Фреймворк для реализации - aiohttp 3.6.0 и выше.

• Хранилище данных - Redis.

• Использование дополнительных библиотек на усмотрение разработчика.

• Реализация неописанных явно форматов и протоколов на усмотрение разработчика.

• Плюсом будет наличие тестов и запуск через docker-compose.

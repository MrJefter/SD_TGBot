# SD_TGBot
Simple telegram bot for Stable Diffusion v1

# Requirements
Для запуска вам понадобится установить библиотеки python-telegram-bot версии 13.0 и requests.

```bash
pip install python-telegram-bot==13.0
pip install requests
```

Перед первым запуском скрипта вам необходимо указать токен вашего Telegram бота в файле configurator.py
(опционально - можете заменить apiIP с "localhost" на необходимый в случае запуска бота не на одной и той же машине с SD).

```python
apiIP = "ваш_IP/localhost"

bot_token = "ваш_токен"
```

Так же перед запуском скрипта убедитесь в наличии logs/ в папке со скриптом, иначе он выдаст exception.

# Run
Запуск выполняется стандартным путем

```bash
python TGBot.py
```

Поздравляю, вы великолепны.

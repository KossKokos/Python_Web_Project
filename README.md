
Instagram Killer
================

---

## Requirements:
  * python==3.10
  * alembic==1.10.2
  * babel==2.13.0
  * bcrypt==4.0.1
  * cloudinary==1.32.0
  * colorama==0.4.6
  * cryptography==41.0.5
  * docutils==0.19
  * fastapi==0.95.0
  * email-validator==1.3.1
  * fastapi-limiter==0.1.5
  * fastapi-mail==1.2.7
  * httpx==0.25.2
  * jinja2==3.1.2
  * passlib==1.7.4
  * psycopg2==2.9.5
  * pydantic==1.10.7
  * pytest==7.4.3
  * pytest-mock==3.12.0
  * python-dotenv==1.0.0
  * python-jose==3.3.0
  * python-multipart==0.0.6
  * redis==4.5.4
  * requests==2.31.0
  * sniffio==1.3.0
  * sphinx==6.1.3
  * sqlalchemy==2.0.7
  * starlette==0.26.1
  * urllib3==1.26.18
  * uvicorn==0.21.1
  * pytest-asyncio==0.23.2
  * pytest-trio==0.8.0
  * qrcode["pil"]==7.4.2

---

## Command to run API: 
  * uvicorn main:app --host localhost --port 8000 --reload
  * py main.py (You must be in the Instagram_killer directory in the console)

  
3) В папці src знаходиться вся робоча система:
  -  У src\database знаходиться файл db.py, де підключено базу даних Postgresql, Щоб під'єднати власну db, потрібно ввести дані з вашої db у файл .env, що знаходиться у головній директорії проекту. 
  -  У src\models знаходяться моделі таблиць, які ви створюєте і мігруєте їх в базу даних, тільки в цьому файлі.
  -  У src\repository знаходяться crud фунції, кожен файл відповідальних за операції над певним об'єктом, наприклад в users.py тільки crud функції для юзерів і т.д. Нові crud операцї для нового об'єкта - новий файл.
  -  У src\routes знаходяться файли для створення шляхів, наприклад в auth.py будуть api/auth/login, api/auth/signup, api/auth/request_email і так далі, в users.py будуть шляхи які починаються з api/users/ і так для кожних нових шляхів - новий файл.
  -  у src\schemas знаходяться файли в яких моделі для видачі інформації, прийому від користувачів. Ви можете добавляти скільки завгодно моделів та файлів. 
  -  У src\services знаходяться файли: auth.py та email.py, в яких знаходяться класи для виконання операцій по аутентифікації, авторизації і надсилання емейл для підтвердження користувача або скидання паролю. Ви можете добаляти нові сервери, наприклад для роботи з cloudinaryю
  -  У src\templates знахоться темплейти для надсилання емейлів про підтвердження та зміни паролю. 
4) Файл .example.env є прикладом, які дані потрібно записувати. Для того, щоб запустити API, потрібно перейменувати його в .env та ввести свої дані.

5) Файл docker-compose потрібен для запуску відразу двох баз даних: postgres та redis. Це полегшує роботу та збільшує продуктивність. Щоб запустити його, введіть в консолі команду "docker-compose up" або "docker-compose up -d", для того, щоб не бачити логування. Щоб зупинити, введіть в консолі команду "docker-compose down".

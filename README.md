# CodeMaster - Платформа для изучения программирования

Добро пожаловать в **CodeMaster**! Это современная платформа для продажи и изучения курсов по программированию, созданная для тех, кто хочет освоить разработку с нуля до профессионального уровня. На сайте вы найдете интерактивные курсы, личные кабинеты пользователей, удобное форматирование статей в админке и интеграцию с платежной системой YooKassa для покупки курсов.

## О проекте

CodeMaster — это веб-приложение для обучения программированию. Пользователи могут просматривать курсы, читать статьи с поддержкой Markdown-подобного форматирования, управлять своим профилем и оплачивать курсы через YooKassa. Администраторы имеют доступ к удобной панели управления для создания и форматирования контента.

## Технологический стек

- **Django**: Основной фреймворк для серверной логики и управления контентом.
- **HTMX**: Для динамического обновления страниц без перезагрузки.
- **Alpine.js**: Легковесный JavaScript для интерактивности на фронтенде.
- **Tailwind CSS**: Для современного и отзывчивого дизайна.
- **PostgreSQL**: Надежная база данных для хранения данных пользователей и курсов.
- **Docker**: Для контейнеризации и упрощения деплоя.

## Локальный запуск проекта

Следуйте этим шагам, чтобы запустить проект на своей машине:

1. **Клонируйте репозиторий**:

   ```bash
   git clone https://github.com/yourusername/codemaster.git
   cd codemaster
   ```

2. **Создайте и активируйте виртуальное окружение**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. **Установите зависимости**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Настройте базу данных в PostgreSQL**:

   - Убедитесь, что PostgreSQL установлен и запущен.
   - Создайте базу данных через pgAdmin или командную строку:

     ```sql
     CREATE DATABASE codemaster;
     ```
   - Создайте файл `.env` в корне проекта и добавьте следующие переменные:

     ```env
     SECRET_KEY=your_django_secret_key
     POSTGRES_DB=codemaster
     POSTGRES_USER=your_postgres_user
     POSTGRES_PASSWORD=your_postgres_password
     POSTGRES_HOST=localhost
     POSTGRES_PORT=5432
     YOOKASSA_SHOP_ID=your_yookassa_shop_id
     YOOKASSA_SECRET_KEY=your_yookassa_secret_key
     ```

     Замените значения на свои. Для генерации `SECRET_KEY` можно использовать онлайн-генераторы или команду Django.

5. **Выполните миграции**:

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Запустите сервер**:

   ```bash
   python manage.py runserver
   ```

   Проект будет доступен по адресу `http://localhost:8000`.

## Деплой с Docker

Проект включает Docker-контейнер для удобного деплоя на сервер. Перед деплоем замените `domen.com` и `www.domen.com` в файле `settings.py` на ваш домен, получите сертификаты в Let’s Encrypt. Затем выполните:

```bash
docker-compose up --build
```

Теперь ваш CodeMaster готов к работе! 🚀
# API для проекта YaMDB в контейнере Docker
[![API for YaMDB project workflow](https://github.com/maridana/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)](https://github.com/maridana/yamdb_final/actions/workflows/yamdb_workflow.yml)

## Описание
### Возможности проекта
Представляет собой расширение возможностей проекта YaMDB для совершения удаленных операций.   
Благодаря этому проекту зарегистрированные и аутентифицированные пользователи получают 
возможность оставлять рецензии на произведения различных категорий, 
комментировать рецензии других пользователей,просматривать сформированные на основе оценок рейтинги произведений. 
Сайт не предоставляет прямой доступ или ссылки для ознакомления непосредственно с произведениями.
### Расширение функциональности
Функционал проекта адаптирован для использования PostgreSQL и развертывания в контейнерах Docker. Используются инструменты CI и CD.

## Установка
### Шаблон описания файла .env
 - DB_ENGINE=django.db.backends.postgresql
 - DB_NAME=postgres
 - POSTGRES_USER=postgres
 - POSTGRES_PASSWORD=postgres
 - DB_HOST=db
 - DB_PORT=5432
 - SECRET_KEY=<секретный ключ проекта django>
### Инструкции для развертывания и запуска приложения
для Linux-систем все команды необходимо выполнять от имени администратора
- Склонировать репозиторий
```bash
git clone https://github.com/maridana/yamdb_final.git
```
- Выполнить вход на удаленный сервер
- Установить docker на сервер:
```bash
apt install docker.io 
```
- Установить docker-compose на сервер:
```bash
apt install docker-compose
```

- Скопировать файлы docker-compose.yml и default.conf на сервер:
```bash
scp docker-compose.yml <username>@<host>:/home/<username>/docker-compose.yml
scp default.conf <username>@<host>:/home/<username>/default.conf
```
- Создать .env файл по предлагаемому выше шаблону.
- Для работы с Workflow добавить в Secrets GitHub переменные окружения для работы:
    ```
    DB_ENGINE=<django.db.backends.postgresql>
    DB_NAME=<имя базы данных postgres>
    DB_USER=<пользователь бд>
    DB_PASSWORD=<пароль>
    DB_HOST=<db>
    DB_PORT=<5432>
    
    DOCKER_PASSWORD=<пароль от DockerHub>
    DOCKER_USERNAME=<имя пользователя>
    
    SECRET_KEY=<секретный ключ проекта django>

    USER=<username для подключения к серверу>
    HOST=<IP сервера>
    PASSPHRASE=<пароль для сервера, если он установлен>
    SSH_KEY=<ваш SSH ключ (для получения команда: cat ~/.ssh/id_rsa)>

    TELEGRAM_TO=<ID чата, в который придет сообщение>
    TELEGRAM_TOKEN=<токен вашего бота>
    ```
    Workflow состоит из четырёх шагов:
     - Проверка кода на соответствие PEP8.
     - Сборка и публикация образа бекенда на DockerHub.
     - Автоматический деплой на удаленный сервер.
     - Отправка уведомления в телеграм-чат.
- собрать и запустить контейнеры на сервере:
```bash
docker-compose up -d --build
```
- После успешной сборки выполнить следующие действия (только при первом деплое):
    * провести миграции внутри контейнеров:
    ```bash
    docker-compose exec web python manage.py migrate
    ```
    * собрать статику проекта:
    ```bash
    docker-compose exec web python manage.py collectstatic --no-input
    ```  
    * Создать суперпользователя Django, после запроса от терминала ввести логин и пароль для суперпользователя:
    ```bash
    docker-compose exec web python manage.py createsuperuser
    ```

### Команды для заполнения базы данными
- Заполнить базу данными
- Создать резервную копию данных:
```bash
docker-compose exec web python manage.py dumpdata > fixtures.json
```
- Остановить и удалить неиспользуемые элементы инфраструктуры Docker:
```bash
docker-compose down -v --remove-orphans
```

## Авторы
- Личинин Виталий
- Горовенко Валентин
- Данилова Марина

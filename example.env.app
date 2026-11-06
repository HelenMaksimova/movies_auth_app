APP_HOST=0.0.0.0
APP_PORT=8030
APP_PROJECT_NAME="Сервис аутентификации и авторизации пользователей"
APP_DESCRIPTION="Сервис аутентификации и авторизации пользователей"
APP_LOG_LEVEL=debug
APP_ENTRYPOINT=main:app

REDIS__HOST=redis
REDIS__PORT=6379
REDIS__DB=1
REDIS__PASSWORD=redispass

DB__DATABASE=auth_service
DB__HOST=postgres
DB__PORT=5432
DB__USERNAME=auth_app
DB__PASSWORD=123qwe
DB__CONTENT_SCHEMA=auth_data

FERNET_MASTER_KEY=BDksEeMPoutwAitOtpVVJW_aMqVXTAD86faQdJp9CgQ=
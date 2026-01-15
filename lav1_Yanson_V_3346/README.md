# Lab1 News API

FastAPI приложение для новостного портала.

## API Endpoints

## Autori

- `POST	/auth/register`	- Регистрация нового пользователя	
- `POST	/auth/login`	- Вход в систему	
- `POST	/auth/refresh`	- Обновление токенов	
- `POST	/auth/logout`	- Выход из системы	
- `POST	/auth/logout-all`	- Выход со всех устройств	
- `GET	/auth/sessions`	- Мои активные сессии	
- `GET	/auth/github/login`	- OAuth через GitHub	
- `GET	/auth/github/callback`	- Callback для GitHub OAuth	
- `GET	/users/me`	- С токеном + получаем данные для пользователя	

### Users
- `POST /users/` - создать пользователя
- `GET /users/` - список пользователей  
- `GET /users/{user_id}` - получить пользователя

### News
- `POST /news/` - создать новость (только авторы)
- `GET /news/{news_id}` - получить новость
- `PATCH /news/{news_id}` - обновить новость
- `DELETE /news/{news_id}` - удалить новость

### Comments
- `POST /comments/` - создать комментарий
- `PATCH /comments/{comment_id}` - обновить комментарий
- `DELETE /comments/{comment_id}` - удалить комментарий

## Запуск проекта

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload

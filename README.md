# Book App API

A Django-based RESTful API for managing a book catalog, featuring user authentication, book management, and interactive API documentation via Swagger.

## Features

- **User Authentication**: Secure registration and login functionalities.
- **Book Management**: Create, read, update, and delete book entries.
- **Interactive Documentation**: Explore and test API endpoints through Swagger UI.
- **Modular Architecture**: Clean separation of concerns with apps like `user`, `book`, and `catalog`.

## Tech Stack

- **Backend Framework**: Django
- **API Development**: Django REST Framework
- **Documentation**: drf-yasg (Swagger/OpenAPI)
- **Database**: PostgresSql
- **Deployment**: NGINX, Gunicorn, Certbot for HTTPS

## API Documentation
Swagger UI is available at: https://www.developpex.com/api/docs/

## Authentication & Token Usage

This API uses **Token Authentication**.

### Get Your Token

1. **Register a New User**  
   Send a `POST` request to:
   /api/user/create/


2. **Obtain a Token**  
After registering, obtain your token with a `POST` request to:
/api/user/token/

Provide your `username` and `password` in the request body. You’ll receive a token like this:

```json
{
  "token": "abcd1234efgh5678..."
}
```

## Authenticate in Swagger UI
You can authorize your requests directly in the Swagger interface:

1. **Click the Authorize button (top right)**  

2. **For tokenAuth (apiKey) enter your token as:**  
  ```
   Token your_token_here
  ```
4. **Click Authorize and then Close**  
  your token will now be used for all protected endpoints.

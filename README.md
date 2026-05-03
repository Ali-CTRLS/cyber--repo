# Secure File Sharing Platform

A Java 21 Spring Boot demo for secure file upload, download, and token-based sharing.

## Features

- User registration and JWT authentication
- Secure file upload/download per user
- Token-based share links with expiration
- H2 in-memory persistence for users, metadata, and share tokens
- File storage on disk under `storage/`

## Run

1. Build the project:
   ```bash
   mvn clean package
   ```
2. Start the application:
   ```bash
   mvn spring-boot:run
   ```
3. Access the API at `http://localhost:8080`

## API Endpoints

### Auth
- `POST /api/auth/register` - register a user
- `POST /api/auth/login` - login and receive JWT token

### Files
- `POST /api/files/upload` - upload a file (multipart/form-data, header `Authorization: Bearer <token>`)
- `GET /api/files` - list user's files
- `GET /api/files/{id}/download` - download a file owned by the user
- `DELETE /api/files/{id}` - delete owned file
- `POST /api/files/share` - create a share link
- `GET /share/{token}` - download a shared file via token

## Notes

- Update `security.jwt.secret` in `src/main/resources/application.properties` to a secure base64 key for production.
- The application uses H2 in-memory database by default.

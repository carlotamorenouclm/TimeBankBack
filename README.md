# TimeBankBack

Backend of the **TimeBank** web application developed for the Web Systems Development laboratory assignment.

TimeBank is a peer-to-peer service exchange platform where users offer and request services using a virtual currency called **time credits** or **coins**.

## Repository

- Backend: [https://github.com/carlotamorenouclm/TimeBankBack](https://github.com/carlotamorenouclm/TimeBankBack)
- Frontend: [https://github.com/carlotamorenouclm/TimeBankFront](https://github.com/carlotamorenouclm/TimeBankFront)

## Main Features

- User registration and login.
- JWT-based authentication.
- User and administrator roles.
- Administrator panel support for listing users/admins and changing roles.
- Authenticated user profile management.
- Service catalog.
- Service publication and deletion.
- Service request flow.
- Inbox for accepting or rejecting received requests.
- Wallet balance and wallet recharges.
- Transaction history for purchases and sales.

## Tech Stack

- Python
- FastAPI
- SQLAlchemy
- Pydantic
- MySQL
- PyMySQL
- Passlib bcrypt
- Python JOSE for JWT tokens
- Uvicorn

## Project Structure

```text
app/
  api/routes/       HTTP route definitions
  core/             Authentication, security, and configuration
  db/               Database session, initialization, and queries
  models/           SQLAlchemy ORM models
  schemas/          Pydantic DTOs and validation schemas
  services/         Business logic used by routes
  main.py           FastAPI app entry point
```

## Environment Variables

Create a `.env` file in the `TimeBankBack` directory:

```env
DB_HOST=localhost
DB_PORT=3306
DB_NAME=timebank
DB_USER=<database-user>
DB_PASSWORD=<database-password>
SECRET_KEY=<secret-key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows, activate the virtual environment with:

```bash
.venv\Scripts\activate
```

## Run the API

```bash
uvicorn app.main:app --reload
```

The API will usually be available at:

```text
http://localhost:8000
```

The interactive FastAPI documentation is available at:

```text
http://localhost:8000/docs
```

## CORS

The backend currently allows requests from the Vite frontend running on:

- `http://localhost:5173`
- `http://127.0.0.1:5173`
- `http://localhost:5174`
- `http://127.0.0.1:5174`

## API Summary

### Health

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| GET | `/health` | No | Checks that the backend is running. |

### Authentication

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| POST | `/auth/token` | No | Logs in and returns a JWT access token. |

### Users

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| POST | `/users/signup` | No | Creates a new user account. |
| GET | `/users` | Admin | Lists all users. |
| GET | `/users/{user_id}` | Admin | Gets a user by id. |
| POST | `/users/update/{user_id}` | Admin | Updates a user's profile data. |
| DELETE | `/users/delete/{user_id}` | Admin | Deletes a user. |

### Current User

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| GET | `/me` | User | Returns the authenticated user's profile. |
| POST | `/me/update` | User | Updates the authenticated user's profile. |
| DELETE | `/me/delete` | User | Deletes the authenticated user's own account. |
| POST | `/me/isAdmin` | User | Checks whether the authenticated user is an admin. |

### Admins

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| GET | `/admins` | Admin | Lists administrator accounts. |
| POST | `/admins/updateRole/{user_id}` | Admin | Changes a user's role to `USER` or `ADMIN`. |

### Portal

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| GET | `/portal/summary` | User | Returns user summary data for the portal sidebar. |
| GET | `/portal/dashboard` | User | Returns available services and own services. |
| GET | `/portal/history` | User | Returns purchase and sale history. |
| GET | `/portal/inbox` | User | Returns received service requests. |
| POST | `/portal/inbox/{request_id}/accept` | User | Accepts a received service request. |
| POST | `/portal/inbox/{request_id}/reject` | User | Rejects a received service request. |
| GET | `/portal/wallet` | User | Returns wallet balance, status, and recharges. |
| POST | `/portal/wallet/recharge` | User | Recharges the wallet. |
| POST | `/portal/services/{service_offer_id}/request` | User | Requests a service and deducts the payment. |
| POST | `/portal/services` | User | Publishes a new service offer. |
| DELETE | `/portal/services/{service_offer_id}` | User | Deletes one of the authenticated user's services. |

## Authentication

Protected endpoints require this header:

```http
Authorization: Bearer <access_token>
```

The token is obtained from `/auth/token` using `application/x-www-form-urlencoded` credentials:

```text
username=<email>
password=<password>
```

## Validation Notes

- Passwords must contain at least 8 characters, one uppercase letter, one lowercase letter, one number, and one special character.
- Name and surname fields accept letters, spaces, accents, and hyphens.
- Wallet recharge amounts must be greater than 0 and at most 1000.
- Service prices must be greater than 0 and at most 1000.
- Non-home services require street and street number.

## Frontend Configuration

The frontend must point to this API by setting `VITE_API_URL` in the frontend `.env` file:

```env
VITE_API_URL=http://localhost:8000
```

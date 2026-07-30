# Journal App API

A Flask REST API for user accounts and personal journal entries. Authentication uses a server-side session; entries are always scoped to the signed-in user.

## Installation

1. Install [Pipenv] and Python 3.12.
2. Install the project dependencies:

   ```bash
   pipenv install
   ```

3. Create the database from the included migration:

   ```bash
   pipenv run flask --app app db upgrade
   ```

4. populate the local database with Faker-generated users and journal entries. This resets existing database data; all seeded users use the password `password123`.

   ```bash
   pipenv run python seed.py
   ```

## Running the API

Start the development server on port 5555:

```bash
pipenv run python app.py
```

Alternatively, run Flask directly:

```bash
pipenv run flask --app app run --port 5555 --debug
```

## API endpoints

All request and response bodies use JSON. Except for sign-up and login, endpoints require the session cookie returned after a successful login.

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/signup` | Creates a user. Send `username` and `password`. |
| `POST` | `/login` | Authenticates a user with `username` and `password`, then starts a session. |
| `GET` | `/checkSession` | Returns the currently signed-in user and their journal entries. |
| `DELETE` | `/logout` | Ends the current user session. |
| `GET` | `/entries` | Returns the signed-in user's entries. Supports optional `page` (default `1`) and `per_page` (default `5`) query parameters. |
| `POST` | `/add_entry` | Creates an entry for the signed-in user. Send `title` and `content`; the user ID is assigned from the session. |
| `PATCH` | `/patch/<id>` | Updates the signed-in user's entry with the supplied numeric ID. Send either `title` or `content` (or both). |
| `DELETE` | `/delete/<id>` | Deletes the signed-in user's entry with the supplied numeric ID. |

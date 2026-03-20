# Flask + MySQL Bookstore Service

This project provides a REST API using Flask and MySQL with Docker support.

## Endpoints

- `GET /status`
- `POST /books`
- `PUT /books/{ISBN}`
- `GET /books/{ISBN}`
- `GET /books/isbn/{ISBN}`
- `POST /customers`
- `GET /customers/{id}`
- `GET /customers?userId={email}`

## Run with Docker

1. Copy `.env.example` to `.env` and update values as needed.
2. Point `MYSQL_HOST` to your external MySQL instance (for example, AWS RDS endpoint).
3. Start the API service:

```bash
docker compose up --build
```

Base URL: `http://localhost:5001`

## Notes

- Book ISBN is the primary key.
- Customer `id` is auto-generated numeric primary key.
- `POST /books` attempts to generate a summary through the Gemini API when `GEMINI_API_KEY` is configured.
- Validation is intentionally limited to assignment requirements only.

## Data setup for local testing

Insert sample rows:

```bash
python -m scripts.seed_data
```

Clear rows before submission:

```bash
python -m scripts.clear_data
```

The service creates the `books` and `customers` tables automatically if they do not exist.

## Quick checks

```bash
curl -i http://localhost:5001/status
```

```bash
curl -i -X POST http://localhost:5001/books \
  -H "Content-Type: application/json" \
  -d '{
    "ISBN": "978-0136886099",
    "title": "Software Architecture in Practice",
    "Author": "Bass, L.",
    "description": "The definitive guide to architecting modern software",
    "genre": "non-fiction",
    "price": 59.95,
    "quantity": 106
  }'
```

```bash
curl -i "http://localhost:5001/customers?userId=starlord2002%40gmail.com"
```

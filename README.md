# Afvalstoffendienst

Small application to scrape the dates of afvalstoffendienstkalender.nl and make it available through a REST API.
The API exposes the **reminder dates** which is the date one day before the pick up date.

## Getting started

Create a file named `.env` containing your information

```
POSTAL_CODE=<Postal code>
NUMBER=<House number>
```

## Running the API

Visit https://python-poetry.org/docs/#installation to install Poetry

Install the requirements:
```
poetry install
```

Run the API:
```
poetry run uvicorn api:app
```

This will fill an SQLite database for your address. The data is exposed through FastAPI on localhost port 8000.

- Docs: `/docs`
- All dates: `/dates`
- Specific date: `/dates/{date}`

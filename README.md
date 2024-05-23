# BTC Price Tracker (POC)

The approach utilizes [yfinance](https://pypi.org/project/yfinance/), an embedded
[SQLite database](https://www.sqlite.org/index.html) managed with [SQLAlchemy](https://www.sqlalchemy.org/),
and is powered by [FastAPI](https://fastapi.tiangolo.com/) to retrieve BTC prices in specified currencies
at configurable time intervals. Daily and monthly averages are calculated based on the retrieved data,
with configurable data retention.

## API Endpoints

Protected API endpoints (accessible with the `--api-key` argument, passed as `api-key` header):

1. `/prices/current`: Retrieves the current prices for specified currencies of a given ticker.
2. `/prices/averages`: Provides the daily and monthly average prices for specified currencies.

Additional endpoints:

1. `/health`: Checks the health status of the API.
2. `/docs`: Accesses the OpenAPI schema, which is customized to include the API key in the security definitions.

## Application structure

```text
app
├── database | SQLAlchemy utilities and models
├── routers  | FastAPI routers (endpoints)
├── schemas  | Pydantic models for documentation
└── services | Background services (yfinance, etc.)
```

### Running the application

The application follows [The Twelve-Factor Methodology](https://12factor.net/). 
Configuration can be provided at startup or through environmental variables (see also the `.env` file).

Example:

```text
❯ pip install -r requirements.txt
❯ python3 app/main.py --help

usage: main.py [-h] [-d DIR] [-n NAME] [--retention-days RETENTION_DAYS] [-t TICKER] [-c CURRENCIES [CURRENCIES ...]]
               [--clean-up-interval-mins CLEAN_UP_INTERVAL_MINS] [--fetch-interval-mins FETCH_INTERVAL_MINS] [--api-key API_KEY] [--debug]
               [--host HOST] [--port PORT]

optional arguments:
  -h, --help            show this help message and exit
  --api-key API_KEY     API key for accessing the service
  --debug               Should we run the script in debug mode?
  --host HOST           Bind socket to this host
  --port PORT           Bind socket to this port

Database arguments:
  -d DIR, --dir DIR     Directory for SqLite database
  -n NAME, --name NAME  Name for SqLite database file
  --retention-days RETENTION_DAYS
                        Database data retention days

Currency parameters:
  -t TICKER, --ticker TICKER
                        Ticker symbol for the cryptocurrency
  -c CURRENCIES [CURRENCIES ...], --currencies CURRENCIES [CURRENCIES ...]
                        List of currencies to store prices for

Service(s) parameters:
  --clean-up-interval-mins CLEAN_UP_INTERVAL_MINS
                        Interval (in minutes) to run DB clean up
  --fetch-interval-mins FETCH_INTERVAL_MINS
                        Interval (in minutes) to retrieve prices

```

### Docker testing

```text

❯ docker build -t price-svc .
❯ docker run -p 8000:8000 --env-file .env price-svc
❯ curl -s -H "api-key: test" -X GET http://localhost:8000/prices/current | jq
{
  "prices": {
    "EUR": {
      "price": 72442.14224577416,
      "currency": "EUR",
      "request_time": "2024-05-23T18:32:22.299216",
      "server_data_time": "2024-05-23T18:32:17"
    },
    "CZK": {
      "price": 2928.2629724391445,
      "currency": "CZK",
      "request_time": "2024-05-23T18:32:22.299216",
      "server_data_time": "2024-05-23T18:32:17"
    }
  }
}

```

### Minikube testing

```text

❯ minikube start
❯ eval $(minikube docker-env)
❯ docker build -t price-svc .

❯ cd deployment/app-chart
❯ helm template . --name-template dummy --values ../values-test.yaml | kubectl apply -f -
❯ kubectl port-forward -n prices-svc service/dummy-app-chart 8000:8000
❯ curl -s -H "api-key: test" -X GET http://localhost:8000/prices/averages | jq
{
  "averages": {
    "EUR": {
      "daily_average": 72474.41419486888,
      "monthly_average": null
    },
    "CZK": {
      "daily_average": 2931.2929522524937,
      "monthly_average": null
    }
  }
}

```

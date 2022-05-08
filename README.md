# Exchange rates data storage using Docker and scheduled API calls with cron

## Description
Learning task: Simple docker app running scheduled script that calls the ExchangeRates API https://exchangeratesapi.io/,
and saves selected exchange rates to csv files. 
* Columns in csv files represent BASE/CURRENCY rates e.g. EUR/USD, EUR/PLN, 
EUR/GBP... 
* Files are backed up from the container cache to local directory every 12 hours using [**restic**](https://restic.net/).
* When the cache is filled up older files are deleted. 

Requirements: docker <br>
For the sake of simplicity the API keys and backup password are hardcoded

## Contents
- backup.sh
- entrypoint.sh
- main.py
- Dockerfile
- requirements.txt
- README.md

## Execution

1) Build the docker image

Parameters: <br>
cache (int): limit of the amount of csv files with ticker data (default: 7)

```
docker build -t mlops-api-cron --build-arg cache=7 <path/to/Dockerfile>
```
Dockerfile includes hardcoded definition of crontab schedule (API call every 3h, backup every 12h)

2) Run the container

Requires the path to local backup directory. Local backup won't be created without it.

```
docker run --name my-api -t -d -v <path/to/local/backup>:/backups mlops-api-cron
```

3) Optional: Manual container configuration check (paths included in `Mounts` section)

```
docker inspect mlops-api-cron
```
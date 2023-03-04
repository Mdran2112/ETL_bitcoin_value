### ETL for analyses of bitcoin price correlation

As mentioned in the article _Is Bitcoin Price Correlated to the Stock Market?_
(https://decrypt.co/63468/is-bitcoin-price-correlated-to-stock-market), there may be some 
correlations between Bitcoin price and stock exchange values. So the idea is to build a system that 
could continuously store the Bitcoin price and the stock market value of technology companies, in order
to allow doing data analyses, searching for correlations or even building a machine learning algorithm 
to predict BTC price.

This project consists in an ETL. The first step, Extract, will obtain the BTC price from the Coinbase API 
and the stock market value of five companies: Tesla, Microsoft, Amazon, AMD and Intel. The source 
for obtaining the stock market values will be Yahoo Finance's API (https://pypi.org/project/yfinance/).
In the Transformation step, some new features will be calculated based on the raw values; these features colud
be, for example, predictors for making a machine learning model. The final step (Load) will consist in inserting 
the new data in a PostgreSQL table. 

For making an automated pipeline, the project uses Apache Airflow for building a scheduled DAG that will be 
triggered automatically once a day. Some filters will be taken into account in order to not store bad data 
(for example btc price on weekend) or duplicated data.

#### Build and deploy
The script `docker_build.sh` will build a docker image with tag `airflow-etl:latest`.

Use the `docker-compose.yml` to deploy the services. The compose will use some environment
variables defined in the .env file.

Enter to airflow server through port 8080 (by default).

#### Connecting to Database

In the Airflow web server, go to Admin -> Connections -> click to `+` button to add a new connection.
In **Connection Type**, select `Postgres`. In **Connection Id** introduce `postgres_localhost`.
Then complete the rest of the fields (**host**, **schema**, **login**, **password**, **port**).

The data will be stored in the table `btc_value` (will be created automatically during the Load task, if it doesn't exist.)

Note: If you want to use the same Postgres service that is used by Airflow server, you have to fill
the fields **schema**, **login** and **password** with the values `POSTGRES_DB`, `POSTGRES_USER` and `POSTGRES_PASSWORD` 
defined in the `.env` file.



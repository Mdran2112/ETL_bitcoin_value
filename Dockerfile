#FROM quay.io/astronomer/astro-runtime:7.3.0
FROM apache/airflow:2.5.0

USER root
RUN apt-get update && apt-get install -y curl && curl -sSL https://get.docker.com/ | sh && apt install -y vim

WORKDIR /opt/airflow

COPY requirements.txt /opt/airflow/requirements.txt

USER airflow
RUN pip install -r requirements.txt

COPY config/airflow.cfg /opt/airflow/airflow.cfg
COPY plugins /opt/airflow/plugins

USER root
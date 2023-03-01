#!/bin/bash

export DOCKER_BUILDKIT=1

docker build --tag=airflow-etl .
docker image prune -f
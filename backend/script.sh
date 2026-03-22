#!/bin/bash

# sudo apt update
# sudo apt install -y postgresql postgresql-contrib
export POSTGRES_PASSWORD=$(cat .env | grep POSTGRES_PASSWORD | cut -d '=' -f2 | tr -d '"' | tr -d "'" | tr -d '\r' | xargs)

export POSTGRES_HOST=$(cat .env | grep POSTGRES_HOST | cut -d '=' -f2 | tr -d '"' | tr -d "'" | tr -d '\r' | xargs)

export POSTGRES_USER=$(cat .env | grep POSTGRES_USER | cut -d '=' -f2 | tr -d '"' | tr -d "'" | tr -d '\r' | xargs)

export POSTGRES_PORT=$(cat .env | grep POSTGRES_PORT | cut -d '=' -f2 | xargs)

echo $POSTGRES_PORT
echo "[$POSTGRES_PASSWORD]"

cd database_migrations

PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST --port $POSTGRES_PORT -U $POSTGRES_USER  -d postgres -f ./sql/01_init_app_db.sql 
PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST --port $POSTGRES_PORT -U $POSTGRES_USER  -d postgres -f ./sql/01_init_master_db.sql 
PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST --port $POSTGRES_PORT -U $POSTGRES_USER  -d postgres -f ./sql/02_app_schema.sql 
PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST --port $POSTGRES_PORT -U $POSTGRES_USER  -d postgres -f ./sql/02_master_schema.sql 
cd ..

python ./database_migrations/scripts/load_csv.py

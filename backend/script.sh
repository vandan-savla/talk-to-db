#!/bin/bash

# sudo apt update
# sudo apt install -y postgresql postgresql-contrib
export POSTGRES_MASTER_PASSWORD=$(cat .env | grep POSTGRES_MASTER_PASSWORD | cut -d '=' -f2 | tr -d '"' | tr -d "'" | tr -d '\r' | xargs)

echo "[$POSTGRES_MASTER_PASSWORD]"

cd database_migrations

PGPASSWORD=$POSTGRES_MASTER_PASSWORD psql -h dpg-d6tdb6pj16oc73f97o1g-a.oregon-postgres.render.com -U primary_backend_data_user -d postgres -f ./sql/01_init_app_db.sql 
PGPASSWORD=$POSTGRES_MASTER_PASSWORD psql -h dpg-d6tdb6pj16oc73f97o1g-a.oregon-postgres.render.com -U primary_backend_data_user -d postgres -f ./sql/01_init_master_db.sql 
PGPASSWORD=$POSTGRES_MASTER_PASSWORD psql -h dpg-d6tdb6pj16oc73f97o1g-a.oregon-postgres.render.com -U primary_backend_data_user -d postgres -f ./sql/02_app_schema.sql 
PGPASSWORD=$POSTGRES_MASTER_PASSWORD psql -h dpg-d6tdb6pj16oc73f97o1g-a.oregon-postgres.render.com -U primary_backend_data_user -d postgres -f ./sql/02_master_schema.sql 
cd ..

python ./database_migrations/scripts/load_csv.py

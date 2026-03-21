#!/bin/bash

sudo apt update
sudo apt install -y postgresql postgresql-contrib

cd database_migrations/sql

psql -U postgres -d postgres -p 5433 -f ./sql/01_init_app_db.sql --password admin
psql -U postgres -d postgres -p 5433 -f ./sql/01_init_master_db.sql --password admin
psql -U postgres -d postgres -p 5433 -f ./sql/02_app_schema.sql --password admin
psql -U postgres -d postgres -p 5433 -f ./sql/02_master_schema.sql --password admin

cd ../scripts

python3 load_csv.py

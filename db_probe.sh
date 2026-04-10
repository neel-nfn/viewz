#!/usr/bin/env bash
set -e
for PORT in 5433 54322 5432; do
  if PGPASSWORD=postgres psql -h localhost -p $PORT -U postgres -d postgres -c "select 1;" >/dev/null 2>&1; then
    echo "OK postgresql://postgres:postgres@localhost:$PORT/postgres"
    exit 0
  fi
done
echo "FAIL"
exit 1

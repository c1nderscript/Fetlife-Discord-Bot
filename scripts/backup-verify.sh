#!/usr/bin/env bash
set -euo pipefail

if ! command -v docker >/dev/null 2>&1; then
  echo "docker is required" >&2
  exit 1
fi

if [[ ${EUID:-$(id -u)} -eq 0 ]]; then
  echo "Warning: running backup verification as root" >&2
fi

container=backup-verify-db
backup=$(mktemp)
trap 'rm -f "$backup"; docker rm -f "$container" >/dev/null 2>&1 || true' EXIT

docker run -d --rm --name "$container" -e POSTGRES_PASSWORD=test postgres:15 >/dev/null

# wait for db
until docker exec "$container" pg_isready -U postgres >/dev/null 2>&1; do
  sleep 1
done

# create sample data
docker exec "$container" psql -U postgres -c 'CREATE DATABASE verify;'
docker exec "$container" psql -U postgres -d verify -c 'CREATE TABLE sample(id int primary key); INSERT INTO sample VALUES (1);'

# dump backup
docker exec "$container" pg_dump -U postgres verify > "$backup"

# drop and restore
docker exec "$container" psql -U postgres -c 'DROP DATABASE verify; CREATE DATABASE verify;'
docker exec -i "$container" psql -U postgres -d verify < "$backup"

# verify
if docker exec "$container" psql -U postgres -d verify -c 'SELECT count(*) FROM sample;' | grep -q 1; then
  echo "Backup restore and integrity check succeeded"
else
  echo "Verification query failed" >&2
  exit 1
fi
